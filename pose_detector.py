import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, List, Tuple, Optional
import math

class TaekwondoPoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.current_landmarks = None
        self.calibration_data = None
        
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
            'pose_quality': 0.0
        }
        
        if results.pose_landmarks:
            analysis['pose_detected'] = True
            analysis['landmarks'] = results.pose_landmarks
            self.current_landmarks = results.pose_landmarks
            
            # Analyze pose quality and provide feedback
            analysis.update(self._analyze_pose(results.pose_landmarks, frame))
            
        return analysis
    
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
        
        # Check posture alignment
        shoulder_alignment = abs(left_shoulder[1] - right_shoulder[1])
        if shoulder_alignment > 20:
            errors.append("Keep shoulders level")
            pose_quality -= 15
        
        # Check stance width
        hip_width = abs(left_hip[0] - right_hip[0])
        if hip_width < 50:
            errors.append("Widen your stance")
            pose_quality -= 10
        
        # Check knee alignment over ankles
        left_knee_ankle_diff = abs(left_knee[0] - left_ankle[0])
        right_knee_ankle_diff = abs(right_knee[0] - right_ankle[0])
        
        if left_knee_ankle_diff > 30:
            errors.append("Align left knee over ankle")
            pose_quality -= 10
            
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
        """Analyze front stance specifically"""
        h, w, _ = frame.shape
        feedback = []
        errors = []
        
        left_hip = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.LEFT_HIP, w, h)
        right_hip = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.RIGHT_HIP, w, h)
        left_knee = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.LEFT_KNEE, w, h)
        right_knee = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.RIGHT_KNEE, w, h)
        left_ankle = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.LEFT_ANKLE, w, h)
        right_ankle = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.RIGHT_ANKLE, w, h)
        
        # Check front leg (assuming left is front)
        front_leg_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
        
        if front_leg_angle < 150 or front_leg_angle > 180:
            errors.append("Front leg should be more straight")
        else:
            feedback.append("Good front leg position")
            
        # Check back leg bend
        back_leg_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
        
        if back_leg_angle < 120 or back_leg_angle > 150:
            errors.append("Bend back leg more for stability")
        else:
            feedback.append("Good back leg bend")
        
        return {'feedback': feedback, 'errors': errors}
    
    def analyze_roundhouse_kick(self, landmarks, frame: np.ndarray) -> Dict:
        """Analyze roundhouse kick technique"""
        h, w, _ = frame.shape
        feedback = []
        errors = []
        
        # Check if leg is raised
        left_knee = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.LEFT_KNEE, w, h)
        right_knee = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.RIGHT_KNEE, w, h)
        left_hip = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.LEFT_HIP, w, h)
        right_hip = self.get_landmark_coordinates(landmarks, self.mp_pose.PoseLandmark.RIGHT_HIP, w, h)
        
        # Assuming right leg is kicking
        if right_knee[1] < right_hip[1] - 50:  # Knee raised above hip
            feedback.append("Good knee lift!")
            
            # Check hip rotation (simplified)
            hip_rotation = abs(left_hip[1] - right_hip[1])
            if hip_rotation > 15:
                feedback.append("Good hip rotation")
            else:
                errors.append("Rotate hips more for power")
        else:
            errors.append("Lift kicking knee higher")
        
        return {'feedback': feedback, 'errors': errors}
    
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
    
    def close(self):
        """Clean up resources"""
        self.pose.close()