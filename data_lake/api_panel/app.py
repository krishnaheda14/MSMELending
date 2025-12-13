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
from datetime import datetime

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
    if not customer_id:
        print("  [SECURITY] Rejecting analytics pipeline call without customer_id")
        return jsonify({'error': 'Analytics must be requested per-customer. Provide customer_id.'}), 400
    
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
