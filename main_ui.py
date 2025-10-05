import sys
import os
import cv2
import json
import numpy as np
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QCheckBox, QStackedWidget,
    QGraphicsDropShadowEffect, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor
from pose_detector import PoseDetector
from pose_comparator import compare_pose, PoseComparator
from voice_feedback import VoiceFeedback
from utils.image_overlay import draw_feedback_overlay, make_contact_sheet


# Stylesheet with Apple-style gradient and card design
APPLE_STYLESHEET = """
* {
    font-family: -apple-system, 'Segoe UI', 'SF Pro Text', Roboto, Arial, sans-serif;
}

QMainWindow {
    background: #1a2332;
}

QWidget#Card {
    background: rgba(255, 255, 255, 0.72);
    border-radius: 22px;
    padding: 18px;
}

QPushButton#Primary {
    background: #2563eb;
    color: white;
    border-radius: 12px;
    padding: 12px 20px;
    font-size: 15px;
    font-weight: 600;
    border: none;
}

QPushButton#Primary:hover {
    background: #1d4ed8;
}

QPushButton#Primary:pressed {
    background: #1e40af;
}

QPushButton#Secondary {
    background: rgba(255, 255, 255, 0.9);
    color: #2563eb;
    border: 2px solid #2563eb;
    border-radius: 12px;
    padding: 10px 18px;
    font-size: 14px;
    font-weight: 500;
}

QPushButton#Secondary:hover {
    background: rgba(37, 99, 235, 0.1);
}

QLabel#Title {
    font-size: 32px;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.2;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

QLabel#Subtitle {
    font-size: 16px;
    color: #64748b;
    line-height: 1.5;
}

QLabel#PoseName {
    font-size: 24px;
    font-weight: 600;
    color: #1e293b;
}

QLabel#CountdownOverlay {
    font-size: 96px;
    font-weight: 700;
    color: white;
    background: rgba(0, 0, 0, 0.6);
    border-radius: 20px;
}

QComboBox {
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
    min-width: 200px;
}

QComboBox:hover {
    border-color: #2563eb;
}

QCheckBox {
    font-size: 14px;
    color: #475569;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid #cbd5e1;
}

QCheckBox::indicator:checked {
    background: #2563eb;
    border-color: #2563eb;
}

QListWidget {
    background: rgba(255, 255, 255, 0.5);
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px;
    font-size: 14px;
}

QListWidget::item {
    padding: 6px;
    border-radius: 4px;
}

QListWidget::item:selected {
    background: rgba(37, 99, 235, 0.1);
    color: #2563eb;
}
"""


class VideoThread(QThread):
    """Thread for capturing live video from webcam"""
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        while self._run_flag:
            ret, frame = cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                self.change_pixmap_signal.emit(frame)

        cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()


class WelcomeScreen(QWidget):
    """Welcome screen with hero gradient and start button"""
    start_session_signal = pyqtSignal(list, bool)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)

        # Logo
        logo_label = QLabel()
        logo_path = "logo_transparent.png" if os.path.exists("logo_transparent.png") else "logo.png"
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            scaled_logo = logo_pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)

        # Subtitle
        subtitle = QLabel("Your AI-powered bodybuilding pose coach")
        subtitle.setObjectName("Subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 16px; color: #ffffff; font-weight: 600; background: rgba(0, 0, 0, 0.3); padding: 8px 16px; border-radius: 8px;")
        layout.addWidget(subtitle)

        # Card container
        card = QWidget()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(20)

        # Pose sequence selector
        sequence_label = QLabel("Pose Sequence:")
        sequence_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #475569;")
        card_layout.addWidget(sequence_label)

        self.pose_combo = QComboBox()
        self.pose_combo.addItem("Classic 4-Pose Flow (Default)")
        card_layout.addWidget(self.pose_combo)

        # Voice guidance toggle
        self.voice_checkbox = QCheckBox("Enable voice guidance")
        self.voice_checkbox.setChecked(True)
        card_layout.addWidget(self.voice_checkbox)

        # Start button
        start_btn = QPushButton("Start Session")
        start_btn.setObjectName("Primary")
        start_btn.setMinimumHeight(50)
        start_btn.clicked.connect(self.start_session)
        card_layout.addWidget(start_btn)

        # Apply shadow to card
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 30))
        card.setGraphicsEffect(shadow)

        layout.addWidget(card)
        layout.addStretch()

    def start_session(self):
        # Default pose sequence
        pose_sequence = [
            {"name": "Back Double Biceps", "ref": "reference_poses/pose1.jpg"},
            {"name": "Front Double Biceps", "ref": "reference_poses/pose2.jpg"},
            {"name": "Side Chest", "ref": "reference_poses/pose3.jpg"},
            {"name": "Back Lat Spread", "ref": "reference_poses/pose4.jpg"},
        ]
        voice_enabled = self.voice_checkbox.isChecked()
        self.start_session_signal.emit(pose_sequence, voice_enabled)


