"""
Flask API Debug Panel for Data Lake Exploration.
Provides web interface to view raw vs clean datasets.
"""
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import json
import subprocess
import sys
import threading
from typing import List, Dict
from datetime import datetime, timedelta

# Project directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW_DIR = os.path.join(BASE_DIR, 'raw')
CLEAN_DIR = os.path.join(BASE_DIR, 'clean')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
ANALYTICS_DIR = os.path.join(BASE_DIR, 'analytics')
FRONTEND_BUILD = os.path.join(BASE_DIR, 'frontend', 'build')
PIPELINE_CACHE_DIR = os.path.join(LOGS_DIR, 'pipeline_cache')
PIPELINE_BUFFER_DIR = os.path.join(LOGS_DIR, 'pipeline_buffer')

# Flask app + SocketIO
app = Flask(__name__, static_folder=FRONTEND_BUILD, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")


def count_lines(path: str) -> int:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def load_ndjson(path: str, limit: int = 100) -> List[Dict]:
    out = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= limit:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except Exception:
                    out.append({'raw': line})
    except FileNotFoundError:
        return []
    return out


# ---- Pipeline cache helpers ----
def ensure_pipeline_cache_dir():
    try:
        os.makedirs(PIPELINE_CACHE_DIR, exist_ok=True)
    except Exception:
        pass

def pipeline_cache_path(customer_id: str) -> str:
    ensure_pipeline_cache_dir()
    safe = customer_id.replace('/', '_')
    return os.path.join(PIPELINE_CACHE_DIR, f"{safe}_pipeline.json")

def load_pipeline_cache(customer_id: str) -> Dict:
    path = pipeline_cache_path(customer_id)
    if not os.path.exists(path):
        return {'customer_id': customer_id, 'logs': [], 'steps': {}, 'pipelineStatus': 'idle', 'last_updated': None}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {'customer_id': customer_id, 'logs': [], 'steps': {}, 'pipelineStatus': 'idle', 'last_updated': None}

def save_pipeline_cache(customer_id: str, state: Dict):
    path = pipeline_cache_path(customer_id)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception:
        # If writing fails (disk/DB disconnect etc), buffer state to a local queue for later flushing
        try:
            os.makedirs(PIPELINE_BUFFER_DIR, exist_ok=True)
            fname = f"buffer_{customer_id}_{datetime.utcnow().strftime('%Y%m%dT%H%M%S%f')}.json"
            bufpath = os.path.join(PIPELINE_BUFFER_DIR, fname)
            with open(bufpath, 'w', encoding='utf-8') as bf:
                json.dump({'target_path': path, 'state': state}, bf, ensure_ascii=False, indent=2)
            print(f"[WARN] save_pipeline_cache failed; buffered to {bufpath}")
        except Exception as e:
            print(f"[ERROR] Failed to buffer pipeline cache: {e}")

def append_cache_log(customer_id: str, level: str, message: str):
    state = load_pipeline_cache(customer_id)
    entry = {'timestamp': datetime.utcnow().isoformat() + 'Z', 'level': level, 'message': message}
    state.setdefault('logs', []).append(entry)
    # keep last 1000 logs
    state['logs'] = state['logs'][-1000:]
    state['last_updated'] = datetime.utcnow().isoformat() + 'Z'
    save_pipeline_cache(customer_id, state)

def update_cache_progress(customer_id: str, stepId: int, step: str, progress: int, status: str, pipelineStatus: str = None):
    state = load_pipeline_cache(customer_id)
    steps = state.setdefault('steps', {})
    steps[str(stepId)] = {'step': step, 'progress': progress, 'status': status}
    if pipelineStatus:
        state['pipelineStatus'] = pipelineStatus
    state['last_updated'] = datetime.utcnow().isoformat() + 'Z'
    save_pipeline_cache(customer_id, state)

def is_raw_dataset_present(customer_id: str) -> bool:
    # simple heuristic: check for any file in RAW_DIR starting with customer_id
    try:
        if not os.path.exists(RAW_DIR):
            return False
        for fn in os.listdir(RAW_DIR):
            if fn.startswith(customer_id + '_') or fn.startswith(customer_id):
                return True
    except Exception:
        return False
    return False


def _parse_iso_datetime(s: str):
    if not s:
        return None
    try:
        # Support naive ISO strings
        return datetime.fromisoformat(s.replace('Z', '+00:00'))
    except Exception:
        try:
            return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')
        except Exception:
            return None


def verify_consent_token(customer_id: str, token: str):
    """Verify token exists, matches cache, not expired, and not reused outside scope."""
    if not customer_id or not token:
        return False, 'customer_id and token required'

    cache = load_pipeline_cache(customer_id)
    stored = cache.get('consent_token')
    status = cache.get('consent_status')
    if not stored or stored != token:
        return False, 'invalid_token'
    if status != 'APPROVED':
        return False, 'consent_not_approved'

    # expiry check
    consent_expiry = cache.get('consent_expiry')
    if consent_expiry:
        dt = _parse_iso_datetime(consent_expiry)
        if dt and datetime.utcnow() > dt.replace(tzinfo=None):
            return False, 'token_expired'

    # ONETIME reuse check
    fetch_type = cache.get('fetch_type')
    if fetch_type == 'ONETIME' and cache.get('token_used'):
        return False, 'token_already_used'

    # token is valid
    return True, 'ok'


def mark_token_used(customer_id: str):
    state = load_pipeline_cache(customer_id)
    state['token_used'] = True
    state['last_updated'] = datetime.utcnow().isoformat() + 'Z'
    save_pipeline_cache(customer_id, state)


def flush_pipeline_buffer_once():
    """Try to flush any buffered pipeline cache items to their target paths."""
    if not os.path.exists(PIPELINE_BUFFER_DIR):
        return 0
    flushed = 0
    for fn in sorted(os.listdir(PIPELINE_BUFFER_DIR)):
        fp = os.path.join(PIPELINE_BUFFER_DIR, fn)
        try:
            with open(fp, 'r', encoding='utf-8') as f:
                obj = json.load(f)
            target = obj.get('target_path')
            state = obj.get('state')
            append_mode = obj.get('append', False)
            records = obj.get('records')
            if not target or state is None:
                # malformed buffer, remove
                os.remove(fp)
                continue
            # ensure dir exists and write
            os.makedirs(os.path.dirname(target), exist_ok=True)
            if append_mode and isinstance(records, list):
                # append each record as ndjson
                try:
                    with open(target, 'a', encoding='utf-8') as tf:
                        for rec in records:
                            tf.write(json.dumps(rec, ensure_ascii=False) + '\n')
                except Exception:
                    # append failed; keep file for later retry
                    print(f"[WARN] Append to {target} failed during flush; will retry later")
                    continue
            else:
                with open(target, 'w', encoding='utf-8') as tf:
                    json.dump(state, tf, ensure_ascii=False, indent=2)
            os.remove(fp)
            flushed += 1
            print(f"[INFO] Flushed buffered pipeline cache to {target}")
        except Exception as e:
            print(f"[WARN] Failed to flush buffer file {fp}: {e}")
            # keep file for later retry
            continue
    return flushed


def _buffer_flush_worker():
    import time
    while True:
        try:
            cnt = flush_pipeline_buffer_once()
            if cnt:
                print(f"[INFO] Flushed {cnt} buffered pipeline cache items")
        except Exception as e:
            print(f"[ERROR] Buffer flush worker exception: {e}")
        time.sleep(int(os.environ.get('PIPELINE_BUFFER_FLUSH_INTERVAL', '30')))


@app.route('/api/flush-buffer', methods=['POST'])
def flush_buffer_endpoint():
    """Manual trigger to flush buffered pipeline cache items."""
    try:
        flushed = flush_pipeline_buffer_once()
        return jsonify({'flushed': flushed}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# start background flush worker
try:
    os.makedirs(PIPELINE_BUFFER_DIR, exist_ok=True)
    t_buf = threading.Thread(target=_buffer_flush_worker, daemon=True)
    t_buf.start()
    print(f"[INFO] Started pipeline buffer flush worker (dir={PIPELINE_BUFFER_DIR})")
except Exception:
    print("[WARN] Could not start pipeline buffer flush worker")


@app.route('/api/data/<dataset>')
def get_data(dataset):
    """Return raw/clean NDJSON snippets for a dataset."""
    print(f"\n[REQUEST] GET /api/data/{dataset}")
    data_type = request.args.get('type', 'raw')
    limit = int(request.args.get('limit', 100))

    file_map = {
        'transactions': 'transactions',
        'accounts': 'accounts',
        'gst': 'gst',
        'credit_reports': 'credit_reports',
        'policies': 'policies',
        'mutual_funds': 'mutual_funds',
        'ondc_orders': 'ondc_orders',
        'ocen_applications': 'ocen_applications',
        'consent': 'consent'
    }

    if dataset not in file_map:
        print(f"  [ERROR] Invalid dataset: {dataset}")
        return jsonify({'error': 'Invalid dataset'}), 400

    if data_type == 'raw':
        filepath = os.path.join(RAW_DIR, f'raw_{file_map[dataset]}.ndjson')
    else:
        filepath = os.path.join(CLEAN_DIR, f'{file_map[dataset]}_clean.ndjson')

    data = load_ndjson(filepath, limit)

    if not data:
        return jsonify({
            'dataset': dataset,
            'type': data_type,
            'count': 0,
            'data': [],
            'error': 'No data found. Have you generated the dataset yet?'
        })

    return jsonify({
        'dataset': dataset,
        'type': data_type,
        'count': len(data),
        'data': data
    })
    
    data = load_ndjson(filepath, limit)
    
    if not data:
        return jsonify({
            'dataset': dataset,
            'type': data_type,
            'count': 0,
            'data': [],
            'error': 'No data found. Have you generated the dataset yet?'
        })
    
    return jsonify({
        'dataset': dataset,
        'type': data_type,
        'count': len(data),
        'data': data
    })


@app.route('/api/logs/<log_type>')
def get_logs(log_type):
    """Get transformation logs."""
    print(f"\n[REQUEST] GET /api/logs/{log_type}")
    
    log_files = {
        'parsing': 'transaction_parsing_log.json',
        'cleaning': 'transaction_cleaning_log.json',
        'validation': 'transaction_validation_errors.json'
    }
    
    log_file = log_files.get(log_type)
    if not log_file:
        print(f"  [ERROR] Invalid log type: {log_type}")
        return jsonify({'error': 'Invalid log type'}), 400
    
    filepath = os.path.join(LOGS_DIR, log_file)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"  [✓] Loaded {len(data)} log entries")
        return jsonify(data[:100])  # Limit to 100 entries
    except FileNotFoundError:
        print(f"  [!] Log file not found: {filepath}")
        return jsonify({'error': 'Log file not found. Have you run the cleaning pipeline?'}), 404


@app.route('/api/stats')
def get_stats():
    """Get overall statistics."""
    print("\n[REQUEST] GET /api/stats")
    
    datasets = {
        'transactions': 'raw_transactions.ndjson',
        'accounts': 'raw_accounts.ndjson',
        'gst': 'raw_gst.ndjson',
        'credit_reports': 'raw_credit_reports.ndjson',
        'policies': 'raw_policies.ndjson',
        'mutual_funds': 'raw_mutual_funds.ndjson',
        'ondc_orders': 'raw_ondc_orders.ndjson',
        'ocen_applications': 'raw_ocen_applications.ndjson',
        'consent': 'raw_consent.ndjson'
    }
    
    stats = {
        'total_raw_records': 0,
        'total_clean_records': 0,
        'datasets': {}
    }
    
    for dataset, filename in datasets.items():
        raw_path = os.path.join(RAW_DIR, filename)
        # derive clean filename from raw file name (raw_xxx.ndjson -> xxx_clean.ndjson)
        base = filename
        if base.startswith('raw_'):
            base = base[len('raw_'):]
        base = base.replace('.ndjson', '')
        clean_filename = f"{base}_clean.ndjson"
        clean_path = os.path.join(CLEAN_DIR, clean_filename)

        raw_count = count_lines(raw_path)
        clean_count = count_lines(clean_path)

        stats['datasets'][dataset] = {
            'raw': raw_count,
            'clean': clean_count
        }

        stats['total_raw_records'] += raw_count
        stats['total_clean_records'] += clean_count
    
    print(f"  [✓] Total raw records: {stats['total_raw_records']:,}")
    print(f"  [✓] Total clean records: {stats['total_clean_records']:,}")
    
    return jsonify(stats)


# ===== PIPELINE CONTROL ENDPOINTS =====

@app.route('/api/pipeline/generate', methods=['POST'])
def run_generate():
    """Start data generation pipeline."""
    print("\n[REQUEST] POST /api/pipeline/generate")
    print("  [DEBUG] Preparing to start data generation pipeline")
    # Enforce per-customer execution: require `customer_id` in POST JSON or query
    payload = request.get_json(silent=True) or {}
    customer_id = payload.get('customer_id') or request.args.get('customer_id')
    if not customer_id:
        print("  [SECURITY] Rejecting generate pipeline call without customer_id")
        return jsonify({'error': 'Generation must be requested per-customer. Provide customer_id.'}), 400

    # Require consent token for generation
    token = payload.get('token') or request.args.get('token')
    ok, reason = verify_consent_token(customer_id, token)
    if not ok:
        print(f"  [SECURITY] Consent verification failed for generate: {reason}")
        return jsonify({'error': 'Consent verification failed', 'reason': reason}), 403
    # Mark token used immediately for ONETIME fetches
    cache = load_pipeline_cache(customer_id)
    if cache.get('fetch_type') == 'ONETIME':
        mark_token_used(customer_id)
    
    def run_generation():
        print("  [DEBUG] Generation thread started")
        socketio.emit('pipeline_log', {'level': 'info', 'message': 'Starting data generation pipeline...', 'timestamp': str(datetime.now())})
        append_cache_log(customer_id, 'info', 'Starting data generation pipeline...')
        socketio.emit('pipeline_progress', {'stepId': 1, 'step': 'generate', 'progress': 0, 'status': 'running', 'pipelineStatus': 'running'})
        update_cache_progress(customer_id, 1, 'generate', 0, 'running', 'running')
        socketio.sleep(0.1)
        
        try:
            # Run generate_all.py
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUNBUFFERED'] = '1'
            print("  [DEBUG] Executing generate_all.py with UTF-8 encoding")
            
            socketio.emit('pipeline_log', {'level': 'info', 'message': f'Executing: {sys.executable} generate_all.py --customer-id {customer_id}', 'timestamp': str(datetime.now())})
            append_cache_log(customer_id, 'info', f'Executing: {sys.executable} generate_all.py --customer-id {customer_id}')
            socketio.emit('pipeline_progress', {'stepId': 1, 'step': 'generate', 'progress': 25, 'status': 'running'})
            update_cache_progress(customer_id, 1, 'generate', 25, 'running')
            socketio.sleep(0.1)
            
            # call generator in per-customer mode
            cmd = [sys.executable, os.path.join(BASE_DIR, 'generate_all.py'), '--customer-id', str(customer_id)]
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=0,
                env=env,
                cwd=BASE_DIR,
                universal_newlines=True
            )

            # Stream stdout/stderr lines in real-time
            while True:
                line = proc.stdout.readline()
                if not line and proc.poll() is not None:
                    break
                if line:
                    line = line.rstrip('\n\r')
                    if line.strip():
                        socketio.emit('pipeline_log', {'level': 'info', 'message': f'  {line}', 'timestamp': str(datetime.now())})
                        append_cache_log(customer_id, 'info', line)
                        print(f"  [PROC] {line}")
                        socketio.sleep(0.01)

            rc = proc.wait()
            socketio.emit('pipeline_progress', {'stepId': 1, 'step': 'generate', 'progress': 75, 'status': 'running'})
            update_cache_progress(customer_id, 1, 'generate', 75, 'running')
            socketio.sleep(0.1)

            if rc == 0:
                print("  [DEBUG] Generation completed successfully")
                socketio.emit('pipeline_log', {'level': 'success', 'message': 'Data generation completed successfully!', 'timestamp': str(datetime.now())})
                append_cache_log(customer_id, 'success', 'Data generation completed successfully!')
                socketio.emit('pipeline_log', {'level': 'info', 'message': f'Generated files in: {RAW_DIR}', 'timestamp': str(datetime.now())})
                append_cache_log(customer_id, 'info', f'Generated files in: {RAW_DIR}')
                socketio.emit('pipeline_progress', {'stepId': 1, 'step': 'generate', 'progress': 100, 'status': 'completed', 'pipelineStatus': 'idle'})
                update_cache_progress(customer_id, 1, 'generate', 100, 'completed', 'idle')
            else:
                print(f"  [DEBUG] Generation failed with return code {rc}")
                socketio.emit('pipeline_log', {'level': 'error', 'message': f'Generation failed with code {rc}', 'timestamp': str(datetime.now())})
                append_cache_log(customer_id, 'error', f'Generation failed with code {rc}')
                socketio.emit('pipeline_progress', {'stepId': 1, 'step': 'generate', 'progress': 0, 'status': 'failed', 'pipelineStatus': 'idle'})
                update_cache_progress(customer_id, 1, 'generate', 0, 'failed', 'idle')
        except Exception as e:
            print(f"  [DEBUG] Exception in generation: {str(e)}")
            import traceback
            traceback.print_exc()
            socketio.emit('pipeline_log', {'level': 'error', 'message': f'Exception: {str(e)}', 'timestamp': str(datetime.now())})
            append_cache_log(customer_id, 'error', f'Exception: {str(e)}')
            socketio.emit('pipeline_progress', {'stepId': 1, 'step': 'generate', 'progress': 0, 'status': 'failed', 'pipelineStatus': 'idle'})
            update_cache_progress(customer_id, 1, 'generate', 0, 'failed', 'idle')
    
    # Run generation as a socketio background task so emits run in eventlet context
    try:
        socketio.start_background_task(run_generation)
        print("  [DEBUG] Generation background task launched via socketio")
    except Exception:
        th = threading.Thread(target=run_generation)
        th.daemon = True
        th.start()
        print("  [WARN] socketio.start_background_task failed; launched plain thread")
    
    return jsonify({'status': 'started', 'message': 'Data generation pipeline started'})


