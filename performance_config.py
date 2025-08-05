"""Performance configuration settings for Taekwondo.AI"""

class PerformanceConfig:
    """Configuration for performance optimizations"""
    
    # Video processing settings
    VIDEO_FPS = 30  # Increased for smoother video
    FRAME_SKIP_RATE = 2  # Process every 2nd frame for better responsiveness
    
    # MediaPipe settings
    MEDIAPIPE_MODEL_COMPLEXITY = 1  # 0 = fastest, 1 = balanced, 2 = most accurate
    MEDIAPIPE_MIN_DETECTION_CONFIDENCE = 0.5  # Lowered for better detection
    MEDIAPIPE_MIN_TRACKING_CONFIDENCE = 0.5  # Lowered for better tracking
    MEDIAPIPE_SMOOTH_LANDMARKS = True
    
    # UI update settings
    FEEDBACK_UPDATE_INTERVAL = 0.3  # Reduced for more responsive feedback
    QUALITY_BAR_UPDATE_INTERVAL = 0.1  # Reduced for smoother quality bar
    MAX_FEEDBACK_LINES = 100  # Maximum lines in feedback text
    
    # Processing thread settings
    POSE_QUEUE_SIZE = 1  # Reduced queue size to minimize lag
    
    # Voice feedback settings
    VOICE_MIN_INTERVAL = 3  # Minimum seconds between voice feedback
    
    # Image scaling
    USE_FAST_SCALING = True  # Use Qt.FastTransformation instead of Qt.SmoothTransformation
    
    @classmethod
    def get_performance_mode(cls):
        """Get current performance mode"""
        return "optimized"
    
    @classmethod
    def apply_high_performance(cls):
        """Apply settings for maximum performance"""
        cls.VIDEO_FPS = 15
        cls.FRAME_SKIP_RATE = 4
        cls.MEDIAPIPE_MODEL_COMPLEXITY = 0
        cls.USE_FAST_SCALING = True
    
    @classmethod
    def apply_balanced(cls):
        """Apply balanced settings"""
        cls.VIDEO_FPS = 20
        cls.FRAME_SKIP_RATE = 3
        cls.MEDIAPIPE_MODEL_COMPLEXITY = 0
        cls.USE_FAST_SCALING = True
    
    @classmethod
    def apply_quality(cls):
        """Apply settings for best quality"""
        cls.VIDEO_FPS = 30
        cls.FRAME_SKIP_RATE = 1
        cls.MEDIAPIPE_MODEL_COMPLEXITY = 1
        cls.USE_FAST_SCALING = False