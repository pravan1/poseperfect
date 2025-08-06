import pyttsx3
import threading
import queue
import time


class VoiceFeedback:
    """Offline voice feedback system using pyttsx3"""
    
    def __init__(self):
        self.engine = None
        self.feedback_queue = queue.Queue()
        self.last_feedback_time = 0
        self.min_feedback_interval = 3.0  # Minimum seconds between feedbacks
        self.is_speaking = False
        
        # Initialize TTS engine
        self.init_engine()
        
        # Start feedback thread
        self.feedback_thread = threading.Thread(target=self._feedback_worker, daemon=True)
        self.feedback_thread.start()
    
    def init_engine(self):
        """Initialize the TTS engine"""
        try:
            self.engine = pyttsx3.init()
            
            # Configure voice properties
            voices = self.engine.getProperty('voices')
            if voices:
                # Try to use a female voice for more natural Siri-like sound
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            
            # Set speech rate and volume for more natural sound
            self.engine.setProperty('rate', 135)  # Slower, more natural pace
            self.engine.setProperty('volume', 0.6)  # Quieter volume (0.0 to 1.0)
            
            print("Voice feedback system initialized successfully")
        except Exception as e:
            print(f"Error initializing voice feedback: {e}")
            self.engine = None
    
    def _feedback_worker(self):
        """Worker thread for processing feedback queue"""
        while True:
            try:
                feedback = self.feedback_queue.get(timeout=1)
                if feedback and self.engine:
                    current_time = time.time()
                    
                    # Check if enough time has passed since last feedback
                    if current_time - self.last_feedback_time >= self.min_feedback_interval:
                        self.is_speaking = True
                        self.engine.say(feedback)
                        self.engine.runAndWait()
                        self.last_feedback_time = current_time
                        self.is_speaking = False
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in voice feedback worker: {e}")
                self.is_speaking = False
    
    def speak(self, text, priority="normal"):
        """Add feedback to the queue"""
        if not self.engine:
            return
        
        # Clear queue for high priority messages
        if priority == "high" and not self.feedback_queue.empty():
            while not self.feedback_queue.empty():
                try:
                    self.feedback_queue.get_nowait()
                except queue.Empty:
                    break
        
        # Add to queue if not currently speaking or high priority
        if not self.is_speaking or priority == "high":
            self.feedback_queue.put(text)
    
    def speak_pose_correction(self, pose_name, corrections):
        """Speak pose-specific corrections"""
        if not corrections:
            return
        
        # Prioritize the most important correction
        correction_text = corrections[0]
        
        # Add pose context for clarity
        full_text = f"For {pose_name}: {correction_text}"
        self.speak(full_text, priority="high")
    
    def speak_encouragement(self):
        """Speak encouraging messages"""
        encouragements = [
            "Great form! Keep it up!",
            "Excellent pose! Hold it steady.",
            "Perfect! You're doing great.",
            "Outstanding symmetry!",
            "Impressive muscle control!"
        ]
        
        import random
        self.speak(random.choice(encouragements))
    
    def speak_score(self, score):
        """Announce the current score"""
        if score >= 90:
            message = f"Excellent! {int(score)} percent match. Professional level!"
        elif score >= 80:
            message = f"Great job! {int(score)} percent match. Almost perfect!"
        elif score >= 70:
            message = f"Good work! {int(score)} percent match. Keep improving!"
        elif score >= 60:
            message = f"{int(score)} percent match. Focus on the corrections."
        else:
            message = f"{int(score)} percent match. Adjust your pose."
        
        self.speak(message)
    
    def test_voice(self):
        """Test the voice system"""
        if self.engine:
            test_message = "Voice feedback system is ready. Let's perfect your bodybuilding poses!"
            self.engine.say(test_message)
            self.engine.runAndWait()
            return True
        return False
    
    def shutdown(self):
        """Shutdown the voice system"""
        if self.engine:
            self.engine.stop()


# Pose-specific voice cues
POSE_INSTRUCTIONS = {
    "Rear Double Biceps": [
        "Face away from the camera",
        "Raise arms like front double biceps",
        "Flex calves by raising on toes",
        "Squeeze shoulder blades together"
    ],
    "Front Double Biceps": [
        "Stand with feet shoulder-width apart",
        "Raise both arms to shoulder level",
        "Flex biceps and rotate wrists outward",
        "Keep chest expanded and abs tight"
    ],
    "Side Chest": [
        "Turn your body to the side",
        "Bring front arm across your chest",
        "Flex the chest and bicep",
        "Keep rear leg slightly bent"
    ],
    "Back Lat Spread": [
        "Face away from the camera",
        "Spread your lats as wide as possible",
        "Keep elbows forward and out",
        "Flex your back muscles"
    ]
}


def get_pose_instructions(pose_name):
    """Get voice instructions for a specific pose"""
    return POSE_INSTRUCTIONS.get(pose_name, ["Position yourself for the pose"])