@app.route('/api/pipeline/state', methods=['GET'])
def pipeline_state():
    """Return cached pipeline state and whether raw dataset exists for a customer."""
    customer_id = request.args.get('customer_id')
    if not customer_id and request.is_json:
        customer_id = (request.get_json(silent=True) or {}).get('customer_id')
    if not customer_id:
        return jsonify({'error': 'customer_id required'}), 400
    cache = load_pipeline_cache(customer_id)
    raw_present = is_raw_dataset_present(customer_id)
    return jsonify({'customer_id': customer_id, 'cache': cache, 'raw_present': raw_present})


@app.route('/api/request-consent', methods=['POST'])
def request_consent():
    """Simulate user consent approval and return a success token."""
    print("\n[REQUEST] POST /api/request-consent")
    payload = request.get_json(silent=True) or {}
    customer_id = payload.get('customer_id') or request.args.get('customer_id')
    if not customer_id:
        print("  [ERROR] Missing customer_id")
        return jsonify({'error': 'customer_id required'}), 400
    
    # Accept optional consent metadata from payload
    payload_fields = {}
    for k in ('consent_id', 'data_from', 'data_to', 'consent_types', 'fip_ids', 'consent_mode', 'frequency_unit', 'fetch_type', 'consent_expiry'):
        if k in payload:
            payload_fields[k] = payload.get(k)

    # Generate consent token
    import time
    token = f"CONSENT-{customer_id}-{int(time.time() * 1000)}"

    # Default expiry: 24 hours if not provided
    if 'consent_expiry' not in payload_fields or not payload_fields.get('consent_expiry'):
        expiry_dt = datetime.utcnow() + timedelta(hours=24)
        payload_fields['consent_expiry'] = expiry_dt.isoformat() + 'Z'

    # Store token and consent metadata in pipeline cache
    state = load_pipeline_cache(customer_id)
    state['consent_token'] = token
    state['consent_status'] = 'APPROVED'
    state['consent_timestamp'] = datetime.utcnow().isoformat() + 'Z'
    state['token_created_at'] = datetime.utcnow().isoformat() + 'Z'
    state['token_used'] = False
    # store provided metadata (scope)
    state.setdefault('consent_scope', {}).update(payload_fields)
    # also mirror some top-level keys for convenience
    state['consent_expiry'] = payload_fields.get('consent_expiry')
    state['frequency_unit'] = payload_fields.get('frequency_unit')
    state['fetch_type'] = payload_fields.get('fetch_type')
    save_pipeline_cache(customer_id, state)
    
    # Log to terminal and socketio
    print(f"  [CONSENT] ✓ APPROVED for {customer_id}")
    print(f"  [TOKEN] {token}")
    socketio.emit('pipeline_log', {
        'level': 'success',
        'message': f'Consent APPROVED for {customer_id}',
        'timestamp': str(datetime.utcnow())
    })
    socketio.emit('pipeline_log', {
        'level': 'info',
        'message': f'Token: {token}',
        'timestamp': str(datetime.utcnow())
    })
    append_cache_log(customer_id, 'success', f'Consent APPROVED for {customer_id}')
    append_cache_log(customer_id, 'info', f'Token: {token}')
    
    return jsonify({
        'status': 'success',
        'token': token,
        'customer_id': customer_id,
        'message': 'Consent approved successfully'
    }), 200


