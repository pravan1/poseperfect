#!/usr/bin/env python3
"""
Test script to verify project structure and basic functionality
without requiring all dependencies to be installed.
"""

import os
import sys
import ast

def check_file_exists(filepath):
    """Check if a file exists and return status"""
    exists = os.path.exists(filepath)
    print(f"{'✓' if exists else '✗'} {filepath}")
    return exists

def check_python_syntax(filepath):
    """Check if a Python file has valid syntax"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        ast.parse(source)
        print(f"  ✓ Valid Python syntax")
        return True
    except SyntaxError as e:
        print(f"  ✗ Syntax error: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error reading file: {e}")
        return False

def test_project_structure():
    """Test the complete project structure"""
    print("=== Taekwondo.AI Project Structure Test ===\n")
    
    required_files = [
        'main_ui.py',
        'pose_detector.py', 
        'calibration.py',
        'voice_feedback.py',
        'server.py',
        'requirements.txt',
        'README.md',
        '.gitignore',
        'utils/__init__.py',
        'utils/angle_utils.py',
        'utils/feedback_utils.py'
    ]
    
    required_dirs = [
        'utils',
        'static'
    ]
    
    print("1. Checking required files:")
    file_results = []
    for file in required_files:
        result = check_file_exists(file)
        file_results.append(result)
        
        # Check Python syntax for .py files
        if file.endswith('.py') and result:
            check_python_syntax(file)
    
    print("\n2. Checking required directories:")
    dir_results = []
    for directory in required_dirs:
        result = os.path.isdir(directory)
        print(f"{'✓' if result else '✗'} {directory}/")
        dir_results.append(result)
    
    print("\n3. Checking requirements.txt content:")
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            requirements = f.read().strip().split('\n')
        
        expected_packages = ['PyQt5', 'Flask', 'mediapipe', 'opencv-python', 'pyttsx3']
        found_packages = []
        
        for req in requirements:
            package_name = req.split('==')[0].split('>=')[0].strip()
            if package_name in expected_packages:
                found_packages.append(package_name)
                print(f"  ✓ {req}")
        
        missing = set(expected_packages) - set(found_packages)
        if missing:
            print(f"  ✗ Missing packages: {', '.join(missing)}")
    
    print("\n4. Checking import structure:")
    # Test utils package structure
    try:
        sys.path.insert(0, '.')
        
        # Check if utils can be imported as a package
        import utils
        print("  ✓ utils package imports successfully")
        
        # Check individual modules
        from utils import angle_utils
        print("  ✓ utils.angle_utils imports successfully")
        
        from utils import feedback_utils  
        print("  ✓ utils.feedback_utils imports successfully")
        
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
    
    print("\n=== Test Summary ===")
    files_passed = sum(file_results)
    dirs_passed = sum(dir_results)
    
    print(f"Files: {files_passed}/{len(required_files)} ({'✓' if files_passed == len(required_files) else '✗'})")
    print(f"Directories: {dirs_passed}/{len(required_dirs)} ({'✓' if dirs_passed == len(required_dirs) else '✗'})")
    
    if files_passed == len(required_files) and dirs_passed == len(required_dirs):
        print("\n🎉 Project structure is complete and ready!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the application: python main_ui.py")
        print("3. Create GitHub repository and push code")
        return True
    else:
        print("\n❌ Project structure has issues that need to be resolved.")
        return False

if __name__ == "__main__":
    test_project_structure()