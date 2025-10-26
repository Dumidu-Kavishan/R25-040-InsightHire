"""
Improved Voice Confidence Detection for InsightHire
More accurate and reliable voice analysis
"""
import numpy as np
import logging
from datetime import datetime
from scipy import stats
from scipy.signal import find_peaks
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class ImprovedVoiceDetector:
    def __init__(self):
        """Initialize with improved confidence detection"""
        self.confidence_thresholds = {
            'energy': {'min': 0.005, 'max': 0.05},
            'pitch_stability': {'min': 0.7, 'max': 0.95},
            'speech_clarity': {'min': 0.6, 'max': 0.9},
            'voice_strength': {'min': 0.3, 'max': 0.8}
        }
        
    def detect_confidence_from_audio_data(self, audio_data, sample_rate=22050):
        """Main confidence detection method"""
        try:
            if isinstance(audio_data, list):
                audio_data = np.array(audio_data, dtype=np.float32)
            
            if len(audio_data) == 0:
                return {'confidence_level': 'no_audio', 'confidence': 0.0}
            
            # Normalize audio
            if np.max(np.abs(audio_data)) > 0:
                audio_data = audio_data / np.max(np.abs(audio_data))
            
            # Extract key confidence indicators
            confidence_metrics = self._extract_confidence_metrics(audio_data, sample_rate)
            
            # Calculate overall confidence score
            confidence_score = self._calculate_confidence_score(confidence_metrics)
            
            # Determine confidence level
            confidence_level = self._determine_confidence_level(confidence_score)
            
            # Convert to binary as requested
            binary_confidence = 1 if confidence_level == 'confident' else 0
            
            return {
                'confidence_level': confidence_level,
                'confidence': binary_confidence,
                'confidence_score': confidence_score,
                'metrics': confidence_metrics,
                'method': 'improved_voice_analysis',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in improved voice detection: {e}")
            return {'confidence_level': 'error', 'confidence': 0.0, 'error': str(e)}
    
    def _extract_confidence_metrics(self, audio_data, sample_rate):
        """Extract key metrics that indicate voice confidence"""
        metrics = {}
        
        # 1. Voice Energy (how strong/clear the voice is)
        metrics['energy'] = np.sqrt(np.mean(audio_data**2))
        
        # 2. Pitch Stability (consistent pitch indicates confidence)
        metrics['pitch_stability'] = self._calculate_pitch_stability(audio_data, sample_rate)
        
        # 3. Speech Clarity (clear articulation)
        metrics['speech_clarity'] = self._calculate_speech_clarity(audio_data, sample_rate)
        
        # 4. Voice Strength (overall voice power)
        metrics['voice_strength'] = np.max(np.abs(audio_data))
        
        # 5. Speech Rate (confident people speak at steady pace)
        metrics['speech_rate'] = self._calculate_speech_rate(audio_data, sample_rate)
        
        # 6. Voice Consistency (stable voice characteristics)
        metrics['voice_consistency'] = self._calculate_voice_consistency(audio_data)
        
        return metrics
    
    def _calculate_pitch_stability(self, audio_data, sample_rate):
        """Calculate how stable the pitch is (higher = more confident)"""
        try:
            # Use autocorrelation to find pitch
            autocorr = np.correlate(audio_data, audio_data, mode='full')
            autocorr = autocorr[autocorr.size // 2:]
            
            # Find peaks in autocorrelation
            peaks, _ = find_peaks(autocorr, height=np.max(autocorr) * 0.3)
            
            if len(peaks) > 1:
                # Calculate pitch variation
                pitches = sample_rate / peaks[:5]  # First 5 peaks
                pitch_variance = np.var(pitches)
                pitch_mean = np.mean(pitches)
                
                # Stability is inverse of normalized variance
                if pitch_mean > 0:
                    stability = 1 / (1 + pitch_variance / (pitch_mean ** 2))
                    return min(1.0, max(0.0, stability))
            
            return 0.5  # Default moderate stability
        except:
            return 0.5
    
    def _calculate_speech_clarity(self, audio_data, sample_rate):
        """Calculate speech clarity based on spectral characteristics"""
        try:
            # FFT analysis
            fft = np.fft.fft(audio_data)
            magnitude = np.abs(fft[:len(fft)//2])
            freqs = np.fft.fftfreq(len(fft), 1/sample_rate)[:len(fft)//2]
            
            # Focus on speech frequency range (300-3400 Hz)
            speech_mask = (freqs >= 300) & (freqs <= 3400)
            speech_energy = np.sum(magnitude[speech_mask])
            total_energy = np.sum(magnitude)
            
            if total_energy > 0:
                clarity = speech_energy / total_energy
                return min(1.0, max(0.0, clarity))
            
            return 0.5
        except:
            return 0.5
    
    def _calculate_speech_rate(self, audio_data, sample_rate):
        """Calculate speech rate (words per minute estimate)"""
        try:
            # Find speech segments using energy
            window_size = int(0.025 * sample_rate)  # 25ms windows
            energy_windows = []
            
            for i in range(0, len(audio_data) - window_size, window_size):
                window_energy = np.mean(audio_data[i:i+window_size]**2)
                energy_windows.append(window_energy)
            
            # Find speech vs silence
            energy_threshold = np.mean(energy_windows) * 0.1
            speech_segments = [e > energy_threshold for e in energy_windows]
            
            # Count speech segments (rough word count)
            word_count = sum(speech_segments) / 10  # Rough conversion
            duration_minutes = len(audio_data) / sample_rate / 60
            
            if duration_minutes > 0:
                wpm = word_count / duration_minutes
                # Normalize WPM (100-200 is good range)
                normalized_wpm = min(1.0, max(0.0, (wpm - 50) / 150))
                return normalized_wpm
            
            return 0.5
        except:
            return 0.5
    
    def _calculate_voice_consistency(self, audio_data):
        """Calculate how consistent the voice characteristics are"""
        try:
            # Split audio into segments
            segment_length = len(audio_data) // 4
            segments = [audio_data[i:i+segment_length] for i in range(0, len(audio_data), segment_length)]
            
            if len(segments) < 2:
                return 0.5
            
            # Calculate energy for each segment
            segment_energies = [np.sqrt(np.mean(seg**2)) for seg in segments if len(seg) > 0]
            
            if len(segment_energies) > 1:
                # Consistency is inverse of coefficient of variation
                mean_energy = np.mean(segment_energies)
                std_energy = np.std(segment_energies)
                
                if mean_energy > 0:
                    cv = std_energy / mean_energy
                    consistency = 1 / (1 + cv)
                    return min(1.0, max(0.0, consistency))
            
            return 0.5
        except:
            return 0.5
    
    def _calculate_confidence_score(self, metrics):
        """Calculate overall confidence score from metrics"""
        try:
            # Weighted combination of metrics
            weights = {
                'energy': 0.25,
                'pitch_stability': 0.25,
                'speech_clarity': 0.20,
                'voice_strength': 0.15,
                'speech_rate': 0.10,
                'voice_consistency': 0.05
            }
            
            # Normalize each metric to 0-1 range
            normalized_metrics = {}
            for key, value in metrics.items():
                if key in weights:
                    # Apply sigmoid normalization for better distribution
                    normalized_metrics[key] = 1 / (1 + np.exp(-5 * (value - 0.5)))
            
            # Calculate weighted score
            total_score = 0
            total_weight = 0
            
            for key, weight in weights.items():
                if key in normalized_metrics:
                    total_score += normalized_metrics[key] * weight
                    total_weight += weight
            
            if total_weight > 0:
                final_score = total_score / total_weight
                return min(1.0, max(0.0, final_score))
            
            return 0.5
        except:
            return 0.5
    
    def _determine_confidence_level(self, confidence_score):
        """Determine confidence level based on score"""
        if confidence_score >= 0.7:
            return 'confident'
        elif confidence_score >= 0.4:
            return 'moderate'
        else:
            return 'not_confident'

# Alternative: Machine Learning Based Approach
class MLVoiceDetector:
    """Machine Learning based voice confidence detection"""
    
    def __init__(self):
        self.features = [
            'energy', 'pitch_stability', 'speech_clarity', 
            'voice_strength', 'speech_rate', 'voice_consistency'
        ]
        
    def detect_confidence_from_audio_data(self, audio_data, sample_rate=22050):
        """ML-based confidence detection"""
        try:
            # Extract features
            detector = ImprovedVoiceDetector()
            metrics = detector._extract_confidence_metrics(audio_data, sample_rate)
            
            # Simple ML-like decision tree
            confidence_score = self._ml_confidence_prediction(metrics)
            confidence_level = detector._determine_confidence_level(confidence_score)
            binary_confidence = 1 if confidence_level == 'confident' else 0
            
            return {
                'confidence_level': confidence_level,
                'confidence': binary_confidence,
                'confidence_score': confidence_score,
                'metrics': metrics,
                'method': 'ml_voice_analysis',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in ML voice detection: {e}")
            return {'confidence_level': 'error', 'confidence': 0.0, 'error': str(e)}
    
    def _ml_confidence_prediction(self, metrics):
        """Simple ML-like prediction using decision rules"""
        score = 0.0
        
        # Rule 1: Energy check
        if metrics['energy'] > 0.01:
            score += 0.3
        elif metrics['energy'] > 0.005:
            score += 0.2
        
        # Rule 2: Pitch stability
        if metrics['pitch_stability'] > 0.8:
            score += 0.25
        elif metrics['pitch_stability'] > 0.6:
            score += 0.15
        
        # Rule 3: Speech clarity
        if metrics['speech_clarity'] > 0.7:
            score += 0.2
        elif metrics['speech_clarity'] > 0.5:
            score += 0.1
        
        # Rule 4: Voice strength
        if metrics['voice_strength'] > 0.5:
            score += 0.15
        elif metrics['voice_strength'] > 0.3:
            score += 0.1
        
        # Rule 5: Speech rate (moderate is best)
        if 0.4 <= metrics['speech_rate'] <= 0.7:
            score += 0.1
        
        return min(1.0, score)
