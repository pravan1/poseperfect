import numpy as np
import math
from typing import Dict, List, Optional


def compare_pose(user_landmarks, ref_landmarks, joints_config=None) -> dict:
    """
    Compare user pose with reference pose and return detailed feedback.

    Returns:
      {
        "score": float,          # 0-100
        "per_joint": { "left_elbow": {"delta_deg": 12.3, "advice": "Raise left elbow 10°"}, ... },
        "symmetry": float,       # 0-100
        "alignment": float,      # 0-100
        "top_tips": [ "Open lats", "Straighten wrists", ... ]
      }
    """
    if not user_landmarks or not ref_landmarks:
        return {
            "score": 0,
            "per_joint": {},
            "symmetry": 0,
            "alignment": 0,
            "top_tips": ["Cannot detect pose clearly. Ensure full body is visible."]
        }

    # Use default joints config if not provided
    if joints_config is None:
        joints_config = PoseComparator.POSE_KEY_ANGLES.get('Front Double Biceps', [])

    per_joint = {}
    angle_differences = []
    tips = []

    # Calculate joint angle differences
    for angle_joints in joints_config:
        joint1_idx = PoseComparator.POSE_LANDMARKS[angle_joints[0]]
        joint2_idx = PoseComparator.POSE_LANDMARKS[angle_joints[1]]
        joint3_idx = PoseComparator.POSE_LANDMARKS[angle_joints[2]]

        user_angle = PoseComparator.calculate_angle(
            user_landmarks[joint1_idx],
            user_landmarks[joint2_idx],
            user_landmarks[joint3_idx]
        )

        ref_angle = PoseComparator.calculate_angle(
            ref_landmarks[joint1_idx],
            ref_landmarks[joint2_idx],
            ref_landmarks[joint3_idx]
        )

        delta = user_angle - ref_angle
        angle_differences.append(abs(delta))

        # Generate advice for this joint
        joint_name = angle_joints[1]
        advice = _generate_joint_advice(joint_name, delta)

        per_joint[joint_name] = {
            "delta_deg": round(delta, 1),
            "advice": advice
        }

        # Add to tips if significant deviation
        if abs(delta) > 10:
            tips.append(advice)

    # Calculate scores
    alignment = max(0, 100 - np.mean(angle_differences) * 2)
    symmetry = PoseComparator.calculate_symmetry(user_landmarks)
    overall_score = (alignment * 0.7 + symmetry * 0.3)

    # Add symmetry tip if needed
    if symmetry < 80:
        tips.append("Balance left and right sides")

    # Limit to top 3 tips
    top_tips = tips[:3] if tips else ["Great form!"]

    return {
        "score": round(overall_score, 1),
        "per_joint": per_joint,
        "symmetry": round(symmetry, 1),
        "alignment": round(alignment, 1),
        "top_tips": top_tips
    }


def _generate_joint_advice(joint_name: str, delta_deg: float) -> str:
    """
    Generate specific advice for a joint based on angle delta.

    Args:
        joint_name: Name of the joint (e.g., "left_elbow")
        delta_deg: Angle difference (positive = user angle is larger)

    Returns:
        Human-readable advice string
    """
    # Round to nearest 5 degrees for cleaner advice
    delta_rounded = int(round(abs(delta_deg) / 5) * 5)

    if abs(delta_deg) < 5:
        return f"Perfect {joint_name.replace('_', ' ')}"

    joint_display = joint_name.replace('_', ' ')

    # Determine direction based on joint type and delta sign
    if 'elbow' in joint_name or 'knee' in joint_name:
        # For elbows and knees, positive delta means more bent
        if delta_deg > 0:
            action = "Straighten"
        else:
            action = "Bend"
    elif 'shoulder' in joint_name or 'hip' in joint_name:
        # For shoulders/hips, direction depends on context
        if delta_deg > 0:
            action = "Lower"
        else:
            action = "Raise"
    elif 'wrist' in joint_name or 'ankle' in joint_name:
        if delta_deg > 0:
            action = "Adjust down"
        else:
            action = "Adjust up"
    else:
        action = "Adjust"

    return f"{action} {joint_display} {delta_rounded}°"


