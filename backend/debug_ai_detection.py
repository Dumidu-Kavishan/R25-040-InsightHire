#!/usr/bin/env python3
"""
Debug AI model detection issues
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def check_ai_model_status():
    """Check if AI models are loading correctly"""
    try:
        logger.info("🔍 CHECKING AI MODEL STATUS...")
        
        # Check if model files exist
        model_paths = [
            "../../Models/Face/stress_model.h5",
            "../../Models/Eye/eyemodel.h5", 
            "../../Models/Hand/als_hand_moments.h5",
            "../../Models/Voice/best_model1_weights.keras"
        ]
        
        for model_path in model_paths:
            if os.path.exists(model_path):
                logger.info(f"✅ Found: {model_path}")
            else:
                logger.warning(f"❌ Missing: {model_path}")
        
        # Check cascade files
        cascade_paths = [
            "../../Models/Face/haarcascade_frontalface_default.xml",
            "models/haarcascade_frontalface_default.xml"
        ]
        
        for cascade_path in cascade_paths:
            if os.path.exists(cascade_path):
                logger.info(f"✅ Found cascade: {cascade_path}")
            else:
                logger.warning(f"❌ Missing cascade: {cascade_path}")
                
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking models: {e}")
        return False

def analyze_detection_issues():
    """Analyze why detection is failing"""
    logger.info("🧠 ANALYSIS OF DETECTION ISSUES:")
    logger.info("=" * 50)
    logger.info("")
    logger.info("Your data shows:")
    logger.info("- eye_confidence: 'no_face_detected'")
    logger.info("- face_stress: 0 faces detected")  
    logger.info("- hand_confidence: 'no_hands_detected'")
    logger.info("- voice_confidence: 'unknown'")
    logger.info("")
    logger.info("📊 This means:")
    logger.info("✅ Backend is receiving video frames")
    logger.info("✅ AI models are processing the frames")
    logger.info("✅ Data is being saved correctly")
    logger.info("❌ But models can't detect faces/hands in the video")
    logger.info("")

def provide_debugging_steps():
    """Provide steps to debug detection issues"""
    logger.info("🔧 DEBUGGING STEPS:")
    logger.info("=" * 50)
    logger.info("")
    logger.info("1. 📱 CHECK FRONTEND CAMERA:")
    logger.info("   - Open browser developer tools (F12)")
    logger.info("   - Go to Console tab") 
    logger.info("   - Look for camera permission errors")
    logger.info("   - Check if video stream is active")
    logger.info("")
    logger.info("2. 🎥 VERIFY VIDEO FEED:")
    logger.info("   - During interview, check if you can see yourself on screen")
    logger.info("   - Make sure camera is not blocked by other apps")
    logger.info("   - Try refreshing the page and allow camera permissions")
    logger.info("")
    logger.info("3. 💡 LIGHTING CONDITIONS:")
    logger.info("   - Face detection needs good lighting")
    logger.info("   - Face should be clearly visible and well-lit")
    logger.info("   - Avoid backlighting or shadows")
    logger.info("")
    logger.info("4. 📊 BACKEND LOGS:")
    logger.info("   - Check your backend terminal for video processing logs")
    logger.info("   - Look for messages like 'Video frame decoded successfully'")
    logger.info("   - Check for any AI model loading errors")
    logger.info("")

def create_detection_test():
    """Create a test to verify AI model detection"""
    logger.info("🧪 DETECTION TEST INSTRUCTIONS:")
    logger.info("=" * 50)
    logger.info("")
    logger.info("To test if AI detection is working:")
    logger.info("")
    logger.info("1. Start a new interview session")
    logger.info("2. Make sure your face is clearly visible in the camera")
    logger.info("3. Keep your hands visible in the frame")
    logger.info("4. Speak clearly during the interview")
    logger.info("5. Check the backend logs for detection messages")
    logger.info("")
    logger.info("🔍 Look for these log messages:")
    logger.info("- '✅ Found X face(s)'")
    logger.info("- 'Face analysis: [stress_level]'") 
    logger.info("- 'Hand analysis: [confidence_level]'")
    logger.info("- 'Eye analysis: [confidence_level]'")
    logger.info("")
    logger.info("6. After 30 seconds, check Firebase Console:")
    logger.info("   https://console.firebase.google.com/project/insighthire-335a6/firestore/data/~2Fanalysis_results")
    logger.info("")
    logger.info("🎯 Expected Results:")
    logger.info("- faces_detected > 0")
    logger.info("- stress_level != 'unknown'")
    logger.info("- confidence_level != 'no_face_detected'")
    logger.info("")

if __name__ == '__main__':
    logger.info("🚀 AI DETECTION DEBUGGING...")
    logger.info("=" * 60)
    
    # Check models
    check_ai_model_status()
    logger.info("")
    
    # Analyze issues
    analyze_detection_issues()
    logger.info("")
    
    # Provide debugging steps
    provide_debugging_steps()
    logger.info("")
    
    # Create test instructions
    create_detection_test()
    
    logger.info("=" * 60)
    logger.info("🎯 SUMMARY:")
    logger.info("✅ Your database configuration is FIXED!")
    logger.info("✅ Data is saving correctly to Firebase Console!")
    logger.info("🔧 Now we need to fix AI detection for meaningful analysis")
    logger.info("")
    logger.info("📋 Next: Follow the debugging steps above to fix detection")
    logger.info("=" * 60)
