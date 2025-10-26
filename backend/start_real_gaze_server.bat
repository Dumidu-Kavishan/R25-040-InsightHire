@echo off
echo ========================================
echo REAL GAZE TRACKING MODEL SERVER STARTUP
echo ========================================
echo.

REM Activate the GazeTracking conda environment
echo Activating GazeTracking conda environment...
call conda activate GazeTracking

if errorlevel 1 (
    echo ERROR: Failed to activate GazeTracking environment
    echo Please make sure the GazeTracking conda environment exists
    echo Run: conda create -n GazeTracking python=3.8
    pause
    exit /b 1
)

echo ✅ GazeTracking environment activated

REM Check if we're in the correct environment
echo Checking environment...
python -c "import sys; print(f'Python: {sys.executable}'); print(f'Environment: GazeTracking' if 'GazeTracking' in sys.executable else 'WARNING: Not in GazeTracking environment')"

REM Change to backend directory
cd /d "c:\Users\PM_User\Desktop\Projects\Research Project\R25-040-InsightHire\backend"

echo.
echo Starting REAL gaze tracking model server...
echo Model Location: Models\Eye\eye_train_model\gaze_tracking
echo Port: 5001
echo Environment: GazeTracking
echo.

REM Start the real trained model server
python eye_model_server_real_trained.py

echo.
echo Server stopped.
pause