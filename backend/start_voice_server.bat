@echo off
echo Starting Voice Model Server...
echo.
echo Make sure you have VoiceTracking conda environment set up with:
echo   conda create -n VoiceTracking python=3.9
echo   conda activate VoiceTracking  
echo   pip install -r Models/Voice/requirements.txt
echo.

REM Activate VoiceTracking environment and start server
call conda activate VoiceTracking
if %errorlevel% neq 0 (
    echo ERROR: Could not activate VoiceTracking environment
    echo Please create it first: conda create -n VoiceTracking python=3.9
    pause
    exit /b 1
)

echo VoiceTracking environment activated
echo Starting voice model server on port 5003...
python voice_model_server.py

pause