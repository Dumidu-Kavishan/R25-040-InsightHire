"""
Hand Confidence Detection Script for InsightHire
Using HaGRID Dynamic Gestures ONNX models for real-time gesture recognition
"""
import cv2
import numpy as np
import os
import sys
import logging
from datetime import datetime
import onnxruntime as ort
from scipy.special import softmax

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('DynamicGestures')

class DynamicGesturesDetector:
    """HaGRID Dynamic Gestures Detection using ONNX models"""
    
    def __init__(self):
        self.logger = logger
        self.hand_detector_path = r"C:\Users\PM_User\Desktop\Projects\Research Project\R25-040-InsightHire\Models\Hand\dynamic_gestures\models\hand_detector.onnx"
        self.gesture_classifier_path = r"C:\Users\PM_User\Desktop\Projects\Research Project\R25-040-InsightHire\Models\Hand\dynamic_gestures\models\crops_classifier.onnx"
        
        # Load ONNX models
        self._load_onnx_models()
        
        self.logger.info("🚀 DynamicGesturesDetector initialized with HaGRID ONNX models")

    def _load_onnx_models(self):
        """Load ONNX models for hand detection and gesture classification"""
        try:
            if not os.path.exists(self.hand_detector_path):
                self.logger.error(f"❌ Hand detector model not found: {self.hand_detector_path}")
                return False
            
            if not os.path.exists(self.gesture_classifier_path):
                self.logger.error(f"❌ Gesture classifier model not found: {self.gesture_classifier_path}")
                return False
            
            # Load models with CPU provider
            self.hand_detector = ort.InferenceSession(self.hand_detector_path, providers=['CPUExecutionProvider'])
            self.gesture_classifier = ort.InferenceSession(self.gesture_classifier_path, providers=['CPUExecutionProvider'])
            
            self.logger.info("✅ ONNX models loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load ONNX models: {e}")
            return False
    
    def detect_confidence(self, frame):
        """Main detection method with gesture-based confidence calculation"""
        try:
            return self._perform_onnx_detection(frame)
        except Exception as e:
            self.logger.error(f"❌ Error in hand detection: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                'confidence_level': 'not_confident',
                'confidence': 0.0,
                'gestures_detected': ['error'],
                'hands_detected': 0,
                'method': 'error',
                'timestamp': datetime.now().isoformat()
            }

    def _perform_onnx_detection(self, frame):
        """Perform ONNX-based hand detection and gesture classification"""
        try:
            if not hasattr(self, 'hand_detector') or not hasattr(self, 'gesture_classifier'):
                self.logger.error("❌ ONNX models not loaded")
                return {
                    'confidence_level': 'not_confident',
                    'confidence': 0.0,
                    'gestures_detected': ['model_not_loaded'],
                    'hands_detected': 0,
                    'method': 'error',
                    'timestamp': datetime.now().isoformat()
                }

            # Preprocess frame for hand detection (320x240)
            detection_frame = self._preprocess_frame_for_detection(frame)
            
            # Run hand detection
            detection_input = {self.hand_detector.get_inputs()[0].name: detection_frame}
            detection_outputs = self.hand_detector.run(None, detection_input)
            
            # Parse detection results
            hands_detected = 0
            detected_gestures = []
            total_confidence = 0.0
            
            # Process detection outputs (assuming YOLO-style outputs)
            if len(detection_outputs) > 0:
                detections = detection_outputs[0]  # First output contains detections
                
                # Filter detections by confidence threshold
                confidence_threshold = 0.5
                for detection in detections:
                    if len(detection) >= 5:  # [x, y, w, h, confidence, ...]
                        conf = float(detection[4])
                        if conf > confidence_threshold:
                            hands_detected += 1
                            
                            # Extract hand region for gesture classification
                            x, y, w, h = detection[:4]
                            hand_crop = self._extract_hand_crop(frame, x, y, w, h)
                            
                            # Classify gesture
                            gesture_name, gesture_conf = self._classify_gesture(hand_crop)
                            detected_gestures.append(gesture_name)
                            total_confidence += gesture_conf

            # Calculate average confidence from model
            avg_confidence = total_confidence / hands_detected if hands_detected > 0 else 0.0
            
            # Calculate gesture-based confidence for interview assessment
            gesture_confidence = self._calculate_gesture_confidence(detected_gestures)
            
            # Determine confidence level based on gesture assessment
            confidence_level = self._determine_confidence_level(gesture_confidence)
            
            self.logger.info(f"📊 Model confidence: {avg_confidence:.2f}, Gesture confidence: {gesture_confidence:.2f}")
            self.logger.info(f"📊 Final result: {confidence_level} (gestures: {detected_gestures})")
            
            return {
                'confidence_level': confidence_level,
                'confidence': float(gesture_confidence),  # Use gesture-based confidence
                'model_confidence': float(avg_confidence),  # Keep original model confidence
                'gestures_detected': detected_gestures,
                'hands_detected': hands_detected,
                'method': 'dynamic_gestures_onnx',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in ONNX detection: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                'confidence_level': 'not_confident',
                'confidence': 0.0,
                'gestures_detected': ['error'],
                'hands_detected': 0,
                'method': 'error',
                'timestamp': datetime.now().isoformat()
            }

    def _preprocess_frame_for_detection(self, frame):
        """Preprocess frame for ONNX hand detection model (320x240)"""
        # Resize to model input size
        resized = cv2.resize(frame, (320, 240))
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        
        # Normalize for HaGRID model - ensure float32 throughout
        normalized = rgb_frame.astype(np.float32)
        normalized = (normalized - 127.0) / 128.0  # Use float32 constants
        
        # Add batch dimension and transpose to NCHW
        input_data = np.transpose(normalized, (2, 0, 1))  # HWC to CHW
        input_data = np.expand_dims(input_data, axis=0)  # Add batch dimension
        
        # Ensure final output is float32
        return input_data.astype(np.float32)

    def _extract_hand_crop(self, frame, x, y, w, h):
        """Extract hand crop from frame for gesture classification"""
        h_frame, w_frame = frame.shape[:2]
        
        # Convert normalized coordinates to pixel coordinates if needed
        if x <= 1.0 and y <= 1.0:  # Normalized coordinates
            x = int(x * w_frame)
            y = int(y * h_frame)
            w = int(w * w_frame)  
            h = int(h * h_frame)
        
        # Ensure crop bounds are within frame
        x1 = max(0, int(x - w/2))
        y1 = max(0, int(y - h/2))
        x2 = min(w_frame, int(x + w/2))
        y2 = min(h_frame, int(y + h/2))
        
        # Extract crop
        crop = frame[y1:y2, x1:x2]
        
        # Resize to classifier input size (assuming 224x224)
        if crop.size > 0:
            crop = cv2.resize(crop, (224, 224))
        else:
            crop = np.zeros((224, 224, 3), dtype=np.uint8)
        
        return crop

    def _classify_gesture(self, hand_crop):
        """Classify gesture from hand crop using ONNX gesture classifier"""
        try:
            # Preprocess crop for gesture classification
            processed_crop = self._preprocess_crop_for_classification(hand_crop)
            
            # Run gesture classification
            classifier_input = {self.gesture_classifier.get_inputs()[0].name: processed_crop}
            classifier_outputs = self.gesture_classifier.run(None, classifier_input)
            
            # Get gesture predictions
            predictions = classifier_outputs[0][0]  # First batch, first output
            
            # Apply softmax to get probabilities
            probabilities = softmax(predictions)
            
            # Get predicted class
            predicted_class = np.argmax(probabilities)
            max_confidence = float(probabilities[predicted_class])
            
            # Map class index to gesture name
            gesture_names = self._get_gesture_names()
            detected_gesture = gesture_names[predicted_class] if predicted_class < len(gesture_names) else 'unknown'
            
            return detected_gesture, max_confidence
            
        except Exception as e:
            self.logger.error(f"Error in gesture classification: {e}")
            return 'unknown', 0.0

    def _preprocess_crop_for_classification(self, crop):
        """Preprocess hand crop for gesture classification"""
        # Convert BGR to RGB
        rgb_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        
        # Normalize for HaGRID model  
        normalized = rgb_crop.astype(np.float32)
        normalized = (normalized - [127, 127, 127]) / [128, 128, 128]
        
        # Add batch dimension and transpose to NCHW
        input_data = np.transpose(normalized, (2, 0, 1))  # HWC to CHW
        input_data = np.expand_dims(input_data, axis=0)  # Add batch dimension
        
        return input_data

    def _determine_confidence_level(self, confidence):
        """Determine confidence level based on numeric confidence"""
        if confidence >= 0.8:
            return 'high'
        elif confidence >= 0.5:
            return 'medium' 
        elif confidence > 0:
            return 'low'
        else:
            return 'not_confident'

    def _perform_onnx_detection(self, frame):
        """Perform ONNX-based hand detection and gesture classification"""
        try:
            # Preprocess frame for hand detection  
            detection_input = self._preprocess_frame_for_detection(frame)
            
            # Run hand detection
            detection_outputs = self.hand_detector.run(None, {"input": detection_input})
            
            hands_count = 0
            detected_gestures = []
            total_confidence = 0.0
            
            # Process detection results
            if len(detection_outputs) > 0 and detection_outputs[0] is not None:
                boxes = detection_outputs[0]  # Shape: [N, 4] where N is number of detections
                scores = detection_outputs[2] if len(detection_outputs) > 2 else []  # Confidence scores
                
                # Check if any detections were found
                if len(boxes) > 0 and len(scores) > 0:
                    # Filter by confidence threshold
                    confidence_threshold = 0.3
                    for i, (box, score) in enumerate(zip(boxes, scores)):
                        if score > confidence_threshold:
                            hands_count += 1
                            total_confidence += score
                            
                            # Extract bounding box coordinates
                            x1, y1, x2, y2 = box[:4]
                            
                            # Crop hand region from original frame
                            h, w = frame.shape[:2]
                            x1, y1, x2, y2 = int(x1 * w), int(y1 * h), int(x2 * w), int(y2 * h)
                            
                            # Ensure valid crop coordinates
                            x1, y1 = max(0, x1), max(0, y1)
                            x2, y2 = min(w, x2), min(h, y2)
                            
                            if x2 > x1 and y2 > y1:
                                hand_crop = frame[y1:y2, x1:x2]
                                
                                # Classify gesture
                                gesture_result = self._classify_gesture(hand_crop)
                                if gesture_result:
                                    detected_gestures.append(gesture_result['gesture'])
                                    total_confidence += gesture_result['confidence']
            
            # Calculate average confidence from model
            avg_confidence = total_confidence / hands_count if hands_count > 0 else 0.0
            
            # Calculate gesture-based confidence for interview assessment
            gesture_confidence = self._calculate_gesture_confidence(detected_gestures)
            
            # Determine confidence level based on gesture assessment
            confidence_level = self._determine_confidence_level(gesture_confidence)
            
            self.logger.info(f"📊 Model confidence: {avg_confidence:.2f}, Gesture confidence: {gesture_confidence:.2f}")
            self.logger.info(f"📊 Final result: {confidence_level} (gestures: {detected_gestures})")
            
            return {
                'confidence_level': confidence_level,
                'confidence': float(gesture_confidence),  # Use gesture-based confidence
                'model_confidence': float(avg_confidence),  # Keep original model confidence
                'gestures_detected': detected_gestures,
                'hands_detected': hands_count,
                'method': 'dynamic_gestures_onnx',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in ONNX detection: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            
            return {
                'confidence_level': 'low',
                'confidence': 0.0,
                'gestures_detected': ['error'],
                'hands_detected': 0,
                'method': 'error',
                'timestamp': datetime.now().isoformat()
            }

    def _preprocess_frame_for_detection(self, frame):
        """Preprocess frame for hand detection model - HaGRID format"""
        # Resize to model input size (320x240)
        resized = cv2.resize(frame, (320, 240))
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        
        # HaGRID normalization - ensure float32 throughout
        normalized = rgb_frame.astype(np.float32)
        normalized = (normalized - 127.0) / 128.0  # Use float32 constants
        
        # Add batch dimension and transpose to NCHW
        input_tensor = np.transpose(normalized, (2, 0, 1))  # HWC to CHW
        input_tensor = np.expand_dims(input_tensor, axis=0)  # Add batch dimension
        
        # Ensure final output is float32
        return input_tensor.astype(np.float32)

    def _classify_gesture(self, hand_crop):
        """Classify gesture from hand crop using ONNX classifier"""
        try:
            # Preprocess crop for classification (224x224)
            resized_crop = cv2.resize(hand_crop, (224, 224))
            rgb_crop = cv2.cvtColor(resized_crop, cv2.COLOR_BGR2RGB)
            
            # HaGRID normalization
            normalized_crop = rgb_crop.astype(np.float32)
            normalized_crop = (normalized_crop - [127, 127, 127]) / [128, 128, 128]
            
            # Transpose to CHW and add batch dimension
            crop_tensor = np.transpose(normalized_crop, (2, 0, 1))
            crop_tensor = np.expand_dims(crop_tensor, axis=0)
            
            # Run gesture classification
            outputs = self.gesture_classifier.run(None, {"input": crop_tensor})
            
            if outputs and len(outputs) > 0:
                predictions = outputs[0][0]  # Remove batch dimension
                
                # Apply softmax to get probabilities
                probabilities = softmax(predictions)
                
                # Get top prediction
                max_idx = np.argmax(probabilities)
                max_prob = probabilities[max_idx]
                
                gesture_names = self._get_gesture_names()
                if max_idx < len(gesture_names) and max_prob > 0.3:
                    return {
                        'gesture': gesture_names[max_idx],
                        'confidence': float(max_prob)
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in gesture classification: {e}")
            return None

    def _get_gesture_names(self):
        """Get list of gesture names supported by the model"""
        return [
            # Static gestures
            'hand_down', 'hand_right', 'hand_left', 'palm',
            'one', 'one_left', 'one_right', 'one_down',
            'two_up', 'two_up_inverted', 'two_left', 'two_right', 'two_down',
            'three', 'three2', 'three3', 'three_gun', 'four',
            'thumb_index', 'thumb_left', 'thumb_right', 'thumb_down',
            'like', 'dislike', 'ok', 'peace', 'peace_inverted',
            'call', 'stop', 'stop_inverted', 'point', 'mute',
            'fist', 'fist_inverted', 'rock', 'grabbing', 'grip',
            'half_up', 'half_left', 'half_right', 'half_down',
            'part_hand_heart', 'part_hand_heart2',
            'little_finger', 'middle_finger',
            # Dynamic gestures
            'SWIPE_RIGHT_1', 'SWIPE_RIGHT_2', 'SWIPE_RIGHT_3',
            'SWIPE_LEFT_1', 'SWIPE_LEFT_2', 'SWIPE_LEFT_3',
            'SWIPE_UP_1', 'SWIPE_UP_2', 'SWIPE_UP_3',
            'SWIPE_DOWN_1', 'SWIPE_DOWN_2', 'SWIPE_DOWN_3',
            'FAST_SWIPE_UP', 'FAST_SWIPE_DOWN',
            'ZOOM_IN', 'ZOOM_OUT',
            'DRAG_AND_DROP_1', 'DRAG_AND_DROP_2', 'DRAG_AND_DROP_3',
            'CLICK', 'TAP', 'DOUBLE_TAP'
        ]
    
    def _get_gesture_categories(self):
        """Categorize gestures as positive, negative, or neutral for confidence calculation"""
        return {
            'positive': {
                # Static gestures - Confident/Professional
                'palm', 'ok', 'peace', 'like', 'thumb_index', 'thumb_left', 'thumb_right', 'thumb_down',
                'one', 'one_left', 'one_right', 'one_down', 'two_up', 'three', 'three2', 'three3', 'four',
                'call', 'point',
                # Dynamic gestures - Positive interaction
                'CLICK', 'TAP', 'DOUBLE_TAP', 'SWIPE_RIGHT_1', 'SWIPE_RIGHT_2', 'SWIPE_RIGHT_3',
                'SWIPE_UP_1', 'SWIPE_UP_2', 'SWIPE_UP_3'
            },
            'negative': {
                # Static gestures - Not confident/Unprofessional
                'dislike', 'stop', 'stop_inverted', 'fist', 'fist_inverted', 'middle_finger', 'mute',
                'grabbing', 'grip', 'rock', 'little_finger',
                # Dynamic gestures - Negative interaction
                'SWIPE_LEFT_1', 'SWIPE_LEFT_2', 'SWIPE_LEFT_3', 'SWIPE_DOWN_1', 'SWIPE_DOWN_2', 'SWIPE_DOWN_3',
                'FAST_SWIPE_DOWN'
            },
            'neutral': {
                # Static gestures - Context-dependent (0.5 points)
                'hand_down', 'hand_right', 'hand_left', 'two_up_inverted', 'two_left', 'two_right', 'two_down',
                'three_gun', 'peace_inverted', 'half_up', 'half_left', 'half_right', 'half_down',
                'part_hand_heart', 'part_hand_heart2',
                # Dynamic gestures - Neutral interaction (0.5 points)
                'ZOOM_IN', 'ZOOM_OUT', 'DRAG_AND_DROP_1', 'DRAG_AND_DROP_2', 'DRAG_AND_DROP_3', 'FAST_SWIPE_UP'
            }
        }
    
    def _calculate_gesture_confidence(self, detected_gestures):
        """Calculate confidence based on positive/negative/neutral gesture ratio"""
        if not detected_gestures:
            return 0.0
        
        categories = self._get_gesture_categories()
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        # Count gesture types
        for gesture in detected_gestures:
            if gesture in categories['positive']:
                positive_count += 1
            elif gesture in categories['negative']:
                negative_count += 1
            elif gesture in categories['neutral']:
                neutral_count += 1
        
        # Calculate total points (neutral = 0.5 points)
        total_gestures = len(detected_gestures)
        positive_points = positive_count + (neutral_count * 0.5)
        
        self.logger.info(f"🎯 Gesture analysis: Positive={positive_count}, Negative={negative_count}, Neutral={neutral_count}")
        self.logger.info(f"📊 Points: {positive_points}/{total_gestures} = {positive_points/total_gestures:.2f}")
        
        # Determine confidence based on gesture ratio
        if negative_count > 0 and positive_count > 0:
            # Mixed gestures = 0.5 confidence
            confidence = 0.5
        elif negative_count > 0 and positive_count == 0:
            # Only negative gestures = 0.0 confidence
            confidence = 0.0
        elif positive_points == total_gestures:
            # All positive gestures = 1.0 confidence
            confidence = 1.0
        elif positive_points > negative_count:
            # More positive than negative = 1.0 confidence
            confidence = 1.0
        else:
            # Calculate proportional confidence
            confidence = positive_points / total_gestures
        
        return min(1.0, max(0.0, confidence))  # Ensure 0.0-1.0 range

    def _determine_confidence_level(self, confidence_score):
        """Convert confidence score to level"""
        if confidence_score >= 0.8:
            return 'high'
        elif confidence_score >= 0.4:
            return 'medium'
        else:
            return 'low'

    def _get_gesture_names(self):
        """Get list of gesture names supported by the model"""
        return [
            # Static gestures
            'hand_down', 'hand_right', 'hand_left', 'palm',
            'one', 'one_left', 'one_right', 'one_down',
            'two_up', 'two_up_inverted', 'two_left', 'two_right', 'two_down',
            'three', 'three2', 'three3', 'three_gun', 'four',
            'thumb_index', 'thumb_left', 'thumb_right', 'thumb_down',
            'like', 'dislike', 'ok', 'peace', 'peace_inverted',
            'call', 'stop', 'stop_inverted', 'point', 'mute',
            'fist', 'fist_inverted', 'rock', 'grabbing', 'grip',
            'half_up', 'half_left', 'half_right', 'half_down',
            'part_hand_heart', 'part_hand_heart2',
            'little_finger', 'middle_finger',
            # Dynamic gestures
            'SWIPE_RIGHT_1', 'SWIPE_RIGHT_2', 'SWIPE_RIGHT_3',
            'SWIPE_LEFT_1', 'SWIPE_LEFT_2', 'SWIPE_LEFT_3',
            'SWIPE_UP_1', 'SWIPE_UP_2', 'SWIPE_UP_3',
            'SWIPE_DOWN_1', 'SWIPE_DOWN_2', 'SWIPE_DOWN_3',
            'FAST_SWIPE_UP', 'FAST_SWIPE_DOWN',
            'ZOOM_IN', 'ZOOM_OUT',
            'DRAG_AND_DROP_1', 'DRAG_AND_DROP_2', 'DRAG_AND_DROP_3',
            'CLICK', 'TAP', 'DOUBLE_TAP'
        ]
    
    def _get_gesture_categories(self):
        """Categorize gestures as positive, negative, or neutral for confidence calculation"""
        return {
            'positive': {
                # Static gestures - Confident/Professional
                'palm', 'ok', 'peace', 'like', 'thumb_index', 'thumb_left', 'thumb_right', 'thumb_down',
                'one', 'one_left', 'one_right', 'one_down', 'two_up', 'three', 'three2', 'three3', 'four',
                'call', 'point',
                # Dynamic gestures - Positive interaction
                'CLICK', 'TAP', 'DOUBLE_TAP', 'SWIPE_RIGHT_1', 'SWIPE_RIGHT_2', 'SWIPE_RIGHT_3',
                'SWIPE_UP_1', 'SWIPE_UP_2', 'SWIPE_UP_3'
            },
            'negative': {
                # Static gestures - Not confident/Unprofessional
                'dislike', 'stop', 'stop_inverted', 'fist', 'fist_inverted', 'middle_finger', 'mute',
                'grabbing', 'grip', 'rock', 'little_finger',
                # Dynamic gestures - Negative interaction
                'SWIPE_LEFT_1', 'SWIPE_LEFT_2', 'SWIPE_LEFT_3', 'SWIPE_DOWN_1', 'SWIPE_DOWN_2', 'SWIPE_DOWN_3',
                'FAST_SWIPE_DOWN'
            },
            'neutral': {
                # Static gestures - Context-dependent (0.5 points)
                'hand_down', 'hand_right', 'hand_left', 'two_up_inverted', 'two_left', 'two_right', 'two_down',
                'three_gun', 'peace_inverted', 'half_up', 'half_left', 'half_right', 'half_down',
                'part_hand_heart', 'part_hand_heart2',
                # Dynamic gestures - Neutral interaction (0.5 points)
                'ZOOM_IN', 'ZOOM_OUT', 'DRAG_AND_DROP_1', 'DRAG_AND_DROP_2', 'DRAG_AND_DROP_3', 'FAST_SWIPE_UP'
            }
        }
    
    def _calculate_gesture_confidence(self, detected_gestures):
        """Calculate confidence based on positive/negative/neutral gesture ratio"""
        if not detected_gestures:
            return 0.0
        
        categories = self._get_gesture_categories()
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        # Count gesture types
        for gesture in detected_gestures:
            if gesture in categories['positive']:
                positive_count += 1
            elif gesture in categories['negative']:
                negative_count += 1
            elif gesture in categories['neutral']:
                neutral_count += 1
        
        # Calculate total points (neutral = 0.5 points)
        total_gestures = len(detected_gestures)
        positive_points = positive_count + (neutral_count * 0.5)
        
        self.logger.info(f"🎯 Gesture analysis: Positive={positive_count}, Negative={negative_count}, Neutral={neutral_count}")
        self.logger.info(f"📊 Points: {positive_points}/{total_gestures} = {positive_points/total_gestures:.2f}")
        
        # Determine confidence based on gesture ratio
        if negative_count > 0 and positive_count > 0:
            # Mixed gestures = 0.5 confidence
            confidence = 0.5
        elif negative_count > 0 and positive_count == 0:
            # Only negative gestures = 0.0 confidence
            confidence = 0.0
        elif positive_points == total_gestures:
            # All positive gestures = 1.0 confidence
            confidence = 1.0
        elif positive_points > negative_count:
            # More positive than negative = 1.0 confidence
            confidence = 1.0
        else:
            # Calculate proportional confidence
            confidence = positive_points / total_gestures
        
        return min(1.0, max(0.0, confidence))  # Ensure 0.0-1.0 range

class HandConfidenceDetector(DynamicGesturesDetector):
    """Alias for compatibility with existing code"""
    pass

def save_hand_data(user_id, session_id, hand_data):
    """Save hand confidence data to database"""
    try:
        if not user_id or not session_id:
            logger.error("Missing user_id or session_id")
            return False
        
        db_manager = DatabaseManager(user_id)
        
        analysis_data = {
            'session_id': session_id,
            'type': 'hand_confidence',
            'timestamp': hand_data.get('timestamp', datetime.now().isoformat()),
            'prediction': hand_data,
            'model_version': '1.0'
        }
        
        result = db_manager.save_analysis_result(session_id, analysis_data)
        
        if result:
            logger.info(f"✅ Saved hand confidence data: {hand_data['confidence_level']}")
            return True
        else:
            logger.error("❌ Failed to save hand confidence data")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error saving hand data: {e}")
        return False

# Test function
def test_hand_confidence_detection():
    """Test hand confidence detection with webcam using new YOLO model"""
    detector = HandConfidenceDetectorWrapper()
    
    # Test with webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        logger.error("Cannot open webcam")
        return
    
    logger.info("Testing YOLO11n-pose hand confidence detection. Press 'q' to quit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect hand confidence using new YOLO model
        result = detector.detect_confidence(frame)
        
        # Display result on frame
        cv2.putText(frame, f"Confidence: {result['confidence_level']}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Score: {result['confidence']:.2f}", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Display additional YOLO model information
        if 'gesture_detected' in result:
            cv2.putText(frame, f"Gesture: {result['gesture_detected']}", (10, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        if 'stability_score' in result:
            cv2.putText(frame, f"Stability: {result['stability_score']:.2f}", (10, 140),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        if 'orientation' in result:
            cv2.putText(frame, f"Orientation: {result['orientation']}", (10, 170),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        cv2.imshow('YOLO11n-pose Hand Confidence Detection Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Test the hand confidence detection
    test_hand_confidence_detection()