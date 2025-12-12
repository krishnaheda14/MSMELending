# 🏦 Indian Financial Data Lake - React UI

Modern React dashboard for monitoring, debugging, and managing the Indian Financial Data Lake pipeline.

## ✨ Features

### 📊 **Dashboard**
- Real-time statistics for all 9 datasets
- Data quality metrics with color-coded indicators
- Raw vs Clean record counts
- Visual dataset cards with icons

### 🔄 **Pipeline Monitor**
- Real-time pipeline execution monitoring via WebSocket
- Live progress bars for each stage (Generate, Clean, Analytics)
- Streaming logs with color-coded severity levels
- Start/Stop controls for each pipeline stage

### 🛠️ **API Debug Console**
- Interactive API testing interface
- Pre-configured endpoint templates
- Support for GET, POST, DELETE, PUT methods
- Query parameter and request body builders
- Response viewer with syntax highlighting
- Response time tracking
- Copy to clipboard functionality

### 📁 **Dataset Viewer**
- Browse all 9 datasets (Transactions, Accounts, GST, etc.)
- Toggle between Raw and Clean versions
- Configurable record limit
- Interactive JSON tree view
- Download datasets as JSON

### 📝 **Logs Viewer**
- View transformation logs (Parsing, Cleaning, Validation)
- Search and filter log entries
- Interactive JSON explorer

### 🗑️ **File Manager**
- View file counts and sizes for all folders
- Delete files from individual folders
- Clear all cache with one click
- File-by-file listing
- Storage usage tracking

## 🚀 Quick Start

### Prerequisites
- Node.js 14+ (https://nodejs.org/)
- Python 3.11+ with venv configured
- Flask backend running on port 5000

### Installation

1. **Install Frontend Dependencies**
   ```bash
   cd frontend
   npm install
   ```
   Or run: `setup_frontend.bat`

2. **Start Development Server**
   ```bash
   npm start
   ```
   Opens browser at http://localhost:3000

### Full Stack Mode

Run both backend and frontend together:
```bash
run_fullstack.bat
```
- Backend: http://localhost:5000
- Frontend: http://localhost:3000

## 📦 Project Structure

```
frontend/
├── public/
│   └── index.html          # HTML entry point
├── src/
│   ├── components/
│   │   ├── Sidebar.js         # Navigation sidebar
│   │   ├── Dashboard.js       # Main dashboard with stats
│   │   ├── PipelineMonitor.js # Real-time pipeline monitoring
│   │   ├── APIConsole.js      # API debugging console
│   │   ├── DatasetViewer.js   # Dataset explorer
│   │   ├── LogsViewer.js      # Transformation logs viewer
│   │   └── FileManager.js     # File management interface
│   ├── App.js              # Main app with routing
│   ├── index.js            # React entry point
│   └── index.css           # Global styles (Tailwind)
├── package.json            # Dependencies
├── tailwind.config.js      # Tailwind configuration
└── .gitignore              # Git ignore rules
```

## 🎨 Tech Stack

- **React 18.2.0** - UI framework
- **React Router 6.20.1** - Client-side routing
- **Tailwind CSS 3.3.6** - Utility-first CSS
- **Axios 1.6.2** - HTTP client
- **Socket.IO Client 4.5.4** - WebSocket communication
- **Lucide React 0.294.0** - Icon library
- **React JSON View 1.21.3** - JSON viewer component
- **Recharts 2.10.3** - Charting library

## 🌐 API Endpoints

### Data Endpoints
- `GET /api/stats` - Overall statistics
- `GET /api/data/:dataset?type=raw&limit=100` - Dataset data
- `GET /api/logs/:logType` - Transformation logs

### Pipeline Endpoints
- `POST /api/pipeline/generate` - Start data generation
- `POST /api/pipeline/clean` - Start data cleaning
- `POST /api/pipeline/analytics` - Start analytics generation

### File Management
- `GET /api/files/status` - Get file counts and sizes
- `DELETE /api/files/:folder` - Delete all files in folder

### WebSocket Events
- `pipeline_progress` - Pipeline progress updates
- `pipeline_log` - Real-time log streaming

## 🎯 Available Scripts

- `npm start` - Start development server (port 3000)
- `npm run build` - Build production bundle
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

## 🔧 Configuration

### Proxy Setup
React dev server proxies API requests to Flask backend:
```json
{
  "proxy": "http://localhost:5000"
}
```

### Tailwind Configuration
Custom theme colors defined in `tailwind.config.js`:
- Primary: Blue gradient (500-700)
- Success: Green
- Warning: Yellow
- Error: Red

## 📸 UI Previews

### Dashboard
- 3 summary cards: Total Raw Records, Total Clean Records, Data Quality %
- 9 dataset cards with raw/clean counts and quality indicators

### Pipeline Monitor
- 3 pipeline stages with progress bars
- Status icons: ⏳ Pending, 🔄 Running, ✅ Completed, ❌ Failed
- Live log stream (last 100 entries)
- Color-coded logs: 🔵 Info, 🟢 Success, 🟡 Warning, 🔴 Error

### API Console
- Dropdown selector with 9 pre-configured endpoints
- HTTP method selector (GET/POST/DELETE/PUT)
- Query parameter input
- JSON request body editor
- Response panel with status, timing, and formatted JSON

## 🐛 Debugging

### WebSocket Connection Issues
- Ensure Flask backend is running with SocketIO enabled
- Check CORS configuration allows connections from localhost:3000
- Verify `flask-socketio` is installed: `pip install flask-socketio`

### API Errors
- Use API Console to test endpoints manually
- Check browser console for detailed error messages
- Verify Flask backend is running on port 5000

### Build Errors
- Delete `node_modules` and run `npm install` again
- Clear npm cache: `npm cache clean --force`
- Check Node.js version: `node --version` (should be 14+)

## 📚 Documentation

- [React Documentation](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [React Router](https://reactrouter.com/)
- [Socket.IO](https://socket.io/)

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/new-feature`
2. Make changes and test thoroughly
3. Commit: `git commit -m "Add new feature"`
4. Push: `git push origin feature/new-feature`

## 📄 License

Part of the Indian Financial Data Lake project.

---

**Built with ❤️ using React and Tailwind CSS**