class PoseComparator:
    """Compare live poses with reference poses for bodybuilding training"""
    
    # MediaPipe pose landmark indices
    POSE_LANDMARKS = {
        'nose': 0,
        'left_eye': 2,
        'right_eye': 5,
        'left_ear': 7,
        'right_ear': 8,
        'left_shoulder': 11,
        'right_shoulder': 12,
        'left_elbow': 13,
        'right_elbow': 14,
        'left_wrist': 15,
        'right_wrist': 16,
        'left_hip': 23,
        'right_hip': 24,
        'left_knee': 25,
        'right_knee': 26,
        'left_ankle': 27,
        'right_ankle': 28
    }
    
    # Key angles for each bodybuilding pose
    POSE_KEY_ANGLES = {
        'Front Double Biceps': [
            ('left_shoulder', 'left_elbow', 'left_wrist'),
            ('right_shoulder', 'right_elbow', 'right_wrist'),
            ('left_hip', 'left_shoulder', 'left_elbow'),
            ('right_hip', 'right_shoulder', 'right_elbow')
        ],
        'Side Chest': [
            ('left_shoulder', 'left_elbow', 'left_wrist'),
            ('left_hip', 'left_shoulder', 'left_elbow'),
            ('left_hip', 'left_knee', 'left_ankle')
        ],
        'Back Lat Spread': [
            ('left_shoulder', 'left_elbow', 'left_wrist'),
            ('right_shoulder', 'right_elbow', 'right_wrist'),
            ('left_hip', 'left_shoulder', 'left_elbow'),
            ('right_hip', 'right_shoulder', 'right_elbow')
        ],
        'Rear Double Biceps': [
            ('left_shoulder', 'left_elbow', 'left_wrist'),
            ('right_shoulder', 'right_elbow', 'right_wrist'),
            ('left_hip', 'left_knee', 'left_ankle'),
            ('right_hip', 'right_knee', 'right_ankle')
        ]
    }
    
    @staticmethod
    def calculate_angle(point1, point2, point3):
        """Calculate angle between three points"""
        v1 = np.array([point1['x'] - point2['x'], point1['y'] - point2['y']])
        v2 = np.array([point3['x'] - point2['x'], point3['y'] - point2['y']])
        
        cosine_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
        
        return np.degrees(angle)
    
    @staticmethod
    def calculate_symmetry(landmarks):
        """Calculate body symmetry score"""
        if not landmarks:
            return 0
        
        symmetry_scores = []
        
        # Compare arm positions
        left_arm_angle = PoseComparator.calculate_angle(
            landmarks[PoseComparator.POSE_LANDMARKS['left_shoulder']],
            landmarks[PoseComparator.POSE_LANDMARKS['left_elbow']],
            landmarks[PoseComparator.POSE_LANDMARKS['left_wrist']]
        )
        right_arm_angle = PoseComparator.calculate_angle(
            landmarks[PoseComparator.POSE_LANDMARKS['right_shoulder']],
            landmarks[PoseComparator.POSE_LANDMARKS['right_elbow']],
            landmarks[PoseComparator.POSE_LANDMARKS['right_wrist']]
        )
        arm_symmetry = max(0, 100 - abs(left_arm_angle - right_arm_angle))
        symmetry_scores.append(arm_symmetry)
        
        # Compare leg positions
        left_leg_angle = PoseComparator.calculate_angle(
            landmarks[PoseComparator.POSE_LANDMARKS['left_hip']],
            landmarks[PoseComparator.POSE_LANDMARKS['left_knee']],
            landmarks[PoseComparator.POSE_LANDMARKS['left_ankle']]
        )
        right_leg_angle = PoseComparator.calculate_angle(
            landmarks[PoseComparator.POSE_LANDMARKS['right_hip']],
            landmarks[PoseComparator.POSE_LANDMARKS['right_knee']],
            landmarks[PoseComparator.POSE_LANDMARKS['right_ankle']]
        )
        leg_symmetry = max(0, 100 - abs(left_leg_angle - right_leg_angle))
        symmetry_scores.append(leg_symmetry)
        
        # Compare shoulder heights
        left_shoulder_y = landmarks[PoseComparator.POSE_LANDMARKS['left_shoulder']]['y']
        right_shoulder_y = landmarks[PoseComparator.POSE_LANDMARKS['right_shoulder']]['y']
        shoulder_symmetry = max(0, 100 - abs(left_shoulder_y - right_shoulder_y) * 500)
        symmetry_scores.append(shoulder_symmetry)
        
        return np.mean(symmetry_scores)
    
    @staticmethod
    def compare_poses(live_landmarks, reference_landmarks, pose_mode):
        """Compare live pose with reference pose"""
        if not live_landmarks or not reference_landmarks:
            return {
                'overall_score': 0,
                'symmetry_score': 0,
                'alignment_score': 0,
                'feedback': ['Cannot detect pose clearly'],
                'joint_errors': []
            }
        
        # Get key angles for the specific pose
        key_angles = PoseComparator.POSE_KEY_ANGLES.get(pose_mode, [])
        angle_differences = []
        joint_errors = []
        feedback = []
        
        for angle_joints in key_angles:
            # Get joint indices
            joint1_idx = PoseComparator.POSE_LANDMARKS[angle_joints[0]]
            joint2_idx = PoseComparator.POSE_LANDMARKS[angle_joints[1]]
            joint3_idx = PoseComparator.POSE_LANDMARKS[angle_joints[2]]
            
            # Calculate angles for live and reference
            live_angle = PoseComparator.calculate_angle(
                live_landmarks[joint1_idx],
                live_landmarks[joint2_idx],
                live_landmarks[joint3_idx]
            )
            
            ref_angle = PoseComparator.calculate_angle(
                reference_landmarks[joint1_idx],
                reference_landmarks[joint2_idx],
                reference_landmarks[joint3_idx]
            )
            
            angle_diff = abs(live_angle - ref_angle)
            angle_differences.append(angle_diff)
            
            # Store joint errors for visualization
            if angle_diff > 10:
                joint_errors.append({
                    'joint': angle_joints[1],
                    'error': angle_diff,
                    'position': (
                        live_landmarks[joint2_idx]['x'] * 640,
                        live_landmarks[joint2_idx]['y'] * 480
                    )
                })
                
                # Generate specific feedback
                if angle_diff > 20:
                    if live_angle > ref_angle:
                        feedback.append(f"Decrease {angle_joints[1].replace('_', ' ')} angle")
                    else:
                        feedback.append(f"Increase {angle_joints[1].replace('_', ' ')} angle")
        
        # Calculate scores
        alignment_score = max(0, 100 - np.mean(angle_differences) * 2)
        symmetry_score = PoseComparator.calculate_symmetry(live_landmarks)
        overall_score = (alignment_score * 0.7 + symmetry_score * 0.3)
        
        # Add pose-specific feedback
        if pose_mode == "Front Double Biceps":
            if alignment_score < 70:
                feedback.append("Raise arms to shoulder level")
                feedback.append("Flex biceps harder")
        elif pose_mode == "Side Chest":
            if alignment_score < 70:
                feedback.append("Turn torso more to the side")
                feedback.append("Bring front arm across chest")
        elif pose_mode == "Back Lat Spread":
            if alignment_score < 70:
                feedback.append("Spread lats wider")
                feedback.append("Keep elbows forward")
        elif pose_mode == "Rear Double Biceps":
            if alignment_score < 70:
                feedback.append("Flex calves")
                feedback.append("Squeeze shoulder blades together")
        
        # Add symmetry feedback
        if symmetry_score < 80:
            feedback.append("Improve left-right symmetry")
        
        return {
            'overall_score': overall_score,
            'symmetry_score': symmetry_score,
            'alignment_score': alignment_score,
            'feedback': feedback[:3],  # Limit to top 3 feedback items
            'joint_errors': joint_errors
        }