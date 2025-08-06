# PosePerfect.AI - AI-Powered Bodybuilding Pose Analyzer

PosePerfect.AI is a cross-platform desktop application that helps bodybuilders refine their posing routines by comparing their real-time webcam pose to professional reference images. Built using PyQt5 for the frontend and MediaPipe for pose detection, the app provides visual overlays, voice guidance, and performance scoring to improve symmetry, muscle engagement, and stage presence.

## Core Features

### Pose Detection with Comparison
- Real-time skeletal landmark extraction using MediaPipe Pose
- Compare live poses to reference poses (pose1.jpg - pose4.jpg)
- Highlight deviations in angle, symmetry, and alignment
- Overlay pose landmarks on both live and target images

### Pose Mode Selection
Choose from classic bodybuilding poses:
- Front Double Biceps
- Side Chest
- Back Lat Spread
- Rear Double Biceps

### Real-Time Feedback
- Visual error indicators with colored overlays
- Text-based corrections and guidance
- Voice feedback for hands-free training
- Percent match scoring based on joint angles and symmetry

### Photo Comparison Mode
- Side-by-side visual comparison of webcam vs target
- Snapshot capture for progress tracking
- Load custom reference images

### Voice Feedback
- Offline guidance using pyttsx3
- Pose-specific corrections
- Encouragement and scoring announcements

## Technology Stack

- **Frontend**: PyQt5
- **Pose Detection**: MediaPipe (Pose module)
- **Camera**: OpenCV
- **Voice**: pyttsx3 (offline TTS)
- **Pose Comparison**: NumPy angle metrics between key joints

## Installation

1. Clone the repository:
```bash
git clone https://github.com/pravan1/poseperfect.ai.git
cd poseperfect.ai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Add your reference pose images to the `reference_poses` folder:
   - pose1.jpg - Front Double Biceps
   - pose2.jpg - Side Chest
   - pose3.jpg - Back Lat Spread
   - pose4.jpg - Rear Double Biceps

## How to Run

```bash
python main_ui.py
```

## Usage

1. **Start the Application**: Launch the app and allow camera access
2. **Select a Pose**: Choose from the dropdown menu which bodybuilding pose to practice
3. **Position Yourself**: Stand in view of the camera with your full body visible
4. **Follow Feedback**: Watch the visual overlays and listen to voice guidance
5. **Track Progress**: Monitor your scores for symmetry, alignment, and overall match

## Pose Accuracy Explanation

The app analyzes your pose using three key metrics:

- **Alignment Score** (70% weight): Measures how closely your joint angles match the reference pose
- **Symmetry Score** (30% weight): Evaluates left-right body balance
- **Overall Score**: Weighted combination providing a final percentage match

Visual feedback includes:
- Red circles: Poor alignment (>15° deviation)
- Yellow circles: Moderate alignment (10-15° deviation)
- Green text: Good performance (>80% match)

## File Structure

```
poseperfect.ai/
│
├── main_ui.py              # PyQt5 interface
├── pose_detector.py        # MediaPipe pose processing
├── pose_comparator.py      # Angle-based comparison logic
├── voice_feedback.py       # Voice correction system
├── reference_poses/        # Reference images folder
│   ├── pose1.jpg
│   ├── pose2.jpg
│   ├── pose3.jpg
│   └── pose4.jpg
├── static/                 # Captured snapshots
├── requirements.txt        # Dependencies
├── README.md              # This file
└── .gitignore            # Git ignore file
```

## System Requirements

- Python 3.8 or higher
- Webcam
- Windows/Mac/Linux desktop environment
- Minimum 4GB RAM
- Audio output for voice feedback (optional)

## Tips for Best Results

1. **Lighting**: Ensure good, even lighting without harsh shadows
2. **Camera Position**: Place camera at chest height, 6-8 feet away
3. **Clothing**: Wear form-fitting clothes in contrasting colors
4. **Background**: Use a plain background for better detection
5. **Full Body**: Ensure your entire body is visible in frame

## Future Enhancements

- [ ] Additional poses (Most Muscular, Ab & Thigh, etc.)
- [ ] Progress tracking over time
- [ ] Video recording and playback
- [ ] Multi-angle camera support
- [ ] Competition prep timer
- [ ] Pose transition training

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under the MIT License.

## Acknowledgments

- MediaPipe team for the excellent pose detection library
- Bodybuilding community for pose standards and techniques
- PyQt5 for the robust desktop framework

---

**PosePerfect.AI** - Your virtual posing coach, available 24/7 to help you achieve competition-ready form!