#!/usr/bin/env python3
"""
Hand Model Server for InsightHire
=================================

Dedicated server for hand gesture detection using the original HaGRID dynamic gestures model.
Runs on port 5002 in dedicated HandModel_Env conda environment.

Usage:
    conda activate HandModel_Env
    python hand_model_server.py
"""

import os
import sys
import cv2
import numpy as np
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
from datetime import datetime
import traceback

# Add the dynamic_gestures directory to path
dynamic_gestures_path = r"C:\Users\PM_User\Desktop\Projects\Research Project\R25-040-InsightHire\Models\Hand\dynamic_gestures"
sys.path.append(dynamic_gestures_path)

try:
    from main_controller import MainController
    from utils import targets
    print("✅ Successfully imported hand gesture modules")
    print(f"📝 Available gestures: {len(targets)} - {targets[:10]}...")  # Show first 10 gestures
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure the dynamic_gestures directory exists and has the required modules")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('HandModelServer')

app = Flask(__name__)
CORS(app)

class HandModelServer:
    """Hand model server using original HaGRID dynamic gestures"""
    
    def __init__(self):
        self.controller = None
        self.gesture_confidence_mapping = {
            # Confident gestures (positive, stable)
            'like': 0.9,
            'peace': 0.8,
            'ok': 0.9,
            'thumb_up': 0.9,
            'palm': 0.7,
            'one': 0.6,
            'two_up': 0.7,
            'three': 0.7,
            'four': 0.7,
            'call': 0.8,
            
            # Medium confidence gestures
            'point': 0.6,
            'hand_up': 0.6,
            'hand_left': 0.5,
            'hand_right': 0.5,
            'thumb_left': 0.5,
            'thumb_right': 0.5,
            
            # Lower confidence gestures (nervous, uncertain)
            'fist': 0.3,
            'fist_inverted': 0.3,
            'hand_down': 0.2,
            'thumb_down': 0.1,
            'dislike': 0.1,
            'stop': 0.3,
            'mute': 0.2,
            'grabbing': 0.3,
            'grip': 0.3,
        }
        
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the hand gesture detection model"""
        try:
            # Model paths
            detection_model = os.path.join(dynamic_gestures_path, "models", "hand_detector.onnx")
            classification_model = os.path.join(dynamic_gestures_path, "models", "crops_classifier.onnx")
            
            if not os.path.exists(detection_model):
                raise FileNotFoundError(f"Detection model not found: {detection_model}")
            if not os.path.exists(classification_model):
                raise FileNotFoundError(f"Classification model not found: {classification_model}")
            
            # Initialize controller with relaxed settings for real-time analysis
            self.controller = MainController(
                detection_model=detection_model,
                classification_model=classification_model,
                max_age=30,
                min_hits=1,        # Reduced from 3 to 1 - confirm hands immediately
                iou_threshold=0.3,
                maxlen=30,
                min_frames=1       # Reduced from 20 to 1 - allow immediate gesture detection
            )
            
            logger.info("✅ Hand gesture model initialized successfully")
            logger.info(f"📁 Detection model: {detection_model}")
            logger.info(f"📁 Classification model: {classification_model}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize hand model: {e}")
            logger.error(traceback.format_exc())
            self.controller = None
    
    def analyze_frame(self, frame):
        """Analyze frame for hand gestures using actual MainController detection"""
        try:
            if self.controller is None:
                return {
                    'confidence_level': 'not_confident',
                    'confidence': 0.0,
                    'gestures_detected': ['model_not_loaded'],
                    'hands_detected': 0,
                    'method': 'error',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Debug step 1: Test detection model directly
            logger.info(f"🔍 Step 1: Testing detection model...")
            detection_bboxes, detection_probs = self.controller.detection_model(frame)
            logger.info(f"   - Detection bboxes: {detection_bboxes.shape if detection_bboxes is not None and hasattr(detection_bboxes, 'shape') else detection_bboxes}")
            logger.info(f"   - Detection probs: {detection_probs.shape if detection_probs is not None and hasattr(detection_probs, 'shape') else detection_probs}")
            
            # Debug step 2: Test classification model if hands detected
            classification_labels = None
            if detection_bboxes is not None and len(detection_bboxes) > 0:
                logger.info(f"🔍 Step 2: Testing classification model on {len(detection_bboxes)} detected hands...")
                try:
                    classification_labels = self.controller.classification_model(frame, detection_bboxes)
                    logger.info(f"   - Classification labels: {classification_labels}")
                    logger.info(f"   - Labels type: {type(classification_labels)}")
                    logger.info(f"   - Labels shape: {classification_labels.shape if hasattr(classification_labels, 'shape') else 'No shape'}")
                    
                    # Convert labels to gesture names
                    if classification_labels is not None:
                        for i, label in enumerate(classification_labels):
                            logger.info(f"   - Label {i}: {label} -> {targets[label] if 0 <= label < len(targets) else 'INVALID_LABEL'}")
                except Exception as e:
                    logger.error(f"   ❌ Classification model error: {e}")
                    logger.error(traceback.format_exc())
            
            # Process frame through the MainController (returns bboxes, ids, labels)
            logger.info(f"🔍 Step 3: Full MainController processing...")
            bboxes, ids, labels = self.controller(frame)
            
            # Debug: Log raw results from controller
            logger.info(f"🔍 MainController results:")
            logger.info(f"   - bboxes: {bboxes.shape if bboxes is not None and hasattr(bboxes, 'shape') else bboxes}")
            logger.info(f"   - ids: {ids}")
            logger.info(f"   - labels: {labels}")
            
            # CRITICAL FIX: If MainController fails but we have direct classification results, use those!
            if (bboxes is None or len(bboxes) == 0) and detection_bboxes is not None and len(detection_bboxes) > 0 and classification_labels is not None:
                logger.warning(f"⚠️ MainController tracking failed, but we have direct classification results. Using direct results!")
                logger.info(f"   - Using direct detection: {len(detection_bboxes)} hands")
                logger.info(f"   - Using direct labels: {classification_labels}")
                
                # Use direct results instead of MainController results
                bboxes = detection_bboxes
                ids = np.arange(1, len(detection_bboxes) + 1)  # Create simple IDs
                labels = classification_labels
                
                logger.info(f"🔧 Fixed results:")
                logger.info(f"   - bboxes: {bboxes.shape}")
                logger.info(f"   - ids: {ids}")
                logger.info(f"   - labels: {labels}")
            
            # Extract gesture information from actual detection results
            detected_gestures = []
            total_confidence = 0.0
            hands_count = 0
            
            # Process detection results if any hands found
            if bboxes is not None and len(bboxes) > 0:
                hands_count = len(bboxes)
                logger.info(f"🤝 Hand detection: Found {hands_count} hands")
                
                # Process each detected hand and its label
                if labels is not None:
                    for i, label in enumerate(labels):
                        logger.info(f"   - Hand {i}: label={label}, type={type(label)}")
                        if label is not None and i < len(bboxes):
                            try:
                                # Convert label index to gesture name using targets
                                gesture_name = targets[label] if label < len(targets) else f"gesture_{label}"
                                detected_gestures.append(gesture_name)
                                
                                # Get confidence from our mapping
                                gesture_conf = self.gesture_confidence_mapping.get(gesture_name, 0.5)
                                total_confidence += gesture_conf
                                
                                logger.info(f"✋ Gesture detected: {gesture_name} (label: {label}, confidence: {gesture_conf})")
                                
                            except Exception as e:
                                logger.warning(f"⚠️ Error processing label {label}: {e}")
                                detected_gestures.append(f"unknown_gesture_{label}")
                                total_confidence += 0.3
                else:
                    logger.warning("⚠️ Labels is None - gesture classification may have failed")
                
                # Check controller tracks for additional gesture information
                if hasattr(self.controller, 'tracks') and len(self.controller.tracks) > 0:
                    logger.info(f"🔍 Checking {len(self.controller.tracks)} tracks for gestures...")
                    for track_idx, track in enumerate(self.controller.tracks):
                        logger.info(f"   - Track {track_idx}: {type(track)}")
                        if isinstance(track, dict) and "hands" in track and len(track["hands"]) > 0:
                            latest_hand = track["hands"][-1]  # Get latest hand in track
                            logger.info(f"     - Latest hand: {type(latest_hand)}, gesture: {getattr(latest_hand, 'gesture', 'No gesture attr')}")
                            if hasattr(latest_hand, 'gesture') and latest_hand.gesture is not None:
                                try:
                                    gesture_name = targets[latest_hand.gesture] if latest_hand.gesture < len(targets) else f"track_gesture_{latest_hand.gesture}"
                                    if gesture_name not in detected_gestures:
                                        detected_gestures.append(gesture_name)
                                        gesture_conf = self.gesture_confidence_mapping.get(gesture_name, 0.5)
                                        total_confidence += gesture_conf
                                        logger.info(f"✋ Track gesture detected: {gesture_name}")
                                except Exception as e:
                                    logger.warning(f"⚠️ Error processing track gesture: {e}")
                        else:
                            logger.info(f"     - Track {track_idx} has no hands or wrong format")
                
                # If we detected hands but no gestures, try alternative approach
                if hands_count > 0 and len(detected_gestures) == 0:
                    logger.warning(f"⚠️ Detected {hands_count} hands but no gestures - using fallback detection")
                    # Add generic hand presence gestures
                    detected_gestures.append("hand_detected")
                    total_confidence = 0.4 * hands_count  # Low confidence for generic detection
            else:
                logger.info("🤝 No hands detected in frame")
            
            # Calculate overall confidence
            if hands_count > 0 and len(detected_gestures) > 0:
                avg_confidence = total_confidence / len(detected_gestures)
                if avg_confidence >= 0.7:
                    confidence_level = 'confident'
                elif avg_confidence >= 0.4:
                    confidence_level = 'medium_confident'
                else:
                    confidence_level = 'not_confident'
            else:
                avg_confidence = 0.0
                confidence_level = 'not_confident'
            
            result = {
                'confidence_level': confidence_level,
                'confidence': round(avg_confidence, 2),
                'gestures_detected': detected_gestures,
                'hands_detected': hands_count,
                'method': 'original_hagrid_onnx',
                'hand_analysis': {
                    'bboxes_count': len(bboxes) if bboxes is not None else 0,
                    'ids_count': len(ids) if ids is not None else 0,
                    'labels_processed': len([l for l in labels if l is not None]) if labels is not None else 0,
                    'tracks_count': len(self.controller.tracks) if hasattr(self.controller, 'tracks') else 0,
                    'labels_none_count': len([l for l in labels if l is None]) if labels is not None else 0
                },
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"🎯 Hand analysis result: {confidence_level} ({avg_confidence:.2f}) - Gestures: {detected_gestures}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing frame: {e}")
            logger.error(traceback.format_exc())
            return {
                'confidence_level': 'not_confident',
                'confidence': 0.0,
                'gestures_detected': ['analysis_error'],
                'hands_detected': 0,
                'method': 'error',
                'timestamp': datetime.now().isoformat()
            }

# Global hand model instance
hand_model = HandModelServer()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        status = "ok" if hand_model.controller is not None else "model_not_loaded"
        return jsonify({
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'model_loaded': hand_model.controller is not None
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze_hand_gesture():
    """Analyze hand gestures in uploaded frame"""
    try:
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        image_data = data['image']
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        # Convert to OpenCV format
        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Failed to decode image'}), 400
        
        # Analyze the frame
        result = hand_model.analyze_frame(frame)
        
        logger.info(f"🤝 Hand analysis result: {result['confidence_level']} ({result['confidence']}) - {result['gestures_detected']}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Analysis error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': str(e),
            'confidence_level': 'not_confident',
            'confidence': 0.0,
            'gestures_detected': ['server_error'],
            'hands_detected': 0,
            'method': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/test_detection', methods=['POST'])
def test_detection():
    """Test detection model with uploaded image to see all raw detections"""
    try:
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        image_data = data['image']
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        # Convert to OpenCV format
        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Failed to decode image'}), 400
        
        logger.info(f"🔍 Testing detection model with image shape: {frame.shape}")
        
        # Test detection model directly
        raw_boxes, raw_probs = hand_model.controller.detection_model(frame)
        
        logger.info(f"   - Raw boxes shape: {raw_boxes.shape}")
        logger.info(f"   - Raw probs shape: {raw_probs.shape}")
        logger.info(f"   - Raw boxes: {raw_boxes}")
        logger.info(f"   - Raw probs: {raw_probs}")
        
        # Filter by different confidence thresholds to see what's available
        thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        filtered_results = {}
        
        for threshold in thresholds:
            mask = raw_probs > threshold
            filtered_boxes = raw_boxes[mask] if len(raw_boxes) > 0 else []
            filtered_probs = raw_probs[mask] if len(raw_probs) > 0 else []
            
            filtered_results[f"threshold_{threshold}"] = {
                "count": len(filtered_boxes),
                "boxes": filtered_boxes.tolist() if len(filtered_boxes) > 0 else [],
                "probs": filtered_probs.tolist() if len(filtered_probs) > 0 else []
            }
            
            logger.info(f"   - Threshold {threshold}: {len(filtered_boxes)} detections")
        
        return jsonify({
            'status': 'Detection test completed',
            'image_shape': frame.shape,
            'raw_detections': {
                'boxes_count': len(raw_boxes),
                'boxes': raw_boxes.tolist() if len(raw_boxes) > 0 else [],
                'probs': raw_probs.tolist() if len(raw_probs) > 0 else []
            },
            'filtered_by_threshold': filtered_results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Detection test error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/test_classification', methods=['GET'])
def test_classification():
    """Test classification model with a simulated hand detection"""
    try:
        # Create a test frame
        test_frame = np.ones((480, 640, 3), dtype=np.uint8) * 128  # Gray background
        
        # Simulate a hand detection (fake bounding box in center)
        fake_bbox = np.array([[250, 150, 350, 250]])  # x1, y1, x2, y2
        
        logger.info(f"🧪 Testing classification model with simulated hand detection...")
        logger.info(f"   - Fake bbox: {fake_bbox}")
        
        # Test classification model directly
        try:
            labels = hand_model.controller.classification_model(test_frame, fake_bbox)
            logger.info(f"   - Classification labels: {labels}")
            logger.info(f"   - Labels type: {type(labels)}")
            logger.info(f"   - Labels shape: {labels.shape if hasattr(labels, 'shape') else 'No shape'}")
            
            # Convert labels to gesture names
            gesture_names = []
            if labels is not None:
                for i, label in enumerate(labels):
                    if 0 <= label < len(targets):
                        gesture_name = targets[label]
                        gesture_names.append(gesture_name)
                        logger.info(f"   - Label {i}: {label} -> {gesture_name}")
                    else:
                        logger.info(f"   - Label {i}: {label} -> INVALID_LABEL")
                        gesture_names.append(f"invalid_{label}")
            
            return jsonify({
                'status': 'Classification test completed',
                'labels': labels.tolist() if labels is not None else None,
                'gesture_names': gesture_names,
                'fake_bbox': fake_bbox.tolist(),
                'targets_available': len(targets),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"   ❌ Classification model error: {e}")
            logger.error(traceback.format_exc())
            return jsonify({
                'error': str(e),
                'status': 'Classification test failed',
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint with dummy data"""
    try:
        # Create a dummy frame for testing
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        result = hand_model.analyze_frame(test_frame)
        
        return jsonify({
            'test_result': result,
            'status': 'Hand model server is working',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 Starting Hand Model Server on port 5002...")
    logger.info(f"📂 Dynamic gestures path: {dynamic_gestures_path}")
    logger.info("🔧 Using original HaGRID ONNX models")
    
    # Test model initialization
    if hand_model.controller is None:
        logger.error("❌ Hand model failed to initialize - server will run but return errors")
    else:
        logger.info("✅ Hand model initialized successfully")
    
    app.run(host='0.0.0.0', port=5002, debug=False)