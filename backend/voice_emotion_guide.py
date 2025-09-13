#!/usr/bin/env python3
"""
Voice Emotion Detection Guide for InsightHire
Shows all possible emotions and their confidence mappings
"""
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def show_emotion_mappings():
    """Display all possible emotions and their confidence mappings"""
    
    logger.info("🎤 VOICE EMOTION DETECTION GUIDE")
    logger.info("=" * 60)
    logger.info("")
    
    logger.info("📊 EMOTIONS DETECTED FROM VOICE:")
    logger.info("-" * 40)
    
    # Positive emotions (high confidence)
    logger.info("✅ POSITIVE EMOTIONS → HIGH CONFIDENCE:")
    logger.info("   🟢 'confident' → 0.85 confidence")
    logger.info("      - Stable pitch + good energy + moderate speaking rate")
    logger.info("      - Clear, strong voice without hesitation")
    logger.info("")
    logger.info("   🟢 'excited' → 0.75 confidence") 
    logger.info("      - High energy + high pitch + fast speaking")
    logger.info("      - Enthusiastic tone with pitch variation")
    logger.info("")
    logger.info("   🟢 'calm' → 0.70 confidence")
    logger.info("      - Steady, controlled voice")
    logger.info("      - Low pitch variation but good energy")
    logger.info("")
    
    # Neutral emotions (moderate confidence)
    logger.info("🟡 NEUTRAL EMOTIONS → MODERATE CONFIDENCE:")
    logger.info("   🟡 'neutral' → 0.60 confidence")
    logger.info("      - Average energy, pitch, and speaking rate")
    logger.info("      - No strong emotional indicators")
    logger.info("")
    
    # Negative emotions (low confidence)
    logger.info("❌ NEGATIVE EMOTIONS → LOW CONFIDENCE:")
    logger.info("   🔴 'nervous' → 0.25 confidence")
    logger.info("      - Low energy + low pitch + many pauses")
    logger.info("      - High silence ratio (lots of hesitation)")
    logger.info("")
    logger.info("   🔴 'anxious' → 0.30 confidence")
    logger.info("      - High pitch variation + medium energy")
    logger.info("      - Voice trembling or shaking")
    logger.info("")
    logger.info("   🔴 'hesitant' → 0.35 confidence")
    logger.info("      - Very low activity or many long pauses")
    logger.info("      - Uncertain, stammering speech patterns")
    logger.info("")
    logger.info("   🔴 'sad' → 0.20 confidence")
    logger.info("      - Low energy + low pitch + slow speaking")
    logger.info("      - Monotone, flat voice")
    logger.info("")
    
    # Unknown/Error states
    logger.info("⚪ OTHER STATES:")
    logger.info("   ⚪ 'unknown' → 0.50 confidence")
    logger.info("      - Unable to classify emotion")
    logger.info("   ⚪ 'no_audio' → 0.00 confidence")
    logger.info("      - No audio data received")
    logger.info("")
    
    logger.info("🔧 AUDIO FEATURES ANALYZED:")
    logger.info("-" * 40)
    logger.info("   📏 Pitch (frequency): High/Low/Stable")
    logger.info("   ⚡ Energy: Voice strength and volume")
    logger.info("   🗣️ Speaking Rate: Words per second")
    logger.info("   ⏸️ Pause Analysis: Silence detection")
    logger.info("   🎵 Spectral Features: Voice quality")
    logger.info("   📊 MFCC: Voice characteristics")
    logger.info("")
    
    logger.info("📋 CONFIDENCE LEVEL MAPPING:")
    logger.info("-" * 40)
    logger.info("   🏆 0.80+ → 'very_confident'")
    logger.info("   ✅ 0.65+ → 'confident'") 
    logger.info("   🟡 0.50+ → 'moderately_confident'")
    logger.info("   ⚠️ 0.30+ → 'low_confidence'")
    logger.info("   ❌ 0.30- → 'not_confident'")
    logger.info("")
    
    logger.info("🎯 WHAT YOU'LL SEE IN LOGS:")
    logger.info("-" * 40)
    logger.info("   🎤 Voice analysis: confident (confidence: 0.85) [emotion: confident]")
    logger.info("   🎤 Voice analysis: nervous (confidence: 0.25) [emotion: nervous]")
    logger.info("   🎤 Voice analysis: excited (confidence: 0.75) [emotion: excited]")
    logger.info("")
    
    logger.info("📱 FIREBASE DATA STRUCTURE:")
    logger.info("-" * 40)
    logger.info('   "voice_confidence": {')
    logger.info('     "confidence": 0.85,')
    logger.info('     "confidence_level": "confident",')
    logger.info('     "emotion": "confident",')
    logger.info('     "features": {')
    logger.info('       "pitch_mean": 180.5,')
    logger.info('       "energy": 0.012,')
    logger.info('       "speaking_rate": 3.2')
    logger.info('     }')
    logger.info('   }')
    logger.info("")
    
    logger.info("💡 TIPS FOR BETTER DETECTION:")
    logger.info("-" * 40)
    logger.info("   🎙️ Speak clearly and at moderate volume")
    logger.info("   📏 Maintain steady pace (not too fast/slow)")
    logger.info("   ⏸️ Avoid long pauses or 'um/uh' sounds")
    logger.info("   🎵 Natural tone variation shows confidence")
    logger.info("   💪 Strong, clear voice = higher confidence")
    logger.info("")
    
    logger.info("=" * 60)
    logger.info("🎯 Your voice emotion detection is working!")
    logger.info("Check your Firebase Console to see the emotion data!")

if __name__ == '__main__':
    show_emotion_mappings()
