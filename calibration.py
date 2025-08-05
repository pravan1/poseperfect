import cv2
import numpy as np
from typing import Dict, Optional, Tuple
import json
import os

class UserCalibration:
    def __init__(self):
        self.calibration_file = "user_calibration.json"
        self.calibration_data = {
            'user_height': None,
            'shoulder_width': None,
            'arm_span': None,
            'leg_length': None,
            'stance_preferences': {},
            'calibrated': False
        }
        self.load_calibration()
    
    def start_calibration_sequence(self, pose_detector) -> Dict:
        """Start the calibration process"""
        return {
            'step': 1,
            'instruction': 'Stand in a relaxed neutral position with arms at your sides',
            'next_action': 'capture_neutral_pose'
        }
    
    def capture_neutral_pose(self, landmarks, frame_dimensions: Tuple[int, int]) -> Dict:
        """Capture user's neutral standing pose for calibration"""
        if not landmarks:
            return {'success': False, 'message': 'No pose detected'}
        
        w, h = frame_dimensions
        
        # Calculate basic body measurements
        left_shoulder = self._get_landmark_coords(landmarks, 11, w, h)  # LEFT_SHOULDER
        right_shoulder = self._get_landmark_coords(landmarks, 12, w, h)  # RIGHT_SHOULDER
        left_hip = self._get_landmark_coords(landmarks, 23, w, h)  # LEFT_HIP
        right_hip = self._get_landmark_coords(landmarks, 24, w, h)  # RIGHT_HIP
        left_ankle = self._get_landmark_coords(landmarks, 27, w, h)  # LEFT_ANKLE
        right_ankle = self._get_landmark_coords(landmarks, 28, w, h)  # RIGHT_ANKLE
        
        # Calculate measurements
        shoulder_width = abs(left_shoulder[0] - right_shoulder[0])
        hip_width = abs(left_hip[0] - right_hip[0])
        
        # Estimate height (head to ankle)
        nose = self._get_landmark_coords(landmarks, 0, w, h)  # NOSE
        avg_ankle_y = (left_ankle[1] + right_ankle[1]) / 2
        body_height_pixels = avg_ankle_y - nose[1]
        
        self.calibration_data.update({
            'shoulder_width': shoulder_width,
            'hip_width': hip_width,
            'body_height_pixels': body_height_pixels,
            'frame_dimensions': (w, h)
        })
        
        return {
            'success': True,
            'step': 2,
            'instruction': 'Great! Now extend both arms out to your sides (T-pose)',
            'next_action': 'capture_t_pose'
        }
    
    def capture_t_pose(self, landmarks, frame_dimensions: Tuple[int, int]) -> Dict:
        """Capture T-pose for arm span measurement"""
        if not landmarks:
            return {'success': False, 'message': 'No pose detected'}
        
        w, h = frame_dimensions
        
        left_wrist = self._get_landmark_coords(landmarks, 15, w, h)  # LEFT_WRIST
        right_wrist = self._get_landmark_coords(landmarks, 16, w, h)  # RIGHT_WRIST
        left_shoulder = self._get_landmark_coords(landmarks, 11, w, h)  # LEFT_SHOULDER
        right_shoulder = self._get_landmark_coords(landmarks, 12, w, h)  # RIGHT_SHOULDER
        
        # Check if arms are properly extended
        left_arm_extended = abs(left_wrist[1] - left_shoulder[1]) < 50  # Arms should be level
        right_arm_extended = abs(right_wrist[1] - right_shoulder[1]) < 50
        
        if not (left_arm_extended and right_arm_extended):
            return {
                'success': False,
                'message': 'Please extend both arms out to your sides parallel to the ground'
            }
        
        arm_span = abs(left_wrist[0] - right_wrist[0])
        self.calibration_data['arm_span'] = arm_span
        
        return {
            'success': True,
            'step': 3,
            'instruction': 'Perfect! Now perform your best front stance',
            'next_action': 'capture_front_stance'
        }
    
    def capture_front_stance(self, landmarks, frame_dimensions: Tuple[int, int]) -> Dict:
        """Capture user's front stance for stance calibration"""
        if not landmarks:
            return {'success': False, 'message': 'No pose detected'}
        
        w, h = frame_dimensions
        
        left_ankle = self._get_landmark_coords(landmarks, 27, w, h)
        right_ankle = self._get_landmark_coords(landmarks, 28, w, h)
        left_knee = self._get_landmark_coords(landmarks, 25, w, h)
        right_knee = self._get_landmark_coords(landmarks, 26, w, h)
        
        stance_width = abs(left_ankle[0] - right_ankle[0])
        stance_length = abs(left_ankle[1] - right_ankle[1])
        
        # Determine which leg is forward
        front_leg = 'left' if left_ankle[1] > right_ankle[1] else 'right'
        
        self.calibration_data['stance_preferences'] = {
            'front_stance_width': stance_width,
            'front_stance_length': stance_length,
            'preferred_front_leg': front_leg
        }
        
        return {
            'success': True,
            'step': 4,
            'instruction': 'Excellent! Calibration complete.',
            'next_action': 'finalize_calibration'
        }
    
    def finalize_calibration(self) -> Dict:
        """Finalize and save calibration data"""
        self.calibration_data['calibrated'] = True
        
        # Calculate relative measurements for better pose analysis
        if 'shoulder_width' in self.calibration_data and 'body_height_pixels' in self.calibration_data:
            shoulder_to_height_ratio = self.calibration_data['shoulder_width'] / self.calibration_data['body_height_pixels']
            self.calibration_data['shoulder_to_height_ratio'] = shoulder_to_height_ratio
        
        self.save_calibration()
        
        return {
            'success': True,
            'message': 'Calibration completed successfully! Your personalized training is ready.',
            'calibration_summary': self._get_calibration_summary()
        }
    
    def _get_calibration_summary(self) -> Dict:
        """Get a summary of calibration data"""
        return {
            'shoulder_width': f"{self.calibration_data.get('shoulder_width', 0):.0f} pixels",
            'arm_span': f"{self.calibration_data.get('arm_span', 0):.0f} pixels",
            'preferred_front_leg': self.calibration_data.get('stance_preferences', {}).get('preferred_front_leg', 'unknown'),
            'stance_width': f"{self.calibration_data.get('stance_preferences', {}).get('front_stance_width', 0):.0f} pixels"
        }
    
    def _get_landmark_coords(self, landmarks, landmark_id: int, w: int, h: int) -> Tuple[int, int]:
        """Get pixel coordinates of a landmark"""
        landmark = landmarks.landmark[landmark_id]
        return (int(landmark.x * w), int(landmark.y * h))
    
    def is_calibrated(self) -> bool:
        """Check if user has completed calibration"""
        return self.calibration_data.get('calibrated', False)
    
    def get_calibration_data(self) -> Dict:
        """Get current calibration data"""
        return self.calibration_data.copy()
    
    def save_calibration(self):
        """Save calibration data to file"""
        try:
            with open(self.calibration_file, 'w') as f:
                json.dump(self.calibration_data, f, indent=2)
        except Exception as e:
            print(f"Error saving calibration: {e}")
    
    def load_calibration(self):
        """Load calibration data from file"""
        try:
            if os.path.exists(self.calibration_file):
                with open(self.calibration_file, 'r') as f:
                    loaded_data = json.load(f)
                    self.calibration_data.update(loaded_data)
        except Exception as e:
            print(f"Error loading calibration: {e}")
    
    def reset_calibration(self):
        """Reset calibration data"""
        self.calibration_data = {
            'user_height': None,
            'shoulder_width': None,
            'arm_span': None,
            'leg_length': None,
            'stance_preferences': {},
            'calibrated': False
        }
        if os.path.exists(self.calibration_file):
            os.remove(self.calibration_file)
    
    def get_personalized_feedback_thresholds(self) -> Dict:
        """Get personalized thresholds based on calibration data"""
        if not self.is_calibrated():
            return self._get_default_thresholds()
        
        # Adjust thresholds based on user's body proportions
        shoulder_width = self.calibration_data.get('shoulder_width', 100)
        
        return {
            'stance_width_min': shoulder_width * 0.8,
            'stance_width_max': shoulder_width * 1.5,
            'shoulder_alignment_threshold': shoulder_width * 0.1,
            'knee_alignment_threshold': shoulder_width * 0.15,
            'balance_threshold': shoulder_width * 0.2
        }
    
    def _get_default_thresholds(self) -> Dict:
        """Get default thresholds for non-calibrated users"""
        return {
            'stance_width_min': 80,
            'stance_width_max': 150,
            'shoulder_alignment_threshold': 20,
            'knee_alignment_threshold': 30,
            'balance_threshold': 40
        }