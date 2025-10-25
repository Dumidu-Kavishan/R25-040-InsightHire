# Dual Environment Run Commands

## Overview
This guide provides commands to run both environments simultaneously:
1. **Main Backend** (InsightHire_Windows environment) - Port 5000
2. **Pure Gaze Tracking Server** (GazeTracking environment) - Port 5001

## Prerequisites
- Miniconda installed
- Both environments created and configured
- Models downloaded and configured

## Method 1: PowerShell Commands (Recommended)

### Terminal 1: Main Backend (Port 5000)
```powershell
# Navigate to backend directory
cd "C:\Users\PM_User\Desktop\Projects\Research Project\R25-040-InsightHire\backend"

# Activate InsightHire_Windows environment
..\InsightHire_Windows\Scripts\activate

# Start main backend server
python app.py
```

### Terminal 2: Pure Gaze Tracking Server (Port 5001)
```powershell
# Navigate to backend directory
cd "C:\Users\PM_User\Desktop\Projects\Research Project\R25-040-InsightHire\backend"

# Activate GazeTracking environment
conda activate GazeTracking

# Start pure gaze tracking server
python eye_model_server_mock_gaze.py
```

## Method 2: Batch Files for Easy Startup

### Create start_main_backend.bat
```batch
@echo off
cd "C:\Users\PM_User\Desktop\Projects\Research Project\R25-040-InsightHire\backend"
call ..\InsightHire_Windows\Scripts\activate.bat
python app.py
pause
```

### Create start_gaze_server.bat
```batch
@echo off
cd "C:\Users\PM_User\Desktop\Projects\Research Project\R25-040-InsightHire\backend"
call conda activate GazeTracking
python eye_model_server_mock_gaze.py
pause
```

## Method 3: VS Code Integrated Terminals

### Terminal 1 (Main Backend):
1. Open new terminal in VS Code
2. Run commands:
```powershell
cd backend
..\InsightHire_Windows\Scripts\activate
python app.py
```

### Terminal 2 (Gaze Server):
1. Open another new terminal in VS Code
2. Run commands:
```powershell
cd backend
conda activate GazeTracking
python eye_model_server_mock_gaze.py
```

## Verification Commands

### Check if both servers are running:
```powershell
# Check port 5000 (Main Backend)
netstat -ano | findstr :5000

# Check port 5001 (Gaze Server)
netstat -ano | findstr :5001

# Check Python processes
tasklist | findstr python
```

### Test server endpoints:
```powershell
# Test main backend
curl http://localhost:5000/health

# Test gaze server
curl http://localhost:5001/health
```

## Expected Output

### Main Backend (Port 5000):
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
🚀 InsightHire backend started successfully
📊 All models initialized
```

### Gaze Server (Port 5001):
```
 * Running on http://127.0.0.1:5001
 * Debug mode: on
🎯 Pure Gaze Tracking Server started
👁️ Using GazeTracking library with dlib
```

## Troubleshooting

### If Main Backend fails:
1. Check InsightHire_Windows environment activation
2. Verify requirements installed: `pip list`
3. Check for port conflicts: `netstat -ano | findstr :5000`

### If Gaze Server fails:
1. Check GazeTracking environment activation: `conda info --envs`
2. Verify dlib installation: `python -c "import dlib; print(dlib.DLIB_VERSION)"`
3. Check for port conflicts: `netstat -ano | findstr :5001`

### Common Issues:
- **Port already in use**: Kill existing processes or change ports
- **Environment not found**: Recreate environments using setup guides
- **Import errors**: Reinstall requirements in respective environments

## Quick Start Commands

For immediate startup, copy and paste these commands in separate terminals:

**Terminal 1 (Main Backend):**
```powershell
cd "C:\Users\PM_User\Desktop\Projects\Research Project\R25-040-InsightHire\backend" ; ..\InsightHire_Windows\Scripts\activate ; python app.py
```

**Terminal 2 (Gaze Server):**
```powershell
cd "C:\Users\PM_User\Desktop\Projects\Research Project\R25-040-InsightHire\backend" ; conda activate GazeTracking ; python eye_model_server_mock_gaze.py
```

## Frontend Access
Once both servers are running, access the frontend at:
- **Frontend**: http://localhost:3000 (if running React frontend)
- **Demo**: Open `demo.html` in browser
- **API Testing**: Use `test_api.html`

## Stopping Servers
- Press `Ctrl+C` in each terminal to stop the respective server
- Or use Task Manager to kill Python processes if needed