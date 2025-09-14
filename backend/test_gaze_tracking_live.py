"""
Live test of the Gaze Tracking system
This will test the gaze tracking with a real webcam feed
"""
import cv2
import numpy as np
import logging
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(__file__))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_gaze_tracking_live():
    """Test gaze tracking with live webcam feed"""
    try:
        logger.info("=== Live Gaze Tracking Test ===")
        
        # Import the hybrid eye model
        from model.hybrid_eye_model import HybridEyeConfidenceDetector
        
        # Initialize the detector
        logger.info("Initializing hybrid eye detector...")
        detector = HybridEyeConfidenceDetector()
        
        # Get model info
        model_info = detector.get_model_info()
        logger.info("Model Status:")
        logger.info("  Gaze Tracking: %s", '✅' if model_info['gaze_tracking_loaded'] else '❌')
        logger.info("  TensorFlow: %s", '✅' if model_info['tensorflow_model_loaded'] else '❌')
        logger.info("  OpenCV Cascades: %s", '✅' if model_info['cascades_loaded'] else '❌')
        
        if not model_info['gaze_tracking_loaded']:
            logger.error("❌ Gaze tracking not available - cannot run live test")
            return False
        
        # Initialize webcam
        logger.info("Initializing webcam...")
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            logger.error("❌ Could not open webcam")
            return False
        
        logger.info("✅ Webcam opened successfully")
        logger.info("Press 'q' to quit, 's' to save a frame")
        
        frame_count = 0
        detection_results = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.error("❌ Failed to read from webcam")
                break
            
            frame_count += 1
            
            # Detect eye confidence
            result = detector.detect_confidence(frame)
            
            # Display results on frame
            cv2.putText(frame, f"Confidence: {result['confidence_level']}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Score: {result['confidence']:.2f}", 
                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Method: {result['method']}", 
                       (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Display gaze data if available
            if 'gaze_data' in result and result['gaze_data']:
                gaze_data = result['gaze_data']
                y_offset = 150
                
                if gaze_data.get('is_blinking'):
                    cv2.putText(frame, "BLINKING", (10, y_offset), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    y_offset += 40
                
                if gaze_data.get('is_center'):
                    cv2.putText(frame, "Looking CENTER", (10, y_offset), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    y_offset += 30
                elif gaze_data.get('is_left'):
                    cv2.putText(frame, "Looking LEFT", (10, y_offset), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                    y_offset += 30
                elif gaze_data.get('is_right'):
                    cv2.putText(frame, "Looking RIGHT", (10, y_offset), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                    y_offset += 30
                
                # Display pupil coordinates
                if gaze_data.get('left_pupil') and gaze_data.get('right_pupil'):
                    left_pupil = gaze_data['left_pupil']
                    right_pupil = gaze_data['right_pupil']
                    cv2.putText(frame, f"Left Pupil: {left_pupil}", (10, y_offset), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                    y_offset += 20
                    cv2.putText(frame, f"Right Pupil: {right_pupil}", (10, y_offset), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                    y_offset += 20
                
                # Display ratios
                if gaze_data.get('horizontal_ratio') is not None:
                    cv2.putText(frame, f"H Ratio: {gaze_data['horizontal_ratio']:.2f}", 
                               (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                    y_offset += 20
                
                if gaze_data.get('vertical_ratio') is not None:
                    cv2.putText(frame, f"V Ratio: {gaze_data['vertical_ratio']:.2f}", 
                               (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
            # Display frame info
            cv2.putText(frame, f"Frame: {frame_count}", (10, frame.shape[0] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Show frame
            cv2.imshow('Gaze Tracking Test', frame)
            
            # Store results for analysis
            if frame_count % 30 == 0:  # Every 30 frames
                detection_results.append(result)
                logger.info(f"Frame {frame_count}: {result['confidence_level']} ({result['confidence']:.2f}) - {result['method']}")
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                logger.info("Quit requested by user")
                break
            elif key == ord('s'):
                # Save current frame
                filename = f"gaze_test_frame_{frame_count}.jpg"
                cv2.imwrite(filename, frame)
                logger.info(f"Saved frame to {filename}")
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        
        # Analyze results
        if detection_results:
            logger.info("=== Detection Analysis ===")
            methods = {}
            confidence_levels = {}
            
            for result in detection_results:
                method = result['method']
                confidence_level = result['confidence_level']
                
                methods[method] = methods.get(method, 0) + 1
                confidence_levels[confidence_level] = confidence_levels.get(confidence_level, 0) + 1
            
            logger.info("Methods used:")
            for method, count in methods.items():
                logger.info(f"  {method}: {count} times")
            
            logger.info("Confidence levels:")
            for level, count in confidence_levels.items():
                logger.info(f"  {level}: {count} times")
        
        logger.info("✅ Live gaze tracking test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in live gaze tracking test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("Starting Live Gaze Tracking Test...")
    logger.info("Make sure you have a webcam connected and dlib installed")
    
    success = test_gaze_tracking_live()
    
    if success:
        logger.info("🎉 Live test completed successfully!")
    else:
        logger.error("❌ Live test failed!")
        sys.exit(1)
