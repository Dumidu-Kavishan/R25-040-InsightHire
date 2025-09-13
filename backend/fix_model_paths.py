#!/usr/bin/env python3
"""
Fix AI model paths to use correct absolute paths
"""
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def get_absolute_model_paths():
    """Get absolute paths to model files"""
    base_path = "/Users/dumidu/Downloads/Projects/InsightHire/Models"
    
    paths = {
        'face_model': f"{base_path}/Face/stress_model.h5",
        'eye_model': f"{base_path}/Eye/eyemodel.h5", 
        'hand_model': f"{base_path}/Hand/als_hand_moments.h5",
        'voice_model': f"{base_path}/Voice/best_model1_weights.keras",
        'voice_scaler': f"{base_path}/Voice/scaler2.pickle",
        'voice_encoder': f"{base_path}/Voice/encoder2.pickle",
        'face_cascade': "/Users/dumidu/Downloads/Projects/InsightHire/backend/venv/lib/python3.12/site-packages/cv2/data/haarcascade_frontalface_default.xml"
    }
    
    # Verify all files exist
    missing = []
    for name, path in paths.items():
        if os.path.exists(path):
            logger.info(f"✅ Found {name}: {path}")
        else:
            missing.append(f"❌ Missing {name}: {path}")
            
    if missing:
        logger.error("Missing files:")
        for m in missing:
            logger.error(m)
        return None
        
    return paths

def create_model_paths_config():
    """Create a configuration file with correct model paths"""
    paths = get_absolute_model_paths()
    if not paths:
        return False
        
    config_content = f'''"""
Model paths configuration - AUTOMATICALLY GENERATED
"""
import os

# Base model directory
BASE_MODELS_PATH = "/Users/dumidu/Downloads/Projects/InsightHire/Models"

# Model file paths
FACE_STRESS_MODEL = "{paths['face_model']}"
EYE_CONFIDENCE_MODEL = "{paths['eye_model']}"
HAND_CONFIDENCE_MODEL = "{paths['hand_model']}"
VOICE_CONFIDENCE_MODEL = "{paths['voice_model']}"

# Support files
VOICE_SCALER = "{paths['voice_scaler']}"
VOICE_ENCODER = "{paths['voice_encoder']}"
FACE_CASCADE = "{paths['face_cascade']}"

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
        raise FileNotFoundError(f"Missing model files: {{missing}}")
        
    return True

if __name__ == '__main__':
    validate_model_paths()
    print("✅ All model paths validated successfully!")
'''
    
    # Write config file
    config_path = "model_paths_config.py"
    with open(config_path, 'w') as f:
        f.write(config_content)
        
    logger.info(f"✅ Created model paths config: {config_path}")
    return True

