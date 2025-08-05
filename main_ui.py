import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QComboBox, 
                             QTextEdit, QProgressBar, QGroupBox, QFrame, 
                             QMessageBox, QSplitter, QCheckBox)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap, QFont, QPalette, QColor
import threading
from optimized_pose_detector import OptimizedPoseDetector
from optimized_camera import OptimizedCamera
from calibration import UserCalibration
from voice_feedback import VoiceFeedback
from pose_processor_thread import PoseProcessorThread
from performance_config import PerformanceConfig
import os

class VideoThread(QThread):
    frame_ready = pyqtSignal(np.ndarray)
    
    def __init__(self):
        super().__init__()
        self.camera = OptimizedCamera()
        self.running = False
        
    def start_capture(self):
        if self.camera.start():
            self.running = True
            self.start()
            return True
        return False
        
    def stop_capture(self):
        self.running = False
        self.wait(200)  # Wait maximum 200ms for thread to finish
        self.camera.stop()
        if self.isRunning():
            self.terminate()  # Force terminate if still running
            self.wait()
        
    def run(self):
        while self.running:
            frame = self.camera.get_frame()
            if frame is not None:
                self.frame_ready.emit(frame)
            self.msleep(int(1000 / 30))  # 30 FPS

class TaekwondoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pose_detector = OptimizedPoseDetector()
        self.calibration = UserCalibration()
        self.voice_feedback = VoiceFeedback()
        self.video_thread = VideoThread()
        
        # Create pose processor thread
        self.pose_processor = PoseProcessorThread(self.pose_detector)
        self.pose_processor.pose_analyzed.connect(self.handle_pose_analysis)
        self.pose_processor.start_processing()
        
        self.current_frame = None
        self.current_mode = "practice"  # practice, calibration
        self.current_move = "front_stance"
        self.calibration_step = 0
        self.frame_counter = 0  # Frame counter for skipping
        self.last_feedback_time = 0  # Throttle feedback updates
        self.last_processed_frame = None  # Store last processed frame
        
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        self.setWindowTitle("Taekwondo.AI - Virtual Training Assistant")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(self.get_app_stylesheet())
        
        # Set window to have rounded corners and shadow (platform-specific)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() & ~Qt.FramelessWindowHint)  # Re-enable frame for now
        
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
                border: 2px solid #cc0000;
                background: linear-gradient(135deg, #000000 0%, #330000 100%);
                border-radius: 16px;
                padding: 2px;
                color: #ffffff;
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
        self.calibration_status.setStyleSheet("color: #ff3b30; font-weight: 600; font-size: 14px;")
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
                background-color: rgba(26, 26, 26, 0.95);
                color: #ffffff;
                border: 1px solid #cc0000;
                border-radius: 12px;
                padding: 12px;
                font-family: 'SF Mono', Menlo, Monaco, 'Courier New', monospace;
                font-size: 13px;
                line-height: 1.5;
            }
            QTextEdit::selection {
                background-color: #cc0000;
                color: white;
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
                border: 1px solid #666666;
                border-radius: 6px;
                text-align: center;
                background-color: #1a1a1a;
                height: 10px;
                font-size: 13px;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #660000, stop:0.5 #cc0000, stop:1 #ff0000);
                border-radius: 5px;
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
        
        # Add checkbox for auto-read instructions
        self.auto_read_instructions = QCheckBox("Auto-read move instructions")
        self.auto_read_instructions.setChecked(True)
        self.auto_read_instructions.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #ffffff;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                background-color: #333333;
                border: 1px solid #cc0000;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #cc0000;
            }
            QCheckBox::indicator:hover {
                border: 1px solid #ff0000;
            }
        """)
        voice_layout.addWidget(self.auto_read_instructions)
        
        right_layout.addWidget(voice_group)
        
        # Instructions
        instructions_group = QGroupBox("Instructions")
        instructions_layout = QVBoxLayout(instructions_group)
        
        self.instruction_label = QLabel("Select a training mode and move to begin.")
        self.instruction_label.setWordWrap(True)
        self.instruction_label.setStyleSheet("""
            QLabel {
                color: #3a3a3c;
                padding: 15px;
                background-color: #f2f2f7;
                border-radius: 12px;
                font-size: 14px;
                line-height: 1.4;
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
        try:
            self.current_frame = frame.copy()
            self.frame_counter += 1
            
            # Process frames based on skip rate configuration
            if self.frame_counter % PerformanceConfig.FRAME_SKIP_RATE == 0:
                # Send frame to processor thread (non-blocking)
                self.pose_processor.add_frame(frame, self.current_mode)
            
            # Always display the current frame to prevent freezing
            # Overlay landmarks if available from last processing
            if hasattr(self, 'last_landmarks') and self.last_landmarks is not None:
                # Draw landmarks on current frame for smooth display
                display_frame = self.pose_detector.draw_landmarks(
                    frame.copy(), self.last_landmarks
                )
                self.display_frame(display_frame)
            else:
                self.display_frame(frame)
        except Exception as e:
            print(f"Error updating frame: {e}")
    
    def handle_pose_analysis(self, analysis):
        """Handle pose analysis from processor thread"""
        try:
            if analysis['pose_detected']:
                # Store landmarks for smooth display
                self.last_landmarks = analysis['landmarks']
                
                # Update feedback
                self.update_feedback_display(analysis)
                
                # Analyze specific move if in practice mode
                if analysis.get('mode') == 'practice' and self.current_frame is not None:
                    move_analysis = self.analyze_current_move(
                        analysis['landmarks'], self.current_frame
                    )
                    if move_analysis:
                        self.update_move_feedback(move_analysis)
                elif analysis.get('mode') == 'calibration':
                    self.handle_calibration_analysis(analysis)
            else:
                # Show visibility feedback if pose not detected
                if 'visibility_score' in analysis and analysis['visibility_score'] < 0.4:
                    self.add_feedback("Cannot detect pose clearly. Please:")
                    self.add_feedback("- Stand further from camera to show full body")
                    self.add_feedback("- Ensure good lighting")
                    self.add_feedback("- Wear contrasting colors")
        except Exception as e:
            print(f"Error handling pose analysis: {e}")
    
    def process_practice_frame(self, frame):
        # This method is now handled by the pose processor thread
        return frame
    
    def process_calibration_frame(self, frame):
        # This method is now handled by the pose processor thread
        return frame
    
    def handle_calibration_analysis(self, analysis):
        """Handle calibration analysis from processor thread"""
        if hasattr(self, 'calibration_in_progress') and self.calibration_in_progress:
            if self.current_frame is not None:
                self.process_calibration_step(
                    analysis['landmarks'], self.current_frame.shape[:2]
                )
    
    def analyze_current_move(self, landmarks, frame):
        # For now, return the basic feedback from the analysis
        # Move-specific analysis can be added later
        return None
    
    def update_feedback_display(self, analysis):
        import time
        current_time = time.time()
        
        # Update pose quality bar (use confidence as quality metric)
        quality = analysis.get('detection_confidence', 0) * 100
        self.quality_bar.setValue(int(quality))
        
        # Throttle text updates to reduce UI overhead
        if current_time - self.last_feedback_time > PerformanceConfig.FEEDBACK_UPDATE_INTERVAL:
            # Update feedback text
            feedback_lines = []
            
            if analysis.get('feedback'):
                feedback_lines.extend(f"✓ {fb}" for fb in analysis['feedback'])
            
            if analysis.get('errors'):
                feedback_lines.extend(f"✗ {err}" for err in analysis['errors'])
            
            if feedback_lines:
                # Limit feedback text buffer size
                if self.feedback_text.document().lineCount() > PerformanceConfig.MAX_FEEDBACK_LINES:
                    self.feedback_text.clear()
                self.feedback_text.append('\n'.join(feedback_lines[:2]))  # Show max 2 items
                self.last_feedback_time = current_time
                
                # Voice feedback (also throttled)
                if self.voice_enabled_button.isChecked() and analysis.get('errors'):
                    self.voice_feedback.speak_feedback(analysis['errors'][0])
    
    def update_move_feedback(self, move_analysis):
        if move_analysis.get('feedback'):
            for feedback in move_analysis['feedback']:
                self.add_feedback(f"Move: {feedback}")
        
        if move_analysis.get('errors'):
            for error in move_analysis['errors']:
                self.add_feedback(f"Move Error: {error}")
        
        # Handle specific corrections with voice feedback
        if move_analysis.get('corrections'):
            for correction in move_analysis['corrections']:
                self.add_feedback(f"Correction: {correction}")
                # Speak the correction if voice is enabled
                if self.voice_enabled_button.isChecked():
                    self.voice_feedback.speak_feedback(correction, priority="high")
    
    def add_feedback(self, message):
        import time
        current_time = time.time()
        # Throttle feedback updates to max once per 0.5 seconds
        if current_time - self.last_feedback_time < 0.5:
            return
        self.last_feedback_time = current_time
        
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
        
        # Scale to fit label with configurable transformation
        pixmap = QPixmap.fromImage(qt_image)
        transform_mode = Qt.FastTransformation if PerformanceConfig.USE_FAST_SCALING else Qt.SmoothTransformation
        scaled_pixmap = pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, transform_mode)
        self.video_label.setPixmap(scaled_pixmap)
    
    def capture_photo(self):
        if self.current_frame is not None:
            # Create static directory if it doesn't exist
            os.makedirs('static/captures', exist_ok=True)
            
            # Generate filename
            from datetime import datetime
            filename = f"static/captures/pose_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            
            # Process frame with pose landmarks
            analysis = self.pose_detector.process_frame(self.current_frame)
            if analysis['pose_detected']:
                capture_frame = self.pose_detector.draw_landmarks(self.current_frame.copy(), analysis['landmarks'])
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
            self.calibration_status.setStyleSheet("color: #34c759; font-weight: 600; font-size: 14px;")
        else:
            self.calibration_status.setText("Status: Not Calibrated")
            self.calibration_status.setStyleSheet("color: #ff3b30; font-weight: 600; font-size: 14px;")
    
    def mode_changed(self, mode_text):
        if "Calibration" in mode_text:
            self.current_mode = "calibration"
        else:
            self.current_mode = "practice"
        self.add_feedback(f"Mode changed to: {mode_text}")
    
    def move_changed(self, move_text):
        self.current_move = move_text.lower().replace(" ", "_")
        self.add_feedback(f"Selected move: {move_text}")
        
        # Note: Move instructions handled separately now
        # instructions = self.pose_detector.set_current_move(self.current_move)
        
        # Update instruction label with the first instruction
        if instructions:
            self.instruction_label.setText(instructions[0])
        
        # Speak all instructions if voice is enabled and auto-read is checked
        if self.voice_enabled_button.isChecked() and self.auto_read_instructions.isChecked() and instructions:
            # First, announce the move
            self.voice_feedback.speak_instruction(f"Now learning {move_text}")
            # Then speak each instruction with a slight delay
            for i, instruction in enumerate(instructions):
                # Use QTimer to delay each instruction (start after 2 seconds, then 3 seconds apart)
                QTimer.singleShot(2000 + (i * 3000), lambda inst=instruction: self.voice_feedback.speak_instruction(inst))
    
    def toggle_voice_feedback(self, enabled):
        if enabled:
            self.voice_enabled_button.setText("Disable Voice Feedback")
            self.add_feedback("Voice feedback enabled")
        else:
            self.voice_enabled_button.setText("Enable Voice Feedback")
            self.add_feedback("Voice feedback disabled")
    
    def closeEvent(self, event):
        # Stop all threads properly
        try:
            # Stop pose processor first
            if hasattr(self, 'pose_processor'):
                self.pose_processor.stop_processing()
            
            # Stop video thread
            if hasattr(self, 'video_thread'):
                self.video_thread.stop_capture()
            
            # Close pose detector
            if hasattr(self, 'pose_detector'):
                self.pose_detector.close()
        except Exception as e:
            print(f"Error during cleanup: {e}")
        finally:
            event.accept()
    
    def get_app_stylesheet(self):
        return """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a1a, stop:1 #000000);
                color: #ffffff;
                font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Helvetica, Arial, sans-serif;
            }
            QGroupBox {
                font-weight: 600;
                font-size: 13px;
                color: #cccccc;
                border: 1px solid #cc0000;
                background-color: rgba(26, 26, 26, 0.9);
                border-radius: 12px;
                margin-top: 20px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #ff0000;
                font-size: 17px;
                font-weight: 600;
            }
            QLabel {
                font-size: 15px;
                color: #ffffff;
            }
        """
    
    def get_button_stylesheet(self, color):
        # Black and red theme color mapping
        theme_colors = {
            "#4CAF50": "#cc0000",  # Green -> Red
            "#f44336": "#ff0000",  # Red -> Bright Red
            "#2196F3": "#cc0000",  # Blue -> Red
            "#FF9800": "#ff3333"   # Orange -> Light Red
        }
        theme_color = theme_colors.get(color, color)
        
        return f"""
            QPushButton {{
                background: {theme_color};
                border: 1px solid {theme_color};
                color: white;
                padding: 12px 24px;
                text-align: center;
                font-size: 15px;
                font-weight: 600;
                border-radius: 12px;
                font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", sans-serif;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {theme_color}, stop:1 #000000);
                border: 1px solid #ff0000;
                transform: scale(1.02);
            }}
            QPushButton:pressed {{
                background: #660000;
                transform: scale(0.98);
            }}
            QPushButton:disabled {{
                background: #333333;
                color: #666666;
                border: 1px solid #444444;
            }}
        """
    
    def get_combo_stylesheet(self):
        return """
            QComboBox {
                border: 1px solid #cc0000;
                border-radius: 10px;
                padding: 10px 15px;
                background-color: #1a1a1a;
                color: #ffffff;
                font-size: 15px;
                font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", sans-serif;
                min-height: 20px;
            }
            QComboBox:hover {
                border-color: #ff0000;
                background-color: #262626;
            }
            QComboBox:focus {
                border-color: #ff0000;
                border-width: 2px;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #cc0000;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #1a1a1a;
                border: 1px solid #cc0000;
                border-radius: 10px;
                selection-background-color: #cc0000;
                selection-color: white;
                padding: 5px;
                color: #ffffff;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #cc0000;
                color: white;
            }
        """
    
    def get_toggle_button_stylesheet(self):
        return """
            QPushButton {
                background-color: #333333;
                border: 1px solid #666666;
                color: #cccccc;
                padding: 12px 20px;
                text-align: center;
                font-size: 15px;
                font-weight: 500;
                border-radius: 12px;
                font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", sans-serif;
            }
            QPushButton:checked {
                background-color: #cc0000;
                color: white;
                border: 1px solid #ff0000;
            }
            QPushButton:hover {
                background-color: #404040;
                border: 1px solid #cc0000;
            }
            QPushButton:checked:hover {
                background-color: #ff0000;
            }
        """

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    # Set dark black and red palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(26, 26, 26))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(0, 0, 0))
    palette.setColor(QPalette.AlternateBase, QColor(51, 51, 51))
    palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(51, 51, 51))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(204, 0, 0))
    palette.setColor(QPalette.Highlight, QColor(204, 0, 0))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    window = TaekwondoApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()