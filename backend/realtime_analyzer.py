"""
Real-time Analysis Engine for InsightHire
Combines all four models (Face, Hand, Eye, Voice) for comprehensive candidate analysis
"""
import cv2
import numpy as np
import threading
import queue
import time
import logging
from datetime import datetime
import requests
import base64
import json

from model.face_model import FaceStressDetector
from hand_model_client import hand_client
# REMOVED: from model.eye_model import EyeConfidenceDetector - Using pure gaze tracking server instead
from model.voice_model import VoiceConfidenceDetector
from utils.database import DatabaseManager

logger = logging.getLogger(__name__)

class RealTimeAnalyzer:
    def __init__(self, session_id, user_id, job_role_id=None, socketio=None):
        self.session_id = session_id
        self.user_id = user_id
        self.job_role_id = job_role_id
        self.socketio = socketio
        self.db_manager = DatabaseManager(user_id)
        
        # Initialize models
        self.face_detector = FaceStressDetector()
        # HAND MODEL: Using dedicated server on port 5002 via hand_client
        # PURE GAZE TRACKING: Using dedicated server on port 5001 (NO fallback)
        self.gaze_server_url = 'http://localhost:5001'
        self.voice_detector = VoiceConfidenceDetector()
        
        # Video processing
        self.video_frame_queue = queue.Queue(maxsize=10)
        self.audio_data_queue = queue.Queue(maxsize=10)
        self.results_queue = queue.Queue()
        
        # Threading
        self.processing_thread = None
        self.is_running = False
        self.analysis_lock = threading.Lock()  # Prevent multiple simultaneous analysis
        self.save_lock = threading.Lock()  # Prevent multiple simultaneous saves
        self.analysis_in_progress = False  # Flag to track if analysis is running
        self.model_cycle = 0  # Cycle through models to reduce CPU load
        
        # Analysis settings
        self.analysis_interval = 5.0  # Analyze every 5 seconds for faster response
        self.last_analysis_time = 0
        self.last_audio_time = 0  # Track when audio was last received
        
        # Audio buffering for continuous analysis
        self.audio_buffer = []
        self.audio_buffer_duration = 5.0  # 5 seconds buffer
        self.voice_analysis_interval = 5.0  # Analyze every 5 seconds for faster response
        self.last_voice_analysis_time = 0
        self.audio_start_time = None  # Track when audio collection started
        self.last_audio_received = 0  # Track when audio was last received
        
        # Results storage
        self.current_results = {
            'face_stress': {'stress_level': 'no_data', 'confidence': 0.0},
            'hand_confidence': {'confidence_level': 'no_data', 'confidence': 0.0},
            'eye_confidence': {'confidence_level': 'no_data', 'confidence': 0.0},
            'voice_confidence': {'confidence_level': 'unknown', 'confidence': 0.0, 'emotion': 'neutral', 'method': 'initialized'}
        }
    
    def start_analysis(self):
        """Start the real-time analysis"""
        if not self.is_running:
            self.is_running = True
            self.processing_thread = threading.Thread(target=self._analysis_loop)
            self.processing_thread.daemon = True
            self.processing_thread.start()
            logger.info(f"Started real-time analysis for session {self.session_id}")
    
    def stop_analysis(self):
        """Stop the real-time analysis safely"""
        logger.info(f"🛑 Stopping analysis for session {self.session_id}")
        
        # Set flags to stop immediately
        self.is_running = False
        self.analysis_in_progress = False
        
        # Perform immediate analysis on any remaining audio before stopping
        if self.audio_buffer:
            logger.info(f"🎤 Performing final voice analysis on {len(self.audio_buffer)} remaining audio chunks")
            try:
                self._perform_voice_analysis()
                # Set final voice state
                self.current_results['voice_confidence'] = {
                    'confidence_level': 'session_stopped',
                    'confidence': 0.0,
                    'emotion': 'session_stopped',
                    'method': 'session_stopped',
                    'timestamp': datetime.now().isoformat()
                }
                # Save final results
                self.save_results(self.current_results)
                logger.info("🎤 ✅ Final voice analysis completed")
            except Exception as e:
                logger.error(f"🎤 Error in final voice analysis: {e}")
        
        # Clear queues first to stop any pending processing
        self._clear_queues()
        
        # Wait for thread to stop
        if self.processing_thread and self.processing_thread.is_alive():
            logger.info(f"⏳ Waiting for analysis thread to stop for session {self.session_id}")
            try:
                self.processing_thread.join(timeout=2.0)  # Reduced timeout to 2 seconds
                if self.processing_thread.is_alive():
                    logger.warning(f"⚠️ Analysis thread for session {self.session_id} did not stop gracefully - forcing stop")
                    # Force stop by setting daemon flag and clearing thread reference
                    self.processing_thread.daemon = True
                    self.processing_thread = None
                else:
                    logger.info(f"✅ Analysis thread stopped for session {self.session_id}")
            except Exception as e:
                logger.error(f"❌ Error stopping thread for session {self.session_id}: {e}")
                # Force cleanup even if thread stop fails
                self.processing_thread = None
        
        # Reset all analysis state
        self.current_results = {
            'face_stress': {'stress_level': 'unknown', 'confidence': 0},
            'hand_confidence': {'confidence_level': 'unknown', 'confidence': 0},
            'eye_confidence': {'confidence_level': 'unknown', 'confidence': 0},
            'voice_confidence': {'confidence_level': 'no_audio', 'confidence': 0, 'emotion': 'no_audio', 'method': 'session_stopped'},
            'overall': {'confidence_score': 0.5, 'stress_score': 0.5}
        }
        
        # Reset audio state
        self.reset_audio_state()
        
        logger.info(f"🧹 Analysis cleanup completed for session {self.session_id}")
    
    def _clear_queues(self):
        """Clear all queues safely"""
        try:
            # Clear video frames
            while not self.video_frame_queue.empty():
                try:
                    self.video_frame_queue.get_nowait()
                except:
                    break
            
            # Clear audio data
            while not self.audio_data_queue.empty():
                try:
                    self.audio_data_queue.get_nowait()
                except:
                    break
            
            # Clear results
            while not self.results_queue.empty():
                try:
                    self.results_queue.get_nowait()
                except:
                    break
                    
            # Clear audio buffer
            if hasattr(self, 'audio_buffer'):
                self.audio_buffer.clear()
            
            logger.debug(f"🧹 Queues cleared for session {self.session_id}")
            
        except Exception as e:
            logger.error(f"❌ Error clearing queues for session {self.session_id}: {e}")
    
    def add_video_frame(self, frame):
        """Add a video frame for analysis"""
        try:
            if not self.video_frame_queue.full():
                self.video_frame_queue.put(frame, block=False)
        except queue.Full:
            # Skip frame if queue is full
            pass
    
    def add_audio_data(self, audio_data, sample_rate):
        """Add new audio data for analysis"""
        try:
            if not self.audio_data_queue.full():
                self.audio_data_queue.put((audio_data, sample_rate), block=False)
                self.last_audio_time = time.time()  # Update last audio time
                logger.debug(f"Added audio data to queue: {len(audio_data)} samples at {sample_rate}Hz")
            else:
                logger.warning("Audio queue full, dropping frame")
        except queue.Full:
            logger.warning("Audio queue full, couldn't add new data")
    
    def reset_audio_state(self):
        """Reset audio state when interview stops"""
        logger.info("🎤 Resetting audio state - interview stopped")
        self.audio_buffer.clear()  # Clear audio buffer
        self.audio_start_time = None  # Reset audio timing
        self.current_results['voice_confidence'] = {
            'confidence_level': 'unknown',
            'confidence': 0.0,
            'emotion': 'neutral',
            'method': 'interview_stopped'
        }
        self.last_audio_time = 0  # Reset timeout tracking
        self.last_voice_analysis_time = 0  # Reset analysis timing
    
    def _detect_pure_gaze_tracking(self, frame):
        """
        Call pure gaze tracking server on port 5001 - NO OpenCV fallback
        This ensures ONLY the real gaze tracking model is used
        """
        try:
            # Convert frame to base64
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')

            # Call pure gaze tracking server
            response = requests.post(
                f"{self.gaze_server_url}/detect_gaze",
                json={'image': f"data:image/jpeg;base64,{frame_base64}"},
                timeout=3.0
            )

            if response.status_code == 200:
                result = response.json()

                # Convert pure gaze tracking result to expected format
                gaze_analysis = result.get('gaze_analysis', {})

                # Some gaze servers use 'gaze_detected' while some may use 'eyes_detected'
                # Map both to a single boolean used by the frontend
                eyes_detected = result.get('eyes_detected', result.get('gaze_detected', False))

                # Build gaze_movements_detected similar to hand model's gestures_detected
                # If the server already provides it, use that. Otherwise synthesize from gaze_analysis.
                gaze_movements_detected = result.get('gaze_movements_detected', []) or []
                if not gaze_movements_detected and isinstance(gaze_analysis, dict):
                    # Common boolean flags from gaze_analysis
                    for key in ('is_blinking', 'is_right', 'is_left', 'is_center'):
                        val = gaze_analysis.get(key)
                        if val is True:
                            gaze_movements_detected.append(key)

                    # Derive directions from ratios when explicit flags are missing
                    try:
                        hr = float(gaze_analysis.get('horizontal_ratio', 0) or 0)
                        vr = float(gaze_analysis.get('vertical_ratio', 0) or 0)
                        # Thresholds chosen to match likely left/right/center judgments
                        if hr >= 0.65 and 'is_right' not in gaze_movements_detected:
                            gaze_movements_detected.append('is_right_ratio')
                        elif hr <= 0.35 and 'is_left' not in gaze_movements_detected:
                            gaze_movements_detected.append('is_left_ratio')
                        else:
                            # If neither extreme, consider center
                            if 0.35 < hr < 0.65 and 'is_center' not in gaze_movements_detected:
                                gaze_movements_detected.append('is_center_ratio')

                        # Vertical movements (optional)
                        if vr >= 0.6 and 'is_down_ratio' not in gaze_movements_detected:
                            gaze_movements_detected.append('is_down_ratio')
                        elif vr <= 0.4 and 'is_up_ratio' not in gaze_movements_detected:
                            gaze_movements_detected.append('is_up_ratio')
                    except Exception:
                        # Ignore any conversion errors and continue
                        pass

                # Map to the format expected by the frontend
                formatted_result = {
                    'confidence': result.get('confidence', 0.95),
                    'confidence_level': result.get('confidence_level', 'confident'),
                    'method': 'PURE_GAZE_TRACKING',  # NO fallback indicator
                    'eyes_detected': bool(eyes_detected),
                    'faces_detected': result.get('faces_detected', 1),
                    'gaze_movements_detected': gaze_movements_detected,  # Like gestures_detected in hand model
                    'timestamp': result.get('timestamp', datetime.now().isoformat()),
                    'gaze_details': result.get('gaze_details', {}),  # Include detailed gaze data
                    'gaze_data': gaze_analysis  # Include full gaze analysis for compatibility
                }

                logger.info(f"🎯 PURE gaze tracking success: {formatted_result['method']} - confidence: {formatted_result['confidence']:.2f}")
                return formatted_result

            else:
                logger.error(f"❌ Pure gaze tracking server error: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to connect to pure gaze tracking server: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error in pure gaze tracking: {e}")
            return None

    def get_latest_results(self):
        """Get the latest analysis results"""
        return self.current_results.copy()
    
    def _analysis_loop(self):
        """Main analysis loop running in separate thread"""
        while self.is_running:
            try:
                current_time = time.time()
                
                # Check if it's time for analysis (with strict 10-second intervals)
                time_since_last = current_time - self.last_analysis_time
                if time_since_last >= self.analysis_interval and not self.analysis_in_progress:
                    logger.info(f"⏰ Time for analysis: {time_since_last:.1f}s since last analysis (interval: {self.analysis_interval}s)")
                    self.analysis_in_progress = True
                    try:
                        self._perform_analysis()
                        self.last_analysis_time = current_time
                    finally:
                        self.analysis_in_progress = False
                elif self.analysis_in_progress:
                    logger.debug(f"⏳ Analysis already in progress, skipping")
                else:
                    logger.debug(f"⏳ Waiting for analysis: {time_since_last:.1f}s / {self.analysis_interval}s")
                
                # Check for audio stops more frequently
                current_time = time.time()
                if hasattr(self, 'last_audio_received') and self.last_audio_received > 0:
                    time_since_last_audio = current_time - self.last_audio_received
                    if time_since_last_audio > 2.0 and self.audio_buffer:
                        self.process_audio_stop()
                
                time.sleep(0.5)  # Check every 0.5 seconds for faster response
                
            except Exception as e:
                logger.error(f"Error in analysis loop: {e}")
                time.sleep(1)  # Wait before retrying
    
    def _perform_analysis(self):
        """Perform analysis on latest frames and audio"""
        try:
            # Get latest video frame
            latest_frame = None
            while not self.video_frame_queue.empty():
                try:
                    latest_frame = self.video_frame_queue.get(block=False)
                except queue.Empty:
                    break
            
            # Get latest audio data
            latest_audio = None
            while not self.audio_data_queue.empty():
                try:
                    latest_audio = self.audio_data_queue.get(block=False)
                except queue.Empty:
                    break
            
            # Analyze video frame if available
            if latest_frame is not None:
                self._analyze_video_frame(latest_frame)
            
            # Analyze audio if available
            if latest_audio is not None:
                self._analyze_audio(latest_audio[0], latest_audio[1])
            else:
                # Check if no audio has been received for too long
                current_time = time.time()
                if self.last_audio_time > 0 and (current_time - self.last_audio_time) > 5.0:  # 5 seconds timeout (reduced from 10)
                    if self.audio_buffer:
                        logger.warning("🎤 No audio received for 5+ seconds, clearing audio buffer")
                        self.audio_buffer.clear()
                        self.audio_start_time = None  # Reset timing for next audio session
                    
                    # Reset voice confidence to indicate no audio
                    self.current_results['voice_confidence'] = {
                        'confidence_level': 'no_audio',
                        'confidence': 0.0,
                        'emotion': 'no_audio',
                        'method': 'no_audio_detected',
                        'timestamp': datetime.now().isoformat()
                    }
                    logger.info("🎤 Voice confidence reset to 'no_audio' due to timeout")
            
            # Calculate overall scores
            self._calculate_overall_scores()
            
            # Convert to simple binary format for frontend display
            self._convert_to_simple_format()
            
            # Save results to database and emit via Socket.IO
            self.save_results(self.current_results)
            
        except Exception as e:
            logger.error(f"Error performing analysis: {e}")
    
    def _analyze_video_frame(self, frame):
        """Analyze a single video frame with all visual models"""
        try:
            logger.info(f"🔍 Analyzing video frame: {frame.shape}")
            
            # Cycle through models to reduce CPU load - only run one model per analysis
            model_index = self.model_cycle % 3  # 3 visual models (face, hand, eye)
            
            if model_index == 0:
                # Face stress detection
                face_result = self.face_detector.detect_stress(frame)
                if face_result and 'stress_level' in face_result:
                    self.current_results['face_stress'] = face_result
                    logger.info(f"😊 Face analysis: {face_result.get('stress_level')} (confidence: {face_result.get('confidence', 0.0):.2f})")
                    
            elif model_index == 1:
                # Hand confidence detection
                hand_result = hand_client.detect_confidence(frame)
                if hand_result and 'confidence_level' in hand_result:
                    self.current_results['hand_confidence'] = hand_result
                    logger.info(f"✋ Hand analysis: {hand_result.get('confidence_level')} (confidence: {hand_result.get('confidence', 0.0):.2f})")
                    
            elif model_index == 2:
                # PURE GAZE TRACKING: Call dedicated server on port 5001 (NO fallback)
                eye_result = self._detect_pure_gaze_tracking(frame)
                if eye_result and 'confidence_level' in eye_result:
                    self.current_results['eye_confidence'] = eye_result
                    logger.info(f"👁️ PURE Gaze analysis: {eye_result.get('confidence_level')} (confidence: {eye_result.get('confidence', 0.0):.2f}) - NO fallback!")
            
            # Increment cycle for next analysis
            self.model_cycle += 1
            
            logger.info(f"📊 Analysis completed - Model {model_index} processed (cycle: {self.model_cycle})")
            
        except Exception as e:
            logger.error(f"Error analyzing video frame: {e}")
            # Set default values on error
            self.current_results['face_stress'] = {'stress_level': 'error', 'confidence': 0.0}
            self.current_results['hand_confidence'] = {'confidence_level': 'error', 'confidence': 0.0}
            self.current_results['eye_confidence'] = {'confidence_level': 'error', 'confidence': 0.0}
    
    def _analyze_audio(self, audio_data, sample_rate):
        """Analyze audio data with continuous 5-second analysis"""
        try:
            logger.info(f"🎤 Processing audio data: length={len(audio_data)}, sample_rate={sample_rate}")
            
            # Check if audio data is meaningful (not just silence)
            if len(audio_data) == 0:
                logger.warning("🎤 Empty audio data received")
                return  # Don't reset confidence for empty audio
            
            # Check if audio is just silence/noise
            audio_rms = np.sqrt(np.mean(np.array(audio_data)**2))
            if audio_rms < 0.001:  # Very quiet audio
                logger.warning(f"🎤 Audio too quiet (RMS: {audio_rms:.6f})")
                return  # Don't reset confidence for quiet audio
            
            # Add audio to buffer with timestamp
            current_time = time.time()
            
            # Initialize audio start time if this is the first audio
            if self.audio_start_time is None:
                self.audio_start_time = current_time
                logger.info("🎤 Starting audio collection timer")
            
            self.audio_buffer.append({
                'data': audio_data,
                'sample_rate': sample_rate,
                'timestamp': current_time
            })
            
            # Update last audio received time
            self.last_audio_received = current_time
            
            # Remove audio older than buffer duration (rolling window)
            cutoff_time = current_time - self.audio_buffer_duration
            self.audio_buffer = [item for item in self.audio_buffer if item['timestamp'] > cutoff_time]
            
            # Perform analysis every 5 seconds from start of audio collection
            time_since_start = current_time - self.audio_start_time
            analysis_intervals_passed = int(time_since_start / self.voice_analysis_interval)
            expected_analyses = analysis_intervals_passed
            actual_analyses = int((self.last_voice_analysis_time - self.audio_start_time) / self.voice_analysis_interval) if self.last_voice_analysis_time > 0 else 0
            
            # Check if it's time for the next 5-second analysis
            if expected_analyses > actual_analyses and len(self.audio_buffer) >= 1:
                logger.info(f"🎤 Time for voice analysis #{expected_analyses + 1} (after {time_since_start:.1f}s)")
                logger.info(f"🎤 Audio buffer has {len(self.audio_buffer)} chunks")
                self._perform_voice_analysis()
                self.last_voice_analysis_time = current_time
            elif len(self.audio_buffer) >= 1 and self.last_voice_analysis_time == 0:
                # Fallback: perform analysis if we have audio and haven't done any analysis yet
                logger.info(f"🎤 Fallback voice analysis with {len(self.audio_buffer)} chunks")
                self._perform_voice_analysis()
                self.last_voice_analysis_time = current_time
            else:
                logger.debug(f"🎤 Voice analysis conditions: expected={expected_analyses}, actual={actual_analyses}, buffer_chunks={len(self.audio_buffer)}")
            
        except Exception as e:
            logger.error(f"🎤 Error processing audio: {e}")
    
    def process_audio_stop(self):
        """Process when audio stops - perform immediate analysis on remaining buffer"""
        try:
            current_time = time.time()
            time_since_last_audio = current_time - self.last_audio_received
            
            # If we haven't received audio for more than 2 seconds, consider it stopped
            if time_since_last_audio > 2.0 and self.audio_buffer:
                logger.info(f"🎤 Audio appears to have stopped (no audio for {time_since_last_audio:.1f}s)")
                logger.info(f"🎤 Performing immediate analysis on remaining {len(self.audio_buffer)} audio chunks")
                
                # Perform immediate analysis on remaining buffer
                self._perform_voice_analysis()
                
                # Set voice confidence to no_audio state
                self.current_results['voice_confidence'] = {
                    'confidence_level': 'no_audio',
                    'confidence': 0.0,
                    'emotion': 'no_audio',
                    'method': 'no_audio_detected',
                    'timestamp': datetime.now().isoformat()
                }
                
                # Save results immediately
                self.save_results(self.current_results)
                
                logger.info("🎤 ✅ Immediate analysis completed for audio stop")
                
        except Exception as e:
            logger.error(f"🎤 Error processing audio stop: {e}")
    
    def _perform_voice_analysis(self):
        """Perform voice analysis on current 10-second buffer"""
        try:
            if not self.audio_buffer:
                logger.warning("🎤 No audio in buffer for analysis")
                return
            
            # Combine all buffered audio data (last 10 seconds)
            combined_audio = []
            sample_rate = self.audio_buffer[0]['sample_rate']
            
            for item in self.audio_buffer:
                combined_audio.extend(item['data'])
            
            buffer_duration = len(combined_audio) / sample_rate
            logger.info(f"🎤 Analyzing {len(combined_audio)} samples ({buffer_duration:.1f}s) from {len(self.audio_buffer)} chunks")
            
            # Voice confidence detection on combined audio
            logger.info("🎤 Calling voice detector...")
            voice_result = self.voice_detector.detect_confidence_from_audio_data(combined_audio, sample_rate)
            logger.info(f"🎤 Voice detector returned: {voice_result}")
            
            if voice_result and 'confidence_level' in voice_result:
                self.current_results['voice_confidence'] = voice_result
                emotion = voice_result.get('emotion', 'neutral')
                confidence = voice_result.get('confidence', 0.0)
                level = voice_result.get('confidence_level', 'unknown')
                method = voice_result.get('method', 'unknown')
                logger.info(f"🎤 ✅ Voice analysis result: {emotion} → {level} (confidence: {confidence:.2f}, method: {method})")
            else:
                logger.warning("🎤 Voice analysis returned no valid result")
                # Keep previous result instead of resetting
                current_level = self.current_results['voice_confidence']['confidence_level']
                logger.info(f"🎤 Keeping previous voice confidence: {current_level}")
            
        except Exception as e:
            logger.error(f"🎤 Error in voice analysis: {e}")
            # Set default value on error
            self.current_results['voice_confidence'] = {
                'confidence_level': 'error', 
                'confidence': 0.0,
                'emotion': 'neutral',
                'method': 'error',
                'error': str(e)
            }
    
    def _calculate_overall_scores(self):
        """Calculate overall confidence and stress scores"""
        try:
            # Calculate overall confidence score
            confidence_scores = []
            
            # Hand confidence
            hand_conf = self.current_results.get('hand_confidence', {})
            if hand_conf.get('confidence_level') in ['confident', 'very_confident', 'somewhat_confident']:
                confidence_scores.append(hand_conf.get('confidence', 0.5))
            elif hand_conf.get('confidence_level') == 'not_confident':
                confidence_scores.append(1.0 - hand_conf.get('confidence', 0.5))
            
            # Eye confidence
            eye_conf = self.current_results.get('eye_confidence', {})
            if eye_conf.get('confidence_level') in ['confident', 'very_confident', 'somewhat_confident']:
                confidence_scores.append(eye_conf.get('confidence', 0.5))
            elif eye_conf.get('confidence_level') == 'not_confident':
                confidence_scores.append(1.0 - eye_conf.get('confidence', 0.5))
            
            # Voice confidence
            voice_conf = self.current_results.get('voice_confidence', {})
            if voice_conf.get('confidence_level') in ['confident', 'very_confident', 'somewhat_confident']:
                confidence_scores.append(voice_conf.get('confidence', 0.5))
            elif voice_conf.get('confidence_level') == 'not_confident':
                confidence_scores.append(1.0 - voice_conf.get('confidence', 0.5))
            
            # Calculate overall confidence
            if confidence_scores:
                overall_confidence = np.mean(confidence_scores)
            else:
                overall_confidence = 0.5  # Neutral if no data
            
            # Calculate stress score from face analysis
            stress_score = 0.5  # Default neutral
            face_stress = self.current_results.get('face_stress', {})
            
            if face_stress.get('stress_level') in ['stressed', 'high_stress']:
                stress_score = face_stress.get('confidence', 0.5)
            elif face_stress.get('stress_level') in ['not_stressed', 'low_stress']:
                stress_score = 1.0 - face_stress.get('confidence', 0.5)
            elif face_stress.get('stress_level') == 'moderate_stress':
                stress_score = 0.5  # Neutral for moderate stress
            
            # Add overall scores to results
            self.current_results['overall'] = {
                'confidence_score': float(overall_confidence),
                'stress_score': float(stress_score),
                'timestamp': datetime.now().isoformat(),
                'components_used': len(confidence_scores)
            }
            
            logger.debug(f"Overall scores calculated - Confidence: {overall_confidence:.2f}, "
                        f"Stress: {stress_score:.2f}, Components: {len(confidence_scores)}")
            
        except Exception as e:
            logger.error(f"Error calculating overall scores: {e}")
            # Set default scores on error
            self.current_results['overall'] = {
                'confidence_score': 0.5,
                'stress_score': 0.5,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def save_results(self, analysis_data):
        """Save analysis results to database and emit via Socket.IO"""
        try:
            # Prepare data for storage
            analysis_data_with_meta = {
                'timestamp': datetime.now().isoformat(),
                'session_id': self.session_id,
                'user_id': self.user_id,
                'job_role_id': self.job_role_id,
                **analysis_data
            }
            
            logger.info(f"🔄 Attempting to save analysis data for session {self.session_id}")
            
            # Save to Firestore for permanent storage (PRIMARY STORAGE)
            firestore_success = False
            try:
                result = self.db_manager.save_analysis_result(self.session_id, analysis_data_with_meta)
                if result:
                    logger.info(f"✅ Analysis saved to Firestore for session {self.session_id}, doc_id: {result}")
                    firestore_success = True
                else:
                    logger.error(f"❌ Firestore save returned None for session {self.session_id}")
            except Exception as db_error:
                logger.error(f"❌ Firestore save failed for session {self.session_id}: {db_error}")
            
            # Save to Realtime Database for live updates (OPTIONAL - DISABLED DUE TO AUTH ISSUES)
            # The Realtime Database save is causing authentication errors, but Firestore works perfectly
            # Since all data is being saved to Firestore successfully, we'll skip RTDB for now
            try:
                # Comment out the problematic Realtime DB save
                # rtdb_result = self.db_manager.save_realtime_analysis(self.session_id, analysis_data_with_meta)
                # if rtdb_result:
                #     logger.info(f"✅ Analysis saved to Realtime DB for session {self.session_id}, key: {rtdb_result}")
                # else:
                #     logger.error(f"❌ Realtime DB save returned None for session {self.session_id}")
                logger.debug(f"📝 Realtime DB save disabled (using Firestore only) for session {self.session_id}")
            except Exception as rtdb_error:
                logger.warning(f"⚠️ Realtime DB save skipped for session {self.session_id}: {rtdb_error}")
            
            # Emit results via Socket.IO for real-time updates (THIS IS WORKING)
            if self.socketio:
                self.socketio.emit('analysis_update', {
                    'session_id': self.session_id,
                    'timestamp': analysis_data_with_meta['timestamp'],
                    'analysis': analysis_data_with_meta
                })
                logger.info(f"✅ Analysis results emitted via Socket.IO for session {self.session_id}")
            else:
                logger.warning(f"⚠️ No Socket.IO instance available for session {self.session_id}")
            
            # NOTE: Removed realtime_analysis collection save - only save to analysis_results
            # Real-time analysis will be saved only to analysis_results collection
            
            # Report overall success if Firestore worked (which is the main storage)
            if firestore_success:
                logger.info(f"🎉 Analysis pipeline completed successfully for session {self.session_id}")
            else:
                logger.error(f"❌ Analysis save failed for session {self.session_id}")
            
        except Exception as e:
            logger.error(f"❌ Error in save_results for session {self.session_id}: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
    
    
    def get_session_summary(self):
        """Get analysis summary for the session"""
        try:
            all_results = self.db_manager.get_session_results(self.session_id)
            
            if not all_results:
                return {'status': 'no_data'}
            
            # Calculate averages
            confidence_scores = []
            stress_scores = []
            
            for result in all_results:
                if 'overall_scores' in result:
                    if 'confidence_score' in result['overall_scores']:
                        confidence_scores.append(result['overall_scores']['confidence_score'])
                    if 'stress_score' in result['overall_scores']:
                        stress_scores.append(result['overall_scores']['stress_score'])
            
            summary = {
                'total_analysis_points': len(all_results),
                'average_confidence': np.mean(confidence_scores) if confidence_scores else 0.5,
                'average_stress': np.mean(stress_scores) if stress_scores else 0.5,
                'confidence_trend': self._calculate_trend(confidence_scores),
                'stress_trend': self._calculate_trend(stress_scores),
                'session_duration': self._calculate_session_duration(all_results)
            }
            
            # Add recommendations
            summary['recommendations'] = self._generate_recommendations(summary)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting session summary: {e}")
            return {'status': 'error'}
    
    def _calculate_trend(self, scores):
        """Calculate trend (improving, declining, stable)"""
        if len(scores) < 2:
            return 'insufficient_data'
        
        first_half = np.mean(scores[:len(scores)//2])
        second_half = np.mean(scores[len(scores)//2:])
        
        diff = second_half - first_half
        
        if diff > 0.1:
            return 'improving'
        elif diff < -0.1:
            return 'declining'
        else:
            return 'stable'
    
    def _calculate_session_duration(self, results):
        """Calculate session duration in minutes"""
        if len(results) < 2:
            return 0
        
        try:
            start_time = datetime.fromisoformat(results[0]['timestamp'])
            end_time = datetime.fromisoformat(results[-1]['timestamp'])
            duration = (end_time - start_time).total_seconds() / 60
            return round(duration, 2)
        except:
            return 0
    
    def _generate_recommendations(self, summary):
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if summary['average_confidence'] < 0.4:
            recommendations.append("Consider practicing confident body language and maintaining eye contact")
        
        if summary['average_stress'] > 0.6:
            recommendations.append("Try relaxation techniques before interviews to manage stress levels")
        
        if summary['confidence_trend'] == 'declining':
            recommendations.append("Focus on maintaining confidence throughout the interview")
        
        if summary['stress_trend'] == 'improving':
            recommendations.append("Good progress on stress management during the session")
        
        if not recommendations:
            recommendations.append("Overall performance looks good - keep up the positive interview presence")
        
        return recommendations
    
    def _convert_to_simple_format(self):
        """Convert analysis results to binary format as requested"""
        try:
            # Transform Face Stress to binary format
            face_stress = self.current_results.get('face_stress', {})
            stress_level = face_stress.get('stress_level', 'no_data')
            faces_detected = face_stress.get('faces_detected', 0)

            # Check if no face is detected - don't map to stress/non_stress
            if faces_detected == 0 or stress_level == 'no_face_detected':
                # Keep the no_face_detected status without converting to binary
                self.current_results['face_stress'] = {
                    'stress_level': 'no_face_detected',
                    'emotion': 'no_face_detected',
                    'emotion_confidence': 0.0,
                    'face_coordinates': [],
                    'faces_detected': 0,
                    'method': face_stress.get('method', 'no_face_detected'),
                    'timestamp': face_stress.get('timestamp', datetime.now().isoformat())
                }
            # Convert stress_level to binary: stress=1, non_stress=0
            elif stress_level == 'stress':
                # Replace the entire face_stress object with binary format
                self.current_results['face_stress'] = {
                    'stress': 1,
                    'stress_level': 'stress',
                    'emotion': face_stress.get('emotion', 'neutral'),
                    'emotion_confidence': face_stress.get('emotion_confidence', 0.0),
                    'face_coordinates': face_stress.get('face_coordinates', []),
                    'faces_detected': face_stress.get('faces_detected', 0),
                    'method': face_stress.get('method', 'unknown'),
                    'timestamp': face_stress.get('timestamp', datetime.now().isoformat())
                }
            else:
                # Replace the entire face_stress object with binary format
                self.current_results['face_stress'] = {
                    'stress': 0,
                    'stress_level': 'non_stress',
                    'emotion': face_stress.get('emotion', 'neutral'),
                    'emotion_confidence': face_stress.get('emotion_confidence', 0.0),
                    'face_coordinates': face_stress.get('face_coordinates', []),
                    'faces_detected': face_stress.get('faces_detected', 0),
                    'method': face_stress.get('method', 'unknown'),
                    'timestamp': face_stress.get('timestamp', datetime.now().isoformat())
                }
            
            # Transform Hand Confidence to binary format
            hand_confidence = self.current_results.get('hand_confidence', {})
            confidence_level = hand_confidence.get('confidence_level', 'no_data')
            
            # Convert confidence to binary: confident=1, not_confident=0
            if confidence_level and 'confident' in confidence_level.lower() and 'not' not in confidence_level.lower():
                # Replace the entire hand_confidence object with binary format
                self.current_results['hand_confidence'] = {
                    'confidence': 1,
                    'confidence_level': 'confident',
                    'hands_detected': hand_confidence.get('hands_detected', 0),
                    'gestures_detected': hand_confidence.get('gestures_detected', []),  # ✅ ADD THIS
                    'method': hand_confidence.get('method', 'unknown'),
                    'timestamp': hand_confidence.get('timestamp', datetime.now().isoformat())
                }
            else:
                # Replace the entire hand_confidence object with binary format
                self.current_results['hand_confidence'] = {
                    'confidence': 0,
                    'confidence_level': 'not_confident',
                    'hands_detected': hand_confidence.get('hands_detected', 0),
                    'gestures_detected': hand_confidence.get('gestures_detected', []),  # ✅ ADD THIS
                    'method': hand_confidence.get('method', 'unknown'),
                    'timestamp': hand_confidence.get('timestamp', datetime.now().isoformat())
                }
            
            # Transform Eye Confidence to binary format
            eye_confidence = self.current_results.get('eye_confidence', {})
            eye_confidence_level = eye_confidence.get('confidence_level', 'no_data')
            
            # Convert confidence to binary: confident=1, not_confident=0
            # ⚠️ PRESERVE the original eyes_detected and gaze_movements_detected from gaze server
            if eye_confidence_level and 'confident' in eye_confidence_level.lower() and 'not' not in eye_confidence_level.lower():
                # Replace the entire eye_confidence object with binary format
                self.current_results['eye_confidence'] = {
                    'confidence': 1,
                    'confidence_level': 'confident',
                    'eyes_detected': eye_confidence.get('eyes_detected', False),  # 🔧 PRESERVE original, default False
                    'faces_detected': eye_confidence.get('faces_detected', 0),
                    'gaze_movements_detected': eye_confidence.get('gaze_movements_detected', []),  # 🔧 PRESERVE gaze movements
                    'method': eye_confidence.get('method', 'unknown'),
                    'timestamp': eye_confidence.get('timestamp', datetime.now().isoformat())
                }
            else:
                # Replace the entire eye_confidence object with binary format
                self.current_results['eye_confidence'] = {
                    'confidence': 0,
                    'confidence_level': 'not_confident',
                    'eyes_detected': eye_confidence.get('eyes_detected', False),  # 🔧 PRESERVE original, default False
                    'faces_detected': eye_confidence.get('faces_detected', 0),
                    'gaze_movements_detected': eye_confidence.get('gaze_movements_detected', []),  # 🔧 PRESERVE gaze movements
                    'method': eye_confidence.get('method', 'unknown'),
                    'timestamp': eye_confidence.get('timestamp', datetime.now().isoformat())
                }
            
            # Transform Voice Confidence to binary format
            voice_confidence = self.current_results.get('voice_confidence', {})
            voice_confidence_level = voice_confidence.get('confidence_level', 'unknown')
            emotion = voice_confidence.get('emotion', 'neutral')
            
            # Convert confidence to binary: confident=1, not_confident=0
            # Good emotions (happy, calm, neutral) → confident
            # Bad emotions (angry, sad, fearful, stressed) → not_confident
            good_emotions = ['happy', 'calm', 'neutral']
            bad_emotions = ['angry', 'sad', 'fearful', 'stressed', 'fear', 'disgust']
            
            if (voice_confidence_level and 'confident' in voice_confidence_level.lower() and 'not' not in voice_confidence_level.lower()) or emotion in good_emotions:
                # Replace the entire voice_confidence object with binary format
                self.current_results['voice_confidence'] = {
                    'confidence': 1,
                    'confidence_level': 'confident',
                    'emotion': emotion,
                    'method': voice_confidence.get('method', 'unknown'),
                    'timestamp': voice_confidence.get('timestamp', datetime.now().isoformat())
                }
            else:
                # Replace the entire voice_confidence object with binary format
                self.current_results['voice_confidence'] = {
                    'confidence': 0,
                    'confidence_level': 'not_confident',
                    'emotion': emotion,
                    'method': voice_confidence.get('method', 'unknown'),
                    'timestamp': voice_confidence.get('timestamp', datetime.now().isoformat())
                }
                
            # Log the conversion results
            face_status = self.current_results['face_stress'].get('stress_level', 'N/A')
            if face_status == 'no_face_detected':
                logger.info(f"📊 Face stress: NO FACE DETECTED - kept as is (not converted to binary)")
            else:
                logger.debug(f"📊 Converted to binary format - Face stress: {self.current_results['face_stress'].get('stress', 'N/A')}, "
                            f"Hand confidence: {self.current_results['hand_confidence'].get('confidence', 'N/A')}, "
                            f"Eye confidence: {self.current_results['eye_confidence'].get('confidence', 'N/A')}, "
                            f"Voice confidence: {self.current_results['voice_confidence'].get('confidence', 'N/A')}")
            
        except Exception as e:
            logger.error(f"Error converting to binary format: {e}")
