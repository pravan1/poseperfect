"""Test script to verify pose detection is working"""
import cv2
import mediapipe as mp
import numpy as np

def test_pose_detection():
    # Initialize MediaPipe
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    
    # Create pose detector with optimized settings
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,  # Try medium complexity for better detection
        enable_segmentation=False,
        min_detection_confidence=0.5,  # Lower threshold for better detection
        min_tracking_confidence=0.5,
        smooth_landmarks=True
    )
    
    # Open camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    # Set camera buffer to minimum
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    print("Starting pose detection test...")
    print("Press 'q' to quit")
    print("Stand in front of the camera with your full body visible")
    
    frame_count = 0
    detected_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break
        
        # Mirror the frame
        frame = cv2.flip(frame, 1)
        frame_count += 1
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = pose.process(rgb_frame)
        
        # Check if pose is detected
        if results.pose_landmarks:
            detected_count += 1
            
            # Draw landmarks
            mp_drawing.draw_landmarks(
                frame, 
                results.pose_landmarks, 
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
            )
            
            # Add detection status
            cv2.putText(frame, "POSE DETECTED", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Show landmark visibility scores
            if results.pose_landmarks.landmark:
                nose = results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
                visibility_text = f"Nose visibility: {nose.visibility:.2f}"
                cv2.putText(frame, visibility_text, (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        else:
            cv2.putText(frame, "NO POSE DETECTED", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Show detection rate
        if frame_count > 0:
            detection_rate = (detected_count / frame_count) * 100
            rate_text = f"Detection rate: {detection_rate:.1f}% ({detected_count}/{frame_count})"
            cv2.putText(frame, rate_text, (10, frame.shape[0] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Display the frame
        cv2.imshow('Pose Detection Test', frame)
        
        # Check for quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    pose.close()
    
    print(f"\nTest completed!")
    print(f"Total frames: {frame_count}")
    print(f"Frames with pose detected: {detected_count}")
    if frame_count > 0:
        print(f"Detection rate: {(detected_count/frame_count)*100:.1f}%")

if __name__ == "__main__":
    test_pose_detection()