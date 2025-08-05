import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QComboBox, 
                             QTextEdit, QProgressBar, QGroupBox, QFrame, 
                             QMessageBox, QSplitter)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap, QFont, QPalette, QColor
import threading
from pose_detector import TaekwondoPoseDetector
from calibration import UserCalibration
from voice_feedback import VoiceFeedback
import os

class VideoThread(QThread):
    frame_ready = pyqtSignal(np.ndarray)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.cap = None
        
    def start_capture(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            return False
        self.running = True
        self.start()
        return True
        
    def stop_capture(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.quit()
        self.wait()
        
    def run(self):
        while self.running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)  # Mirror the image
                self.frame_ready.emit(frame)
            self.msleep(30)  # ~33 FPS

class TaekwondoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pose_detector = TaekwondoPoseDetector()
        self.calibration = UserCalibration()
        self.voice_feedback = VoiceFeedback()
        self.video_thread = VideoThread()
        
        self.current_frame = None
        self.current_mode = "practice"  # practice, calibration
        self.current_move = "front_stance"
        self.calibration_step = 0
        
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        self.setWindowTitle("Taekwondo.AI - Virtual Training Assistant")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(self.get_app_stylesheet())
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panes
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Video and controls
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Feedback and settings
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set initial splitter sizes
        splitter.setSizes([800, 400])
        
    def create_left_panel(self):
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Video display
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("""
            QLabel {
                border: 2px solid #333;
                background-color: #1a1a1a;
                border-radius: 10px;
            }
        """)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setText("Click 'Start Camera' to begin")
        left_layout.addWidget(self.video_label)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Camera")
        self.start_button.setStyleSheet(self.get_button_stylesheet("#4CAF50"))
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Camera")
        self.stop_button.setStyleSheet(self.get_button_stylesheet("#f44336"))
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        self.capture_button = QPushButton("Capture Photo")
        self.capture_button.setStyleSheet(self.get_button_stylesheet("#2196F3"))
        self.capture_button.setEnabled(False)
        button_layout.addWidget(self.capture_button)
        
        left_layout.addLayout(button_layout)
        
        return left_widget
    
    def create_right_panel(self):
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Mode selection
        mode_group = QGroupBox("Training Mode")
        mode_layout = QVBoxLayout(mode_group)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Practice Mode", "Calibration Mode"])
        self.mode_combo.setStyleSheet(self.get_combo_stylesheet())
        mode_layout.addWidget(self.mode_combo)
        
        # Move selection
        self.move_combo = QComboBox()
        self.move_combo.addItems([
            "Front Stance", "Horse Stance", "Back Stance",
            "Front Kick", "Roundhouse Kick", "Side Kick",
            "Low Block", "Middle Block", "High Block"
        ])
        self.move_combo.setStyleSheet(self.get_combo_stylesheet())
        mode_layout.addWidget(self.move_combo)
        
        right_layout.addWidget(mode_group)
        
        # Calibration section
        calibration_group = QGroupBox("Calibration")
        calibration_layout = QVBoxLayout(calibration_group)
        
        self.calibration_status = QLabel("Status: Not Calibrated")
        self.calibration_status.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        calibration_layout.addWidget(self.calibration_status)
        
        self.calibration_button = QPushButton("Start Calibration")
        self.calibration_button.setStyleSheet(self.get_button_stylesheet("#FF9800"))
        calibration_layout.addWidget(self.calibration_button)
        
        self.calibration_progress = QProgressBar()
        self.calibration_progress.setVisible(False)
        calibration_layout.addWidget(self.calibration_progress)
        
        right_layout.addWidget(calibration_group)
        
        # Feedback section
        feedback_group = QGroupBox("Real-time Feedback")
        feedback_layout = QVBoxLayout(feedback_group)
        
        self.feedback_text = QTextEdit()
        self.feedback_text.setMaximumHeight(150)
        self.feedback_text.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Segoe UI';
                font-size: 12px;
            }
        """)
        self.feedback_text.setReadOnly(True)
        feedback_layout.addWidget(self.feedback_text)
        
        # Pose quality indicator
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Pose Quality:"))
        
        self.quality_bar = QProgressBar()
        self.quality_bar.setRange(0, 100)
        self.quality_bar.setValue(0)
        self.quality_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555;
                border-radius: 5px;
                text-align: center;
                background-color: #2b2b2b;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff6b6b, stop:0.5 #ffa726, stop:1 #66bb6a);
                border-radius: 3px;
            }
        """)
        quality_layout.addWidget(self.quality_bar)
        
        feedback_layout.addLayout(quality_layout)
        right_layout.addWidget(feedback_group)
        
        # Voice controls
        voice_group = QGroupBox("Voice Feedback")
        voice_layout = QVBoxLayout(voice_group)
        
        self.voice_enabled_button = QPushButton("Enable Voice Feedback")
        self.voice_enabled_button.setCheckable(True)
        self.voice_enabled_button.setStyleSheet(self.get_toggle_button_stylesheet())
        voice_layout.addWidget(self.voice_enabled_button)
        
        right_layout.addWidget(voice_group)
        
        # Instructions
        instructions_group = QGroupBox("Instructions")
        instructions_layout = QVBoxLayout(instructions_group)
        
        self.instruction_label = QLabel("Select a training mode and move to begin.")
        self.instruction_label.setWordWrap(True)
        self.instruction_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                padding: 10px;
                background-color: #2b2b2b;
                border-radius: 5px;
            }
        """)
        instructions_layout.addWidget(self.instruction_label)
        
        right_layout.addWidget(instructions_group)
        
        return right_widget
    
    def setup_connections(self):
        # Button connections
        self.start_button.clicked.connect(self.start_camera)
        self.stop_button.clicked.connect(self.stop_camera)
        self.capture_button.clicked.connect(self.capture_photo)
        self.calibration_button.clicked.connect(self.toggle_calibration)
        
        # Combo box connections
        self.mode_combo.currentTextChanged.connect(self.mode_changed)
        self.move_combo.currentTextChanged.connect(self.move_changed)
        
        # Voice toggle
        self.voice_enabled_button.clicked.connect(self.toggle_voice_feedback)
        
        # Video thread connection
        self.video_thread.frame_ready.connect(self.update_frame)
        
        # Check initial calibration status
        self.update_calibration_status()
    
    def start_camera(self):
        if self.video_thread.start_capture():
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.capture_button.setEnabled(True)
            self.add_feedback("Camera started successfully!")
        else:
            QMessageBox.warning(self, "Camera Error", "Could not start camera. Please check your webcam connection.")
    
    def stop_camera(self):
        self.video_thread.stop_capture()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.capture_button.setEnabled(False)
        self.video_label.setText("Camera stopped")
        self.add_feedback("Camera stopped.")
    
    def update_frame(self, frame):
        self.current_frame = frame.copy()
        
        # Process frame based on current mode
        if self.current_mode == "calibration":
            processed_frame = self.process_calibration_frame(frame)
        else:
            processed_frame = self.process_practice_frame(frame)
        
        # Convert to Qt format and display
        self.display_frame(processed_frame)
    
    def process_practice_frame(self, frame):
        # Detect pose
        analysis = self.pose_detector.detect_pose(frame)
        
        if analysis['pose_detected']:
            # Draw pose landmarks
            frame = self.pose_detector.draw_pose_landmarks(frame, analysis['landmarks'])
            
            # Update feedback
            self.update_feedback_display(analysis)
            
            # Analyze specific move
            move_analysis = self.analyze_current_move(analysis['landmarks'], frame)
            if move_analysis:
                self.update_move_feedback(move_analysis)
        
        return frame
    
    def process_calibration_frame(self, frame):
        # Handle calibration process
        analysis = self.pose_detector.detect_pose(frame)
        
        if analysis['pose_detected']:
            frame = self.pose_detector.draw_pose_landmarks(frame, analysis['landmarks'])
            
            # Process calibration step
            if hasattr(self, 'calibration_in_progress') and self.calibration_in_progress:
                self.process_calibration_step(analysis['landmarks'], frame.shape[:2])
        
        return frame
    
    def analyze_current_move(self, landmarks, frame):
        move_map = {
            "Front Stance": self.pose_detector.analyze_front_stance,
            "Roundhouse Kick": self.pose_detector.analyze_roundhouse_kick,
        }
        
        move_name = self.move_combo.currentText()
        if move_name in move_map:
            return move_map[move_name](landmarks, frame)
        
        return None
    
    def update_feedback_display(self, analysis):
        # Update pose quality bar
        quality = analysis.get('pose_quality', 0)
        self.quality_bar.setValue(int(quality))
        
        # Update feedback text
        feedback_lines = []
        
        if analysis.get('feedback'):
            feedback_lines.extend(f"✓ {fb}" for fb in analysis['feedback'])
        
        if analysis.get('errors'):
            feedback_lines.extend(f"✗ {err}" for err in analysis['errors'])
        
        if feedback_lines:
            self.feedback_text.append('\n'.join(feedback_lines))
            
            # Voice feedback
            if self.voice_enabled_button.isChecked() and analysis.get('errors'):
                self.voice_feedback.speak_feedback(analysis['errors'][0])
    
    def update_move_feedback(self, move_analysis):
        if move_analysis.get('feedback'):
            for feedback in move_analysis['feedback']:
                self.add_feedback(f"Move: {feedback}")
        
        if move_analysis.get('errors'):
            for error in move_analysis['errors']:
                self.add_feedback(f"Move Error: {error}")
    
    def add_feedback(self, message):
        self.feedback_text.append(f"[{self.get_timestamp()}] {message}")
        
        # Auto-scroll to bottom
        scrollbar = self.feedback_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def get_timestamp(self):
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def display_frame(self, frame):
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        # Scale to fit label
        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.video_label.setPixmap(scaled_pixmap)
    
    def capture_photo(self):
        if self.current_frame is not None:
            # Create static directory if it doesn't exist
            os.makedirs('static/captures', exist_ok=True)
            
            # Generate filename
            from datetime import datetime
            filename = f"static/captures/pose_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            
            # Process frame with pose landmarks
            analysis = self.pose_detector.detect_pose(self.current_frame)
            if analysis['pose_detected']:
                capture_frame = self.pose_detector.draw_pose_landmarks(self.current_frame.copy(), analysis['landmarks'])
            else:
                capture_frame = self.current_frame.copy()
            
            # Save image
            cv2.imwrite(filename, capture_frame)
            self.add_feedback(f"Photo captured: {filename}")
            
            QMessageBox.information(self, "Photo Captured", f"Pose photo saved to:\n{filename}")
    
    def toggle_calibration(self):
        if not hasattr(self, 'calibration_in_progress'):
            self.calibration_in_progress = False
            
        if not self.calibration_in_progress:
            self.start_calibration()
        else:
            self.stop_calibration()
    
    def start_calibration(self):
        self.calibration_in_progress = True
        self.calibration_step = 1
        self.calibration_button.setText("Stop Calibration")
        self.calibration_progress.setVisible(True)
        self.calibration_progress.setValue(0)
        self.current_mode = "calibration"
        
        # Start calibration sequence
        result = self.calibration.start_calibration_sequence(self.pose_detector)
        self.instruction_label.setText(result['instruction'])
        self.add_feedback("Calibration started. Follow the on-screen instructions.")
    
    def stop_calibration(self):
        self.calibration_in_progress = False
        self.calibration_button.setText("Start Calibration")
        self.calibration_progress.setVisible(False)
        self.current_mode = "practice"
        self.instruction_label.setText("Calibration stopped.")
        self.add_feedback("Calibration stopped.")
    
    def process_calibration_step(self, landmarks, frame_dimensions):
        if self.calibration_step == 1:
            result = self.calibration.capture_neutral_pose(landmarks, frame_dimensions)
        elif self.calibration_step == 2:
            result = self.calibration.capture_t_pose(landmarks, frame_dimensions)
        elif self.calibration_step == 3:
            result = self.calibration.capture_front_stance(landmarks, frame_dimensions)
        else:
            return
        
        if result['success']:
            self.calibration_step = result.get('step', self.calibration_step + 1)
            self.instruction_label.setText(result['instruction'])
            self.calibration_progress.setValue(self.calibration_step * 25)
            
            if result.get('next_action') == 'finalize_calibration':
                final_result = self.calibration.finalize_calibration()
                if final_result['success']:
                    self.add_feedback("Calibration completed successfully!")
                    self.stop_calibration()
                    self.update_calibration_status()
        else:
            self.instruction_label.setText(result.get('message', 'Continue with calibration...'))
    
    def update_calibration_status(self):
        if self.calibration.is_calibrated():
            self.calibration_status.setText("Status: Calibrated ✓")
            self.calibration_status.setStyleSheet("color: #66bb6a; font-weight: bold;")
        else:
            self.calibration_status.setText("Status: Not Calibrated")
            self.calibration_status.setStyleSheet("color: #ff6b6b; font-weight: bold;")
    
    def mode_changed(self, mode_text):
        if "Calibration" in mode_text:
            self.current_mode = "calibration"
        else:
            self.current_mode = "practice"
        self.add_feedback(f"Mode changed to: {mode_text}")
    
    def move_changed(self, move_text):
        self.current_move = move_text.lower().replace(" ", "_")
        self.add_feedback(f"Selected move: {move_text}")
    
    def toggle_voice_feedback(self, enabled):
        if enabled:
            self.voice_enabled_button.setText("Disable Voice Feedback")
            self.add_feedback("Voice feedback enabled")
        else:
            self.voice_enabled_button.setText("Enable Voice Feedback")
            self.add_feedback("Voice feedback disabled")
    
    def closeEvent(self, event):
        self.video_thread.stop_capture()
        self.pose_detector.close()
        event.accept()
    
    def get_app_stylesheet(self):
        return """
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 10px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """
    
    def get_button_stylesheet(self, color):
        return f"""
            QPushButton {{
                background-color: {color};
                border: none;
                color: white;
                padding: 10px;
                text-align: center;
                font-size: 14px;
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:pressed {{
                background-color: {color}aa;
            }}
            QPushButton:disabled {{
                background-color: #555;
                color: #888;
            }}
        """
    
    def get_combo_stylesheet(self):
        return """
            QComboBox {
                border: 2px solid #555;
                border-radius: 5px;
                padding: 8px;
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QComboBox:drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """
    
    def get_toggle_button_stylesheet(self):
        return """
            QPushButton {
                background-color: #555;
                border: 2px solid #777;
                color: white;
                padding: 10px;
                text-align: center;
                font-size: 12px;
                border-radius: 8px;
            }
            QPushButton:checked {
                background-color: #4CAF50;
                border-color: #66bb6a;
            }
            QPushButton:hover {
                border-color: #999;
            }
        """

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    # Set dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(45, 45, 45))
    palette.setColor(QPalette.AlternateBase, QColor(60, 60, 60))
    palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(45, 45, 45))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)
    
    window = TaekwondoApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()