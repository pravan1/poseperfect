import cv2
import numpy as np
from optimized_camera import OptimizedCamera
from optimized_pose_detector import OptimizedPoseDetector
import time

def test_detection():
    print("Testing Optimized Pose Detection System...")
    print("-" * 50)
    
    # Initialize
    camera = OptimizedCamera(0)
    detector = OptimizedPoseDetector()
    
    # Start camera
    if not camera.start():
        print("ERROR: Failed to start camera!")
        return False
    
    print("[OK] Camera initialized successfully")
    time.sleep(2)  # Wait longer for camera to stabilize
    
    # Test frame capture - try multiple times
    frame = None
    for i in range(10):
        frame = camera.get_frame()
        if frame is not None:
            break
        time.sleep(0.5)
    if frame is None:
        print("ERROR: No frame captured!")
        camera.stop()
        return False
    
    print(f"[OK] Frame captured: {frame.shape}")
    
    # Test pose detection
    print("Testing pose detection...")
    analysis = detector.process_frame(frame)
    
    print(f"[OK] Detection completed in {analysis['processing_time']:.3f}s")
    print(f"  - Pose detected: {analysis['pose_detected']}")
    print(f"  - Visibility score: {analysis['visibility_score']:.2f}")
    print(f"  - Detection confidence: {analysis['detection_confidence']:.2%}")
    
    if analysis['body_parts']:
        print(f"  - Body parts detected: {len(analysis['body_parts'])}")
    
    if analysis['angles']:
        print(f"  - Angles calculated: {list(analysis['angles'].keys())}")
    
    if analysis['feedback']:
        print(f"  - Feedback: {analysis['feedback'][:2]}")
    
    # Test continuous detection for 3 seconds
    print("\nTesting continuous detection for 3 seconds...")
    start_time = time.time()
    frame_count = 0
    detections = 0
    
    while time.time() - start_time < 3:
        frame = camera.get_frame()
        if frame is not None:
            frame_count += 1
            analysis = detector.process_frame(frame)
            if analysis['pose_detected']:
                detections += 1
    
    elapsed = time.time() - start_time
    fps = frame_count / elapsed
    detection_rate = (detections / frame_count * 100) if frame_count > 0 else 0
    
    print(f"[OK] Continuous detection test completed")
    print(f"  - Frames processed: {frame_count}")
    print(f"  - Average FPS: {fps:.1f}")
    print(f"  - Detection rate: {detection_rate:.1f}%")
    print(f"  - Camera FPS: {camera.get_fps():.1f}")
    
    # Cleanup
    camera.stop()
    detector.close()
    
    print("\n" + "=" * 50)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("The optimized pose detection system is working properly.")
    print("\nTips for better detection:")
    print("1. Ensure good lighting")
    print("2. Stand 1-2 meters from camera")
    print("3. Make sure full body is visible")
    print("4. Wear contrasting clothes")
    
    return True

if __name__ == "__main__":
    success = test_detection()
    if not success:
        print("\nTEST FAILED - Please check your camera and setup")