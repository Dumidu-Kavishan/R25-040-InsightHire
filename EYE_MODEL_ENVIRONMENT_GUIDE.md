🚀 EYE MODEL ENVIRONMENT GUIDE - HOW TO RUN
=============================================

## **🎯 Current Implementation Status**
- ✅ **Currently Working**: Eye model in `InsightHire_Windows/` environment (same as hand model)
- ⏳ **Future Enhancement**: Isolated `EyeTracking_Env/` for gaze tracking (when dlib is installed)

---

## **🔥 METHOD 1: Run in Main System (RECOMMENDED - Currently Working)**

### **Activate InsightHire_Windows Environment:**
```powershell
# Navigate and activate main environment (same as hand model)
cd "C:\Users\PM_User\Desktop\Projects\Research Project\R25-040-InsightHire\InsightHire_Windows\Scripts"
.\activate.ps1
cd "C:\Users\PM_User\Desktop\Projects\Research Project\R25-040-InsightHire\backend"
```

### **Test Eye Model Directly:**
```python
# Quick test of eye detection
python -c "from model.eye_model import EyeConfidenceDetector; import numpy as np; detector = EyeConfidenceDetector(); frame = np.zeros((480, 640, 3), dtype=np.uint8); result = detector.detect_confidence(frame); print('Eye Result:', result)"
```

### **Test with Real-Time Analyzer (Like Hand Model):**
```python
# Test integrated with main system
python -c "from realtime_analyzer import RealTimeAnalyzer; import numpy as np; analyzer = RealTimeAnalyzer('test', 'test'); frame = np.zeros((480, 640, 3), dtype=np.uint8); result = analyzer.eye_detector.detect_confidence(frame); print('Eye detection result:', result['confidence_level'], result['confidence'])"
```

### **Run Full Backend Server:**
```python
# Start the complete backend with eye model included
python app.py
```

---

## **🔧 METHOD 2: Isolated EyeTracking_Env (READY - Eye Model Server on Port 5001)**

### **Run Eye Model Server (Like Hand Model Pattern):**
```powershell
# Navigate and run eye model server (EXACT same pattern as your hand model command)
cd "C:\Users\PM_User\Desktop\Projects\Research Project\R25-040-InsightHire\backend"
..\EyeTracking_Env\Scripts\activate
python eye_model_server.py
```

### **Your Original Hand Model Command (Port 5000):**
```powershell
# Hand model + main backend (port 5000)
cd "C:\Users\PM_User\Desktop\Projects\Research Project\R25-040-InsightHire\backend"
..\InsightHire_Windows\Scripts\activate
python app.py
```

### **Now Run Both Simultaneously:**
```powershell
# Terminal 1: Hand Model + Main Backend (Port 5000)
cd "C:\Users\PM_User\Desktop\Projects\Research Project\R25-040-InsightHire\backend"
..\InsightHire_Windows\Scripts\activate
python app.py

# Terminal 2: Eye Model Server (Port 5001)
cd "C:\Users\PM_User\Desktop\Projects\Research Project\R25-040-InsightHire\backend"
..\EyeTracking_Env\Scripts\activate
python eye_model_server.py
```

### **Test Eye Model Server:**
```powershell
# Test eye model server endpoints
curl http://localhost:5001/health
curl http://localhost:5001/eye/test
```

---

## **🎮 INTERACTIVE TESTING**

### **Test Eye Detection with Camera:**
```python
# Create test script
python -c "
import cv2
from model.eye_model import EyeConfidenceDetector

detector = EyeConfidenceDetector()
cap = cv2.VideoCapture(0)

print('Press q to quit')
while True:
    ret, frame = cap.read()
    if ret:
        result = detector.detect_confidence(frame)
        print(f'Eye Confidence: {result[\"confidence_level\"]} ({result[\"confidence\"]:.2f})')
        
        cv2.putText(frame, f'{result[\"confidence_level\"]}', (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('Eye Detection', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
"
```

---

## **📊 TESTING COMMANDS QUICK REFERENCE**

### **Basic Eye Model Test:**
```powershell
# In InsightHire_Windows environment
python -c "from model.eye_model import EyeConfidenceDetector; print('Eye model ready!')"
```

### **Confidence Detection Test:**
```powershell
# Test confidence levels
python -c "from model.eye_model import EyeConfidenceDetector; import numpy as np; detector = EyeConfidenceDetector(); frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8); result = detector.detect_confidence(frame); print(f'Confidence: {result[\"confidence_level\"]} - {result[\"confidence\"]}')"
```

### **Integration Test:**
```powershell
# Test with real-time analyzer (like hand model)
python -c "from realtime_analyzer import RealTimeAnalyzer; analyzer = RealTimeAnalyzer('test', 'test'); print('Eye detector loaded:', hasattr(analyzer, 'eye_detector'))"
```

---

## **🚨 TROUBLESHOOTING**

### **If Eye Model Fails to Load:**
1. **Check Environment**: Make sure you're in `InsightHire_Windows/` environment
2. **Check Dependencies**: `pip list | findstr opencv`
3. **Check File Path**: Verify `backend/model/eye_model.py` exists

### **If Gaze Tracking Not Working:**
- **Current Status**: Uses OpenCV fallback (working)
- **Future Enhancement**: Install dlib in `EyeTracking_Env/` for full gaze tracking

### **If Integration Fails:**
```powershell
# Test imports
python -c "import sys; print('Python Path:'); [print(p) for p in sys.path[:3]]"
python -c "from model.eye_model import EyeConfidenceDetector; print('✅ Eye model imports OK')"
```

---

## **⚡ CURRENT STATUS**

✅ **Working Now**: Eye model in `InsightHire_Windows/` (same pattern as hand model)
✅ **Confidence Detection**: Returns `high_confident`, `confident`, `moderate`, `not_confident`
✅ **Firebase Ready**: Saves results every 5 seconds like hand model
✅ **Real-time Analysis**: Integrated with `realtime_analyzer.py`

🔄 **Future Enhancement**: Full gaze tracking in isolated `EyeTracking_Env/` when dlib is installed

---

## **💡 RECOMMENDED WORKFLOW**

1. **Daily Use**: Run in `InsightHire_Windows/` environment (current working setup)
2. **Testing**: Use the quick test commands above
3. **Development**: Eye model follows exact same pattern as hand model
4. **Production**: Integrated with main backend system

🎉 **Your eye model is ready and working exactly like your hand model!**