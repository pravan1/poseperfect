import cv2
import numpy as np
from typing import Dict, List, Tuple


def draw_feedback_overlay(image: np.ndarray, per_joint_feedback: Dict) -> np.ndarray:
    """
    Draw feedback overlay on captured user image showing joint deviations.

    Args:
        image: BGR image (numpy array)
        per_joint_feedback: Dict with joint names as keys and feedback dicts as values
                          e.g., {"left_elbow": {"delta_deg": 12.3, "advice": "Raise left elbow 10°"}}

    Returns:
        Annotated image with feedback overlays
    """
    overlay = image.copy()
    height, width = image.shape[:2]

    # Define landmark positions (approximate, should be passed from actual landmarks)
    # For now, we'll just add text overlays

    # Add semi-transparent overlay for text background
    overlay_bg = image.copy()

    y_offset = 30
    for joint_name, feedback in per_joint_feedback.items():
        if 'delta_deg' not in feedback:
            continue

        delta = feedback['delta_deg']
        advice = feedback.get('advice', '')

        # Color based on severity
        if abs(delta) > 15:
            color = (0, 0, 255)  # Red for large deviations
        elif abs(delta) > 10:
            color = (0, 165, 255)  # Orange for moderate
        else:
            color = (0, 255, 255)  # Yellow for small

        # Draw text
        text = f"{joint_name.replace('_', ' ').title()}: {abs(delta):.0f}°"
        cv2.putText(overlay, text, (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        y_offset += 25

    return overlay


def draw_joint_badges(image: np.ndarray, landmarks: List, joint_issues: Dict) -> np.ndarray:
    """
    Draw numbered badges on joints that need attention.

    Args:
        image: BGR image
        landmarks: List of landmark dicts with x, y coordinates
        joint_issues: Dict mapping joint indices to issue severity (0-3)

    Returns:
        Image with joint badges
    """
    overlay = image.copy()
    height, width = image.shape[:2]

    for joint_idx, severity in joint_issues.items():
        if joint_idx >= len(landmarks):
            continue

        lm = landmarks[joint_idx]
        x = int(lm['x'] * width) if lm['x'] <= 1 else int(lm['x'])
        y = int(lm['y'] * height) if lm['y'] <= 1 else int(lm['y'])

        # Color based on severity
        colors = {
            0: (0, 255, 0),    # Green - good
            1: (0, 255, 255),  # Yellow - minor issue
            2: (0, 165, 255),  # Orange - moderate issue
            3: (0, 0, 255)     # Red - major issue
        }
        color = colors.get(severity, (128, 128, 128))

        # Draw circle badge
        cv2.circle(overlay, (x, y), 12, color, -1)
        cv2.circle(overlay, (x, y), 12, (255, 255, 255), 2)

        # Draw issue number
        cv2.putText(overlay, str(severity), (x-5, y+5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

    return overlay


def draw_delta_arrows(image: np.ndarray, landmarks: List, joint_deltas: Dict) -> np.ndarray:
    """
    Draw directional arrows showing how to adjust joints.

    Args:
        image: BGR image
        landmarks: List of landmark dicts
        joint_deltas: Dict mapping joint names to movement vectors
                     e.g., {"left_elbow": {"direction": "up", "magnitude": 15}}

    Returns:
        Image with directional arrows
    """
    overlay = image.copy()
    height, width = image.shape[:2]

    # Map joint names to landmark indices (MediaPipe pose)
    joint_map = {
        'left_shoulder': 11, 'right_shoulder': 12,
        'left_elbow': 13, 'right_elbow': 14,
        'left_wrist': 15, 'right_wrist': 16,
        'left_hip': 23, 'right_hip': 24,
        'left_knee': 25, 'right_knee': 26,
        'left_ankle': 27, 'right_ankle': 28
    }

    for joint_name, delta_info in joint_deltas.items():
        if joint_name not in joint_map:
            continue

        joint_idx = joint_map[joint_name]
        if joint_idx >= len(landmarks):
            continue

        lm = landmarks[joint_idx]
        x = int(lm['x'] * width) if lm['x'] <= 1 else int(lm['x'])
        y = int(lm['y'] * height) if lm['y'] <= 1 else int(lm['y'])

        # Determine arrow direction and endpoint
        direction = delta_info.get('direction', 'up')
        magnitude = min(delta_info.get('magnitude', 20), 50)  # Cap at 50 pixels

        if direction == 'up':
            end_pt = (x, y - magnitude)
        elif direction == 'down':
            end_pt = (x, y + magnitude)
        elif direction == 'left':
            end_pt = (x - magnitude, y)
        elif direction == 'right':
            end_pt = (x + magnitude, y)
        else:
            continue

        # Draw arrow
        cv2.arrowedLine(overlay, (x, y), end_pt, (255, 255, 0), 3, tipLength=0.3)

    return overlay


def create_side_by_side_comparison(ref_image: np.ndarray, user_image: np.ndarray,
                                   labels: Tuple[str, str] = ("Reference", "You")) -> np.ndarray:
    """
    Create side-by-side comparison image.

    Args:
        ref_image: Reference pose image
        user_image: User's captured image
        labels: Tuple of (reference_label, user_label)

    Returns:
        Combined side-by-side image
    """
    # Resize both to same height
    target_height = 400

    ref_h, ref_w = ref_image.shape[:2]
    user_h, user_w = user_image.shape[:2]

    ref_aspect = ref_w / ref_h
    user_aspect = user_w / user_h

    ref_resized = cv2.resize(ref_image, (int(target_height * ref_aspect), target_height))
    user_resized = cv2.resize(user_image, (int(target_height * user_aspect), target_height))

    # Add labels
    ref_labeled = ref_resized.copy()
    user_labeled = user_resized.copy()

    cv2.putText(ref_labeled, labels[0], (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
    cv2.putText(user_labeled, labels[1], (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

    # Combine horizontally
    combined = np.hstack([ref_labeled, user_labeled])

    return combined


def make_contact_sheet(session_dir, out_path, pose_names: List[str] = None):
    """
    Create a contact sheet (horizontal strip) of all 4 pose captures.

    Args:
        session_dir: Path to session directory
        out_path: Output file path for contact sheet
        pose_names: Optional list of pose names for labels
    """
    import os
    from pathlib import Path

    session_path = Path(session_dir)

    # Load all pose images
    images = []
    default_names = ["Front Double Biceps", "Side Chest", "Back Lat Spread", "Rear Double Biceps"]
    labels = pose_names or default_names

    for i in range(1, 5):
        img_path = session_path / f"pose{i}_user.jpg"
        if img_path.exists():
            img = cv2.imread(str(img_path))
            if img is not None:
                # Resize to standard height
                h, w = img.shape[:2]
                target_h = 300
                aspect = w / h
                resized = cv2.resize(img, (int(target_h * aspect), target_h))

                # Add label
                label = labels[i-1] if i-1 < len(labels) else f"Pose {i}"
                cv2.putText(resized, label, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

                images.append(resized)

    if not images:
        # Create blank image if no captures
        blank = np.zeros((300, 400, 3), dtype=np.uint8)
        cv2.putText(blank, "No captures", (100, 150),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        cv2.imwrite(str(out_path), blank)
        return

    # Combine horizontally
    contact_sheet = np.hstack(images)
    cv2.imwrite(str(out_path), contact_sheet)