@app.route('/api/pipeline/clean', methods=['POST'])
def run_clean():
    """Start data cleaning pipeline."""
    print("\n[REQUEST] POST /api/pipeline/clean")
    print("  [DEBUG] Preparing to start data cleaning pipeline")
    # Enforce per-customer execution
    payload = request.get_json(silent=True) or {}
    customer_id = payload.get('customer_id') or request.args.get('customer_id')
    if not customer_id:
        print("  [SECURITY] Rejecting clean pipeline call without customer_id")
        return jsonify({'error': 'Cleaning must be requested per-customer. Provide customer_id.'}), 400

    # Require consent token for cleaning
    token = payload.get('token') or request.args.get('token')
    ok, reason = verify_consent_token(customer_id, token)
    if not ok:
        print(f"  [SECURITY] Consent verification failed for clean: {reason}")
        return jsonify({'error': 'Consent verification failed', 'reason': reason}), 403
    if load_pipeline_cache(customer_id).get('fetch_type') == 'ONETIME':
        mark_token_used(customer_id)
    
    def run_cleaning():
        print("  [DEBUG] Cleaning thread started")
        socketio.emit('pipeline_log', {'level': 'info', 'message': 'Starting data cleaning pipeline...', 'timestamp': str(datetime.now())})
        append_cache_log(customer_id, 'info', 'Starting data cleaning pipeline...')
        socketio.emit('pipeline_progress', {'stepId': 2, 'step': 'clean', 'progress': 0, 'status': 'running', 'pipelineStatus': 'running'})
        update_cache_progress(customer_id, 2, 'clean', 0, 'running', 'running')
        socketio.sleep(0.1)
        
        try:
            # Run clean_data.py
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUNBUFFERED'] = '1'
            print("  [DEBUG] Executing clean_data.py with UTF-8 encoding")
            
            socketio.emit('pipeline_log', {'level': 'info', 'message': 'Executing: python pipeline/clean_data.py', 'timestamp': str(datetime.now())})
            append_cache_log(customer_id, 'info', 'Executing: python pipeline/clean_data.py')
            socketio.emit('pipeline_progress', {'stepId': 2, 'step': 'clean', 'progress': 25, 'status': 'running'})
            update_cache_progress(customer_id, 2, 'clean', 25, 'running')
            socketio.sleep(0.1)
            
            cmd = [sys.executable, os.path.join(BASE_DIR, 'pipeline', 'clean_data.py'), '--customer-id', str(customer_id)]
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=0,
                env=env,
                cwd=BASE_DIR,
                universal_newlines=True
            )

            while True:
                line = proc.stdout.readline()
                if not line and proc.poll() is not None:
                    break
                if line:
                    line = line.rstrip('\n\r')
                    if line.strip():
                        socketio.emit('pipeline_log', {'level': 'info', 'message': f'  {line}', 'timestamp': str(datetime.now())})
                        append_cache_log(customer_id, 'info', line)
                        print(f"  [PROC] {line}")
                        socketio.sleep(0.01)

            rc = proc.wait()
            socketio.emit('pipeline_progress', {'stepId': 2, 'step': 'clean', 'progress': 75, 'status': 'running'})
            update_cache_progress(customer_id, 2, 'clean', 75, 'running')
            socketio.sleep(0.1)

            if rc == 0:
                print("  [DEBUG] Cleaning completed successfully")
                socketio.emit('pipeline_log', {'level': 'success', 'message': 'Data cleaning completed successfully!', 'timestamp': str(datetime.now())})
                append_cache_log(customer_id, 'success', 'Data cleaning completed successfully!')
                socketio.emit('pipeline_log', {'level': 'info', 'message': f'Cleaned files in: {CLEAN_DIR}', 'timestamp': str(datetime.now())})
                append_cache_log(customer_id, 'info', f'Cleaned files in: {CLEAN_DIR}')
                socketio.emit('pipeline_log', {'level': 'info', 'message': f'Logs generated in: {LOGS_DIR}', 'timestamp': str(datetime.now())})
                append_cache_log(customer_id, 'info', f'Logs generated in: {LOGS_DIR}')
                socketio.emit('pipeline_progress', {'stepId': 2, 'step': 'clean', 'progress': 100, 'status': 'completed', 'pipelineStatus': 'idle'})
                update_cache_progress(customer_id, 2, 'clean', 100, 'completed', 'idle')
            else:
                print(f"  [DEBUG] Cleaning failed with return code {rc}")
                socketio.emit('pipeline_log', {'level': 'error', 'message': f'Cleaning failed with code {rc}', 'timestamp': str(datetime.now())})
                append_cache_log(customer_id, 'error', f'Cleaning failed with code {rc}')
                socketio.emit('pipeline_progress', {'stepId': 2, 'step': 'clean', 'progress': 0, 'status': 'failed', 'pipelineStatus': 'idle'})
                update_cache_progress(customer_id, 2, 'clean', 0, 'failed', 'idle')
        except Exception as e:
            print(f"  [DEBUG] Exception in cleaning: {str(e)}")
            import traceback
            traceback.print_exc()
            socketio.emit('pipeline_log', {'level': 'error', 'message': f'Exception: {str(e)}', 'timestamp': str(datetime.now())})
            append_cache_log(customer_id, 'error', f'Exception: {str(e)}')
            socketio.emit('pipeline_progress', {'stepId': 2, 'step': 'clean', 'progress': 0, 'status': 'failed', 'pipelineStatus': 'idle'})
            update_cache_progress(customer_id, 2, 'clean', 0, 'failed', 'idle')
    
    # Run cleaning as a socketio background task so emits run in eventlet context
    try:
        socketio.start_background_task(run_cleaning)
        print("  [DEBUG] Cleaning background task launched via socketio")
    except Exception:
        th = threading.Thread(target=run_cleaning)
        th.daemon = True
        th.start()
        print("  [WARN] socketio.start_background_task failed; launched plain thread")
    
    return jsonify({'status': 'started', 'message': 'Data cleaning pipeline started'})


