import pyttsx3
import threading
import time
from typing import List, Optional
import os

class VoiceFeedback:
    def __init__(self):
        self.engine = None
        self.is_initialized = False
        self.is_speaking = False
        self.speak_queue = []
        self.last_feedback_time = 0
        self.min_feedback_interval = 3  # Minimum seconds between voice feedback
        
        self.initialize_engine()
        
        # Predefined feedback messages for common scenarios
        self.feedback_messages = {
            # Stance corrections
            "keep shoulders level": "Keep your shoulders level and aligned",
            "widen your stance": "Widen your stance for better stability",
            "align left knee over ankle": "Align your left knee over your ankle",
            "align right knee over ankle": "Align your right knee over your ankle",
            "front leg should be more straight": "Keep your front leg straighter",
            "bend back leg more for stability": "Bend your back leg more for better balance",
            
            # Kick corrections
            "lift kicking knee higher": "Lift your kicking knee higher",
            "rotate hips more for power": "Rotate your hips more to generate power",
            "keep balance on standing leg": "Maintain balance on your standing leg",
            
            # Positive reinforcement
            "excellent form": "Excellent form! Keep it up!",
            "good posture": "Good posture, you're doing great!",
            "good front leg position": "Perfect front leg position!",
            "good back leg bend": "Great back leg positioning!",
            "good knee lift": "Excellent knee lift!",
            "good hip rotation": "Perfect hip rotation!",
            
            # General instructions
            "pose detected": "Pose detected, analyzing your form",
            "no pose detected": "Please step into the camera view",
            "calibration complete": "Calibration completed successfully",
            "ready to train": "Ready to begin training"
        }
    
    def initialize_engine(self):
        """Initialize the text-to-speech engine"""
        try:
            self.engine = pyttsx3.init()
            
            # Configure voice settings
            voices = self.engine.getProperty('voices')
            if voices:
                # Try to use a female voice if available, otherwise use the first one
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
                else:
                    self.engine.setProperty('voice', voices[0].id)
            
            # Set speech rate (words per minute)
            self.engine.setProperty('rate', 150)  # Slightly slower for clarity
            
            # Set volume (0.0 to 1.0)
            self.engine.setProperty('volume', 0.8)
            
            self.is_initialized = True
            
        except Exception as e:
            print(f"Warning: Could not initialize voice feedback: {e}")
            self.is_initialized = False
    
    def speak_feedback(self, message: str, priority: str = "normal"):
        """
        Speak feedback message with priority control
        
        Args:
            message: The message to speak
            priority: "high", "normal", or "low"
        """
        if not self.is_initialized or not message:
            return
        
        current_time = time.time()
        
        # Rate limiting for normal and low priority messages
        if priority != "high":
            if current_time - self.last_feedback_time < self.min_feedback_interval:
                return
        
        # Clean and prepare message
        cleaned_message = self._clean_message(message.lower())
        
        # Get predefined message if available
        speech_text = self.feedback_messages.get(cleaned_message, message)
        
        # Add to queue and speak
        self._queue_speech(speech_text, priority)
        
        self.last_feedback_time = current_time
    
    def speak_instruction(self, instruction: str):
        """Speak calibration or training instructions"""
        if not self.is_initialized:
            return
        
        self._queue_speech(instruction, "high")
    
    def speak_encouragement(self):
        """Speak random encouragement"""
        encouragements = [
            "You're doing great! Keep practicing!",
            "Excellent progress! Stay focused!",
            "Good work! Remember to breathe!",
            "Perfect! Maintain that form!",
            "Outstanding technique! Keep it up!"
        ]
        
        import random
        message = random.choice(encouragements)
        self.speak_feedback(message, "normal")
    
    def speak_move_instruction(self, move_name: str):
        """Speak instructions for specific Taekwondo moves"""
        move_instructions = {
            "front_stance": "Step forward into front stance. Front leg straight, back leg bent. Weight evenly distributed.",
            "horse_stance": "Stand with feet wide apart, knees bent, back straight. Hold the position.",
            "back_stance": "Step back with one foot. Most weight on back leg, front leg light.",
            "front_kick": "Lift your knee high, extend leg forward, then retract quickly.",
            "roundhouse_kick": "Lift knee high, rotate hip, strike with the top of your foot.",
            "side_kick": "Lift knee to chest, extend leg sideways, strike with the heel.",
            "low_block": "Start high, sweep down and across to block low attacks.",
            "middle_block": "Block across your body at chest level.",
            "high_block": "Raise your arm to protect your head area."
        }
        
        instruction = move_instructions.get(move_name, f"Practice your {move_name.replace('_', ' ')}")
        self.speak_instruction(instruction)
    
    def _clean_message(self, message: str) -> str:
        """Clean message for lookup in predefined messages"""
        # Remove common prefixes
        message = message.replace("✗ ", "").replace("✓ ", "")
        message = message.replace("move: ", "").replace("move error: ", "")
        return message.strip()
    
    def _queue_speech(self, text: str, priority: str):
        """Queue speech with priority handling"""
        if self.is_speaking and priority == "high":
            # Stop current speech for high priority
            try:
                self.engine.stop()
            except:
                pass
        
        # Start speech in a separate thread
        thread = threading.Thread(target=self._speak_text, args=(text,))
        thread.daemon = True
        thread.start()
    
    def _speak_text(self, text: str):
        """Speak the text (called in separate thread)"""
        try:
            self.is_speaking = True
            self.engine.say(text)
            self.engine.runAndWait()
            self.is_speaking = False
        except Exception as e:
            print(f"Error speaking text: {e}")
            self.is_speaking = False
    
    def stop_speech(self):
        """Stop current speech"""
        if self.is_initialized and self.is_speaking:
            try:
                self.engine.stop()
                self.is_speaking = False
            except:
                pass
    
    def set_rate(self, rate: int):
        """Set speech rate (words per minute)"""
        if self.is_initialized:
            try:
                self.engine.setProperty('rate', rate)
            except:
                pass
    
    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)"""
        if self.is_initialized:
            try:
                volume = max(0.0, min(1.0, volume))  # Clamp between 0 and 1
                self.engine.setProperty('volume', volume)
            except:
                pass
    
    def test_voice(self):
        """Test the voice feedback system"""
        if self.is_initialized:
            self.speak_feedback("Voice feedback system is working correctly", "high")
            return True
        else:
            print("Voice feedback system is not available")
            return False
    
    def speak_session_summary(self, session_data: dict):
        """Speak a summary of the training session"""
        if not session_data:
            return
        
        summary_parts = []
        
        # Session duration
        if 'duration' in session_data:
            duration = session_data['duration']
            summary_parts.append(f"Training session completed in {duration} minutes")
        
        # Average pose quality
        if 'avg_quality' in session_data:
            quality = session_data['avg_quality']
            if quality >= 80:
                summary_parts.append("Excellent performance with high accuracy")
            elif quality >= 60:
                summary_parts.append("Good performance with room for improvement")
            else:
                summary_parts.append("Keep practicing to improve your form")
        
        # Most common error
        if 'common_error' in session_data:
            error = session_data['common_error']
            summary_parts.append(f"Focus on improving: {error}")
        
        # Encouragement
        summary_parts.append("Great work today! Keep practicing regularly to improve your Taekwondo skills.")
        
        # Speak the complete summary
        full_summary = ". ".join(summary_parts)
        self.speak_instruction(full_summary)
    
    def close(self):
        """Clean up the voice feedback system"""
        self.stop_speech()
        if self.is_initialized and self.engine:
            try:
                self.engine.stop()
            except:
                pass

# Audio file fallback for systems without TTS
class AudioFileFeedback:
    """Fallback class for pre-recorded audio feedback"""
    
    def __init__(self, audio_dir: str = "static/audio"):
        self.audio_dir = audio_dir
        self.audio_files = {}
        self.is_available = False
        
        # Check if pygame is available for audio playback
        try:
            import pygame
            pygame.mixer.init()
            self.is_available = True
        except ImportError:
            print("pygame not available for audio feedback")
    
    def load_audio_files(self):
        """Load pre-recorded audio files"""
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)
            return
        
        # Map audio files to feedback messages
        audio_mappings = {
            "shoulders_level.wav": "keep shoulders level",
            "widen_stance.wav": "widen your stance",
            "excellent_form.wav": "excellent form",
            "good_posture.wav": "good posture"
        }
        
        for filename, message in audio_mappings.items():
            filepath = os.path.join(self.audio_dir, filename)
            if os.path.exists(filepath):
                self.audio_files[message] = filepath
    
    def play_feedback(self, message: str):
        """Play pre-recorded audio feedback"""
        if not self.is_available:
            return
        
        cleaned_message = message.lower().strip()
        
        if cleaned_message in self.audio_files:
            try:
                import pygame
                sound = pygame.mixer.Sound(self.audio_files[cleaned_message])
                sound.play()
            except Exception as e:
                print(f"Error playing audio: {e}")

# Factory function to create appropriate feedback system
def create_voice_feedback() -> VoiceFeedback:
    """Create the best available voice feedback system"""
    voice_feedback = VoiceFeedback()
    
    if voice_feedback.is_initialized:
        return voice_feedback
    else:
        print("TTS not available, voice feedback disabled")
        return voice_feedback  # Return even if not initialized for graceful degradation