import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, List, Tuple, Optional
import time

class OptimizedPoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Initialize MediaPipe Pose with optimized settings
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=0,  # Use lightest model for speed
            enable_segmentation=False,
            smooth_landmarks=True,
            min_detection_confidence=0.3,  # Lower threshold for better detection
            min_tracking_confidence=0.3   # Lower threshold for continuous tracking
        )
        
        self.landmarks = None
        self.world_landmarks = None
        self.last_detection_time = 0
        self.detection_fps = 0
        self.detection_count = 0
        self.last_fps_calc_time = time.time()
        
        # Cache for performance
        self.last_valid_landmarks = None
        self.frames_without_detection = 0
        self.max_frames_without_detection = 10
        
    def process_frame(self, frame: np.ndarray) -> Dict:
        """Process a single frame and detect pose"""
        start_time = time.time()
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.pose.process(rgb_frame)
        
        # Prepare analysis results
        analysis = {
            'pose_detected': False,
            'landmarks': None,
            'world_landmarks': None,
            'visibility_score': 0.0,
            'detection_confidence': 0.0,
            'body_parts': {},
            'angles': {},
            'feedback': []
        }
        
        if results.pose_landmarks:
            self.landmarks = results.pose_landmarks
            self.world_landmarks = results.pose_world_landmarks
            self.last_valid_landmarks = self.landmarks
            self.frames_without_detection = 0
            
            # Calculate visibility score
            visibility_score = self._calculate_visibility_score(self.landmarks)
            
            if visibility_score > 0.3:  # Lower threshold for detection
                analysis['pose_detected'] = True
                analysis['landmarks'] = self.landmarks
                analysis['world_landmarks'] = self.world_landmarks
                analysis['visibility_score'] = visibility_score
                analysis['detection_confidence'] = self._calculate_confidence(self.landmarks)
                
                # Extract body part positions
                analysis['body_parts'] = self._extract_body_parts(self.landmarks, frame.shape)
                
                # Calculate key angles
                analysis['angles'] = self._calculate_key_angles(analysis['body_parts'])
                
                # Generate feedback
                analysis['feedback'] = self._generate_feedback(analysis['angles'], analysis['body_parts'])
            else:
                analysis['feedback'].append("Move closer or ensure full body is visible")
        else:
            self.frames_without_detection += 1
            
            # Use last valid landmarks if recent
            if self.last_valid_landmarks and self.frames_without_detection < self.max_frames_without_detection:
                analysis['pose_detected'] = True
                analysis['landmarks'] = self.last_valid_landmarks
                analysis['visibility_score'] = 0.3
                analysis['feedback'].append("Tracking last known position")
        
        # Calculate detection FPS
        self.detection_count += 1
        current_time = time.time()
        if current_time - self.last_fps_calc_time > 1.0:
            self.detection_fps = self.detection_count / (current_time - self.last_fps_calc_time)
            self.detection_count = 0
            self.last_fps_calc_time = current_time
        
        # Add processing time to analysis
        analysis['processing_time'] = time.time() - start_time
        analysis['detection_fps'] = self.detection_fps
        
        return analysis
    
    def _calculate_visibility_score(self, landmarks) -> float:
        """Calculate overall visibility of key body parts"""
        key_points = [
            self.mp_pose.PoseLandmark.NOSE,
            self.mp_pose.PoseLandmark.LEFT_SHOULDER,
            self.mp_pose.PoseLandmark.RIGHT_SHOULDER,
            self.mp_pose.PoseLandmark.LEFT_ELBOW,
            self.mp_pose.PoseLandmark.RIGHT_ELBOW,
            self.mp_pose.PoseLandmark.LEFT_WRIST,
            self.mp_pose.PoseLandmark.RIGHT_WRIST,
            self.mp_pose.PoseLandmark.LEFT_HIP,
            self.mp_pose.PoseLandmark.RIGHT_HIP,
            self.mp_pose.PoseLandmark.LEFT_KNEE,
            self.mp_pose.PoseLandmark.RIGHT_KNEE,
            self.mp_pose.PoseLandmark.LEFT_ANKLE,
            self.mp_pose.PoseLandmark.RIGHT_ANKLE
        ]
        
        total_visibility = 0
        for point in key_points:
            landmark = landmarks.landmark[point]
            total_visibility += landmark.visibility
        
        return total_visibility / len(key_points)
    
    def _calculate_confidence(self, landmarks) -> float:
        """Calculate overall detection confidence"""
        total_confidence = 0
        count = 0
        
        for landmark in landmarks.landmark:
            if landmark.visibility > 0.5:
                total_confidence += landmark.visibility
                count += 1
        
        return total_confidence / count if count > 0 else 0
    
    def _extract_body_parts(self, landmarks, frame_shape) -> Dict:
        """Extract key body part positions"""
        h, w = frame_shape[:2]
        body_parts = {}
        
        # Define body part mappings
        part_mappings = {
            'nose': self.mp_pose.PoseLandmark.NOSE,
            'left_shoulder': self.mp_pose.PoseLandmark.LEFT_SHOULDER,
            'right_shoulder': self.mp_pose.PoseLandmark.RIGHT_SHOULDER,
            'left_elbow': self.mp_pose.PoseLandmark.LEFT_ELBOW,
            'right_elbow': self.mp_pose.PoseLandmark.RIGHT_ELBOW,
            'left_wrist': self.mp_pose.PoseLandmark.LEFT_WRIST,
            'right_wrist': self.mp_pose.PoseLandmark.RIGHT_WRIST,
            'left_hip': self.mp_pose.PoseLandmark.LEFT_HIP,
            'right_hip': self.mp_pose.PoseLandmark.RIGHT_HIP,
            'left_knee': self.mp_pose.PoseLandmark.LEFT_KNEE,
            'right_knee': self.mp_pose.PoseLandmark.RIGHT_KNEE,
            'left_ankle': self.mp_pose.PoseLandmark.LEFT_ANKLE,
            'right_ankle': self.mp_pose.PoseLandmark.RIGHT_ANKLE,
            'left_heel': self.mp_pose.PoseLandmark.LEFT_HEEL,
            'right_heel': self.mp_pose.PoseLandmark.RIGHT_HEEL,
            'left_foot': self.mp_pose.PoseLandmark.LEFT_FOOT_INDEX,
            'right_foot': self.mp_pose.PoseLandmark.RIGHT_FOOT_INDEX
        }
        
        for name, landmark_id in part_mappings.items():
            landmark = landmarks.landmark[landmark_id]
            if landmark.visibility > 0.3:
                body_parts[name] = {
                    'x': int(landmark.x * w),
                    'y': int(landmark.y * h),
                    'z': landmark.z,
                    'visibility': landmark.visibility
                }
        
        return body_parts
    
    def _calculate_angle(self, p1: Dict, p2: Dict, p3: Dict) -> float:
        """Calculate angle between three points"""
        if not all([p1, p2, p3]):
            return 0
        
        # Create vectors
        v1 = np.array([p1['x'] - p2['x'], p1['y'] - p2['y']])
        v2 = np.array([p3['x'] - p2['x'], p3['y'] - p2['y']])
        
        # Calculate angle
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
        
        return np.degrees(angle)
    
    def _calculate_key_angles(self, body_parts: Dict) -> Dict:
        """Calculate important angles for movement analysis"""
        angles = {}
        
        # Left arm angle
        if all(k in body_parts for k in ['left_shoulder', 'left_elbow', 'left_wrist']):
            angles['left_elbow'] = self._calculate_angle(
                body_parts['left_shoulder'],
                body_parts['left_elbow'],
                body_parts['left_wrist']
            )
        
        # Right arm angle
        if all(k in body_parts for k in ['right_shoulder', 'right_elbow', 'right_wrist']):
            angles['right_elbow'] = self._calculate_angle(
                body_parts['right_shoulder'],
                body_parts['right_elbow'],
                body_parts['right_wrist']
            )
        
        # Left knee angle
        if all(k in body_parts for k in ['left_hip', 'left_knee', 'left_ankle']):
            angles['left_knee'] = self._calculate_angle(
                body_parts['left_hip'],
                body_parts['left_knee'],
                body_parts['left_ankle']
            )
        
        # Right knee angle
        if all(k in body_parts for k in ['right_hip', 'right_knee', 'right_ankle']):
            angles['right_knee'] = self._calculate_angle(
                body_parts['right_hip'],
                body_parts['right_knee'],
                body_parts['right_ankle']
            )
        
        # Hip angle (for kicks)
        if all(k in body_parts for k in ['left_shoulder', 'left_hip', 'left_knee']):
            angles['left_hip'] = self._calculate_angle(
                body_parts['left_shoulder'],
                body_parts['left_hip'],
                body_parts['left_knee']
            )
        
        if all(k in body_parts for k in ['right_shoulder', 'right_hip', 'right_knee']):
            angles['right_hip'] = self._calculate_angle(
                body_parts['right_shoulder'],
                body_parts['right_hip'],
                body_parts['right_knee']
            )
        
        return angles
    
    def _generate_feedback(self, angles: Dict, body_parts: Dict) -> List[str]:
        """Generate movement feedback based on detected pose"""
        feedback = []
        
        # Check stance width
        if 'left_ankle' in body_parts and 'right_ankle' in body_parts:
            stance_width = abs(body_parts['left_ankle']['x'] - body_parts['right_ankle']['x'])
            if stance_width < 100:
                feedback.append("Widen your stance")
            elif stance_width > 300:
                feedback.append("Narrow your stance slightly")
        
        # Check knee angles for squats/stances
        if 'left_knee' in angles:
            if angles['left_knee'] < 70:
                feedback.append("Left knee bent too much")
            elif angles['left_knee'] > 170:
                feedback.append("Bend left knee more")
        
        if 'right_knee' in angles:
            if angles['right_knee'] < 70:
                feedback.append("Right knee bent too much")
            elif angles['right_knee'] > 170:
                feedback.append("Bend right knee more")
        
        # Check arm positions
        if 'left_elbow' in angles and 'right_elbow' in angles:
            if angles['left_elbow'] < 90 or angles['right_elbow'] < 90:
                feedback.append("Keep arms in guard position")
        
        # Check shoulder alignment
        if 'left_shoulder' in body_parts and 'right_shoulder' in body_parts:
            shoulder_diff = abs(body_parts['left_shoulder']['y'] - body_parts['right_shoulder']['y'])
            if shoulder_diff > 30:
                feedback.append("Level your shoulders")
        
        # Positive feedback if pose looks good
        if len(feedback) == 0:
            feedback.append("Good form! Keep it up!")
        
        return feedback
    
    def draw_landmarks(self, frame: np.ndarray, landmarks) -> np.ndarray:
        """Draw pose landmarks on frame"""
        if landmarks:
            # Use MediaPipe's optimized drawing
            self.mp_drawing.draw_landmarks(
                frame,
                landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )
        return frame
    
    def draw_analysis(self, frame: np.ndarray, analysis: Dict) -> np.ndarray:
        """Draw analysis results on frame"""
        if not analysis['pose_detected']:
            return frame
        
        # Draw landmarks
        if analysis['landmarks']:
            frame = self.draw_landmarks(frame, analysis['landmarks'])
        
        # Draw body part labels and angles
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Draw angles on joints
        for angle_name, angle_value in analysis['angles'].items():
            if angle_name in ['left_knee', 'right_knee', 'left_elbow', 'right_elbow']:
                joint_name = angle_name.replace('_', ' ').title()
                body_part_key = angle_name.replace('_knee', '_knee').replace('_elbow', '_elbow')
                
                if body_part_key in analysis['body_parts']:
                    pos = analysis['body_parts'][body_part_key]
                    cv2.putText(frame, f"{int(angle_value)}°", 
                              (pos['x'] + 10, pos['y'] - 10),
                              font, 0.5, (0, 255, 0), 2)
        
        # Draw feedback
        y_offset = 30
        for feedback_text in analysis['feedback'][:3]:  # Show top 3 feedback items
            cv2.putText(frame, feedback_text, (10, y_offset),
                       font, 0.6, (0, 255, 255), 2)
            y_offset += 25
        
        # Draw stats
        cv2.putText(frame, f"Detection FPS: {analysis['detection_fps']:.1f}", 
                   (frame.shape[1] - 150, 30),
                   font, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Confidence: {analysis['detection_confidence']:.0%}", 
                   (frame.shape[1] - 150, 50),
                   font, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def close(self):
        """Clean up resources"""
        if self.pose:
            self.pose.close()