def fix_model_import_paths():
    """Update model scripts to use absolute paths"""
    
    # Face stress detection fix
    face_script = "model_scripts/face_stress_detection.py"
    if os.path.exists(face_script):
        logger.info(f"🔧 Fixing {face_script}...")
        
        # Read current content
        with open(face_script, 'r') as f:
            content = f.read()
            
        # Replace model loading logic
        old_model_paths = '''        model_paths = [
                './Models/Face/stress_model.h5',
                '../Models/Face/stress_model.h5',
                '../../Models/Face/stress_model.h5'
            ]'''
            
        new_model_paths = '''        # Use absolute path
        model_path = "/Users/dumidu/Downloads/Projects/InsightHire/Models/Face/stress_model.h5"
        if os.path.exists(model_path):
            self.model = tf.keras.models.load_model(model_path)
            logger.info(f"✅ Loaded face stress model from: {model_path}")
            return
        else:
            raise FileNotFoundError(f"Face stress model not found at: {model_path}")'''
        
        if old_model_paths in content:
            content = content.replace(old_model_paths, new_model_paths)
            # Remove the old loading loop
            old_loop = '''            for path in model_paths:
                if os.path.exists(path):
                    self.model = tf.keras.models.load_model(path)
                    logger.info(f"✅ Loaded face stress model from: {path}")
                    return
            
            raise FileNotFoundError("Face stress model not found in any of the expected paths")'''
            content = content.replace(old_loop, "")
            
            # Write updated content
            with open(face_script, 'w') as f:
                f.write(content)
            logger.info(f"✅ Updated {face_script}")
        else:
            logger.info(f"⚠️ {face_script} - pattern not found, may already be updated")
    
    # Eye confidence detection fix  
    eye_script = "model_scripts/eye_confidence_detection.py"
    if os.path.exists(eye_script):
        logger.info(f"🔧 Fixing {eye_script}...")
        
        with open(eye_script, 'r') as f:
            content = f.read()
            
        old_model_paths = '''        model_paths = [
                './Models/Eye/eyemodel.h5',
                '../Models/Eye/eyemodel.h5',
                '../../Models/Eye/eyemodel.h5'
            ]'''
            
        new_model_paths = '''        # Use absolute path
        model_path = "/Users/dumidu/Downloads/Projects/InsightHire/Models/Eye/eyemodel.h5"
        if os.path.exists(model_path):
            self.model = tf.keras.models.load_model(model_path)
            logger.info(f"✅ Loaded eye confidence model from: {model_path}")
            return
        else:
            raise FileNotFoundError(f"Eye confidence model not found at: {model_path}")'''
            
        if old_model_paths in content:
            content = content.replace(old_model_paths, new_model_paths)
            # Remove old loop
            old_loop = '''            for path in model_paths:
                if os.path.exists(path):
                    self.model = tf.keras.models.load_model(path)
                    logger.info(f"✅ Loaded eye confidence model from: {path}")
                    return
            
            raise FileNotFoundError("Eye confidence model not found in any of the expected paths")'''
            content = content.replace(old_loop, "")
            
            with open(eye_script, 'w') as f:
                f.write(content)
            logger.info(f"✅ Updated {eye_script}")
            
    # Hand confidence detection fix
    hand_script = "model_scripts/hand_confidence_detection.py"  
    if os.path.exists(hand_script):
        logger.info(f"🔧 Fixing {hand_script}...")
        
        with open(hand_script, 'r') as f:
            content = f.read()
            
        old_model_paths = '''        model_paths = [
                './Models/Hand/als_hand_moments.h5',
                '../Models/Hand/als_hand_moments.h5',
                '../../Models/Hand/als_hand_moments.h5'
            ]'''
            
        new_model_paths = '''        # Use absolute path
        model_path = "/Users/dumidu/Downloads/Projects/InsightHire/Models/Hand/als_hand_moments.h5"
        if os.path.exists(model_path):
            self.model = tf.keras.models.load_model(model_path)
            logger.info(f"✅ Loaded hand confidence model from: {model_path}")
            return
        else:
            raise FileNotFoundError(f"Hand confidence model not found at: {model_path}")'''
            
        if old_model_paths in content:
            content = content.replace(old_model_paths, new_model_paths)
            # Remove old loop
            old_loop = '''            for path in model_paths:
                if os.path.exists(path):
                    self.model = tf.keras.models.load_model(path)
                    logger.info(f"✅ Loaded hand confidence model from: {path}")
                    return
            
            raise FileNotFoundError("Hand confidence model not found in any of the expected paths")'''
            content = content.replace(old_loop, "")
            
            with open(hand_script, 'w') as f:
                f.write(content)
            logger.info(f"✅ Updated {hand_script}")
            
    logger.info("✅ All model scripts updated with absolute paths!")

if __name__ == '__main__':
    logger.info("🔧 FIXING AI MODEL PATHS...")
    logger.info("=" * 50)
    
    # Check model availability
    paths = get_absolute_model_paths()
    if not paths:
        logger.error("❌ Cannot proceed - missing model files")
        exit(1)
        
    # Create configuration
    create_model_paths_config()
    
    # Fix import paths
    fix_model_import_paths()
    
    logger.info("=" * 50)
    logger.info("✅ MODEL PATH FIXES COMPLETE!")
    logger.info("📋 Next: Restart your backend with 'python3 app.py'")
    logger.info("🎯 Then test interview session - AI detection should work!")
