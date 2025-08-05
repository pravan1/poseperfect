import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, List, Tuple, Optional
import math
from performance_config import PerformanceConfig
from move_instructions import TaekwondoMoveInstructions

class TaekwondoPoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=PerformanceConfig.MEDIAPIPE_MODEL_COMPLEXITY,
            enable_segmentation=False,
            min_detection_confidence=PerformanceConfig.MEDIAPIPE_MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=PerformanceConfig.MEDIAPIPE_MIN_TRACKING_CONFIDENCE,
            smooth_landmarks=PerformanceConfig.MEDIAPIPE_SMOOTH_LANDMARKS
        )
        
        self.current_landmarks = None
        self.calibration_data = None
        self.move_instructions = TaekwondoMoveInstructions()
        self.current_move = None
        
    def calculate_angle(self, a: Tuple[float, float], b: Tuple[float, float], c: Tuple[float, float]) -> float:
        """Calculate angle between three points"""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle
    
    def get_landmark_coordinates(self, landmarks, landmark_id: int, frame_width: int, frame_height: int) -> Tuple[int, int]:
        """Get pixel coordinates of a landmark"""
        landmark = landmarks.landmark[landmark_id]
        # Check if landmark is visible enough
        if landmark.visibility < 0.3:
            return None
        return (int(landmark.x * frame_width), int(landmark.y * frame_height))
    
    def detect_pose(self, frame: np.ndarray) -> Dict:
        """Detect pose in frame and return analysis results"""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(frame_rgb)
        
        analysis = {
            'pose_detected': False,
            'landmarks': None,
            'feedback': [],
            'errors': [],
            'pose_quality': 0.0,
            'visibility_score': 0.0
        }
        
        if results.pose_landmarks:
            # Check overall visibility of key landmarks
            visibility_score = self._calculate_visibility_score(results.pose_landmarks)
            analysis['visibility_score'] = visibility_score
            
            # Only consider pose detected if visibility is good enough
            if visibility_score > 0.4:
                analysis['pose_detected'] = True
                analysis['landmarks'] = results.pose_landmarks
                self.current_landmarks = results.pose_landmarks
                
                # Analyze pose quality and provide feedback
                analysis.update(self._analyze_pose(results.pose_landmarks, frame))
            else:
                analysis['feedback'].append("Move closer to camera or ensure full body is visible")
            
        return analysis
    
    def _calculate_visibility_score(self, landmarks) -> float:
        """Calculate overall visibility score for key landmarks"""
        key_landmarks = [
            self.mp_pose.PoseLandmark.NOSE,
            self.mp_pose.PoseLandmark.LEFT_SHOULDER,
            self.mp_pose.PoseLandmark.RIGHT_SHOULDER,
            self.mp_pose.PoseLandmark.LEFT_HIP,
            self.mp_pose.PoseLandmark.RIGHT_HIP,
            self.mp_pose.PoseLandmark.LEFT_KNEE,
            self.mp_pose.PoseLandmark.RIGHT_KNEE,
            self.mp_pose.PoseLandmark.LEFT_ANKLE,
            self.mp_pose.PoseLandmark.RIGHT_ANKLE
        ]
        
        total_visibility = sum(landmarks.landmark[lm].visibility for lm in key_landmarks)
        return total_visibility / len(key_landmarks)
    
    def _analyze_pose(self, landmarks, frame: np.ndarray) -> Dict:
        """Analyze pose for Taekwondo-specific feedback"""
        h, w, _ = frame.shape
        feedback = []
        errors = []
        pose_quality = 100.0
        
        # Key landmark coordinates
        left_shoulder = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.LEFT_SHOULDER, w, h)
        right_shoulder = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.RIGHT_SHOULDER, w, h)
        left_hip = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.LEFT_HIP, w, h)
        right_hip = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.RIGHT_HIP, w, h)
        left_knee = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.LEFT_KNEE, w, h)
        right_knee = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.RIGHT_KNEE, w, h)
        left_ankle = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.LEFT_ANKLE, w, h)
        right_ankle = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.RIGHT_ANKLE, w, h)
        
        # Check if key landmarks are visible
        if None in [left_shoulder, right_shoulder, left_hip, right_hip]:
            feedback.append("Upper body not fully visible")
            return {'feedback': feedback, 'errors': errors, 'pose_quality': 0}
        
        # Check posture alignment
        if left_shoulder and right_shoulder:
            shoulder_alignment = abs(left_shoulder[1] - right_shoulder[1])
            if shoulder_alignment > 20:
                errors.append("Keep shoulders level")
                pose_quality -= 15
        
        # Check stance width
        if left_hip and right_hip:
            hip_width = abs(left_hip[0] - right_hip[0])
            if hip_width < 50:
                errors.append("Widen your stance")
                pose_quality -= 10
        
        # Check knee alignment over ankles
        if left_knee and left_ankle:
            left_knee_ankle_diff = abs(left_knee[0] - left_ankle[0])
            if left_knee_ankle_diff > 30:
                errors.append("Align left knee over ankle")
                pose_quality -= 10
        
        if right_knee and right_ankle:
            right_knee_ankle_diff = abs(right_knee[0] - right_ankle[0])
            if right_knee_ankle_diff > 30:
                errors.append("Align right knee over ankle")
                pose_quality -= 10
        
        # Provide positive feedback
        if pose_quality > 85:
            feedback.append("Excellent form!")
        elif pose_quality > 70:
            feedback.append("Good posture, minor adjustments needed")
        elif pose_quality > 50:
            feedback.append("Keep practicing your stance")
        
        return {
            'feedback': feedback,
            'errors': errors,
            'pose_quality': max(0, pose_quality)
        }
    
    def analyze_front_stance(self, landmarks, frame: np.ndarray) -> Dict:
        """Analyze front stance with detailed corrections"""
        h, w, _ = frame.shape
        feedback = []
        errors = []
        corrections = []
        
        # Get key points
        left_hip = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.LEFT_HIP, w, h)
        right_hip = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.RIGHT_HIP, w, h)
        left_knee = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.LEFT_KNEE, w, h)
        right_knee = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.RIGHT_KNEE, w, h)
        left_ankle = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.LEFT_ANKLE, w, h)
        right_ankle = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.RIGHT_ANKLE, w, h)
        left_shoulder = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.LEFT_SHOULDER, w, h)
        right_shoulder = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.RIGHT_SHOULDER, w, h)
        
        # Get target parameters for this move
        key_points = self.move_instructions.get_move_key_points("Front Stance")
        error_corrections = self.move_instructions.get_move_error_corrections("Front Stance")
        
        # Determine which leg is front (lower y-coordinate means higher on screen/closer to camera)
        if left_ankle[1] < right_ankle[1]:  # Left leg is front
            front_leg_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
            back_leg_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
            front_knee_pos = left_knee
            front_ankle_pos = left_ankle
        else:  # Right leg is front
            front_leg_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
            back_leg_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
            front_knee_pos = right_knee
            front_ankle_pos = right_ankle
        
        # Check front knee angle (should be 80-100 degrees)
        target_range = key_points["front_knee_angle"]
        if front_leg_angle < target_range[0]:
            corrections.append(error_corrections.get("front_knee_over_toes", "Adjust front knee angle"))
        elif front_leg_angle > target_range[1]:
            corrections.append("Bend your front knee more, aim for a 90-degree angle")
        else:
            feedback.append("Perfect front knee angle")
            
        # Check back leg (should be nearly straight, 160-180 degrees)
        target_range = key_points["back_knee_angle"]
        if back_leg_angle < target_range[0]:
            corrections.append(error_corrections.get("back_leg_bent", "Straighten back leg"))
        else:
            feedback.append("Good back leg position")
        
        # Check if front knee is over ankle
        knee_ankle_diff = abs(front_knee_pos[0] - front_ankle_pos[0])
        if knee_ankle_diff > 30:
            corrections.append(error_corrections.get("front_knee_over_toes", "Align knee over ankle"))
        
        # Check shoulder alignment
        shoulder_diff = abs(left_shoulder[1] - right_shoulder[1])
        if shoulder_diff > 20:
            corrections.append(error_corrections.get("shoulders_uneven", "Level your shoulders"))
        else:
            feedback.append("Good shoulder alignment")
        
        # Check stance width
        stance_width = abs(left_ankle[0] - right_ankle[0])
        hip_width = abs(left_hip[0] - right_hip[0])
        if stance_width < hip_width * 1.3:
            corrections.append(error_corrections.get("stance_too_narrow", "Widen your stance"))
        
        return {
            'feedback': feedback, 
            'errors': errors,
            'corrections': corrections
        }
    
    def analyze_roundhouse_kick(self, landmarks, frame: np.ndarray) -> Dict:
        """Analyze roundhouse kick with detailed corrections"""
        h, w, _ = frame.shape
        feedback = []
        errors = []
        corrections = []
        
        # Get key points
        left_knee = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.LEFT_KNEE, w, h)
        right_knee = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.RIGHT_KNEE, w, h)
        left_hip = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.LEFT_HIP, w, h)
        right_hip = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.RIGHT_HIP, w, h)
        left_ankle = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.LEFT_ANKLE, w, h)
        right_ankle = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.RIGHT_ANKLE, w, h)
        
        # Get correction messages
        error_corrections = self.move_instructions.get_move_error_corrections("Roundhouse Kick")
        
        # Determine which leg is kicking (higher knee)
        if right_knee[1] < left_knee[1] - 20:  # Right leg is kicking
            kicking_knee = right_knee
            kicking_hip = right_hip
            kicking_ankle = right_ankle
            supporting_ankle = left_ankle
        elif left_knee[1] < right_knee[1] - 20:  # Left leg is kicking
            kicking_knee = left_knee
            kicking_hip = left_hip
            kicking_ankle = left_ankle
            supporting_ankle = right_ankle
        else:
            corrections.append("Lift your kicking knee higher to chamber the kick")
            return {'feedback': feedback, 'errors': errors, 'corrections': corrections}
        
        # Check knee height (should be at hip level or higher)
        if kicking_knee[1] < kicking_hip[1]:  # Knee above hip
            feedback.append("Excellent knee lift for roundhouse kick")
        elif kicking_knee[1] < kicking_hip[1] + 30:  # Knee near hip level
            feedback.append("Good knee height")
        else:
            corrections.append(error_corrections.get("low_knee", "Lift knee higher"))
        
        # Check hip rotation
        hip_rotation = abs(left_hip[0] - right_hip[0])
        hip_vertical_diff = abs(left_hip[1] - right_hip[1])
        
        if hip_rotation > 40 or hip_vertical_diff > 15:
            feedback.append("Great hip rotation for power")
        else:
            corrections.append(error_corrections.get("no_hip_rotation", "Rotate hips more"))
        
        # Check supporting leg stability
        # Supporting foot should be pivoted (we can estimate this from hip rotation)
        if hip_rotation > 30:
            feedback.append("Good pivot on supporting foot")
        else:
            corrections.append(error_corrections.get("no_pivot", "Pivot on supporting foot"))
        
        return {
            'feedback': feedback,
            'errors': errors,
            'corrections': corrections
        }
    
    def draw_pose_landmarks(self, frame: np.ndarray, landmarks) -> np.ndarray:
        """Draw pose landmarks on frame"""
        if landmarks:
            self.mp_drawing.draw_landmarks(
                frame, landmarks, self.mp_pose.POSE_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
            )
        return frame
    
    def set_calibration_data(self, calibration_data: Dict):
        """Set user calibration data for personalized feedback"""
        self.calibration_data = calibration_data
    
    def set_current_move(self, move_name: str):
        """Set the current move being practiced"""
        self.current_move = move_name
        return self.move_instructions.get_move_instructions(move_name)
    
    def close(self):
        """Clean up resources"""
        self.pose.close()