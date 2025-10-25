🎯 MANUAL INSTALLATION GUIDE - PURE GAZE TRACKING ONLY
========================================================

## **CRITICAL: To Get ONLY Gaze Tracking Model Working**

Since you want ONLY the real gaze tracking model (no OpenCV fallback), you need dlib installed. Here's the exact manual process:

---

## **🔧 METHOD 1: Install Visual Studio Build Tools (RECOMMENDED)**

### **Step 1: Download Visual Studio Build Tools**
1. Go to: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Download **"Build Tools for Visual Studio 2022"**
3. Run the installer

### **Step 2: Install C++ Build Tools**
1. In the installer, select **"C++ build tools"** workload
2. Make sure these are checked:
   - ✅ MSVC v143 - VS 2022 C++ x64/x86 build tools
   - ✅ Windows 10/11 SDK (latest version)
   - ✅ CMake tools for Visual Studio
3. Click **Install** (this will take 10-15 minutes)

### **Step 3: Install dlib**
```powershell
# After Visual Studio Build Tools are installed:
cd "C:\Users\PM_User\Desktop\Projects\Research Project\R25-040-InsightHire\EyeTracking_Env\Scripts"
.\activate.ps1
pip install dlib==19.24.4
```

### **Step 4: Test Pure Gaze Tracking**
```powershell
# Test that dlib works:
python -c "import dlib; print('dlib version:', dlib.__version__)"

# Run ONLY gaze tracking server:
cd "C:\Users\PM_User\Desktop\Projects\Research Project\R25-040-InsightHire\backend"
..\EyeTracking_Env\Scripts\activate
python eye_model_server_pure_gaze.py
```

---

## **🔧 METHOD 2: Use Miniconda (EASIER)**

### **Step 1: Install Miniconda**
1. Go to: https://docs.conda.io/en/latest/miniconda.html
2. Download **"Miniconda3 Windows 64-bit"**
3. Run installer and choose **"Add Miniconda3 to PATH"**
4. Restart PowerShell

### **Step 2: Create GazeTracking Environment**
```powershell
# Initialize conda (first time only):
conda init powershell
# Restart PowerShell

# Create environment from your gaze tracking specs:
cd "C:\Users\PM_User\Desktop\Projects\Research Project\R25-040-InsightHire"
conda env create -f "Models\Eye\eye_train_model\environment.yml"

# Activate and install project dependencies:
conda activate GazeTracking
pip install firebase-admin flask flask-cors flask-socketio requests
```

### **Step 3: Test Gaze Tracking**
```powershell
# Test dlib and gaze tracking:
conda activate GazeTracking
python -c "import dlib; print('dlib version:', dlib.__version__)"
cd Models\Eye\eye_train_model
python -c "from gaze_tracking import GazeTracking; gt = GazeTracking(); print('Gaze tracking loaded')"
```

### **Step 4: Run Pure Gaze Server**
```powershell
# Terminal 1: Hand Model (unchanged)
cd "C:\Users\PM_User\Desktop\Projects\Research Project\R25-040-InsightHire\backend"
..\InsightHire_Windows\Scripts\activate
python app.py

# Terminal 2: PURE Gaze Tracking
cd "C:\Users\PM_User\Desktop\Projects\Research Project\R25-040-InsightHire\backend"
conda activate GazeTracking
python eye_model_server_pure_gaze.py
```

---

## **🎉 SUCCESS INDICATORS**

### **When Pure Gaze Tracking Works:**
```
INFO:PureGazeTracking:✅ dlib version: 19.24.4
INFO:PureGazeTracking:✅ Real gaze tracking model loaded successfully
INFO:PureGazeTracking:🚀 PureGazeTracking initialized - ONLY real gaze model
* Running on http://127.0.0.1:5001
```

### **Test Results:**
```json
{
  "confidence": 0.87,
  "confidence_level": "high_confident", 
  "method": "pure_gaze_tracking",
  "pupils_detected": true,
  "left_pupil": [120, 180],
  "right_pupil": [200, 185],
  "horizontal_ratio": 0.45,
  "vertical_ratio": 0.52
}
```

---

## **🚨 TROUBLESHOOTING**

### **If Build Tools Installation Fails:**
- Make sure you have enough disk space (5GB+)
- Run installer as Administrator
- Restart computer after installation

### **If Conda Installation Fails:**
- Choose "Add to PATH" during installation
- Restart PowerShell completely
- Run `conda --version` to verify

### **If dlib Still Fails:**
- Check that Visual Studio Build Tools are properly installed
- Try `pip install --upgrade cmake` first
- Ensure you're using Python 3.9 (you have this ✅)

---

## **💡 WHY THIS IS NECESSARY**

- **dlib** is written in C++ and requires compilation on Windows
- **Visual Studio Build Tools** provide the C++ compiler
- **Conda** provides pre-compiled dlib binaries (easier option)
- **No workaround** exists - dlib is required for real gaze tracking

---

## **🎯 RECOMMENDATION**

**Use METHOD 2 (Miniconda)** - it's much easier and provides pre-compiled dlib without needing Visual Studio.

Once you have dlib installed, you'll get ONLY the real professional gaze tracking model with:
- ✅ Real pupil detection
- ✅ Gaze direction tracking  
- ✅ Professional confidence levels
- ❌ NO OpenCV fallback (as requested)

**Choose one method above and follow the steps exactly. This will give you ONLY the real gaze tracking model!** 🚀