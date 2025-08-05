# Taekwondo.AI 🥋

A cross-platform desktop application that helps users learn and practice Taekwondo moves at home using computer vision and real-time pose analysis.

![Taekwondo.AI](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-Private-red.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## 🎯 Features

### Core Functionality
- **Real-time Pose Detection**: Uses MediaPipe to analyze your Taekwondo form in real-time
- **Personalized Calibration**: Calibrates to your body dimensions for accurate feedback
- **Visual & Audio Feedback**: On-screen guidance with optional voice instructions
- **Photo Capture**: Save snapshots of your poses with skeletal overlays for review
- **Progress Tracking**: Session summaries with improvement suggestions

### Supported Techniques
- **Stances**: Front stance, horse stance, back stance
- **Kicks**: Front kick, roundhouse kick, side kick  
- **Blocks**: Low block, middle block, high block

### User Experience
- **Beginner-Friendly**: Clean, intuitive interface designed for all skill levels
- **Offline Capable**: Works completely offline once installed
- **Cross-Platform**: Runs on Windows, macOS, and Linux

## 🛠 Technology Stack

- **Frontend**: PyQt5 for the desktop interface
- **Backend**: Flask API for pose processing
- **Computer Vision**: MediaPipe for pose detection and OpenCV for camera handling
- **Audio**: pyttsx3 for text-to-speech feedback
- **Data Processing**: NumPy for mathematical calculations

## 📋 Requirements

### System Requirements
- Python 3.8 or higher
- Webcam (built-in or external)
- 4GB RAM minimum (8GB recommended)
- Windows 10/11, macOS 10.14+, or Linux Ubuntu 18.04+

### Python Dependencies
See `requirements.txt` for complete list. Main dependencies:
- PyQt5==5.15.9
- Flask==2.3.3
- mediapipe==0.10.7
- opencv-python==4.8.1.78
- pyttsx3==2.90

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/pravan1/taekwondo.ai.git
cd taekwondo.ai
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\\Scripts\\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Test Installation
```bash
python main_ui.py
```

## 📖 Usage Guide

### Quick Start
1. **Launch the Application**
   ```bash
   python main_ui.py
   ```

2. **Initial Setup**
   - Click "Start Camera" to activate your webcam
   - Select "Calibration Mode" from the dropdown
   - Click "Start Calibration" and follow the on-screen instructions

3. **Training Session**
   - Switch to "Practice Mode"
   - Select a Taekwondo move from the dropdown
   - Follow the real-time feedback to improve your form

### Calibration Process
The calibration helps personalize feedback to your body dimensions:

1. **Neutral Pose**: Stand relaxed with arms at your sides
2. **T-Pose**: Extend arms out horizontally  
3. **Front Stance**: Perform your best front stance
4. **Complete**: Calibration data is saved for future sessions

### Training Tips
- Ensure good lighting and clear camera view
- Wear contrasting colors for better pose detection
- Start with basic stances before advancing to kicks
- Use voice feedback for hands-free training

## 🎮 Interface Overview

### Main Window Layout
- **Left Panel**: Live camera feed with pose landmarks
- **Right Panel**: Controls, feedback, and session info

### Key Controls
- **Start/Stop Camera**: Control webcam activation
- **Capture Photo**: Save pose snapshots with analysis
- **Mode Selection**: Switch between Practice and Calibration
- **Move Selection**: Choose specific techniques to practice
- **Voice Toggle**: Enable/disable audio feedback

### Feedback System
- **Visual Indicators**: Red outlines for errors, green for good form
- **Text Feedback**: Real-time suggestions in the feedback panel
- **Pose Quality Bar**: Overall form score (0-100)
- **Voice Instructions**: Optional audio guidance

## 📊 Session Tracking

Each training session provides:
- **Duration**: Time spent practicing
- **Poses Analyzed**: Number of poses processed
- **Average Quality**: Overall performance score
- **Common Errors**: Most frequent mistakes to work on
- **Improvement Trend**: Progress over the session
- **Next Steps**: Personalized suggestions for improvement

## 🔧 Advanced Features

### API Endpoints
The Flask backend provides REST API endpoints:
- `GET /api/health` - Health check
- `POST /api/analyze_pose` - Analyze pose from image
- `POST /api/calibration/start` - Start calibration
- `GET /api/session/summary` - Get session statistics

### Customization
- **Feedback Sensitivity**: Adjust pose analysis thresholds
- **Voice Settings**: Change speech rate and volume
- **Move Difficulty**: Configure beginner/intermediate/advanced modes

## 📁 Project Structure

```
taekwondo.ai/
├── main_ui.py              # Main PyQt5 application
├── pose_detector.py        # MediaPipe pose detection
├── calibration.py          # User calibration system
├── voice_feedback.py       # Text-to-speech functionality
├── server.py              # Flask API backend
├── utils/                 # Utility functions
│   ├── angle_utils.py     # Angle calculations
│   ├── feedback_utils.py  # Feedback generation
│   └── __init__.py
├── static/                # Static files and captures
│   └── captures/          # Saved pose photos
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🚨 Troubleshooting

### Common Issues

**Camera Not Working**
- Check webcam permissions in system settings
- Try different camera index in code (0, 1, 2...)
- Restart the application

**Poor Pose Detection**
- Ensure good lighting conditions
- Stand further from camera for full body view
- Wear fitted clothing with good contrast

**Voice Feedback Not Working**  
- Check system audio settings
- Install additional TTS voices if needed
- Try running as administrator (Windows)

**Application Won't Start**
- Verify Python version (3.8+)
- Check all dependencies are installed
- Try creating a fresh virtual environment

### Performance Optimization
- Close other camera applications
- Use a dedicated webcam for better quality
- Reduce background applications for smoother processing

## 🤝 Contributing

This is a private repository. For bug reports or feature suggestions, please contact the development team.

## 📄 License

This project is proprietary software. All rights reserved.

## 🙏 Acknowledgments

- **MediaPipe Team** - For the excellent pose detection framework
- **PyQt5 Community** - For the robust GUI framework  
- **Taekwondo Community** - For technique guidance and feedback
- **OpenCV Contributors** - For computer vision tools

## 📞 Support

For technical support or questions:
- Create an issue in the private repository
- Contact the development team directly
- Check the troubleshooting section above

---

**Happy Training! 🥋✨**

*Improve your Taekwondo skills with the power of AI and computer vision.*