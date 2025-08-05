import numpy as np
import math
from typing import Tuple, List, Dict, Optional

def calculate_angle_between_points(point_a: Tuple[float, float], 
                                 point_b: Tuple[float, float], 
                                 point_c: Tuple[float, float]) -> float:
    """
    Calculate angle at point_b formed by points a-b-c
    
    Args:
        point_a: First point (x, y)
        point_b: Vertex point (x, y)
        point_c: Third point (x, y)
    
    Returns:
        Angle in degrees (0-180)
    """
    a = np.array(point_a)
    b = np.array(point_b)
    c = np.array(point_c)
    
    # Create vectors
    ba = a - b
    bc = c - b
    
    # Calculate angle using dot product
    cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    
    # Clamp to valid range to avoid numerical errors
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    
    angle_rad = np.arccos(cos_angle)
    angle_deg = np.degrees(angle_rad)
    
    return angle_deg

def calculate_slope_angle(point_a: Tuple[float, float], 
                         point_b: Tuple[float, float]) -> float:
    """
    Calculate the slope angle of a line between two points
    
    Args:
        point_a: Starting point (x, y)
        point_b: Ending point (x, y)
    
    Returns:
        Angle in degrees (-90 to 90)
    """
    dx = point_b[0] - point_a[0]
    dy = point_b[1] - point_a[1]
    
    if dx == 0:
        return 90.0 if dy > 0 else -90.0
    
    angle_rad = math.atan(dy / dx)
    angle_deg = math.degrees(angle_rad)
    
    return angle_deg

def calculate_distance(point_a: Tuple[float, float], 
                      point_b: Tuple[float, float]) -> float:
    """
    Calculate Euclidean distance between two points
    
    Args:
        point_a: First point (x, y)
        point_b: Second point (x, y)
    
    Returns:
        Distance in pixels
    """
    return math.sqrt((point_b[0] - point_a[0])**2 + (point_b[1] - point_a[1])**2)

def is_point_above(point_a: Tuple[float, float], 
                   point_b: Tuple[float, float], 
                   threshold: float = 0) -> bool:
    """
    Check if point_a is above point_b (considering image coordinate system)
    
    Args:
        point_a: First point (x, y)
        point_b: Second point (x, y)
        threshold: Minimum difference to consider "above"
    
    Returns:
        True if point_a is above point_b
    """
    return point_a[1] < point_b[1] - threshold

def is_point_to_left(point_a: Tuple[float, float], 
                     point_b: Tuple[float, float], 
                     threshold: float = 0) -> bool:
    """
    Check if point_a is to the left of point_b
    
    Args:
        point_a: First point (x, y)
        point_b: Second point (x, y)
        threshold: Minimum difference to consider "to the left"
    
    Returns:
        True if point_a is to the left of point_b
    """
    return point_a[0] < point_b[0] - threshold

def calculate_body_alignment_score(left_shoulder: Tuple[float, float],
                                 right_shoulder: Tuple[float, float],
                                 left_hip: Tuple[float, float],
                                 right_hip: Tuple[float, float]) -> float:
    """
    Calculate body alignment score based on shoulder and hip alignment
    
    Args:
        left_shoulder: Left shoulder coordinates
        right_shoulder: Right shoulder coordinates  
        left_hip: Left hip coordinates
        right_hip: Right hip coordinates
    
    Returns:
        Alignment score (0-100, higher is better)
    """
    # Calculate shoulder alignment
    shoulder_diff = abs(left_shoulder[1] - right_shoulder[1])
    
    # Calculate hip alignment
    hip_diff = abs(left_hip[1] - right_hip[1])
    
    # Calculate shoulder-hip parallelism
    shoulder_slope = calculate_slope_angle(left_shoulder, right_shoulder)
    hip_slope = calculate_slope_angle(left_hip, right_hip)
    slope_diff = abs(shoulder_slope - hip_slope)
    
    # Score components (lower differences = higher scores)
    shoulder_score = max(0, 100 - shoulder_diff * 2)
    hip_score = max(0, 100 - hip_diff * 2)
    parallelism_score = max(0, 100 - slope_diff * 5)
    
    # Weighted average
    total_score = (shoulder_score * 0.4 + hip_score * 0.4 + parallelism_score * 0.2)
    
    return min(100, max(0, total_score))

