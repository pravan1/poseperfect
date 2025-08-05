import cv2
import sys
import time
from optimized_camera import OptimizedCamera
from optimized_pose_detector import OptimizedPoseDetector

def main():
    print("Starting Optimized Taekwondo Pose Detection System...")
    print("Press 'q' to quit, 'r' to reset detection")
    print("-" * 50)
    
    # Initialize camera and detector
    camera = OptimizedCamera(camera_index=0)
    detector = OptimizedPoseDetector()
    
    # Start camera
    if not camera.start():
        print("Failed to start camera!")
        return
    
    print("Camera started successfully!")
    print("Waiting for camera to stabilize...")
    time.sleep(1)
    
    # FPS tracking
    fps_start_time = time.time()
    frame_count = 0
    display_fps = 0
    
    # Main loop
    try:
        while True:
            # Get frame from camera
            frame = camera.get_frame()
            
            if frame is None:
                continue
            
            # Process frame for pose detection
            analysis = detector.process_frame(frame)
            
            # Draw analysis on frame
            display_frame = detector.draw_analysis(frame, analysis)
            
            # Calculate and display FPS
            frame_count += 1
            current_time = time.time()
            if current_time - fps_start_time > 1.0:
                display_fps = frame_count / (current_time - fps_start_time)
                frame_count = 0
                fps_start_time = current_time
            
            # Add system info overlay
            cv2.putText(display_frame, f"System FPS: {display_fps:.1f}", 
                       (10, display_frame.shape[0] - 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(display_frame, f"Camera FPS: {camera.get_fps():.1f}", 
                       (10, display_frame.shape[0] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Status indicator
            if analysis['pose_detected']:
                status_color = (0, 255, 0)  # Green
                status_text = "POSE DETECTED"
            else:
                status_color = (0, 0, 255)  # Red
                status_text = "NO POSE"
            
            cv2.putText(display_frame, status_text, 
                       (display_frame.shape[1] - 150, display_frame.shape[0] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
            
            # Print console feedback periodically
            if frame_count % 30 == 0 and analysis['pose_detected']:
                print(f"\nPose Analysis:")
                print(f"  Visibility: {analysis['visibility_score']:.2f}")
                print(f"  Confidence: {analysis['detection_confidence']:.2%}")
                if analysis['angles']:
                    print(f"  Detected angles: {', '.join(analysis['angles'].keys())}")
                if analysis['feedback']:
                    print(f"  Feedback: {', '.join(analysis['feedback'][:2])}")
            
            # Display the frame
            cv2.imshow('Optimized Taekwondo Pose Detection', display_frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                print("\nResetting detection...")
                detector = OptimizedPoseDetector()
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("\nCleaning up...")
        camera.stop()
        detector.close()
        cv2.destroyAllWindows()
        print("Done!")

if __name__ == "__main__":
    main()