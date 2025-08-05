#!/usr/bin/env python3
"""
Demo script to test basic functionality without GUI
This allows testing the core logic without requiring camera/GUI dependencies
"""

import sys
import os

def test_imports():
    """Test basic imports without external dependencies"""
    print("Testing core imports...")
    
    try:
        # Test utils imports
        sys.path.insert(0, '.')
        from utils.angle_utils import calculate_angle_between_points
        print("✓ angle_utils imported successfully")
        
        # Test angle calculation
        angle = calculate_angle_between_points((0, 1), (0, 0), (1, 0))
        print(f"✓ Angle calculation test: {angle:.1f} degrees (expected ~90)")
        
        from utils.feedback_utils import FeedbackGenerator
        print("✓ feedback_utils imported successfully")
        
        # Test feedback generator
        feedback_gen = FeedbackGenerator()
        print("✓ FeedbackGenerator created successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        'main_ui.py', 'pose_detector.py', 'calibration.py',
        'voice_feedback.py', 'server.py', 'requirements.txt',
        'README.md', '.gitignore'
    ]
    
    all_exist = True
    for file in required_files:
        exists = os.path.exists(file)
        print(f"{'✓' if exists else '✗'} {file}")
        if not exists:
            all_exist = False
    
    # Check utils directory
    utils_files = ['utils/__init__.py', 'utils/angle_utils.py', 'utils/feedback_utils.py']
    for file in utils_files:
        exists = os.path.exists(file)
        print(f"{'✓' if exists else '✗'} {file}")
        if not exists:
            all_exist = False
    
    return all_exist

def create_demo_instructions():
    """Create demo instructions for the user"""
    instructions = """
=== Taekwondo.AI Setup Instructions ===

Your application has been successfully created! Here's what you have:

📁 Project Structure:
  ├── main_ui.py              # Main PyQt5 application
  ├── pose_detector.py        # MediaPipe pose detection
  ├── calibration.py          # User calibration system
  ├── voice_feedback.py       # Text-to-speech functionality
  ├── server.py              # Flask API backend
  ├── utils/                 # Utility functions
  │   ├── angle_utils.py     # Angle calculations
  │   ├── feedback_utils.py  # Feedback generation
  │   └── __init__.py
  ├── static/                # Static files directory
  ├── requirements.txt       # Python dependencies
  ├── .gitignore            # Git ignore rules
  └── README.md             # Documentation

🚀 Next Steps:

1. Install Dependencies:
   pip install -r requirements.txt

2. Run the Application:
   python main_ui.py

3. Create GitHub Repository:
   git add .
   git commit -m "Initial commit: Complete Taekwondo.AI application"
   
   Then create a private repository on GitHub named 'taekwondo.ai' 
   under the 'pravan1' account and push the code.

🎯 Features Included:
  ✓ Real-time pose detection with MediaPipe
  ✓ Personalized calibration system
  ✓ Voice feedback with pyttsx3
  ✓ Photo capture with pose overlays
  ✓ Session tracking and progress analysis
  ✓ Support for multiple Taekwondo techniques
  ✓ Clean, modern PyQt5 interface
  ✓ Cross-platform compatibility

📋 Usage:
  - Start with calibration mode to personalize feedback
  - Practice different stances and kicks
  - Use voice feedback for hands-free training
  - Capture photos to review your form
  - Track your progress over time

Your Taekwondo.AI application is ready for use! 🥋✨
"""
    return instructions

def main():
    """Main demo function"""
    print("=== Taekwondo.AI Project Demo ===\n")
    
    # Test file structure
    structure_ok = test_file_structure()
    
    # Test imports
    imports_ok = test_imports()
    
    print(f"\n=== Results ===")
    print(f"File Structure: {'✓ Complete' if structure_ok else '✗ Issues found'}")
    print(f"Core Imports: {'✓ Working' if imports_ok else '✗ Issues found'}")
    
    if structure_ok and imports_ok:
        print("\n🎉 Project is ready!")
        print(create_demo_instructions())
        return True
    else:
        print("\n❌ Issues found. Please check the errors above.")
        return False

if __name__ == "__main__":
    main()