@app.route('/api/pipeline/analytics', methods=['POST'])
def run_analytics():
    """Start analytics generation pipeline."""
    print("\n[REQUEST] POST /api/pipeline/analytics")
    print("  [DEBUG] Preparing to start analytics generation pipeline")
    # Enforce per-customer execution
    payload = request.get_json(silent=True) or {}
    customer_id = payload.get('customer_id') or request.args.get('customer_id')
    token = payload.get('token') or request.args.get('token')
    
    if not customer_id:
        print("  [SECURITY] Rejecting analytics pipeline call without customer_id")
        return jsonify({'error': 'Analytics must be requested per-customer. Provide customer_id.'}), 400

    # Require consent token for analytics
    if not token:
        return jsonify({'error': 'token required for analytics'}), 403

    ok, reason = verify_consent_token(customer_id, token)
    if not ok:
        print(f"  [SECURITY] Consent verification failed for analytics: {reason}")
        return jsonify({'error': 'Consent verification failed', 'reason': reason}), 403
    # mark used for ONETIME
    if load_pipeline_cache(customer_id).get('fetch_type') == 'ONETIME':
        mark_token_used(customer_id)
    
    def run_analytics_gen():
        print("  [DEBUG] Analytics thread started")
        socketio.emit('pipeline_log', {'level': 'info', 'message': 'Starting analytics generation pipeline...', 'timestamp': str(datetime.now())})
        append_cache_log(customer_id, 'info', 'Starting analytics generation pipeline...')
        socketio.emit('pipeline_progress', {'stepId': 3, 'step': 'analytics', 'progress': 0, 'status': 'running', 'pipelineStatus': 'running'})
        update_cache_progress(customer_id, 3, 'analytics', 0, 'running', 'running')
        socketio.sleep(0.1)
        
        try:
            # Run generate_summaries.py
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUNBUFFERED'] = '1'
            print("  [DEBUG] Executing generate_summaries.py with UTF-8 encoding")
            
            socketio.emit('pipeline_log', {'level': 'info', 'message': 'Executing: python analytics/generate_summaries.py', 'timestamp': str(datetime.now())})
            append_cache_log(customer_id, 'info', 'Executing: python analytics/generate_summaries.py')
            socketio.emit('pipeline_progress', {'stepId': 3, 'step': 'analytics', 'progress': 25, 'status': 'running'})
            update_cache_progress(customer_id, 3, 'analytics', 25, 'running')
            socketio.sleep(0.1)
            
            cmd = [sys.executable, os.path.join(BASE_DIR, 'analytics', 'generate_summaries.py'), '--customer-id', str(customer_id)]
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=0,
                env=env,
                cwd=BASE_DIR,
                universal_newlines=True
            )

            while True:
                line = proc.stdout.readline()
                if not line and proc.poll() is not None:
                    break
                if line:
                    line = line.rstrip('\n\r')
                    if line.strip():
                        socketio.emit('pipeline_log', {'level': 'info', 'message': f'  {line}', 'timestamp': str(datetime.now())})
                        append_cache_log(customer_id, 'info', line)
                        print(f"  [PROC] {line}")
                        socketio.sleep(0.01)

            rc = proc.wait()
            socketio.emit('pipeline_progress', {'stepId': 3, 'step': 'analytics', 'progress': 75, 'status': 'running'})
            update_cache_progress(customer_id, 3, 'analytics', 75, 'running')
            socketio.sleep(0.1)

            if rc == 0:
                print("  [DEBUG] Analytics completed successfully")
                socketio.emit('pipeline_log', {'level': 'success', 'message': 'Analytics generation completed successfully!', 'timestamp': str(datetime.now())})
                append_cache_log(customer_id, 'success', 'Analytics generation completed successfully!')
                socketio.emit('pipeline_log', {'level': 'info', 'message': f'Analytics files in: {ANALYTICS_DIR}', 'timestamp': str(datetime.now())})
                append_cache_log(customer_id, 'info', f'Analytics files in: {ANALYTICS_DIR}')
                socketio.emit('pipeline_progress', {'stepId': 3, 'step': 'analytics', 'progress': 100, 'status': 'completed', 'pipelineStatus': 'idle'})
                update_cache_progress(customer_id, 3, 'analytics', 100, 'completed', 'idle')
            else:
                print(f"  [DEBUG] Analytics failed with return code {rc}")
                socketio.emit('pipeline_log', {'level': 'error', 'message': f'Analytics failed with code {rc}', 'timestamp': str(datetime.now())})
                append_cache_log(customer_id, 'error', f'Analytics failed with code {rc}')
                socketio.emit('pipeline_progress', {'stepId': 3, 'step': 'analytics', 'progress': 0, 'status': 'failed', 'pipelineStatus': 'idle'})
                update_cache_progress(customer_id, 3, 'analytics', 0, 'failed', 'idle')
        except Exception as e:
            print("  [DEBUG] Exception in analytics: {str(e)}")
            import traceback
            traceback.print_exc()
            socketio.emit('pipeline_log', {'level': 'error', 'message': f'Exception: {str(e)}', 'timestamp': str(datetime.now())})
            append_cache_log(customer_id, 'error', f'Exception: {str(e)}')
            socketio.emit('pipeline_progress', {'stepId': 3, 'step': 'analytics', 'progress': 0, 'status': 'failed', 'pipelineStatus': 'idle'})
            update_cache_progress(customer_id, 3, 'analytics', 0, 'failed', 'idle')
    
    # Run analytics as a socketio background task so emits run in eventlet context
    try:
        socketio.start_background_task(run_analytics_gen)
        print("  [DEBUG] Analytics background task launched via socketio")
    except Exception:
        # fallback to plain thread if start_background_task not available
        th = threading.Thread(target=run_analytics_gen)
        th.daemon = True
        th.start()
        print("  [WARN] socketio.start_background_task failed; launched plain thread")
    
    return jsonify({'status': 'started', 'message': 'Analytics generation pipeline started'})


# ===== ANALYTICS ENDPOINTS =====