class PoseStepScreen(QWidget):
    """Screen for each pose step with camera, countdown, and feedback"""
    next_pose_signal = pyqtSignal()
    retry_pose_signal = pyqtSignal()

    def __init__(self, pose_data, pose_idx, voice_enabled):
        super().__init__()
        self.pose_data = pose_data
        self.pose_idx = pose_idx
        self.voice_enabled = voice_enabled
        self.pose_detector = PoseDetector()
        self.video_thread = None
        self.countdown_timer = QTimer()
        self.countdown_value = 5
        self.current_frame = None
        self.session_dir = None
        self.captured_image = None
        self.feedback_result = None
        self.required_score = 75.0  # Start at 75%
        self.attempt_count = 0

        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)

        # Left column: Camera feed
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setMaximumSize(640, 480)
        self.camera_label.setScaledContents(False)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("border: 2px solid #e2e8f0; border-radius: 12px; background: black;")
        left_layout.addWidget(self.camera_label)

        # Countdown overlay (initially hidden)
        self.countdown_overlay = QLabel(self.camera_label)
        self.countdown_overlay.setObjectName("CountdownOverlay")
        self.countdown_overlay.setAlignment(Qt.AlignCenter)
        self.countdown_overlay.setGeometry(220, 180, 200, 120)
        self.countdown_overlay.hide()

        main_layout.addWidget(left_panel)

        # Right column: Reference and feedback
        right_panel = QWidget()
        right_panel.setObjectName("Card")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)

        # Pose name
        pose_name_label = QLabel(self.pose_data["name"])
        pose_name_label.setObjectName("PoseName")
        right_layout.addWidget(pose_name_label)

        # Reference or comparison image
        self.ref_label = QLabel()
        self.ref_label.setMinimumSize(400, 300)
        self.ref_label.setMaximumSize(400, 300)
        self.ref_label.setScaledContents(False)
        self.ref_label.setAlignment(Qt.AlignCenter)
        self.ref_label.setStyleSheet("border: 2px solid #e2e8f0; border-radius: 8px;")
        right_layout.addWidget(self.ref_label)

        # Load and display reference image
        self.load_reference_image()

        # Tips text
        tips_label = QLabel("Tips:")
        tips_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #475569;")
        right_layout.addWidget(tips_label)

        self.tips_list = QListWidget()
        self.tips_list.setMaximumHeight(120)
        default_tips = [
            "Stand with full body visible in frame",
            "Ensure good lighting without shadows",
            "Hold the pose steady during countdown"
        ]
        for tip in default_tips:
            self.tips_list.addItem(tip)
        right_layout.addWidget(self.tips_list)

        # Control buttons
        btn_layout = QHBoxLayout()

        self.start_btn = QPushButton("Start")
        self.start_btn.setObjectName("Primary")
        self.start_btn.setMinimumHeight(45)
        self.start_btn.clicked.connect(self.start_countdown)
        btn_layout.addWidget(self.start_btn)

        self.retry_btn = QPushButton("Retry")
        self.retry_btn.setObjectName("Secondary")
        self.retry_btn.setMinimumHeight(45)
        self.retry_btn.clicked.connect(self.retry_pose)
        self.retry_btn.hide()
        btn_layout.addWidget(self.retry_btn)

        self.next_btn = QPushButton("Next Pose")
        self.next_btn.setObjectName("Primary")
        self.next_btn.setMinimumHeight(45)
        self.next_btn.clicked.connect(self.next_pose)
        self.next_btn.hide()
        btn_layout.addWidget(self.next_btn)

        right_layout.addLayout(btn_layout)

        # Apply shadow to right panel
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 30))
        right_panel.setGraphicsEffect(shadow)

        main_layout.addWidget(right_panel)

        # Setup countdown timer
        self.countdown_timer.timeout.connect(self.update_countdown)

    def load_reference_image(self):
        """Load and display reference image"""
        ref_path = self.pose_data["ref"]
        if os.path.exists(ref_path):
            img = cv2.imread(ref_path)
            if img is not None:
                self.display_image(img, self.ref_label)

    def start_video(self):
        """Start video thread"""
        if self.video_thread is None:
            self.video_thread = VideoThread()
            self.video_thread.change_pixmap_signal.connect(self.update_camera)
            self.video_thread.start()

    def stop_video(self):
        """Stop video thread"""
        if self.video_thread:
            self.video_thread.stop()
            self.video_thread = None

    def update_camera(self, frame):
        """Update camera display"""
        self.current_frame = frame
        self.display_image(frame, self.camera_label)

    def display_image(self, cv_img, label):
        """Display OpenCV image in QLabel without stretching"""
        if cv_img is None:
            return
        height, width, channel = cv_img.shape
        bytes_per_line = 3 * width
        q_image = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_image)
        # Scale keeping aspect ratio instead of stretching
        label.setScaledContents(False)
        label.setPixmap(pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def start_countdown(self):
        """Begin 5-second countdown"""
        self.start_btn.setEnabled(False)
        self.countdown_value = 5
        self.countdown_overlay.setText(str(self.countdown_value))
        self.countdown_overlay.show()
        self.countdown_timer.start(1000)  # 1 second interval

    def update_countdown(self):
        """Update countdown display"""
        self.countdown_value -= 1
        if self.countdown_value > 0:
            self.countdown_overlay.setText(str(self.countdown_value))
        else:
            self.countdown_overlay.setText("📸")
            self.countdown_timer.stop()
            QTimer.singleShot(200, self.capture_and_analyze)

    def capture_and_analyze(self):
        """Capture frame and run pose comparison"""
        self.countdown_overlay.hide()

        if self.current_frame is None:
            QMessageBox.warning(self, "Error", "No camera frame available")
            self.start_btn.setEnabled(True)
            return

        # Save captured image
        if not self.session_dir:
            return

        # Increment attempt count
        self.attempt_count += 1

        # Save with attempt number
        user_path = self.session_dir / f"pose{self.pose_idx+1}_attempt{self.attempt_count}.jpg"
        cv2.imwrite(str(user_path), self.current_frame)
        self.captured_image = self.current_frame.copy()

        # Get landmarks
        user_lm = self.pose_detector.get_landmarks(self.current_frame)

        # Load reference landmarks
        ref_img = cv2.imread(self.pose_data["ref"])
        ref_lm = self.pose_detector.get_landmarks(ref_img)

        if user_lm is None:
            QMessageBox.warning(self, "Detection Failed",
                              "Couldn't see full body. Try again with better lighting and full body in frame.")
            self.start_btn.setEnabled(True)
            return

        # Get joint config for this pose
        joints_config = PoseComparator.POSE_KEY_ANGLES.get(self.pose_data["name"],
                                                           PoseComparator.POSE_KEY_ANGLES['Front Double Biceps'])

        # Compare poses
        result = compare_pose(user_lm, ref_lm, joints_config)
        self.feedback_result = result

        # Save feedback JSON
        feedback_path = self.session_dir / f"pose{self.pose_idx+1}_attempt{self.attempt_count}_feedback.json"
        with open(feedback_path, 'w') as f:
            json.dump(result, f, indent=2)

        # Draw overlay on captured image
        annotated = draw_feedback_overlay(self.captured_image, result["per_joint"])

        # Update reference label to show side-by-side or just user image
        self.display_image(annotated, self.ref_label)

        # Update tips with detailed feedback
        self.tips_list.clear()
        score = result['score']

        # Show score and required threshold
        self.tips_list.addItem(f"Score: {score:.0f}% | Target: {self.required_score:.0f}% | Attempt: {self.attempt_count}")
        self.tips_list.addItem(f"Symmetry: {result['symmetry']:.0f}%")

        # Add detailed feedback about what went wrong
        if score < self.required_score:
            self.tips_list.addItem("--- What to improve ---")
            for tip in result["top_tips"]:
                self.tips_list.addItem(f"• {tip}")

            # Add specific joint feedback
            per_joint = result.get("per_joint", {})
            major_issues = [(joint, info) for joint, info in per_joint.items()
                          if abs(info.get("delta_deg", 0)) > 15]
            if major_issues:
                self.tips_list.addItem("--- Major adjustments needed ---")
                for joint, info in major_issues[:2]:  # Show top 2 major issues
                    self.tips_list.addItem(f"• {info.get('advice', '')}")
        else:
            self.tips_list.addItem("--- Great job! ---")
            for tip in result["top_tips"]:
                self.tips_list.addItem(f"• {tip}")

        # Voice feedback
        if self.voice_enabled:
            from voice_feedback import VoiceFeedback
            voice = VoiceFeedback()

            # Provide context-aware feedback
            if score < self.required_score:
                voice.speak_tips([f"Score {int(score)} percent. You need {int(self.required_score)} percent."] + result["top_tips"][:2])
            else:
                voice.speak_tips([f"Great job! Score {int(score)} percent. Moving to next level."])

        # Check if score meets threshold
        if score >= self.required_score:
            # Increase difficulty for next attempt by 5%
            self.required_score = min(95.0, self.required_score + 5.0)

            # Show next button to move on
            self.start_btn.hide()
            self.retry_btn.hide()
            self.next_btn.show()
        else:
            # Show retry button to practice more
            self.start_btn.hide()
            self.retry_btn.show()
            self.next_btn.hide()

    def retry_pose(self):
        """Retry current pose"""
        self.retry_btn.hide()
        self.next_btn.hide()
        self.start_btn.show()
        self.start_btn.setEnabled(True)
        self.load_reference_image()

    def next_pose(self):
        """Move to next pose"""
        self.next_pose_signal.emit()

    def set_session_dir(self, session_dir):
        """Set session directory for saving files"""
        self.session_dir = session_dir


class SummaryScreen(QWidget):
    """Summary screen showing all 4 poses and scores"""
    export_session_signal = pyqtSignal()
    new_session_signal = pyqtSignal()

    def __init__(self, session_dir, results):
        super().__init__()
        self.session_dir = session_dir
        self.results = results
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(25)

        # Title
        title = QLabel("Session Complete!")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Results grid
        grid_widget = QWidget()
        grid_layout = QHBoxLayout(grid_widget)
        grid_layout.setSpacing(15)

        pose_names = ["Back Double Biceps", "Front Double Biceps", "Side Chest", "Back Lat Spread"]

        for i in range(4):
            pose_card = QWidget()
            pose_card.setObjectName("Card")
            pose_card_layout = QVBoxLayout(pose_card)

            # Pose image
            img_label = QLabel()
            img_label.setMinimumSize(200, 150)
            img_label.setMaximumSize(200, 150)
            img_label.setScaledContents(False)
            img_label.setAlignment(Qt.AlignCenter)
            img_label.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 8px;")

            # Find the best attempt for this pose
            img_path = None
            attempt = 1
            while True:
                potential_path = self.session_dir / f"pose{i+1}_attempt{attempt}.jpg"
                if potential_path.exists():
                    img_path = potential_path
                    attempt += 1
                else:
                    break

            # Use the last attempt (most recent/best) if any exist
            if img_path and img_path.exists():
                img = cv2.imread(str(img_path))
                if img is not None:
                    h, w = img.shape[:2]
                    bytes_per_line = 3 * w
                    q_image = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
                    pixmap = QPixmap.fromImage(q_image)
                    img_label.setPixmap(pixmap.scaled(img_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

            pose_card_layout.addWidget(img_label)

            # Pose name
            name_label = QLabel(pose_names[i])
            name_label.setStyleSheet("font-size: 14px; font-weight: 600; text-align: center;")
            name_label.setAlignment(Qt.AlignCenter)
            pose_card_layout.addWidget(name_label)

            # Score
            if i < len(self.results):
                score = self.results[i].get("score", 0)
                score_label = QLabel(f"{score:.0f}%")
                score_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #2563eb;")
                score_label.setAlignment(Qt.AlignCenter)
                pose_card_layout.addWidget(score_label)

            # Shadow
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(16)
            shadow.setOffset(0, 4)
            shadow.setColor(QColor(0, 0, 0, 20))
            pose_card.setGraphicsEffect(shadow)

            grid_layout.addWidget(pose_card)

        layout.addWidget(grid_widget)

        # Top tips summary
        tips_label = QLabel("Top 3 Tips Overall:")
        tips_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #475569;")
        layout.addWidget(tips_label)

        overall_tips = self.collect_top_tips()
        tips_list = QListWidget()
        tips_list.setMaximumHeight(100)
        for tip in overall_tips[:3]:
            tips_list.addItem(f"• {tip}")
        layout.addWidget(tips_list)

        # Buttons
        btn_layout = QHBoxLayout()

        export_btn = QPushButton("Export Session")
        export_btn.setObjectName("Secondary")
        export_btn.setMinimumHeight(45)
        export_btn.clicked.connect(self.export_session)
        btn_layout.addWidget(export_btn)

        new_btn = QPushButton("New Session")
        new_btn.setObjectName("Primary")
        new_btn.setMinimumHeight(45)
        new_btn.clicked.connect(self.new_session)
        btn_layout.addWidget(new_btn)

        layout.addLayout(btn_layout)

    def collect_top_tips(self):
        """Collect most common tips from all poses"""
        all_tips = []
        for result in self.results:
            all_tips.extend(result.get("top_tips", []))

        # Count frequency and return top 3
        from collections import Counter
        if all_tips:
            counter = Counter(all_tips)
            return [tip for tip, _ in counter.most_common(3)]
        return ["Great session!", "Keep practicing", "Check your symmetry"]

    def export_session(self):
        """Export session data"""
        # Create summary JSON
        summary = {
            "poses": [
                {
                    "name": ["Back Double Biceps", "Front Double Biceps", "Side Chest", "Back Lat Spread"][i],
                    "score": result.get("score", 0),
                    "top_tips": result.get("top_tips", [])
                }
                for i, result in enumerate(self.results)
            ]
        }

        summary_path = self.session_dir / "summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        # Create contact sheet
        contact_path = self.session_dir / "contact_sheet.png"
        make_contact_sheet(self.session_dir, contact_path)

        QMessageBox.information(self, "Export Complete",
                              f"Session exported to:\n{self.session_dir}")

    def new_session(self):
        """Start new session"""
        self.new_session_signal.emit()


class PosePerfectApp(QMainWindow):
    """Main application with stacked widget wizard"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PosePerfect.AI - Bodybuilding Pose Coach")
        self.setGeometry(100, 100, 1400, 900)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.pose_sequence = []
        self.voice_enabled = False
        self.current_pose_idx = 0
        self.session_dir = None
        self.session_results = []

        # Create welcome screen
        self.welcome_screen = WelcomeScreen()
        self.welcome_screen.start_session_signal.connect(self.start_session)
        self.stacked_widget.addWidget(self.welcome_screen)

        self.pose_step_screens = []

    def start_session(self, pose_sequence, voice_enabled):
        """Start a new guided session"""
        self.pose_sequence = pose_sequence
        self.voice_enabled = voice_enabled
        self.current_pose_idx = 0
        self.session_results = []

        # Create session directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = Path("static") / f"session_{timestamp}"
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # Create pose step screens
        self.pose_step_screens = []
        for i, pose_data in enumerate(self.pose_sequence):
            step_screen = PoseStepScreen(pose_data, i, self.voice_enabled)
            step_screen.set_session_dir(self.session_dir)
            step_screen.next_pose_signal.connect(self.next_pose)
            step_screen.retry_pose_signal.connect(self.retry_pose)
            self.stacked_widget.addWidget(step_screen)
            self.pose_step_screens.append(step_screen)

        # Show first pose
        self.show_pose_step(0)

    def show_pose_step(self, idx):
        """Show specific pose step"""
        if 0 <= idx < len(self.pose_step_screens):
            screen = self.pose_step_screens[idx]
            screen.start_video()
            self.stacked_widget.setCurrentWidget(screen)

            # Animate transition
            self.animate_transition()

    def next_pose(self):
        """Advance to next pose or summary"""
        # Save current result
        current_screen = self.pose_step_screens[self.current_pose_idx]
        current_screen.stop_video()

        if current_screen.feedback_result:
            self.session_results.append(current_screen.feedback_result)

        self.current_pose_idx += 1

        if self.current_pose_idx < len(self.pose_sequence):
            # Show next pose
            self.show_pose_step(self.current_pose_idx)
        else:
            # Show summary
            self.show_summary()

    def retry_pose(self):
        """Retry current pose"""
        # Just reset the current screen
        pass

    def show_summary(self):
        """Show summary screen"""
        summary_screen = SummaryScreen(self.session_dir, self.session_results)
        summary_screen.new_session_signal.connect(self.return_to_welcome)
        self.stacked_widget.addWidget(summary_screen)
        self.stacked_widget.setCurrentWidget(summary_screen)

        self.animate_transition()

    def return_to_welcome(self):
        """Return to welcome screen for new session"""
        # Clear old screens
        while self.stacked_widget.count() > 1:
            widget = self.stacked_widget.widget(1)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()

        self.stacked_widget.setCurrentWidget(self.welcome_screen)
        self.animate_transition()

    def animate_transition(self):
        """Animate screen transition with fade/scale effect"""
        current_widget = self.stacked_widget.currentWidget()
        if current_widget:
            # Simple opacity animation would go here
            # For simplicity, we'll skip complex Qt animations
            pass


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet(APPLE_STYLESHEET)

    window = PosePerfectApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
