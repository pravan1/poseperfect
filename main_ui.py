import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QComboBox, 
                             QProgressBar, QTextEdit, QGroupBox, QSplitter,
                             QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont, QPalette, QColor
from pose_detector import PoseDetector
from pose_comparator import PoseComparator
from voice_feedback import VoiceFeedback


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    pose_data_signal = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.pose_detector = PoseDetector()
        self.target_pose = None
        self.pose_mode = "Front Double Biceps"
        
    def run(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        while self._run_flag:
            ret, frame = cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                
                pose_results = self.pose_detector.process_frame(frame)
                
                if pose_results['landmarks'] is not None:
                    frame_with_pose = self.pose_detector.draw_pose(frame, pose_results['landmarks'])
                    
                    if self.target_pose is not None:
                        comparison_results = PoseComparator.compare_poses(
                            pose_results['landmarks'], 
                            self.target_pose,
                            self.pose_mode
                        )
                        pose_results.update(comparison_results)
                        
                        frame_with_pose = self.pose_detector.draw_comparison_overlay(
                            frame_with_pose, 
                            comparison_results
                        )
                    
                    self.change_pixmap_signal.emit(frame_with_pose)
                    self.pose_data_signal.emit(pose_results)
                else:
                    self.change_pixmap_signal.emit(frame)
                    
        cap.release()
        
    def stop(self):
        self._run_flag = False
        self.wait()
        
    def set_target_pose(self, pose_data):
        self.target_pose = pose_data
        
    def set_pose_mode(self, mode):
        self.pose_mode = mode


class PosePerfectApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PosePerfect.AI - Bodybuilding Pose Analyzer")
        self.setGeometry(100, 100, 1400, 900)
        
        self.apply_dark_theme()
        
        self.voice_feedback = VoiceFeedback()
        self.current_snapshot = None
        self.reference_poses = {}
        self.high_score_achieved = False
        self.auto_advance_timer = QTimer()
        self.auto_advance_timer.timeout.connect(self.advance_to_next_pose)
        self.auto_advance_timer.setSingleShot(True)
        
        self.init_ui()
        self.load_reference_poses()
        
        self.video_thread = VideoThread()
        self.video_thread.change_pixmap_signal.connect(self.update_image)
        self.video_thread.pose_data_signal.connect(self.update_pose_data)
        self.video_thread.start()
        
    def apply_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(dark_palette)
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header_layout = QHBoxLayout()
        logo_label = QLabel("PosePerfect.AI")
        logo_label.setFont(QFont("Arial", 24, QFont.Bold))
        header_layout.addWidget(logo_label)
        header_layout.addStretch()
        
        # Pose Selection
        pose_label = QLabel("Select Pose:")
        pose_label.setFont(QFont("Arial", 12))
        self.pose_combo = QComboBox()
        self.pose_combo.addItems([
            "Rear Double Biceps",
            "Front Double Biceps",
            "Side Chest",
            "Back Lat Spread"
        ])
        self.pose_combo.currentTextChanged.connect(self.on_pose_changed)
        self.pose_combo.setMinimumWidth(200)
        
        header_layout.addWidget(pose_label)
        header_layout.addWidget(self.pose_combo)
        main_layout.addLayout(header_layout)
        
        # Main Content Area
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Left Panel - Camera Feed
        left_panel = QGroupBox("Live Camera Feed")
        left_layout = QVBoxLayout(left_panel)
        
        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setScaledContents(True)
        self.camera_label.setStyleSheet("border: 2px solid #2a82da;")
        left_layout.addWidget(self.camera_label)
        
        # Camera Controls
        camera_controls = QHBoxLayout()
        self.snapshot_btn = QPushButton("Take Snapshot")
        self.snapshot_btn.clicked.connect(self.take_snapshot)
        self.snapshot_btn.setMinimumHeight(40)
        
        self.load_ref_btn = QPushButton("Load Reference")
        self.load_ref_btn.clicked.connect(self.load_custom_reference)
        self.load_ref_btn.setMinimumHeight(40)
        
        camera_controls.addWidget(self.snapshot_btn)
        camera_controls.addWidget(self.load_ref_btn)
        left_layout.addLayout(camera_controls)
        
        content_splitter.addWidget(left_panel)
        
        # Right Panel - Reference and Feedback
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Reference Image
        ref_group = QGroupBox("Reference Pose")
        ref_layout = QVBoxLayout(ref_group)
        self.reference_label = QLabel()
        self.reference_label.setMinimumSize(320, 240)
        self.reference_label.setScaledContents(True)
        self.reference_label.setStyleSheet("border: 2px solid #2a82da;")
        ref_layout.addWidget(self.reference_label)
        right_layout.addWidget(ref_group)
        
        # Performance Metrics
        metrics_group = QGroupBox("Performance Metrics")
        metrics_layout = QVBoxLayout(metrics_group)
        
        # Overall Score
        score_layout = QHBoxLayout()
        score_label = QLabel("Overall Match:")
        self.score_progress = QProgressBar()
        self.score_progress.setRange(0, 100)
        self.score_progress.setTextVisible(True)
        score_layout.addWidget(score_label)
        score_layout.addWidget(self.score_progress)
        metrics_layout.addLayout(score_layout)
        
        # Symmetry Score
        symmetry_layout = QHBoxLayout()
        symmetry_label = QLabel("Symmetry:")
        self.symmetry_progress = QProgressBar()
        self.symmetry_progress.setRange(0, 100)
        self.symmetry_progress.setTextVisible(True)
        symmetry_layout.addWidget(symmetry_label)
        symmetry_layout.addWidget(self.symmetry_progress)
        metrics_layout.addLayout(symmetry_layout)
        
        # Alignment Score
        alignment_layout = QHBoxLayout()
        alignment_label = QLabel("Alignment:")
        self.alignment_progress = QProgressBar()
        self.alignment_progress.setRange(0, 100)
        self.alignment_progress.setTextVisible(True)
        alignment_layout.addWidget(alignment_label)
        alignment_layout.addWidget(self.alignment_progress)
        metrics_layout.addLayout(alignment_layout)
        
        right_layout.addWidget(metrics_group)
        
        # Feedback Area
        feedback_group = QGroupBox("Real-time Feedback")
        feedback_layout = QVBoxLayout(feedback_group)
        self.feedback_text = QTextEdit()
        self.feedback_text.setReadOnly(True)
        self.feedback_text.setMaximumHeight(150)
        feedback_layout.addWidget(self.feedback_text)
        
        # Voice Control
        voice_layout = QHBoxLayout()
        self.voice_btn = QPushButton("Enable Voice Feedback")
        self.voice_btn.setCheckable(True)
        self.voice_btn.clicked.connect(self.toggle_voice)
        self.voice_btn.setMinimumHeight(35)
        voice_layout.addWidget(self.voice_btn)
        feedback_layout.addLayout(voice_layout)
        
        right_layout.addWidget(feedback_group)
        
        content_splitter.addWidget(right_panel)
        content_splitter.setSizes([800, 600])
        
        main_layout.addWidget(content_splitter)
        
        # Status Bar
        self.statusBar().showMessage("Ready - Select a pose and start practicing!")
        
    def load_reference_poses(self):
        reference_dir = "reference_poses"
        if os.path.exists(reference_dir):
            for i in range(1, 5):
                pose_file = os.path.join(reference_dir, f"pose{i}.jpg")
                if os.path.exists(pose_file):
                    img = cv2.imread(pose_file)
                    if img is not None:
                        pose_detector = PoseDetector()
                        results = pose_detector.process_frame(img)
                        pose_names = [
                            "Rear Double Biceps",
                            "Front Double Biceps",
                            "Side Chest",
                            "Back Lat Spread"
                        ]
                        if i <= len(pose_names):
                            self.reference_poses[pose_names[i-1]] = {
                                'image': img,
                                'landmarks': results['landmarks']
                            }
        
        # Load first reference pose
        self.on_pose_changed(self.pose_combo.currentText())
        
    def on_pose_changed(self, pose_name):
        if pose_name in self.reference_poses:
            ref_data = self.reference_poses[pose_name]
            self.display_reference_image(ref_data['image'])
            if hasattr(self, 'video_thread'):
                self.video_thread.set_target_pose(ref_data['landmarks'])
                self.video_thread.set_pose_mode(pose_name)
            self.statusBar().showMessage(f"Loaded reference for {pose_name}")
            # Reset the high score flag when pose changes
            self.high_score_achieved = False
            
    def display_reference_image(self, cv_img):
        if cv_img is not None:
            height, width, channel = cv_img.shape
            bytes_per_line = 3 * width
            q_image = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            self.reference_label.setPixmap(QPixmap.fromImage(q_image))
            
    def update_image(self, cv_img):
        height, width, channel = cv_img.shape
        bytes_per_line = 3 * width
        q_image = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        self.camera_label.setPixmap(QPixmap.fromImage(q_image))
        self.current_snapshot = cv_img
        
    def update_pose_data(self, pose_data):
        if 'overall_score' in pose_data:
            score = pose_data['overall_score']
            self.score_progress.setValue(int(score))
            
            # Check for high score achievement (92% or higher)
            if score >= 92 and not self.high_score_achieved:
                self.high_score_achieved = True
                self.auto_capture_and_advance()
            elif score < 85:
                # Reset the flag if score drops below 85%
                self.high_score_achieved = False
            
        if 'symmetry_score' in pose_data:
            self.symmetry_progress.setValue(int(pose_data['symmetry_score']))
            
        if 'alignment_score' in pose_data:
            self.alignment_progress.setValue(int(pose_data['alignment_score']))
            
        if 'feedback' in pose_data:
            feedback_messages = pose_data['feedback']
            if feedback_messages:
                self.feedback_text.clear()
                for msg in feedback_messages[:5]:  # Show top 5 feedback items
                    self.feedback_text.append(f"• {msg}")
                    
                if self.voice_btn.isChecked() and feedback_messages:
                    self.voice_feedback.speak(feedback_messages[0])
                    
    def take_snapshot(self):
        if self.current_snapshot is not None:
            if not os.path.exists("static"):
                os.makedirs("static")
            
            timestamp = QTimer().interval()
            filename = f"static/snapshot_{self.pose_combo.currentText().replace(' ', '_')}.jpg"
            cv2.imwrite(filename, self.current_snapshot)
            self.statusBar().showMessage(f"Snapshot saved: {filename}")
            
    def load_custom_reference(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Reference Image", 
            "", 
            "Image Files (*.png *.jpg *.jpeg)"
        )
        if file_name:
            img = cv2.imread(file_name)
            if img is not None:
                pose_detector = PoseDetector()
                results = pose_detector.process_frame(img)
                current_pose = self.pose_combo.currentText()
                self.reference_poses[current_pose] = {
                    'image': img,
                    'landmarks': results['landmarks']
                }
                self.on_pose_changed(current_pose)
                
    def toggle_voice(self):
        if self.voice_btn.isChecked():
            self.voice_btn.setText("Disable Voice Feedback")
            self.voice_feedback.speak("Voice feedback enabled")
        else:
            self.voice_btn.setText("Enable Voice Feedback")
    
    def auto_capture_and_advance(self):
        """Automatically capture screenshot and advance to next pose when 92% match achieved"""
        if self.current_snapshot is not None:
            # Create static directory if it doesn't exist
            if not os.path.exists("static"):
                os.makedirs("static")
            
            # Generate filename with pose name and timestamp
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            pose_name = self.pose_combo.currentText().replace(' ', '_')
            filename = f"static/perfect_{pose_name}_{timestamp}.jpg"
            
            # Save the snapshot
            cv2.imwrite(filename, self.current_snapshot)
            self.statusBar().showMessage(f"Perfect pose captured! Saved: {filename}")
            
            # Announce success
            if self.voice_btn.isChecked():
                self.voice_feedback.speak("Excellent! Perfect pose captured. Moving to next pose in 3 seconds.")
            
            # Start timer to advance to next pose after 3 seconds
            self.auto_advance_timer.start(3000)
    
    def advance_to_next_pose(self):
        """Advance to the next pose in the sequence"""
        current_index = self.pose_combo.currentIndex()
        next_index = (current_index + 1) % self.pose_combo.count()
        self.pose_combo.setCurrentIndex(next_index)
        
        # Announce the new pose
        if self.voice_btn.isChecked():
            new_pose = self.pose_combo.currentText()
            self.voice_feedback.speak(f"Now practicing {new_pose}")
            
    def closeEvent(self, event):
        self.video_thread.stop()
        self.auto_advance_timer.stop()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = PosePerfectApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()