@app.route('/api/analytics')
def get_analytics():
    """Get all analytics summaries for a specific customer including all data sources."""
    customer_id = request.args.get('customer_id', 'CUST_MSM_00001')
    print(f"\n[REQUEST] GET /api/analytics?customer_id={customer_id}")
    
    analytics_files = {
        'overall': f'{customer_id}_overall_summary.json',
        'transactions': f'{customer_id}_transaction_summary.json',
        'gst': f'{customer_id}_gst_summary.json',
        'credit': f'{customer_id}_credit_summary.json',
        'anomalies': f'{customer_id}_anomalies_report.json',
        'mutual_funds': f'{customer_id}_mutual_funds_summary.json',
        'insurance': f'{customer_id}_insurance_summary.json',
        'ocen': f'{customer_id}_ocen_summary.json',
        'ondc': f'{customer_id}_ondc_summary.json'
    }
    
    analytics_data = {}

    for key, filename in analytics_files.items():
        filepath = os.path.join(ANALYTICS_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                analytics_data[key] = json.load(f)
            print(f"  [✓] Loaded {filename}")
        except FileNotFoundError:
            print(f"  [!] File not found: {filename}")
            analytics_data[key] = None
        except Exception as e:
            print(f"  [ERROR] Failed to load {filename}: {str(e)}")
            analytics_data[key] = {'error': str(e)}

    # Raw pieces
    overall_raw = analytics_data.get('overall') or {}
    transactions_raw = analytics_data.get('transactions') or {}
    gst_raw = analytics_data.get('gst') or {}
    credit_raw = analytics_data.get('credit') or {}
    anomalies_raw = analytics_data.get('anomalies') or {}
    mf_raw = analytics_data.get('mutual_funds') or {}
    insurance_raw = analytics_data.get('insurance') or {}
    ocen_raw = analytics_data.get('ocen') or {}
    ondc_raw = analytics_data.get('ondc') or {}

    # Normalize into the structure expected by the frontend
    normalized = {}

    # Overall - use from file or construct
    normalized['overall'] = overall_raw if overall_raw else {
        'total_records': transactions_raw.get('total_transactions', 0),
        'datasets_count': sum(1 for v in [transactions_raw, gst_raw, credit_raw, mf_raw, insurance_raw, ocen_raw, ondc_raw] if v),
        'total_accounts': credit_raw.get('open_loans', 0),
        'datasets': overall_raw.get('datasets', {})
    }

    # Transactions - use from file
    normalized['transactions'] = transactions_raw

    # GST - use from file
    normalized['gst'] = gst_raw

    # Credit - use from file
    normalized['credit'] = credit_raw

    # Anomalies - use from file
    normalized['anomalies'] = anomalies_raw

    # New data sources
    normalized['mutual_funds'] = mf_raw
    normalized['insurance'] = insurance_raw
    normalized['ocen'] = ocen_raw
    normalized['ondc'] = ondc_raw

    print(f"  [✓] Analytics data loaded for customer={customer_id}")
    print(f"      - Transactions: {transactions_raw.get('total_transactions', 0)}")
    print(f"      - GST: {gst_raw.get('returns_count', 0)}")
    print(f"      - Mutual Funds: {mf_raw.get('total_portfolios', 0)}")
    print(f"      - Insurance: {insurance_raw.get('total_policies', 0)}")
    print(f"      - OCEN: {ocen_raw.get('total_applications', 0)}")
    print(f"      - ONDC: {ondc_raw.get('total_orders', 0)}")
    return jsonify(normalized)


@app.route('/api/customer-profile')
def get_customer_profile():
    """Get complete customer profile with all available data sources."""
    customer_id = request.args.get('customer_id', 'CUST_MSM_00001')
    print(f"\n[REQUEST] GET /api/customer-profile?customer_id={customer_id}")
    
    analytics_files = {
        'overall': f'{customer_id}_overall_summary.json',
        'transactions': f'{customer_id}_transaction_summary.json',
        'gst': f'{customer_id}_gst_summary.json',
        'credit': f'{customer_id}_credit_summary.json',
        'anomalies': f'{customer_id}_anomalies_report.json',
        'mutual_funds': f'{customer_id}_mutual_funds_summary.json',
        'insurance': f'{customer_id}_insurance_summary.json',
        'ocen': f'{customer_id}_ocen_summary.json',
        'ondc': f'{customer_id}_ondc_summary.json',
        'earnings_spendings': f'{customer_id}_earnings_spendings.json'
        # Note: smart_collect is computed dynamically from /api/smart-collect endpoint (no file)
    }
    
    profile_data = {
        'customer_id': customer_id,
        'loaded_at': datetime.utcnow().isoformat() + 'Z',
        'data_sources': {}
    }

    for key, filename in analytics_files.items():
        filepath = os.path.join(ANALYTICS_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                profile_data['data_sources'][key] = json.load(f)
            print(f"  [✓] Loaded {filename}")
        except FileNotFoundError:
            print(f"  [!] File not found: {filename}")
            profile_data['data_sources'][key] = None
        except Exception as e:
            print(f"  [ERROR] Failed to load {filename}: {str(e)}")
            profile_data['data_sources'][key] = {'error': str(e)}

    print(f"  [✓] Customer profile loaded for {customer_id}")
    return jsonify(profile_data)


@app.route('/api/earnings-spendings')
def get_earnings_spendings():
    """Get earnings vs spendings financial metrics for a specific customer."""
    customer_id = request.args.get('customer_id', 'CUST_MSM_00001')
    print(f"\n[REQUEST] GET /api/earnings-spendings?customer_id={customer_id}")
    
    filename = f'{customer_id}_earnings_spendings.json'
    filepath = os.path.join(ANALYTICS_DIR, filename)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"  [✓] Loaded {filename}")
        return jsonify(data)
    except FileNotFoundError:
        print(f"  [!] File not found: {filename}")
        return jsonify({'error': f'Earnings vs Spendings data not found for {customer_id}. Please generate analytics first.'}), 404
    except Exception as e:
        print(f"  [ERROR] Failed to load {filename}: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# SMART COLLECT - Computed from Original AA Data (No Separate Dataset)
# ============================================================================

def calculate_collection_summary(collection_history, upcoming_collections):
    """Calculate collection summary metrics from history and upcoming collections"""
    successful = [h for h in collection_history if h['status'] == 'SUCCESS']
    failed = [h for h in collection_history if h['status'] == 'FAILED']
    
    total_attempts = len(collection_history)
    successful_count = len(successful)
    failed_count = len(failed)
    
    success_rate = (successful_count / total_attempts * 100) if total_attempts > 0 else 0
    
    # Calculate total amounts
    total_collected = sum(h['emi_amount'] for h in successful)
    total_pending = sum(c['emi_amount'] for c in upcoming_collections)
    
    # Calculate cost savings (₹50 per automated success vs ₹200 manual)
    automated_savings = successful_count * 150  # Saved ₹150 per automated collection
    
    # Average retry count (simplified - assume 1 for success, 2 for failed)
    avg_retry = (successful_count * 1 + failed_count * 2) / total_attempts if total_attempts > 0 else 0
    
    return {
        'total_emis_scheduled': len(upcoming_collections),
        'successful_collections': successful_count,
        'failed_collections': failed_count,
        'pending_collections': len(upcoming_collections),
        'collection_success_rate': round(success_rate, 2),
        'total_amount_collected': round(total_collected, 2),
        'total_amount_pending': round(total_pending, 2),
        'cost_saved': automated_savings,
        'average_retry_count': round(avg_retry, 2)
    }


def compute_smart_collect_analytics(customer_id, earnings_data, transactions_data, credit_data):
    """
    Compute Smart Collect analytics dynamically from original AA data.
    Acts as Account Aggregator - single source of truth.
    """
    import random
    from datetime import datetime, timedelta
    
    # Extract cashflow metrics from earnings
    cashflow = earnings_data.get('cashflow_metrics', {})
    monthly_inflow = cashflow.get('monthly_inflow', {})
    monthly_outflow = cashflow.get('monthly_outflow', {})
    
    # Analyze salary pattern
    salary_pattern = analyze_salary_credit_pattern(cashflow, monthly_inflow)
    
    # Analyze spending pattern
    spending_pattern = analyze_customer_spending(cashflow, monthly_outflow)
    
    # Generate collection schedule based on salary pattern
    upcoming_collections = generate_collection_schedule(salary_pattern, credit_data)
    
    # Generate behavioral insights
    behavioral_insights = {
        'salary_credit_pattern': salary_pattern,
        'spending_pattern': spending_pattern,
        'account_stability': {
            'income_cv': salary_pattern.get('income_cv', 0),
            'balance_volatility': 'High' if salary_pattern.get('income_cv', 0) > 100 else 'Medium' if salary_pattern.get('income_cv', 0) > 50 else 'Low',
            'surplus_ratio': cashflow.get('surplus_ratio', 0)
        }
    }
    
    # Generate recommendations
    recommendations = generate_collection_recommendations(salary_pattern, spending_pattern, cashflow)
    
    # Generate risk signals
    risk_signals = generate_risk_signals(salary_pattern, spending_pattern, cashflow)
    
    # Simulate collection history
    collection_history = generate_collection_history(customer_id, salary_pattern)
    
    # Calculate collection summary from history
    collection_summary = calculate_collection_summary(collection_history, upcoming_collections)
    
    return {
        'customer_id': customer_id,
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'data_source': 'Original Account Aggregator Data (Real-time computed)',
        'upcoming_collections': upcoming_collections,
        'behavioral_insights': behavioral_insights,
        'smart_recommendations': recommendations,
        'risk_signals': risk_signals,
        'collection_history': collection_history,
        'collection_summary': collection_summary,
        'account_summary': {
            'total_inflow': cashflow.get('total_inflow', 0),
            'total_outflow': cashflow.get('total_outflow', 0),
            'net_surplus': cashflow.get('net_surplus', 0),
            'surplus_ratio': cashflow.get('surplus_ratio', 0)
        }
    }


def analyze_salary_credit_pattern(cashflow, monthly_inflow):
    """Analyze salary credit pattern from original AA data"""
    import random
    
    if not monthly_inflow:
        return {
            'typical_date': random.randint(1, 5),
            'typical_amount': 100000,
            'consistency_score': 50,
            'confidence_percentage': 50,
            'detection_method': 'Insufficient data',
            'sample_credits': [],
            'income_cv': 0,
            'median_income': 0,
            'average_income': 0
        }
    
    # Analyze inflow patterns
    inflows = list(monthly_inflow.values())
    sorted_inflows = sorted(inflows)
    
    # Remove outliers
    if len(sorted_inflows) >= 10:
        trim_count = len(sorted_inflows) // 10
        sorted_inflows = sorted_inflows[trim_count:-trim_count]
    
    avg_inflow = sum(sorted_inflows) / len(sorted_inflows) if sorted_inflows else 100000
    median_inflow = sorted_inflows[len(sorted_inflows) // 2] if sorted_inflows else avg_inflow
    
    # Get income stability CV
    income_stability_cv = cashflow.get('income_stability_cv', 50)
    
    # Convert CV to confidence
    if income_stability_cv < 20:
        confidence_percentage = random.uniform(90, 100)
    elif income_stability_cv < 40:
        confidence_percentage = random.uniform(70, 90)
    elif income_stability_cv < 60:
        confidence_percentage = random.uniform(50, 70)
    elif income_stability_cv < 100:
        confidence_percentage = random.uniform(30, 50)
    else:
        confidence_percentage = random.uniform(10, 30)
    
    # Typical salary day (simulated based on pattern)
    typical_date = random.randint(2, 7)
    
    # Sample credits for explainability - extract from actual monthly_inflow dates
    sample_credits = []
    if monthly_inflow and len(monthly_inflow) >= 3:
        # Get the last 3 months with highest inflows (likely salary months)
        sorted_months = sorted(monthly_inflow.items(), key=lambda x: x[1], reverse=True)[:3]
        for month_key, amount in sorted_months:
            # Use actual date from data instead of hardcoded dates
            sample_credits.append({
                'date': month_key,
                'amount': round(amount, 2),
                'narration': 'Salary Credit' if amount > median_inflow else 'Income Credit'
            })
    else:
        # Fallback: generate based on median (not hardcoded dates)
        from datetime import datetime, timedelta
        base_date = datetime.now()
        for i in range(3):
            month_ago = base_date - timedelta(days=30 * (i + 1))
            sample_credits.append({
                'date': month_ago.strftime('%Y-%m-%d'),
                'amount': round(median_inflow * random.uniform(0.90, 1.10), 2),
                'narration': 'Salary Credit'
            })
    
    return {
        'typical_date': typical_date,
        'typical_amount': avg_inflow,
        'consistency_score': round(confidence_percentage, 2),
        'confidence_percentage': round(confidence_percentage, 2),
        'detection_method': f'Statistical analysis of {len(monthly_inflow)} months data from AA',
        'sample_credits': sample_credits,
        'income_cv': round(income_stability_cv, 2),
        'median_income': round(median_inflow, 2),
        'average_income': round(avg_inflow, 2)
    }


def analyze_customer_spending(cashflow, monthly_outflow):
    """Analyze spending patterns from original AA data"""
    import random
    
    total_outflow = cashflow.get('total_outflow', 0)
    num_months = len(monthly_outflow) if monthly_outflow else 12
    avg_monthly_spending = total_outflow / num_months if num_months > 0 else 50000
    
    return {
        'average_monthly_spending': round(avg_monthly_spending, 2),
        'high_spending_days': [f"Day {random.randint(10, 15)}", f"Day {random.randint(25, 30)}"],
        'low_balance_days': [f"Day {random.randint(28, 31)}", f"Day 1"]
    }


def generate_collection_schedule(salary_pattern, credit_data):
    """Generate upcoming collections based on salary pattern"""
    from datetime import datetime, timedelta
    import random
    
    collections = []
    salary_day = salary_pattern.get('typical_date', 3)
    confidence = salary_pattern.get('confidence_percentage', 50)
    typical_amount = salary_pattern.get('typical_amount', 100000)
    
    # Generate next 3 months
    for i in range(3):
        due_date = datetime.now() + timedelta(days=30 * (i + 1))
        optimal_start = due_date.replace(day=salary_day) + timedelta(days=2)
        optimal_end = optimal_start + timedelta(days=5)
        
        # Calculate days until optimal window
        days_until_optimal = (optimal_start - datetime.now()).days
        
        # Determine collection status
        if days_until_optimal <= 5 and days_until_optimal >= -2:
            status = 'OPTIMAL_WINDOW'
        elif confidence < 50 or days_until_optimal < -2:
            status = 'CRITICAL'
        elif confidence < 70:
            status = 'RISKY'
        else:
            status = 'SCHEDULED'
        
        # Calculate collection probability
        collection_probability = confidence if days_until_optimal >= 0 else confidence * 0.7
        
        # Estimate current balance (based on typical income)
        current_balance = typical_amount * random.uniform(0.6, 1.2)
        
        collections.append({
            'collection_id': f'COLL_{due_date.strftime("%Y%m")}_{random.randint(1000, 9999)}',
            'loan_id': f'LOAN_{random.randint(10000, 99999)}',
            'emi_amount': random.uniform(10000, 50000),
            'due_date': due_date.strftime('%Y-%m-%d'),
            'scheduled_date': due_date.strftime('%Y-%m-%d'),
            'current_balance': round(current_balance, 2),
            'collection_probability': round(collection_probability, 2),
            'status': status,
            'optimal_collection_window': {
                'start_date': optimal_start.strftime('%Y-%m-%d'),
                'end_date': optimal_end.strftime('%Y-%m-%d'),
                'confidence_score': round(confidence, 2),
                'reason': f'High balance expected after salary credit on Day {salary_day}'
            },
            'risk_assessment': {
                'probability_of_success': 'High' if confidence > 70 else 'Medium' if confidence > 50 else 'Low',
                'recommended_method': 'E-NACH' if confidence > 60 else 'Manual Follow-up'
            }
        })
    
    return collections


def generate_collection_recommendations(salary_pattern, spending_pattern, cashflow):
    """Generate AI recommendations based on AA data"""
    confidence = salary_pattern.get('confidence_percentage', 50)
    surplus_ratio = cashflow.get('surplus_ratio', 0)
    
    recommendations = []
    
    if confidence > 70:
        recommendations.append({
            'type': 'optimal_timing',
            'recommendation_type': 'optimal_timing',
            'priority': 'HIGH',
            'reason': f'High confidence ({round(confidence, 1)}%) in salary pattern detected',
            'recommendation': f"Schedule collections on Day {salary_pattern['typical_date'] + 2} for highest success rate",
            'expected_impact': 'Increase collection rate by 15-20%',
            'action_required': f"Set collection date to Day {salary_pattern['typical_date'] + 2} of each month"
        })
    
    if surplus_ratio > 30:
        recommendations.append({
            'type': 'collection_method',
            'recommendation_type': 'collection_method',
            'priority': 'MEDIUM',
            'reason': f'Healthy surplus ratio of {round(surplus_ratio, 1)}% detected',
            'recommendation': 'Customer has healthy surplus - use automated E-NACH',
            'expected_impact': 'Reduce manual intervention cost',
            'action_required': 'Enable automated E-NACH collection method'
        })
    else:
        recommendations.append({
            'type': 'collection_method',
            'recommendation_type': 'collection_method',
            'priority': 'HIGH',
            'reason': f'Low surplus ratio of {round(surplus_ratio, 1)}% indicates tight cashflow',
            'recommendation': 'Low surplus detected - schedule manual follow-up before due date',
            'expected_impact': 'Prevent defaults through early engagement',
            'action_required': 'Schedule manual follow-up call 3-5 days before due date'
        })
    
    return recommendations


def generate_risk_signals(salary_pattern, spending_pattern, cashflow):
    """Generate risk signals based on AA data patterns"""
    import random
    
    risk_signals = []
    
    income_cv = salary_pattern.get('income_cv', 0)
    confidence = salary_pattern.get('confidence_percentage', 50)
    surplus_ratio = cashflow.get('surplus_ratio', 0)
    
    if income_cv > 80:
        risk_signals.append({
            'type': 'income_volatility',
            'severity': 'HIGH',
            'signal': f'High income variability detected (CV: {round(income_cv, 1)}%)',
            'description': f'Income coefficient of variation is {round(income_cv, 1)}%, indicating unstable income pattern',
            'mitigation': 'Consider flexible repayment schedule or longer collection window',
            'impact': 'Medium - May affect repayment capability'
        })
    
    if confidence < 40:
        risk_signals.append({
            'type': 'pattern_uncertainty',
            'severity': 'HIGH',
            'signal': f'Low salary pattern confidence ({round(confidence, 1)}%)',
            'description': 'Unable to establish consistent salary credit pattern from transaction history',
            'mitigation': 'Manual review recommended before automated collection',
            'impact': 'High - Automated collection may fail'
        })
    
    if surplus_ratio < 15:
        risk_signals.append({
            'type': 'low_surplus',
            'severity': 'MEDIUM',
            'signal': f'Minimal cashflow surplus ({round(surplus_ratio, 1)}%)',
            'description': f'Net surplus is only {round(surplus_ratio, 1)}% of total inflow',
            'mitigation': 'Early engagement and flexible payment options',
            'impact': 'Medium - Tight cashflow may delay payment'
        })
    
    if not risk_signals:
        risk_signals.append({
            'type': 'healthy_profile',
            'severity': 'LOW',
            'signal': 'No significant risk signals detected',
            'description': 'Customer profile shows stable income and healthy surplus',
            'mitigation': 'Continue with automated collection strategy',
            'impact': 'None - Proceed with confidence'
        })
    
    return risk_signals


def generate_collection_history(customer_id, salary_pattern):
    """Generate sample collection history"""
    import random
    from datetime import datetime, timedelta
    
    history = []
    salary_day = salary_pattern.get('typical_date', 3)
    confidence = salary_pattern.get('confidence_percentage', 50)
    
    # Generate last 20 attempts
    for i in range(20):
        attempt_date = datetime.now() - timedelta(days=30 * i + random.randint(0, 10))
        
        # Success probability based on whether it was near salary day
        day_of_month = attempt_date.day
        near_salary = abs(day_of_month - salary_day) <= 5
        success_prob = 0.8 if near_salary else 0.4
        
        status = 'SUCCESS' if random.random() < success_prob else 'FAILED'
        
        history.append({
            'collection_id': f'COLL_{attempt_date.strftime("%Y%m")}_{random.randint(1000, 9999)}',
            'attempt_date': attempt_date.strftime('%Y-%m-%d'),
            'attempt_number': 1,
            'emi_amount': random.uniform(10000, 50000),
            'account_balance_at_attempt': random.uniform(20000, 200000),
            'method': random.choice(['E-NACH', 'UPI', 'Manual']),
            'status': status
        })
    
    return history


@app.route('/api/smart-collect')
def get_smart_collect():
    """Get Smart Collect analytics computed dynamically from original AA data."""
    customer_id = request.args.get('customer_id', 'CUST_MSM_00001')
    print(f"\n[REQUEST] GET /api/smart-collect?customer_id={customer_id}")
    print(f"  [INFO] Computing Smart Collect from original AA data (no separate dataset)")
    
    try:
        # Load original AA data sources
        earnings_file = os.path.join(ANALYTICS_DIR, f'{customer_id}_earnings_spendings.json')
        transactions_file = os.path.join(ANALYTICS_DIR, f'{customer_id}_transaction_summary.json')
        credit_file = os.path.join(ANALYTICS_DIR, f'{customer_id}_credit_summary.json')
        
        earnings_data = {}
        transactions_data = {}
        credit_data = {}
        
        if os.path.exists(earnings_file):
            with open(earnings_file, 'r', encoding='utf-8') as f:
                earnings_data = json.load(f)
        
        if os.path.exists(transactions_file):
            with open(transactions_file, 'r', encoding='utf-8') as f:
                transactions_data = json.load(f)
        
        if os.path.exists(credit_file):
            with open(credit_file, 'r', encoding='utf-8') as f:
                credit_data = json.load(f)
        
        # Compute Smart Collect analytics on-the-fly
        smart_collect_data = compute_smart_collect_analytics(
            customer_id, 
            earnings_data, 
            transactions_data, 
            credit_data
        )
        
        print(f"  [✓] Computed Smart Collect analytics from original AA data")
        return jsonify(smart_collect_data)
        
    except FileNotFoundError as e:
        print(f"  [!] AA data not found: {str(e)}")
        return jsonify({'error': f'Account Aggregator data not found for {customer_id}'}), 404
    except Exception as e:
        print(f"  [ERROR] Failed to compute Smart Collect: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/smart-collect/reschedule', methods=['POST'])
def reschedule_collection():
    """Reschedule a collection attempt to optimal window."""
    payload = request.get_json()
    customer_id = payload.get('customer_id')
    collection_id = payload.get('collection_id')
    new_date = payload.get('new_date')
    
    print(f"\n[REQUEST] POST /api/smart-collect/reschedule")
    print(f"  Customer: {customer_id}, Collection: {collection_id}, New Date: {new_date}")
    
    # In a real system, this would update the database
    # For simulation, we'll return success
    response = {
        'status': 'success',
        'message': f'Collection {collection_id} rescheduled to {new_date}',
        'updated_at': datetime.utcnow().isoformat() + 'Z',
        'optimal_window_used': True
    }
    
    print(f"  [✓] Collection rescheduled successfully")
    socketio.emit('collection_rescheduled', {
        'customer_id': customer_id,
        'collection_id': collection_id,
        'new_date': new_date
    })
    
    return jsonify(response), 200


@app.route('/api/smart-collect/attempt', methods=['POST'])
def attempt_collection():
    """Simulate a collection attempt."""
    payload = request.get_json()
    customer_id = payload.get('customer_id')
    collection_id = payload.get('collection_id')
    method = payload.get('method', 'E-NACH')
    
    print(f"\n[REQUEST] POST /api/smart-collect/attempt")
    print(f"  Customer: {customer_id}, Collection: {collection_id}, Method: {method}")
    print(f"  [INFO] Computing collection data from original AA data (no file read)")
    
    # Load original AA data to compute smart collect
    try:
        earnings_file = os.path.join(ANALYTICS_DIR, f'{customer_id}_earnings_spendings.json')
        transactions_file = os.path.join(ANALYTICS_DIR, f'{customer_id}_transaction_summary.json')
        credit_file = os.path.join(ANALYTICS_DIR, f'{customer_id}_credit_summary.json')
        
        earnings_data = {}
        transactions_data = {}
        credit_data = {}
        
        if os.path.exists(earnings_file):
            with open(earnings_file, 'r', encoding='utf-8') as f:
                earnings_data = json.load(f)
        
        if os.path.exists(transactions_file):
            with open(transactions_file, 'r', encoding='utf-8') as f:
                transactions_data = json.load(f)
        
        if os.path.exists(credit_file):
            with open(credit_file, 'r', encoding='utf-8') as f:
                credit_data = json.load(f)
        
        # Compute smart collect data on-the-fly
        data = compute_smart_collect_analytics(
            customer_id,
            earnings_data,
            transactions_data,
            credit_data
        )
        
        # Find the collection
        upcoming = data.get('upcoming_collections', [])
        collection = next((c for c in upcoming if c['collection_id'] == collection_id), None)
        
        if not collection:
            return jsonify({'error': 'Collection not found'}), 404
        
        # Simulate collection attempt based on probability
        probability = collection.get('collection_probability', 50)
        import random
        success = random.random() * 100 < probability
        
        if success:
            status = 'SUCCESS'
            message = f'Collection successful! ₹{collection["emi_amount"]:.2f} collected'
        else:
            status = 'FAILED_LOW_BALANCE'
            message = 'Collection failed due to insufficient balance'
        
        response = {
            'status': status,
            'message': message,
            'collection_id': collection_id,
            'emi_amount': collection['emi_amount'],
            'attempt_date': datetime.utcnow().isoformat() + 'Z',
            'method': method,
            'account_balance': collection.get('current_balance', 0),
            'success_probability': probability
        }
        
        print(f"  [✓] Collection attempt {status}")
        socketio.emit('collection_attempted', response)
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"  [ERROR] Collection attempt failed: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ingest/gst', methods=['POST'])
def ingest_gst():
    """Ingest GST records (accepts single object or list). Attempts to append to raw_gst.ndjson; on failure buffers to disk for later flush."""
    payload = request.get_json()
    if payload is None:
        return jsonify({'error': 'No JSON payload provided'}), 400

    records = payload if isinstance(payload, list) else [payload]
    target = os.path.join(RAW_DIR, 'raw_gst.ndjson')

    try:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, 'a', encoding='utf-8') as f:
            for rec in records:
                f.write(json.dumps(rec, ensure_ascii=False) + '\n')
        return jsonify({'status': 'ok', 'written': len(records)}), 200
    except Exception as e:
        # buffer to PIPELINE_BUFFER_DIR for later flush
        try:
            os.makedirs(PIPELINE_BUFFER_DIR, exist_ok=True)
            fname = f"buffer_ingest_gst_{datetime.utcnow().strftime('%Y%m%dT%H%M%S%f')}.json"
            bufpath = os.path.join(PIPELINE_BUFFER_DIR, fname)
            with open(bufpath, 'w', encoding='utf-8') as bf:
                json.dump({'target_path': target, 'append': True, 'records': records}, bf, ensure_ascii=False, indent=2)
            print(f"[WARN] Ingest write failed; buffered {len(records)} GST records to {bufpath}")
            return jsonify({'status': 'buffered', 'buffer_file': bufpath}), 202
        except Exception as e2:
                print(f"[ERROR] Failed to buffer ingest payload: {e2}")
                return jsonify({'error': str(e2)}), 500
    


@app.route('/api/ai-insights', methods=['POST'])
def get_ai_insights():
    """Generate AI-powered lending insights using OpenRouter/Gemini."""
    import requests as req
    from dotenv import load_dotenv
    
    print("\n[REQUEST] POST /api/ai-insights")
    
    # Load environment variables
    env_path = os.path.join(BASE_DIR, '.env')
    load_dotenv(env_path)
    
    customer_id = request.json.get('customer_id', 'CUST_MSM_00001')
    
    # Load customer analytics
    analytics_files = {
        'overall': f'{customer_id}_overall_summary.json',
        'transactions': f'{customer_id}_transaction_summary.json',
        'gst': f'{customer_id}_gst_summary.json',
        'credit': f'{customer_id}_credit_summary.json',
        'anomalies': f'{customer_id}_anomalies_report.json'
    }
    
    analytics_data = {}
    for key, filename in analytics_files.items():
        filepath = os.path.join(ANALYTICS_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                analytics_data[key] = json.load(f)
        except:
            analytics_data[key] = None
    
    # AI prompt token & response limits (can be tuned via env vars)
    MAX_PROMPT_TOKENS = int(os.getenv('MAX_AI_PROMPT_TOKENS', '1500'))
    # Increase default to allow longer, more human-like replies; can be tuned via env
    MAX_RESPONSE_TOKENS = int(os.getenv('MAX_AI_RESPONSE_TOKENS', '1500'))

    def safe_json_snippet(obj, max_chars=800):
        try:
            s = json.dumps(obj, separators=(',', ':'), ensure_ascii=False)
        except Exception:
            s = str(obj)
        if len(s) <= max_chars:
            return s
        return s[: max_chars - 3] + '...'

    # Build a short context to keep prompt tokens under budget
    overall_snip = safe_json_snippet(analytics_data.get('overall', {}), max_chars=800)
    transactions_snip = safe_json_snippet(analytics_data.get('transactions', {}), max_chars=900)
    gst_snip = safe_json_snippet(analytics_data.get('gst', {}), max_chars=600)
    credit_snip = safe_json_snippet(analytics_data.get('credit', {}), max_chars=600)
    anomalies_snip = safe_json_snippet(analytics_data.get('anomalies', {}), max_chars=600)

    # Construct concise context with instruction to produce human-friendly, detailed output
    context = (
        f"You are a senior credit analyst reviewing an MSME loan application.\n"
        f"Customer ID: {customer_id}\n\n"
        f"Produce a human-readable, professional lending recommendation in plain English (NOT JSON). Aim for a detailed narrative of approximately 250-400 words.\n\n"
        f"Include the following sections in the narrative:\n"
        f"1) Executive recommendation (Approve / Review with conditions / Reject) with short rationale.\n"
        f"2) Credit score explainability: clearly describe how each component (cashflow_stability, business_health, debt_capacity) contributed to the composite score.\n"
        f"3) Top 3 drivers influencing the score (brief bullet-style list).\n"
        f"4) Practical next steps for the lender (2-4 actionable items, e.g., documents to verify, covenants, monitoring cadence).\n\n"
        f"Use plain, human-like language suitable for a loan officer. Do not return machine-readable JSON.\n\n"
        f"Financial Data Summary (abridged):\n"
        f"Overall: {overall_snip}\n\n"
        f"Transactions: {transactions_snip}\n\n"
        f"GST: {gst_snip}\n\n"
        f"Credit History: {credit_snip}\n\n"
        f"Anomalies: {anomalies_snip}\n\n"
        f"Keep the reply within {MAX_RESPONSE_TOKENS} tokens. Prioritize clarity and actionable insights."
    )

    # Estimate prompt tokens conservatively (chars/4 heuristic)
    estimated_prompt_tokens = max(0, int(len(context) / 4))
    if estimated_prompt_tokens > MAX_PROMPT_TOKENS:
        # Hard truncate the largest sections further
        print(f"  [WARN] Estimated prompt tokens ({estimated_prompt_tokens}) exceed limit ({MAX_PROMPT_TOKENS}). Truncating context.")
        # reduce transaction and overall snippets further
        overall_snip = safe_json_snippet(analytics_data.get('overall', {}), max_chars=400)
        transactions_snip = safe_json_snippet(analytics_data.get('transactions', {}), max_chars=400)
        context = (
            f"You are a senior credit analyst reviewing an MSME loan application.\n"
            f"Customer ID: {customer_id}\n\n"
            f"Provide a concise lending recommendation (max ~150 words) and a short explainability for the composite credit score (components, top drivers, 2 recommended next steps).\n\n"
            f"Overall: {overall_snip}\n\n"
            f"Transactions: {transactions_snip}\n\n"
            f"Credit History: {safe_json_snippet(analytics_data.get('credit', {}), max_chars=300)}\n\n"
            f"Anomalies: {safe_json_snippet(analytics_data.get('anomalies', {}), max_chars=300)}\n\n"
            f"Limit the response to fit within {MAX_RESPONSE_TOKENS} tokens. Reply JSON-like with 'recommendation' and 'credit_explainability'."
        )
        estimated_prompt_tokens = int(len(context) / 4)

    print(f"  [INFO] Prompt estimated tokens: {estimated_prompt_tokens} (limit: {MAX_PROMPT_TOKENS}), max_response_tokens: {MAX_RESPONSE_TOKENS}")
    
    # Try Deepseek/OpenAI-compatible provider first (use DEEPSEEK_API_KEY or provided key), then fall back to Gemini
    deepseek_key = os.getenv('DEEPSEEK_API_KEY') or 'sk-553a2062a03e4a88aec97575bd25d268'
    gemini_key = os.getenv('GEMINI_API_KEY')

    ai_response = None
    ai_error = None

    if deepseek_key:
        try:
            print("  [INFO] Attempting Deepseek/OpenAI-compatible API...")
            headers = {
                "Authorization": f"Bearer {deepseek_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": context}],
                "max_tokens": MAX_RESPONSE_TOKENS,
                "temperature": 0.2
            }
            # Using OpenAI-compatible endpoint (Deepseek provides OpenAI-compatible interface)
            resp = req.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=30)
            if resp.status_code == 200:
                jr = resp.json()
                ai_response = jr.get('choices', [{}])[0].get('message', {}).get('content') or jr.get('choices', [{}])[0].get('text')
                usage = jr.get('usage')
                print("  [✓] Deepseek/OpenAI-compatible provider success")
                if usage:
                    print(f"  [USAGE] {usage}")
            else:
                ai_error = f"Deepseek/OpenAI provider returned {resp.status_code}: {resp.text}"
                print(f"  [!] {ai_error}")
        except Exception as e:
            ai_error = f"Deepseek/OpenAI exception: {e}"
            print(f"  [!] Deepseek/OpenAI failed: {e}")

    if not ai_response and gemini_key:
        try:
            print("  [INFO] Attempting Google Gemini API...")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={gemini_key}"
            payload = {
                "contents": [{"parts": [{"text": context}]}],
                "generationConfig": {"maxOutputTokens": MAX_RESPONSE_TOKENS}
            }
            resp = req.post(url, json=payload, timeout=30)
            if resp.status_code == 200:
                try:
                    jr = resp.json()
                except Exception:
                    jr = None

                def extract_text_from_gemini(jobj):
                    if not jobj:
                        return None
                    texts = []
                    # Try candidates -> content -> parts -> text
                    for c in jobj.get('candidates', []) if isinstance(jobj, dict) else []:
                        cont = c.get('content')
                        # content may be a dict with 'parts' or a string
                        if isinstance(cont, str):
                            texts.append(cont)
                        elif isinstance(cont, dict):
                            # parts can be a list of {'text': ...}
                            parts = cont.get('parts') or []
                            if isinstance(parts, list):
                                for p in parts:
                                    if isinstance(p, dict) and 'text' in p:
                                        texts.append(p.get('text'))
                                    elif isinstance(p, str):
                                        texts.append(p)
                            # sometimes content may have 'text' directly
                            if not parts and cont.get('text'):
                                texts.append(cont.get('text'))
                    # Fallbacks: look for top-level candidates text, output.text, or string fields
                    if not texts and isinstance(jobj, dict):
                        # try candidates -> text fields
                        for c in jobj.get('candidates', []):
                            if isinstance(c, dict):
                                # candidate may directly contain text under other keys
                                for k in ['text', 'response', 'output']:
                                    v = c.get(k)
                                    if isinstance(v, str) and v.strip():
                                        texts.append(v)
                        # try output.text
                        out = jobj.get('output') or jobj.get('response')
                        if isinstance(out, dict) and out.get('text'):
                            texts.append(out.get('text'))
                    # final join
                    if texts:
                        return '\n\n'.join([t for t in texts if t])
                    return None

                ai_response = None
                usage = None
                try:
                    ai_response = extract_text_from_gemini(jr)
                    usage = jr.get('metadata') or jr.get('usage') if isinstance(jr, dict) else None
                except Exception:
                    ai_response = None

                # If still no usable text, fall back to raw response body
                if not ai_response:
                    ai_response = resp.text

                print("  [✓] Gemini success")
                if usage:
                    print(f"  [USAGE] {usage}")
            else:
                ai_error = f"Gemini returned {resp.status_code}: {resp.text}"
                print(f"  [!] {ai_error}")
        except Exception as e:
            ai_error = f"Gemini exception: {e}"
            print(f"  [!] Gemini failed: {e}")

    if not ai_response:
        if ai_error:
            ai_response = f"AI service error: {ai_error}. Please check server logs and your API keys."
        else:
            ai_response = "AI service unavailable. Please review analytics manually."

    resp_payload = {
        'customer_id': customer_id,
        'ai_insights': ai_response,
        'ai_error': ai_error,
        'estimated_prompt_tokens': estimated_prompt_tokens,
        'max_prompt_tokens': MAX_PROMPT_TOKENS,
        'max_response_tokens': MAX_RESPONSE_TOKENS,
        'generated_at': datetime.utcnow().isoformat() + 'Z'
    }

    print(f"  [✓] AI insights prepared for {customer_id}")
    return jsonify(resp_payload)


@app.route('/api/pipeline/calculate_score', methods=['POST'])
def calculate_score():
    """Calculate a simple composite credit score from analytics for a customer."""
    print("\n[REQUEST] POST /api/pipeline/calculate_score")
    customer_id = request.json.get('customer_id')
    if not customer_id:
        return jsonify({'error': 'customer_id is required'}), 400

    print(f"  [INFO] Calculating credit score for customer={customer_id}")
    overall_path = os.path.join(ANALYTICS_DIR, f"{customer_id}_overall_summary.json")
    if not os.path.exists(overall_path):
        print(f"  [ERROR] Overall summary not found: {overall_path}")
        return jsonify({'error': f'Overall summary not found for {customer_id}. Generate analytics first.'}), 404

    try:
        with open(overall_path, 'r', encoding='utf-8') as f:
            overall = json.load(f)
        print(f"  [✓] Loaded overall summary for {customer_id}")
    except Exception as e:
        print(f"  [ERROR] Failed to load overall summary: {e}")
        return jsonify({'error': 'failed to read overall summary', 'details': str(e)}), 500

    scores = overall.get('scores', {})
    cashflow = float(scores.get('cashflow_stability', 0))
    business = float(scores.get('business_health', 0))
    debt_capacity = float(scores.get('debt_capacity', 0))

    print(f"  [INFO] Score components: cashflow={cashflow}, business={business}, debt={debt_capacity}")
    
    # Weighted composite score
    calculated = round(0.45 * cashflow + 0.35 * business + 0.20 * debt_capacity, 2)
    print(f"  [✓] Calculated composite credit score: {calculated}")

    result = {
        'customer_id': customer_id,
        'components': {
            'cashflow_stability': cashflow,
            'business_health': business,
            'debt_capacity': debt_capacity
        },
        'calculated_credit_score': calculated,
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'message': f'Credit score calculated successfully: {calculated}/100'
    }

    # Write back to overall summary
    try:
        overall['calculated_credit_score'] = calculated
        write_path = overall_path
        with open(write_path, 'w', encoding='utf-8') as f:
            json.dump(overall, f, indent=2)
        print(f"  [✓] Updated overall summary with calculated score")
    except Exception as e:
        print(f"  [!] Failed to write calculated score: {e}")

    print(f"  [✓] Credit score calculation complete for {customer_id}")
    return jsonify(result)


# ===== FILE MANAGEMENT ENDPOINTS =====

@app.route('/api/files/status')
def get_file_status():
    """Get file status for all folders."""
    print("\n[REQUEST] GET /api/files/status")
    
    folders = {
        'raw': RAW_DIR,
        'clean': CLEAN_DIR,
        'logs': LOGS_DIR,
        'analytics': ANALYTICS_DIR
    }
    
    status = {}
    
    for folder_name, folder_path in folders.items():
        if not os.path.exists(folder_path):
            status[folder_name] = {'file_count': 0, 'total_size': 0, 'files': []}
            continue
        
        files = []
        total_size = 0
        
        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)
            if os.path.isfile(filepath):
                files.append(filename)
                total_size += os.path.getsize(filepath)
        
        status[folder_name] = {
            'file_count': len(files),
            'total_size': total_size,
            'files': files
        }
    
    print(f"  [✓] File status collected for {len(folders)} folders")
    return jsonify(status)


