# 🚀 5G IoT Security Monitor - Complete Setup Guide

## 📁 Project Structure
Create this folder structure:

```
5G_IoT_Security_Monitor/
├── backend/
│   ├── server.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   ├── App.css
│   │   ├── index.js
│   │   └── index.css
│   ├── package.json
│   ├── .env
│   ├── tailwind.config.js
│   └── postcss.config.js
├── backend_test.py
└── PROJECT_DOCUMENTATION.md
```

## 🔧 Setup Instructions

### 1. Backend Setup
```bash
mkdir -p 5G_IoT_Security_Monitor/backend
cd 5G_IoT_Security_Monitor/backend

# Create requirements.txt
echo "fastapi==0.110.1
uvicorn==0.25.0
motor==3.3.1
pymongo==4.5.0
pydantic>=2.6.4
numpy>=1.26.0
scikit-learn==1.3.2
websockets==12.0
python-dotenv>=1.0.1" > requirements.txt

# Create .env
echo 'MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"' > .env

# Install dependencies
pip install -r requirements.txt
```

### 2. Frontend Setup
```bash
cd ../
mkdir -p frontend/src

# Create package.json
echo '{
  "name": "frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "axios": "^1.8.4",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "craco start",
    "build": "craco build",
    "test": "craco test"
  },
  "devDependencies": {
    "@craco/craco": "^7.1.0",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.49",
    "tailwindcss": "^3.4.17"
  }
}' > frontend/package.json

# Create frontend .env
echo 'REACT_APP_BACKEND_URL=http://localhost:8001' > frontend/.env

# Install dependencies
cd frontend
yarn install
```

### 3. Copy Source Code Files
Copy the complete source code from the previous output:
- backend/server.py (427 lines)
- frontend/src/App.js (662 lines)
- frontend/src/App.css (Tailwind-based styling)
- Configuration files

### 4. Start Services
```bash
# Terminal 1 - Backend
cd backend
python server.py

# Terminal 2 - Frontend
cd frontend
yarn start
```

### 5. Access Application
Open http://localhost:3000 in your browser

## 🔑 Key Features
✅ AI-powered threat detection
✅ Real-time alerts (browser, sound, visual)
✅ 20 simulated IoT devices
✅ Professional dashboard
✅ WebSocket real-time updates
✅ MongoDB data persistence

## 🧪 Testing
```bash
python backend_test.py
```

Your complete AI-based 5G IoT Security Monitor will be running with all features!