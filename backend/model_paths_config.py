"""
Model paths configuration - AUTOMATICALLY GENERATED
"""
import os

# Base model directory - Updated for Windows paths
BASE_MODELS_PATH = "D:/AI Based Candidate Model Train code/Reserach Project/R25-040-InsightHire/Models"

# Model file paths
FACE_STRESS_MODEL = "D:/AI Based Candidate Model Train code/Reserach Project/R25-040-InsightHire/Models/Face/stress_model.h5"
EYE_CONFIDENCE_MODEL = "D:/AI Based Candidate Model Train code/Reserach Project/R25-040-InsightHire/Models/Eye/eyemodel.h5"
HAND_CONFIDENCE_MODEL = "D:/AI Based Candidate Model Train code/Reserach Project/R25-040-InsightHire/Models/Hand/als_hand_moments.h5"
VOICE_CONFIDENCE_MODEL = "D:/AI Based Candidate Model Train code/Reserach Project/R25-040-InsightHire/Models/Voice/best_model1_weights.keras"

# Support files
VOICE_SCALER = "D:/AI Based Candidate Model Train code/Reserach Project/R25-040-InsightHire/Models/Voice/scaler2.pickle"
VOICE_ENCODER = "D:/AI Based Candidate Model Train code/Reserach Project/R25-040-InsightHire/Models/Voice/encoder2.pickle"
FACE_CASCADE = "D:/AI Based Candidate Model Train code/Reserach Project/R25-040-InsightHire/backend/venv/lib/python3.12/site-packages/cv2/data/haarcascade_frontalface_default.xml"

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
