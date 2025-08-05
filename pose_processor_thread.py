from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
import queue
import time

class PoseProcessorThread(QThread):
    """Separate thread for pose processing to improve performance"""
    pose_analyzed = pyqtSignal(dict)
    
    def __init__(self, pose_detector):
        super().__init__()
        self.pose_detector = pose_detector
        self.frame_queue = queue.Queue(maxsize=2)  # Small buffer to prevent blocking
        self.running = False
        self.processing_enabled = True
        self.last_process_time = 0
        
    def add_frame(self, frame, mode='practice'):
        """Add a frame to be processed (non-blocking)"""
        try:
            # Clear old frames to process only latest
            while not self.frame_queue.empty():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    break
            
            # Add new frame without blocking
            self.frame_queue.put_nowait((frame, mode))
        except queue.Full:
            # Queue is full, skip this frame
            pass
    
    def start_processing(self):
        """Start the processing thread"""
        self.running = True
        self.start()
    
    def stop_processing(self):
        """Stop the processing thread"""
        self.running = False
        # Add dummy frame to unblock the queue
        try:
            self.frame_queue.put_nowait((None, None))
        except:
            pass
        self.wait(200)  # Wait maximum 200ms
        if self.isRunning():
            self.terminate()  # Force terminate if still running
            self.wait()
    
    def toggle_processing(self, enabled):
        """Enable/disable processing temporarily"""
        self.processing_enabled = enabled
    
    def run(self):
        """Main processing loop"""
        while self.running:
            try:
                if not self.processing_enabled:
                    time.sleep(0.05)
                    continue
                    
                # Get frame from queue with shorter timeout for responsiveness
                frame_data = self.frame_queue.get(timeout=0.02)
                
                # Check for stop signal
                if frame_data[0] is None:
                    break
                    
                frame, mode = frame_data
                
                # Rate limit processing to prevent overload
                current_time = time.time()
                if current_time - self.last_process_time < 0.05:  # Max 20 FPS processing
                    continue
                self.last_process_time = current_time
                
                # Process the frame
                analysis = self.pose_detector.process_frame(frame)
                analysis['mode'] = mode
                
                # Emit the results
                self.pose_analyzed.emit(analysis)
                
            except queue.Empty:
                # No frames to process
                continue
            except Exception as e:
                print(f"Error in pose processing: {e}")
                time.sleep(0.01)