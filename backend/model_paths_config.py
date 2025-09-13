"""
Model paths configuration - AUTOMATICALLY GENERATED
"""
import os

# Base model directory
BASE_MODELS_PATH = "/Users/dumidu/Downloads/Projects/InsightHire/Models"

# Model file paths
FACE_STRESS_MODEL = "/Users/dumidu/Downloads/Projects/InsightHire/Models/Face/stress_model.h5"
EYE_CONFIDENCE_MODEL = "/Users/dumidu/Downloads/Projects/InsightHire/Models/Eye/eyemodel.h5"
HAND_CONFIDENCE_MODEL = "/Users/dumidu/Downloads/Projects/InsightHire/Models/Hand/als_hand_moments.h5"
VOICE_CONFIDENCE_MODEL = "/Users/dumidu/Downloads/Projects/InsightHire/Models/Voice/best_model1_weights.keras"

# Support files
VOICE_SCALER = "/Users/dumidu/Downloads/Projects/InsightHire/Models/Voice/scaler2.pickle"
VOICE_ENCODER = "/Users/dumidu/Downloads/Projects/InsightHire/Models/Voice/encoder2.pickle"
FACE_CASCADE = "/Users/dumidu/Downloads/Projects/InsightHire/backend/venv/lib/python3.12/site-packages/cv2/data/haarcascade_frontalface_default.xml"

# Validation function
def validate_model_paths():
    """Validate that all model files exist"""
    paths = [
        FACE_STRESS_MODEL,
        EYE_CONFIDENCE_MODEL, 
        HAND_CONFIDENCE_MODEL,
        VOICE_CONFIDENCE_MODEL,
        VOICE_SCALER,
        VOICE_ENCODER,
        FACE_CASCADE
    ]
    
    missing = []
    for path in paths:
        if not os.path.exists(path):
            missing.append(path)
            
    if missing:
        raise FileNotFoundError(f"Missing model files: {missing}")
        
    return True

if __name__ == '__main__':
    validate_model_paths()
    print("✅ All model paths validated successfully!")
