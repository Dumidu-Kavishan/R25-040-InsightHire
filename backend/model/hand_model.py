"""
Dynamic Hand Gesture Detection Model for InsightHire
Using HaGRID dynamic gestures ONNX models
"""
import cv2
import numpy as np
import os
import logging
import json
import math
from datetime import datetime
from collections import deque

# Try to import ONNX runtime for dynamic gestures
try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    ort = None

# Try to import scipy for softmax
try:
    from scipy.special import softmax
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    softmax = None

# Import fallback models
try:
    from hand_confidence_fallback import HandConfidenceFallback
except ImportError:
    HandConfidenceFallback = None

# Configure logging
logger = logging.getLogger(__name__)


class DynamicGesturesDetector:
    """Dynamic Hand Gestures Detector using HaGRID ONNX models"""
    
    def __init__(self):
        """Initialize Dynamic Gestures Detector"""
        self.hand_detector_session = None
        self.gesture_classifier_session = None
        
        # Configure logging
        self.logger = logging.getLogger('DynamicGesturesDetection')
        
        # Load ONNX models
        self._load_models()
    
    def _load_models(self):
        """Load ONNX models for hand detection and gesture classification"""
        try:
            if not ONNX_AVAILABLE:
                self.logger.warning("⚠️ ONNX Runtime not available")
                return
            
            # Get model paths - go up from backend/model/ to project root, then to Models
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            base_path = os.path.join(project_root, 'Models', 'Hand', 'dynamic_gestures', 'models')
            
            self.logger.info(f"🔍 Looking for models in: {base_path}")
            
            detector_path = os.path.join(base_path, 'hand_detector.onnx')
            classifier_path = os.path.join(base_path, 'crops_classifier.onnx')
            
            # Load hand detector
            if os.path.exists(detector_path):
                self.hand_detector_session = ort.InferenceSession(detector_path)
                self.logger.info("✅ Hand detector ONNX model loaded")
                
                # Get input shape for debugging
                input_info = self.hand_detector_session.get_inputs()[0]
                self.logger.info(f"🔍 Hand detector input shape: {input_info.shape}, name: {input_info.name}")
            else:
                self.logger.warning(f"⚠️ Hand detector not found: {detector_path}")
            
            # Load gesture classifier
            if os.path.exists(classifier_path):
                self.gesture_classifier_session = ort.InferenceSession(classifier_path)
                self.logger.info("✅ Gesture classifier ONNX model loaded")
                
                # Get input shape for debugging
                input_info = self.gesture_classifier_session.get_inputs()[0]
                self.logger.info(f"🔍 Gesture classifier input shape: {input_info.shape}, name: {input_info.name}")
            else:
                self.logger.warning(f"⚠️ Gesture classifier not found: {classifier_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Error loading dynamic gestures models: {e}")
            raise
    
    def detect_confidence(self, frame):
        """Main detection method - returns results in expected format"""
        try:
            # Check if models are loaded
            if self.hand_detector_session is None or self.gesture_classifier_session is None:
                return self._get_no_model_result()
            
            # Implement actual ONNX detection
            return self._perform_onnx_detection(frame)
                
        except Exception as e:
            self.logger.error(f"Error in gesture detection: {e}")
            return self._get_error_result(str(e))
    
    def _perform_onnx_detection(self, frame):
        """Perform actual ONNX model inference"""
        try:
            self.logger.info("🎥 Starting hand detection on new frame")
            
            # Preprocess frame for hand detection
            input_frame = self._preprocess_frame_for_detection(frame)
            if input_frame is None:
                self.logger.warning("⚠️ Frame preprocessing failed")
                return self._get_no_hands_result()
            
            # Run hand detection
            hand_detections = self._run_hand_detection(input_frame, frame)
            
            self.logger.info(f"🔍 Hand detection result: {len(hand_detections)} hands found")
            
            if not hand_detections or len(hand_detections) == 0:
                self.logger.info("❌ No hands detected in frame")
                return self._get_no_hands_result()
            
            # Process each detected hand
            detected_gestures = []
            total_confidence = 0.0
            hands_count = len(hand_detections)
            
            self.logger.info(f"👐 Processing {hands_count} detected hands")
            
            for i, hand_bbox in enumerate(hand_detections):
                self.logger.info(f"🖐️ Processing hand {i+1}: confidence={hand_bbox.get('confidence', 'unknown')}")
                
                # Extract hand region
                hand_crop = self._extract_hand_region(frame, hand_bbox)
                if hand_crop is None:
                    self.logger.warning(f"⚠️ Failed to extract hand region for hand {i+1}")
                    continue
                
                # Classify gesture
                gesture_result = self._classify_gesture(hand_crop)
                if gesture_result:
                    self.logger.info(f"🎯 Hand {i+1} gestures: {gesture_result['gestures']} (conf: {gesture_result['confidence']})")
                    detected_gestures.extend(gesture_result['gestures'])
                    total_confidence += gesture_result['confidence']
                else:
                    self.logger.warning(f"⚠️ Failed to classify gesture for hand {i+1}")
            
            # Calculate average confidence
            avg_confidence = total_confidence / hands_count if hands_count > 0 else 0.0
            
            # Determine confidence level
            confidence_level = self._determine_confidence_level(avg_confidence)
            
            self.logger.info(f"📊 Final result: {confidence_level} (conf: {avg_confidence:.2f}, gestures: {detected_gestures})")
            
            return {
                'confidence_level': confidence_level,
                'confidence': float(avg_confidence),
                'gestures_detected': detected_gestures,
                'hands_detected': hands_count,
                'method': 'dynamic_gestures_onnx',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in ONNX detection: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return self._get_error_result(str(e))
    
    def _preprocess_frame_for_detection(self, frame):
        """Preprocess frame for hand detection model using HaGRID specifications"""
        try:
            # Get the expected input size from the model
            if self.hand_detector_session:
                input_shape = self.hand_detector_session.get_inputs()[0].shape
                # Shape is typically [batch, channels, height, width]
                if len(input_shape) >= 4:
                    _, _, height, width = input_shape
                    target_size = (width, height)  # cv2.resize expects (width, height)
                else:
                    # Fallback to what we learned from the error
                    target_size = (320, 240)
            else:
                target_size = (320, 240)
            
            self.logger.info(f"🔧 Preprocessing frame: {frame.shape} -> {target_size}")
            
            # Resize frame
            resized = cv2.resize(frame, target_size)
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            
            # Apply HaGRID normalization: (image - mean) / std
            mean = np.array([127, 127, 127], dtype=np.float32)
            std = np.array([128, 128, 128], dtype=np.float32)
            normalized = (rgb_frame.astype(np.float32) - mean) / std
            
            # Transpose to (C, H, W) and add batch dimension -> (1, C, H, W)
            input_tensor = np.transpose(normalized, (2, 0, 1))
            input_tensor = np.expand_dims(input_tensor, axis=0)
            
            self.logger.info(f"✅ Preprocessed tensor shape: {input_tensor.shape}")
            
            return input_tensor
            
        except Exception as e:
            self.logger.error(f"Error preprocessing frame: {e}")
            return None
    
    def _run_hand_detection(self, input_tensor, original_frame):
        """Run hand detection using ONNX model"""
        try:
            if input_tensor is None:
                return []
            
            # Get input name for the model
            input_name = self.hand_detector_session.get_inputs()[0].name
            
            # Run inference
            outputs = self.hand_detector_session.run(None, {input_name: input_tensor})
            
            # Parse outputs to get hand bounding boxes
            hand_boxes = self._parse_detection_outputs(outputs, original_frame)
            
            return hand_boxes
            
        except Exception as e:
            self.logger.error(f"Error running hand detection: {e}")
            return []
    
    def _parse_detection_outputs(self, outputs, original_frame):
        """Parse HaGRID detection outputs"""
        try:
            # Log output structure for debugging
            self.logger.info(f"🔍 Detection outputs structure: {len(outputs)} outputs")
            for i, output in enumerate(outputs):
                self.logger.info(f"🔍 Output {i} shape: {output.shape}")
            
            # HaGRID outputs: [boxes, labels, scores]
            boxes = outputs[0] if len(outputs) > 0 else None
            scores = outputs[2] if len(outputs) > 2 else None
            
            if boxes is None or scores is None:
                self.logger.warning("⚠️ Missing detection outputs")
                return []
            
            self.logger.info(f"🔍 Boxes shape: {boxes.shape}, Scores shape: {scores.shape}")
            
            hand_boxes = []
            confidence_threshold = 0.1  # Very low threshold for debugging
            
            # Get original frame dimensions
            frame_height, frame_width = original_frame.shape[:2]
            
            self.logger.info(f"🔍 Processing {len(boxes)} detected boxes")
            
            for i in range(len(boxes)):
                if i < len(scores):
                    conf = scores[i]
                    
                    self.logger.info(f"🔍 Detection {i}: conf={conf}, bbox={boxes[i]}")
                    
                    if conf > confidence_threshold:
                        # HaGRID returns boxes as [x1, y1, x2, y2] in normalized coordinates
                        x1, y1, x2, y2 = boxes[i]
                        
                        # Scale to original frame size (HaGRID example does this)
                        x1 = int(x1 * frame_width)
                        y1 = int(y1 * frame_height)
                        x2 = int(x2 * frame_width)
                        y2 = int(y2 * frame_height)
                        
                        # Convert to [x, y, w, h] format
                        w = x2 - x1
                        h = y2 - y1
                        
                        self.logger.info(f"✅ Hand detected with confidence {conf}: [{x1}, {y1}, {w}, {h}]")
                        hand_boxes.append({
                            'bbox': [float(x1), float(y1), float(w), float(h)],
                            'confidence': float(conf)
                        })
            
            self.logger.info(f"🎯 Found {len(hand_boxes)} hands above threshold {confidence_threshold}")
            return hand_boxes
            
        except Exception as e:
            self.logger.error(f"Error parsing detection outputs: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    def _extract_hand_region(self, frame, hand_bbox):
        """Extract hand region from frame using bounding box"""
        try:
            bbox = hand_bbox['bbox']
            h, w = frame.shape[:2]
            
            # Convert normalized coordinates to absolute if needed
            x1 = int(bbox[0] * w) if bbox[0] <= 1.0 else int(bbox[0])
            y1 = int(bbox[1] * h) if bbox[1] <= 1.0 else int(bbox[1])
            x2 = int((bbox[0] + bbox[2]) * w) if bbox[2] <= 1.0 else int(bbox[0] + bbox[2])
            y2 = int((bbox[1] + bbox[3]) * h) if bbox[3] <= 1.0 else int(bbox[1] + bbox[3])
            
            # Ensure coordinates are within frame bounds
            x1 = max(0, min(x1, w-1))
            y1 = max(0, min(y1, h-1))
            x2 = max(x1+1, min(x2, w))
            y2 = max(y1+1, min(y2, h))
            
            # Extract hand crop
            hand_crop = frame[y1:y2, x1:x2]
            
            return hand_crop
            
        except Exception as e:
            self.logger.error(f"Error extracting hand region: {e}")
            return None
    
    def _classify_gesture(self, hand_crop):
        """Classify gesture using gesture classifier"""
        try:
            if hand_crop is None or hand_crop.size == 0:
                return None
            
            # Preprocess hand crop for classification
            input_tensor = self._preprocess_hand_crop(hand_crop)
            if input_tensor is None:
                return None
            
            # Get input name for classifier
            input_name = self.gesture_classifier_session.get_inputs()[0].name
            
            # Run classification
            outputs = self.gesture_classifier_session.run(None, {input_name: input_tensor})
            
            # Parse classification results
            gesture_result = self._parse_classification_outputs(outputs)
            
            return gesture_result
            
        except Exception as e:
            self.logger.error(f"Error classifying gesture: {e}")
            return None
    
    def _preprocess_hand_crop(self, hand_crop):
        """Preprocess hand crop for gesture classification using HaGRID specifications"""
        try:
            # Get the expected input size from the classifier model
            if self.gesture_classifier_session:
                input_shape = self.gesture_classifier_session.get_inputs()[0].shape
                # Shape is typically [batch, channels, height, width]
                if len(input_shape) >= 4:
                    _, _, height, width = input_shape
                    target_size = (width, height)  # cv2.resize expects (width, height)
                else:
                    target_size = (128, 128)  # HaGRID default
            else:
                target_size = (128, 128)
            
            self.logger.info(f"🔧 Preprocessing hand crop: {hand_crop.shape} -> {target_size}")
            
            # Resize to classifier input size
            resized = cv2.resize(hand_crop, target_size)
            
            # Convert BGR to RGB
            rgb_crop = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            
            # Apply HaGRID normalization: (image - mean) / std
            mean = np.array([127, 127, 127], dtype=np.float32)
            std = np.array([128, 128, 128], dtype=np.float32)
            normalized = (rgb_crop.astype(np.float32) - mean) / std
            
            # Transpose to (C, H, W) and add batch dimension -> (1, C, H, W)
            input_tensor = np.transpose(normalized, (2, 0, 1))
            input_tensor = np.expand_dims(input_tensor, axis=0)
            
            return input_tensor
            
        except Exception as e:
            self.logger.error(f"Error preprocessing hand crop: {e}")
            return None
    
    def _parse_classification_outputs(self, outputs):
        """Parse gesture classification outputs"""
        try:
            # Get the prediction probabilities
            predictions = outputs[0][0]  # Remove batch dimension
            
            # Apply softmax if not already applied
            if SCIPY_AVAILABLE:
                probabilities = softmax(predictions)
            else:
                # Simple softmax implementation
                exp_preds = np.exp(predictions - np.max(predictions))
                probabilities = exp_preds / np.sum(exp_preds)
            
            # Get top predictions
            top_indices = np.argsort(probabilities)[-3:][::-1]  # Top 3
            
            # Map indices to gesture names
            gesture_names = self._get_gesture_names()
            detected_gestures = []
            total_confidence = 0.0
            
            for idx in top_indices:
                if idx < len(gesture_names) and probabilities[idx] > 0.1:  # Threshold
                    detected_gestures.append(gesture_names[idx])
                    total_confidence += probabilities[idx]
            
            return {
                'gestures': detected_gestures,
                'confidence': float(total_confidence / len(detected_gestures)) if detected_gestures else 0.0
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing classification outputs: {e}")
            return {'gestures': [], 'confidence': 0.0}
    
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
    
    def _determine_confidence_level(self, confidence):
        """Determine confidence level from numeric confidence"""
        if confidence >= 0.8:
            return 'very_confident'
        elif confidence >= 0.6:
            return 'confident'
        elif confidence >= 0.4:
            return 'somewhat_confident'
        elif confidence >= 0.2:
            return 'not_confident'
        else:
            return 'very_unconfident'
    
    def _get_no_hands_result(self):
        """Result when no hands are detected"""
        return {
            'confidence_level': 'no_hands_detected',
            'confidence': 0.0,
            'gestures_detected': [],
            'hands_detected': 0,
            'method': 'dynamic_gestures_onnx',
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_no_model_result(self):
        """Result when models are not loaded"""
        return {
            'confidence_level': 'model_not_loaded',
            'confidence': 0.0,
            'gestures_detected': [],
            'hands_detected': 0,
            'method': 'dynamic_gestures_unavailable',
            'error': 'ONNX models not loaded',
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_error_result(self, error_msg):
        """Result when there's an error"""
        return {
            'confidence_level': 'error',
            'confidence': 0.0,
            'gestures_detected': ['error'],
            'hands_detected': 0,
            'method': 'dynamic_gestures_error',
            'error': error_msg,
            'timestamp': datetime.now().isoformat()
        }


# Create global instance for import compatibility
try:
    dynamic_detector = DynamicGesturesDetector()
    logger.info("✅ Dynamic gestures detector initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize dynamic gestures detector: {e}")
    dynamic_detector = None


class HandConfidenceDetector:
    """Legacy compatibility wrapper for dynamic gestures detector"""
    
    def __init__(self):
        """Initialize with DynamicGesturesDetector"""
        self.detector = dynamic_detector
        logger.info("🔄 HandConfidenceDetector initialized with dynamic gestures")
    
    def detect_confidence(self, frame):
        """Delegate to dynamic gestures detector"""
        if self.detector:
            return self.detector.detect_confidence(frame)
        else:
            return {
                'confidence_level': 'detector_not_available',
                'confidence': 0.0,
                'gestures_detected': ['error'],
                'hands_detected': 0,
                'method': 'dynamic_gestures_unavailable',
                'error': 'Dynamic gestures detector not initialized',
                'timestamp': datetime.now().isoformat()
            }
    
    def is_available(self):
        """Check if the model is available"""
        return self.detector is not None
    
    def get_model_info(self):
        """Get information about the loaded model"""
        return {
            'dynamic_gestures_available': ONNX_AVAILABLE,
            'detector_loaded': self.detector is not None,
            'model_type': 'HaGRID Dynamic Gestures ONNX',
            'gestures_supported': 67  # 45 static + 22 dynamic
        }
