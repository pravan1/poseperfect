import cv2
import mediapipe as mp
import numpy as np


class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        # Optimized settings for smooth camera performance
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,  # Balanced complexity for good performance
            smooth_landmarks=True,
            enable_segmentation=False,
            smooth_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
    def process_frame(self, frame):
        """Process a frame and extract pose landmarks with optimized performance"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # To improve performance, we can optionally reduce resolution
        # Uncomment if experiencing lag:
        # rgb_frame = cv2.resize(rgb_frame, (640, 480))
        
        results = self.pose.process(rgb_frame)
        
        if results.pose_landmarks:
            landmarks = []
            for landmark in results.pose_landmarks.landmark:
                landmarks.append({
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z,
                    'visibility': landmark.visibility
                })
            return {
                'landmarks': landmarks,
                'world_landmarks': results.pose_world_landmarks,
                'pose_detected': True
            }
        
        return {
            'landmarks': None,
            'world_landmarks': None,
            'pose_detected': False
        }
    
    def draw_pose(self, frame, landmarks):
        """Draw pose landmarks on the frame with optimized rendering"""
        if landmarks is None:
            return frame
            
        # Import the proper MediaPipe landmark format
        from mediapipe.framework.formats import landmark_pb2
        
        # Create proper MediaPipe landmark list
        pose_landmarks = landmark_pb2.NormalizedLandmarkList()
        
        # Convert our landmarks to MediaPipe format
        for lm in landmarks:
            landmark = pose_landmarks.landmark.add()
            landmark.x = lm['x']
            landmark.y = lm['y']
            landmark.z = lm['z']
            landmark.visibility = lm['visibility']
        
        # Draw the pose with thinner lines for better performance
        self.mp_drawing.draw_landmarks(
            frame,
            pose_landmarks,
            self.mp_pose.POSE_CONNECTIONS,
            self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=2),
            self.mp_drawing.DrawingSpec(color=(0, 128, 255), thickness=1, circle_radius=1)
        )
        
        return frame
    
    def draw_comparison_overlay(self, frame, comparison_results):
        """Draw comparison overlay on the frame efficiently"""
        if not comparison_results:
            return frame
            
        height, width = frame.shape[:2]
        
        # Draw error highlights for joints with poor alignment
        if 'joint_errors' in comparison_results:
            for joint_error in comparison_results['joint_errors']:
                x = int(joint_error['position'][0] * width) if joint_error['position'][0] <= 1 else int(joint_error['position'][0])
                y = int(joint_error['position'][1] * height) if joint_error['position'][1] <= 1 else int(joint_error['position'][1])
                
                if joint_error['error'] > 15:  # Poor alignment
                    cv2.circle(frame, (x, y), 8, (0, 0, 255), 2)
                elif joint_error['error'] > 10:  # Moderate alignment
                    cv2.circle(frame, (x, y), 8, (0, 255, 255), 2)
        
        # Draw score overlay
        if 'overall_score' in comparison_results:
            score_text = f"Match: {comparison_results['overall_score']:.1f}%"
            color = (0, 255, 0) if comparison_results['overall_score'] > 80 else (0, 255, 255)
            cv2.putText(frame, score_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Draw symmetry indicator
        if 'symmetry_score' in comparison_results:
            symmetry_text = f"Symmetry: {comparison_results['symmetry_score']:.1f}%"
            color = (0, 255, 0) if comparison_results['symmetry_score'] > 85 else (0, 255, 255)
            cv2.putText(frame, symmetry_text, (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return frame
    
    def get_joint_angle(self, landmarks, joint1_idx, joint2_idx, joint3_idx):
        """Calculate angle between three joints"""
        if not landmarks:
            return None
            
        try:
            joint1 = landmarks[joint1_idx]
            joint2 = landmarks[joint2_idx]
            joint3 = landmarks[joint3_idx]
            
            # Calculate vectors
            v1 = np.array([joint1['x'] - joint2['x'], joint1['y'] - joint2['y']])
            v2 = np.array([joint3['x'] - joint2['x'], joint3['y'] - joint2['y']])
            
            # Calculate angle
            cosine_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
            angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
            
            return np.degrees(angle)
        except:
            return None
    
    def close(self):
        """Release resources"""
        self.pose.close()