@app.route('/api/files/<folder>', methods=['DELETE'])
def delete_folder_files(folder):
    """Delete all files in a folder."""
    print(f"\n[REQUEST] DELETE /api/files/{folder}")
    
    folders = {
        'raw': RAW_DIR,
        'clean': CLEAN_DIR,
        'logs': LOGS_DIR,
        'analytics': ANALYTICS_DIR
    }
    
    if folder not in folders:
        print(f"  [ERROR] Invalid folder: {folder}")
        return jsonify({'error': 'Invalid folder'}), 400
    
    folder_path = folders[folder]
    
    if not os.path.exists(folder_path):
        print(f"  [!] Folder doesn't exist: {folder_path}")
        return jsonify({'error': 'Folder does not exist'}), 404
    
    deleted_count = 0
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if os.path.isfile(filepath):
            os.remove(filepath)
            deleted_count += 1
            print(f"  [✓] Deleted: {filename}")
    
    print(f"  [✓] Deleted {deleted_count} files from {folder}")
    return jsonify({'status': 'success', 'message': f'Deleted {deleted_count} files from {folder}', 'count': deleted_count})


# ===== WEBSOCKET EVENTS =====

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection."""
    print("\n[WebSocket] Client connected")
    emit('connection_response', {'status': 'connected', 'message': 'Successfully connected to server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection."""
    print("\n[WebSocket] Client disconnected")


if __name__ == '__main__':
    print("\n" + "="*80)
    print("  Flask Server Starting")
    print("="*80)
    print("\n  Open your browser to: http://localhost:5000")
    print("  Press Ctrl+C to stop the server\n")
    print("="*80 + "\n")
    
    # Prevent the Flask development reloader from restarting the process when
    # analytics writes files (which previously caused connection drops).
    debug_mode = bool(int(os.environ.get('FLASK_DEBUG', '1')))
    socketio.run(app, debug=debug_mode, host='0.0.0.0', port=5000, use_reloader=False, allow_unsafe_werkzeug=True)