def calculate_stance_width_score(left_ankle: Tuple[float, float],
                               right_ankle: Tuple[float, float],
                               shoulder_width: float,
                               stance_type: str = 'front') -> float:
    """
    Calculate stance width appropriateness score
    
    Args:
        left_ankle: Left ankle coordinates
        right_ankle: Right ankle coordinates
        shoulder_width: Reference shoulder width
        stance_type: Type of stance ('front', 'horse', 'back')
    
    Returns:
        Width score (0-100, higher is better)
    """
    actual_width = abs(left_ankle[0] - right_ankle[0])
    
    # Ideal width ratios for different stances
    width_ratios = {
        'front': 1.0,    # About shoulder width
        'horse': 1.8,    # About 1.8x shoulder width
        'back': 1.2      # About 1.2x shoulder width
    }
    
    ideal_width = shoulder_width * width_ratios.get(stance_type, 1.0)
    width_diff = abs(actual_width - ideal_width)
    
    # Score decreases with distance from ideal
    score = max(0, 100 - (width_diff / ideal_width) * 100)
    
    return score

def calculate_knee_alignment_score(knee: Tuple[float, float],
                                 ankle: Tuple[float, float],
                                 tolerance: float = 30) -> float:
    """
    Calculate knee-over-ankle alignment score
    
    Args:
        knee: Knee coordinates
        ankle: Ankle coordinates  
        tolerance: Acceptable horizontal deviation in pixels
    
    Returns:
        Alignment score (0-100, higher is better)
    """
    horizontal_diff = abs(knee[0] - ankle[0])
    
    if horizontal_diff <= tolerance:
        score = 100 - (horizontal_diff / tolerance) * 30
    else:
        # Penalty increases more rapidly beyond tolerance
        score = 70 - min(70, (horizontal_diff - tolerance) * 2)
    
    return max(0, score)

def calculate_leg_angle_score(hip: Tuple[float, float],
                            knee: Tuple[float, float],
                            ankle: Tuple[float, float],
                            target_angle: float,
                            tolerance: float = 15) -> float:
    """
    Calculate how close a leg angle is to the target
    
    Args:
        hip: Hip coordinates
        knee: Knee coordinates
        ankle: Ankle coordinates
        target_angle: Target angle in degrees
        tolerance: Acceptable deviation in degrees
    
    Returns:
        Angle score (0-100, higher is better)
    """
    actual_angle = calculate_angle_between_points(hip, knee, ankle)
    angle_diff = abs(actual_angle - target_angle)
    
    if angle_diff <= tolerance:
        score = 100 - (angle_diff / tolerance) * 20
    else:
        # Penalty increases beyond tolerance
        score = 80 - min(80, (angle_diff - tolerance) * 3)
    
    return max(0, score)

def analyze_kick_height(kicking_knee: Tuple[float, float],
                       kicking_hip: Tuple[float, float],
                       target_height: str = 'middle') -> Dict[str, float]:
    """
    Analyze kick height appropriateness
    
    Args:
        kicking_knee: Kicking leg knee coordinates
        kicking_hip: Kicking leg hip coordinates
        target_height: Target height ('low', 'middle', 'high')
    
    Returns:
        Dictionary with height analysis
    """
    knee_hip_diff = kicking_hip[1] - kicking_knee[1]  # Positive = knee above hip
    
    height_thresholds = {
        'low': (-50, 0),      # Knee at or below hip level
        'middle': (0, 80),    # Knee 0-80 pixels above hip
        'high': (80, 150)     # Knee 80-150 pixels above hip
    }
    
    min_thresh, max_thresh = height_thresholds.get(target_height, (0, 80))
    
    if min_thresh <= knee_hip_diff <= max_thresh:
        height_score = 100
        feedback = f"Perfect {target_height} kick height"
    elif knee_hip_diff < min_thresh:
        height_score = max(0, 100 - (min_thresh - knee_hip_diff) * 2)
        feedback = f"Lift knee higher for {target_height} kick"
    else:
        height_score = max(0, 100 - (knee_hip_diff - max_thresh) * 1.5)
        feedback = f"Lower knee slightly for {target_height} kick"
    
    return {
        'height_score': height_score,
        'knee_hip_difference': knee_hip_diff,
        'feedback': feedback,
        'target_height': target_height
    }

