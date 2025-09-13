"""
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
            print(f"\nTesting: {os.path.basename(model_path)}")
            try:
                model = load_model_compatible(model_path, compile_model=False)
                print(f"✅ Success: {os.path.basename(model_path)}")
            except Exception as e:
                print(f"❌ Failed: {os.path.basename(model_path)} - {e}")
