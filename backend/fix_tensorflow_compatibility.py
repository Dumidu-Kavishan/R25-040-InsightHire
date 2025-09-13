#!/usr/bin/env python3
"""
Fix TensorFlow model compatibility issues
"""
import os
import sys
import logging
import tensorflow as tf
from tensorflow.keras.models import load_model
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def fix_model_loading_compatibility():
    """Fix TensorFlow model loading compatibility issues"""
    logger.info("🔧 FIXING TENSORFLOW MODEL COMPATIBILITY...")
    logger.info("=" * 60)
    
    # Set TensorFlow to be more lenient with model loading
    tf.compat.v1.disable_eager_execution()
    
    # Test each model individually
    models_to_test = {
        'Face Stress': '/Users/dumidu/Downloads/Projects/InsightHire/Models/Face/stress_model.h5',
        'Eye Confidence': '/Users/dumidu/Downloads/Projects/InsightHire/Models/Eye/eyemodel.h5', 
        'Hand Confidence': '/Users/dumidu/Downloads/Projects/InsightHire/Models/Hand/als_hand_moments.h5'
    }
    
    for model_name, model_path in models_to_test.items():
        logger.info(f"🧪 Testing {model_name} model...")
        try:
            # Try loading with compile=False to avoid optimizer issues
            model = load_model(model_path, compile=False)
            logger.info(f"✅ {model_name} model loaded successfully!")
            logger.info(f"   - Input shape: {model.input_shape}")
            logger.info(f"   - Output shape: {model.output_shape}")
            
            # Recompile the model with current TensorFlow version
            model.compile(
                optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            logger.info(f"✅ {model_name} model recompiled successfully!")
            
        except Exception as e:
            logger.error(f"❌ {model_name} model failed: {e}")
            logger.info(f"   Attempting alternative loading method...")
            
            try:
                # Try with custom objects
                model = load_model(model_path, compile=False, custom_objects={})
                logger.info(f"✅ {model_name} model loaded with custom_objects!")
                
            except Exception as e2:
                logger.error(f"❌ {model_name} alternative method also failed: {e2}")
    
    logger.info("=" * 60)

def create_compatible_model_loader():
    """Create a model loader that handles compatibility issues"""
    
    loader_code = '''"""
Compatible model loader for TensorFlow 2.15.0
"""
import tensorflow as tf
import logging

logger = logging.getLogger(__name__)

def load_model_compatible(model_path, compile_model=False):
    """
    Load TensorFlow model with compatibility handling
    """
    try:
        # Method 1: Standard loading without compilation
        logger.info(f"Loading model from: {model_path}")
        model = tf.keras.models.load_model(model_path, compile=False)
        
        if compile_model:
            # Recompile with current TensorFlow version
            model.compile(
                optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            logger.info("✅ Model recompiled with current TensorFlow version")
        
        logger.info("✅ Model loaded successfully!")
        return model
        
    except Exception as e:
        logger.warning(f"Standard loading failed: {e}")
        
        try:
            # Method 2: Load with custom objects and options
            logger.info("Attempting alternative loading method...")
            model = tf.keras.models.load_model(
                model_path, 
                compile=False,
                custom_objects={},
                options=tf.saved_model.LoadOptions(allow_partial_checkpoint=True)
            )
            
            if compile_model:
                model.compile(
                    optimizer='adam',
                    loss='categorical_crossentropy', 
                    metrics=['accuracy']
                )
                
            logger.info("✅ Model loaded with alternative method!")
            return model
            
        except Exception as e2:
            logger.error(f"All loading methods failed: {e2}")
            raise e2

# Test the loader
if __name__ == '__main__':
    test_models = [
        '/Users/dumidu/Downloads/Projects/InsightHire/Models/Face/stress_model.h5',
        '/Users/dumidu/Downloads/Projects/InsightHire/Models/Eye/eyemodel.h5',
        '/Users/dumidu/Downloads/Projects/InsightHire/Models/Hand/als_hand_moments.h5'
    ]
    
    for model_path in test_models:
        if os.path.exists(model_path):
            print(f"\\nTesting: {os.path.basename(model_path)}")
            try:
                model = load_model_compatible(model_path, compile_model=False)
                print(f"✅ Success: {os.path.basename(model_path)}")
            except Exception as e:
                print(f"❌ Failed: {os.path.basename(model_path)} - {e}")
'''
    
    with open('compatible_model_loader.py', 'w') as f:
        f.write(loader_code)
    
    logger.info("✅ Created compatible_model_loader.py")

def update_model_scripts():
    """Update model scripts to use compatible loading"""
    logger.info("🔧 Updating model scripts for compatibility...")
    
    # Update Face Stress Detection
    face_script = "model_scripts/face_stress_detection.py"
    if os.path.exists(face_script):
        logger.info(f"Updating {face_script}...")
        
        with open(face_script, 'r') as f:
            content = f.read()
        
        # Add compatible loading import at the top
        if 'from compatible_model_loader import load_model_compatible' not in content:
            import_section = content.split('import logging')[0]
            remaining_content = content.split('import logging')[1]
            
            new_content = import_section + '''import logging
from compatible_model_loader import load_model_compatible
''' + remaining_content
            
            # Replace the model loading line
            old_loading = 'self.model = tf.keras.models.load_model(model_path)'
            new_loading = 'self.model = load_model_compatible(model_path, compile_model=False)'
            
            new_content = new_content.replace(old_loading, new_loading)
            
            with open(face_script, 'w') as f:
                f.write(new_content)
                
            logger.info(f"✅ Updated {face_script}")
    
    # Update Eye Confidence Detection
    eye_script = "model_scripts/eye_confidence_detection.py"
    if os.path.exists(eye_script):
        logger.info(f"Updating {eye_script}...")
        
        with open(eye_script, 'r') as f:
            content = f.read()
        
        if 'from compatible_model_loader import load_model_compatible' not in content:
            import_section = content.split('import logging')[0]
            remaining_content = content.split('import logging')[1]
            
            new_content = import_section + '''import logging
from compatible_model_loader import load_model_compatible
''' + remaining_content
            
            old_loading = 'self.model = tf.keras.models.load_model(model_path)'
            new_loading = 'self.model = load_model_compatible(model_path, compile_model=False)'
            
            new_content = new_content.replace(old_loading, new_loading)
            
            with open(eye_script, 'w') as f:
                f.write(new_content)
                
            logger.info(f"✅ Updated {eye_script}")
    
    # Update Hand Confidence Detection  
    hand_script = "model_scripts/hand_confidence_detection.py"
    if os.path.exists(hand_script):
        logger.info(f"Updating {hand_script}...")
        
        with open(hand_script, 'r') as f:
            content = f.read()
        
        if 'from compatible_model_loader import load_model_compatible' not in content:
            import_section = content.split('import logging')[0]
            remaining_content = content.split('import logging')[1]
            
            new_content = import_section + '''import logging
from compatible_model_loader import load_model_compatible
''' + remaining_content
            
            old_loading = 'self.model = tf.keras.models.load_model(model_path)'
            new_loading = 'self.model = load_model_compatible(model_path, compile_model=False)'
            
            new_content = new_content.replace(old_loading, new_loading)
            
            with open(hand_script, 'w') as f:
                f.write(new_content)
                
            logger.info(f"✅ Updated {hand_script}")

if __name__ == '__main__':
    logger.info(f"TensorFlow version: {tf.__version__}")
    logger.info("Keras is integrated with TensorFlow 2.15.0")
    
    # Test current model loading
    fix_model_loading_compatibility()
    
    # Create compatible loader
    create_compatible_model_loader()
    
    # Update model scripts
    update_model_scripts()
    
    logger.info("=" * 60)
    logger.info("🎯 COMPATIBILITY FIXES COMPLETE!")
    logger.info("📋 Next: Run 'python test_model_loading.py' to verify fixes")
    logger.info("=" * 60)