def calculate_balance_score(left_shoulder: Tuple[float, float],
                          right_shoulder: Tuple[float, float],
                          left_hip: Tuple[float, float],
                          right_hip: Tuple[float, float],
                          left_ankle: Tuple[float, float],
                          right_ankle: Tuple[float, float]) -> float:
    """
    Calculate overall balance score based on body centerline
    
    Args:
        All major body landmarks
    
    Returns:
        Balance score (0-100, higher is better)
    """
    # Calculate center points
    shoulder_center = ((left_shoulder[0] + right_shoulder[0]) / 2,
                      (left_shoulder[1] + right_shoulder[1]) / 2)
    hip_center = ((left_hip[0] + right_hip[0]) / 2,
                  (left_hip[1] + right_hip[1]) / 2)
    ankle_center = ((left_ankle[0] + right_ankle[0]) / 2,
                   (left_ankle[1] + right_ankle[1]) / 2)
    
    # Calculate vertical alignment of center points
    shoulder_hip_diff = abs(shoulder_center[0] - hip_center[0])
    hip_ankle_diff = abs(hip_center[0] - ankle_center[0])
    
    # Score based on vertical alignment
    alignment_score = max(0, 100 - (shoulder_hip_diff + hip_ankle_diff) * 0.5)
    
    return alignment_score

def get_pose_feedback_from_scores(scores: Dict[str, float]) -> List[str]:
    """
    Generate feedback messages based on pose analysis scores
    
    Args:
        scores: Dictionary of various pose scores
    
    Returns:
        List of feedback messages
    """
    feedback = []
    
    # Alignment feedback
    if scores.get('alignment_score', 0) < 70:
        feedback.append("Work on keeping shoulders and hips aligned")
    elif scores.get('alignment_score', 0) > 85:
        feedback.append("Excellent body alignment!")
    
    # Balance feedback
    if scores.get('balance_score', 0) < 60:
        feedback.append("Focus on maintaining better balance")
    elif scores.get('balance_score', 0) > 80:
        feedback.append("Great balance!")
    
    # Stance width feedback
    if scores.get('stance_width_score', 0) < 70:
        feedback.append("Adjust your stance width")
    elif scores.get('stance_width_score', 0) > 85:
        feedback.append("Perfect stance width!")
    
    # Knee alignment feedback
    if scores.get('knee_alignment_score', 0) < 70:
        feedback.append("Align knees over ankles")
    elif scores.get('knee_alignment_score', 0) > 85:
        feedback.append("Excellent knee alignment!")
    
    return feedback

def normalize_coordinates(landmarks, frame_width: int, frame_height: int) -> Dict[str, Tuple[float, float]]:
    """
    Normalize landmark coordinates and return key body points
    
    Args:
        landmarks: MediaPipe pose landmarks
        frame_width: Frame width in pixels
        frame_height: Frame height in pixels
    
    Returns:
        Dictionary of normalized key body points
    """
    def get_coords(landmark_id):
        landmark = landmarks.landmark[landmark_id]
        return (landmark.x * frame_width, landmark.y * frame_height)
    
    # MediaPipe pose landmark indices
    return {
        'nose': get_coords(0),
        'left_shoulder': get_coords(11),
        'right_shoulder': get_coords(12),
        'left_elbow': get_coords(13),
        'right_elbow': get_coords(14),
        'left_wrist': get_coords(15),
        'right_wrist': get_coords(16),
        'left_hip': get_coords(23),
        'right_hip': get_coords(24),
        'left_knee': get_coords(25),
        'right_knee': get_coords(26),
        'left_ankle': get_coords(27),
        'right_ankle': get_coords(28)
    }