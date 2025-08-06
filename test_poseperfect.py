"""
Quick test script to verify PosePerfect.AI is working correctly
"""

import sys
import os
import cv2

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    try:
        import PyQt5
        print("[OK] PyQt5 imported successfully")
    except ImportError as e:
        print(f"[FAIL] PyQt5 import failed: {e}")
        return False
    
    try:
        import mediapipe
        print("[OK] MediaPipe imported successfully")
    except ImportError as e:
        print(f"[FAIL] MediaPipe import failed: {e}")
        return False
    
    try:
        import pyttsx3
        print("[OK] pyttsx3 imported successfully")
    except ImportError as e:
        print(f"[FAIL] pyttsx3 import failed: {e}")
        return False
    
    try:
        import numpy
        print("[OK] NumPy imported successfully")
    except ImportError as e:
        print(f"[FAIL] NumPy import failed: {e}")
        return False
    
    return True

def test_modules():
    """Test PosePerfect modules"""
    print("\nTesting PosePerfect modules...")
    
    try:
        from pose_detector import PoseDetector
        print("[OK] PoseDetector module loaded")
    except ImportError as e:
        print(f"[FAIL] PoseDetector import failed: {e}")
        return False
    
    try:
        from pose_comparator import PoseComparator
        print("[OK] PoseComparator module loaded")
    except ImportError as e:
        print(f"[FAIL] PoseComparator import failed: {e}")
        return False
    
    try:
        from voice_feedback import VoiceFeedback
        print("[OK] VoiceFeedback module loaded")
    except ImportError as e:
        print(f"[FAIL] VoiceFeedback import failed: {e}")
        return False
    
    return True

def test_reference_images():
    """Test reference images exist"""
    print("\nChecking reference images...")
    
    reference_dir = "reference_poses"
    if not os.path.exists(reference_dir):
        print(f"[FAIL] Reference poses directory not found")
        return False
    
    for i in range(1, 5):
        pose_file = os.path.join(reference_dir, f"pose{i}.jpg")
        if os.path.exists(pose_file):
            # Try to load the image
            img = cv2.imread(pose_file)
            if img is not None:
                h, w = img.shape[:2]
                print(f"[OK] pose{i}.jpg loaded successfully ({w}x{h})")
            else:
                print(f"[FAIL] pose{i}.jpg exists but couldn't be loaded")
                return False
        else:
            print(f"[FAIL] pose{i}.jpg not found")
            print(f"  Please add bodybuilding pose images to {reference_dir}/")
            return False
    
    return True

def test_camera():
    """Test camera access"""
    print("\nTesting camera access...")
    
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print("[OK] Camera is working")
            cap.release()
            return True
        else:
            print("[FAIL] Camera opened but couldn't read frame")
            cap.release()
            return False
    else:
        print("[FAIL] Camera not accessible")
        print("  Make sure your webcam is connected and not in use")
        return False

def test_pose_detection():
    """Test pose detection on a sample frame"""
    print("\nTesting pose detection...")
    
    try:
        from pose_detector import PoseDetector
        detector = PoseDetector()
        
        # Try with first reference image
        test_img = cv2.imread("reference_poses/pose1.jpg")
        if test_img is not None:
            results = detector.process_frame(test_img)
            if results['pose_detected']:
                print("[OK] Pose detection working on reference image")
                print(f"  Detected {len(results['landmarks'])} landmarks")
            else:
                print("[FAIL] No pose detected in reference image")
            
            detector.close()
            return results['pose_detected']
        else:
            print("[FAIL] Couldn't load test image")
            return False
            
    except Exception as e:
        print(f"[FAIL] Pose detection test failed: {e}")
        return False

def test_voice():
    """Test voice feedback system"""
    print("\nTesting voice feedback...")
    
    try:
        from voice_feedback import VoiceFeedback
        voice = VoiceFeedback()
        
        if voice.test_voice():
            print("[OK] Voice feedback system is working")
            print("  You should have heard a test message")
            return True
        else:
            print("[WARN] Voice feedback system may not be available")
            print("  The app will still work without voice")
            return True  # Not critical
            
    except Exception as e:
        print(f"[WARN] Voice test failed: {e}")
        print("  The app will still work without voice")
        return True  # Not critical

def main():
    print("=" * 50)
    print("PosePerfect.AI System Test")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Run tests
    if not test_imports():
        all_tests_passed = False
        print("\n[WARN] Please install missing dependencies:")
        print("  pip install -r requirements.txt")
    
    if not test_modules():
        all_tests_passed = False
        print("\n[WARN] PosePerfect modules not working correctly")
    
    if not test_reference_images():
        all_tests_passed = False
        print("\n[WARN] Reference images missing or corrupted")
        print("  Add pose1.jpg, pose2.jpg, pose3.jpg, pose4.jpg to reference_poses/")
    
    if not test_camera():
        print("\n[WARN] Camera not working - app can still analyze reference images")
    
    if test_imports() and test_modules():
        test_pose_detection()
        test_voice()
    
    # Summary
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("[OK] All critical tests passed!")
        print("  You can now run: python main_ui.py")
    else:
        print("[WARN] Some tests failed. Please fix the issues above.")
    print("=" * 50)

if __name__ == "__main__":
    main()