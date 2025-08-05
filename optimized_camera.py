import cv2
import numpy as np
import threading
import queue
import time
from typing import Optional, Callable

class OptimizedCamera:
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.cap = None
        self.running = False
        self.capture_thread = None
        self.frame_queue = queue.Queue(maxsize=2)
        self.last_frame = None
        self.fps = 0
        self.last_fps_time = time.time()
        self.frame_count = 0
        
    def start(self) -> bool:
        """Start the camera capture"""
        if self.cap is not None:
            return True
            
        # Try different backends for better performance
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
        
        for backend in backends:
            self.cap = cv2.VideoCapture(self.camera_index, backend)
            if self.cap.isOpened():
                print(f"Camera opened with backend: {backend}")
                break
        
        if not self.cap or not self.cap.isOpened():
            print("Failed to open camera")
            return False
        
        # Configure camera for optimal performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer for low latency
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        
        # Read and discard first few frames to stabilize
        for _ in range(5):
            self.cap.read()
        
        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        
        return True
    
    def _capture_loop(self):
        """Main capture loop running in separate thread"""
        while self.running:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    # Mirror the frame for natural interaction
                    frame = cv2.flip(frame, 1)
                    
                    # Clear queue and add latest frame (drop old frames)
                    try:
                        while not self.frame_queue.empty():
                            self.frame_queue.get_nowait()
                    except queue.Empty:
                        pass
                    
                    try:
                        self.frame_queue.put_nowait(frame)
                        self.last_frame = frame
                        
                        # Calculate FPS
                        self.frame_count += 1
                        current_time = time.time()
                        if current_time - self.last_fps_time > 1.0:
                            self.fps = self.frame_count / (current_time - self.last_fps_time)
                            self.frame_count = 0
                            self.last_fps_time = current_time
                            
                    except queue.Full:
                        pass
            else:
                time.sleep(0.01)
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get the latest frame"""
        try:
            # Try to get from queue first
            frame = self.frame_queue.get_nowait()
            return frame
        except queue.Empty:
            # Return last known frame if queue is empty
            return self.last_frame
    
    def get_fps(self) -> float:
        """Get current FPS"""
        return self.fps
    
    def stop(self):
        """Stop the camera capture"""
        self.running = False
        
        if self.capture_thread:
            self.capture_thread.join(timeout=1.0)
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        # Clear the queue
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                break
    
    def __del__(self):
        """Cleanup on deletion"""
        self.stop()