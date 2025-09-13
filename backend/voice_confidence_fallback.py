"""
Voice Confidence Detection - Fallback Implementation
Uses audio feature analysis when neural network model fails
"""
import numpy as np
import logging
import librosa
from scipy import stats

logger = logging.getLogger(__name__)

class VoiceConfidenceFallback:
    def __init__(self):
        """Initialize fallback voice confidence detection"""
        logger.info("✅ Voice fallback detection initialized")
        
    def analyze_voice_confidence(self, audio_data, sample_rate=22050):
        """Analyze voice confidence using audio feature analysis with emotion mapping"""
        try:
            if audio_data is None or len(audio_data) == 0:
                return {
                    'confidence': 0,
                    'confidence_level': 'no_audio',
                    'emotion': 'unknown'
                }
            
            # Ensure audio is numpy array
            if not isinstance(audio_data, np.ndarray):
                audio_data = np.array(audio_data, dtype=np.float32)
            
            # Normalize audio
            if np.max(np.abs(audio_data)) > 0:
                audio_data = audio_data / np.max(np.abs(audio_data))
            
            # Extract enhanced audio features for emotion detection
            features = self._extract_enhanced_audio_features(audio_data, sample_rate)
            
            # Detect emotion from audio features
            emotion = self._detect_audio_emotion(features)
            
            # Map emotion to confidence (as you requested)
            confidence_score = self._map_emotion_to_confidence(emotion, features)
            
            # Map confidence to levels with emotion context
            confidence_level = self._map_confidence_level(confidence_score, emotion)
                
            return {
                'confidence': round(confidence_score, 2),
                'confidence_level': confidence_level,
                'emotion': emotion,
                'features': {
                    'pitch_mean': round(features.get('pitch_mean', 0), 2),
                    'energy': round(features.get('energy', 0), 2),
                    'speaking_rate': round(features.get('speaking_rate', 0), 2)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in voice confidence analysis: {e}")
            return {
                'confidence': 0,
                'confidence_level': 'analysis_error',
                'emotion': 'unknown'
            }
    
    def _extract_enhanced_audio_features(self, audio_data, sample_rate):
        """Extract enhanced audio features for emotion and confidence detection"""
        features = {}
        
        try:
            # Basic energy and volume
            features['energy'] = np.mean(audio_data ** 2)
            features['volume'] = np.mean(np.abs(audio_data))
            
            # Pitch analysis using librosa
            pitches, magnitudes = librosa.piptrack(y=audio_data, sr=sample_rate, threshold=0.1)
            pitch_values = []
            
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if pitch_values:
                features['pitch_mean'] = np.mean(pitch_values)
                features['pitch_std'] = np.std(pitch_values)
                features['pitch_range'] = np.max(pitch_values) - np.min(pitch_values)
            else:
                features['pitch_mean'] = 0
                features['pitch_std'] = 0  
                features['pitch_range'] = 0
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
            features['spectral_centroid'] = np.mean(spectral_centroids)
            
            # Zero crossing rate (indicates voice activity)
            zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
            features['zero_crossing_rate'] = np.mean(zcr)
            
            # MFCC features (voice characteristics)
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            features['mfcc_mean'] = np.mean(mfccs)
            features['mfcc_std'] = np.std(mfccs)
            
            # Speaking rate estimation
            onset_frames = librosa.onset.onset_detect(y=audio_data, sr=sample_rate)
            features['speaking_rate'] = len(onset_frames) / (len(audio_data) / sample_rate)
            
            # Pause detection
            features['silence_ratio'] = np.sum(np.abs(audio_data) < 0.01) / len(audio_data)
            
        except Exception as e:
            logger.error(f"Error extracting audio features: {e}")
            # Return default features
            features = {
                'energy': 0, 'volume': 0, 'pitch_mean': 0, 'pitch_std': 0,
                'pitch_range': 0, 'spectral_centroid': 0, 'zero_crossing_rate': 0,
                'mfcc_mean': 0, 'mfcc_std': 0, 'speaking_rate': 0, 'silence_ratio': 1.0
            }
        
        return features
    
    def _detect_audio_emotion(self, features):
        """Detect emotion from audio features"""
        try:
            # Emotion detection based on audio characteristics
            pitch_mean = features.get('pitch_mean', 0)
            energy = features.get('energy', 0)
            speaking_rate = features.get('speaking_rate', 0)
            pitch_std = features.get('pitch_std', 0)
            silence_ratio = features.get('silence_ratio', 1.0)
            
            # Map audio features to basic emotions (like face model)
            
            # Happy: High energy + stable/high pitch + good speaking rate
            if energy > 0.01 and pitch_mean > 180 and 2.5 <= speaking_rate <= 5 and silence_ratio < 0.3:
                return 'happy'
            
            # Angry: High energy + variable pitch + fast speaking
            elif energy > 0.015 and pitch_std > 60 and speaking_rate > 4:
                return 'angry'
            
            # Fear: High pitch + low energy + fast/irregular speaking
            elif pitch_mean > 220 and energy < 0.008 and (speaking_rate > 4.5 or silence_ratio > 0.4):
                return 'fear'
            
            # Sad: Low energy + low pitch + slow speaking + many pauses
            elif energy < 0.005 and pitch_mean < 150 and speaking_rate < 2 and silence_ratio > 0.3:
                return 'sad'
            
            # Disgust: Moderate energy + irregular patterns + pauses
            elif 0.005 <= energy <= 0.01 and pitch_std > 50 and silence_ratio > 0.25:
                return 'disgust'
            
            # Neutral: Balanced features, good voice quality
            elif 0.008 <= energy <= 0.015 and 150 <= pitch_mean <= 200 and 2 <= speaking_rate <= 4:
                return 'neutral'
            
            # Default to neutral for unclear patterns
            else:
                return 'neutral'
                
        except Exception as e:
            logger.error(f"Error detecting emotion: {e}")
            return 'neutral'
    
    def _map_emotion_to_confidence(self, emotion, features):
        """Map detected emotion to confidence score using your mapping"""
        # Your exact mapping
        confident_mapping = {
            'angry': 'Non-Confident',
            'disgust': 'Non-Confident', 
            'fear': 'Non-Confident',
            'happy': 'Confident',
            'neutral': 'Confident',
            'sad': 'Non-Confident'
        }
        
        confidence_category = confident_mapping.get(emotion, 'Confident')
        
        # Convert to numerical scores
        if confidence_category == 'Confident':
            base_confidence = 0.75  # High confidence for positive emotions
        else:  # Non-Confident
            base_confidence = 0.25  # Low confidence for negative emotions
        
        # Fine-tune based on audio quality
        energy = features.get('energy', 0)
        volume = features.get('volume', 0)
        
        # Boost confidence for clear, strong voice
        if energy > 0.012 and volume > 0.1:
            if confidence_category == 'Confident':
                base_confidence = min(0.90, base_confidence + 0.15)
            else:
                base_confidence = min(0.45, base_confidence + 0.1)
        
        # Reduce confidence for very weak/unclear voice
        elif energy < 0.003 or volume < 0.02:
            base_confidence = max(0.1, base_confidence - 0.15)
        
        return base_confidence
    
    def _map_confidence_level(self, confidence_score, emotion):
        """Map confidence score to level with emotion context"""
        # Your mapping categories
        confident_mapping = {
            'angry': 'Non-Confident',
            'disgust': 'Non-Confident',
            'fear': 'Non-Confident', 
            'happy': 'Confident',
            'neutral': 'Confident',
            'sad': 'Non-Confident'
        }
        
        confidence_category = confident_mapping.get(emotion, 'Confident')
        
        # Map to detailed levels
        if confidence_category == 'Confident':
            if confidence_score >= 0.8:
                return 'very_confident'
            elif confidence_score >= 0.65:
                return 'confident'
            else:
                return 'moderately_confident'
        else:  # Non-Confident
            if confidence_score >= 0.4:
                return 'low_confidence'
            else:
                return 'not_confident'
    
    def _extract_audio_features(self, audio_data, sample_rate):
        """Extract audio features for analysis"""
        features = {}
        
        try:
            # Energy/Volume features
            features['rms'] = np.sqrt(np.mean(audio_data**2))
            features['zero_crossing_rate'] = np.mean(librosa.feature.zero_crossing_rate(audio_data)[0])
            
            # Spectral features
            stft = librosa.stft(audio_data)
            magnitude = np.abs(stft)
            
            features['spectral_centroid'] = np.mean(librosa.feature.spectral_centroid(S=magnitude)[0])
            features['spectral_rolloff'] = np.mean(librosa.feature.spectral_rolloff(S=magnitude, sr=sample_rate)[0])
            features['spectral_bandwidth'] = np.mean(librosa.feature.spectral_bandwidth(S=magnitude, sr=sample_rate)[0])
            
            # MFCC features (first 5 coefficients)
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=5)
            for i in range(5):
                features[f'mfcc_{i}'] = np.mean(mfccs[i])
            
            # Pitch/Fundamental frequency
            pitches, magnitudes = librosa.piptrack(y=audio_data, sr=sample_rate)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if pitch_values:
                features['pitch_mean'] = np.mean(pitch_values)
                features['pitch_std'] = np.std(pitch_values)
            else:
                features['pitch_mean'] = 0
                features['pitch_std'] = 0
                
        except Exception as e:
            logger.error(f"❌ Error extracting audio features: {e}")
            # Return default features
            features = {
                'rms': 0, 'zero_crossing_rate': 0, 'spectral_centroid': 0,
                'spectral_rolloff': 0, 'spectral_bandwidth': 0,
                'mfcc_0': 0, 'mfcc_1': 0, 'mfcc_2': 0, 'mfcc_3': 0, 'mfcc_4': 0,
                'pitch_mean': 0, 'pitch_std': 0
            }
        
        return features
    
    def _calculate_voice_confidence(self, features):
        """Calculate voice confidence based on extracted features"""
        try:
            confidence_factors = []
            
            # Voice activity detection based on energy
            if features['rms'] > 0.01:  # Minimum energy threshold
                confidence_factors.append(0.2)
            
            # Spectral clarity (higher spectral centroid suggests clearer speech)
            if features['spectral_centroid'] > 1000:
                confidence_factors.append(0.15)
            
            # Pitch stability (lower std suggests more controlled speech)
            if features['pitch_std'] < 50 and features['pitch_mean'] > 80:
                confidence_factors.append(0.2)
            
            # MFCC patterns (speech-like characteristics)
            mfcc_energy = sum([abs(features[f'mfcc_{i}']) for i in range(5)])
            if mfcc_energy > 5:
                confidence_factors.append(0.15)
            
            # Zero crossing rate (moderate values suggest speech)
            if 0.05 < features['zero_crossing_rate'] < 0.3:
                confidence_factors.append(0.1)
            
            # Spectral bandwidth (moderate values suggest clear speech)
            if 1000 < features['spectral_bandwidth'] < 4000:
                confidence_factors.append(0.1)
            
            # Spectral rolloff (speech characteristics)
            if 2000 < features['spectral_rolloff'] < 8000:
                confidence_factors.append(0.1)
            
            # Calculate final confidence
            base_confidence = 0.3  # Base confidence for any audio
            feature_confidence = sum(confidence_factors)
            
            final_confidence = min(0.95, base_confidence + feature_confidence)
            
            return final_confidence
            
        except Exception as e:
            logger.error(f"❌ Error calculating voice confidence: {e}")
            return 0.3  # Default low confidence
