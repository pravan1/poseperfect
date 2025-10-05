# PosePerfect.AI - AI-Powered Bodybuilding Pose Analyzer

PosePerfect.AI is a modern cross-platform desktop application that helps bodybuilders perfect their posing routines through an intuitive Apple-inspired guided workflow. Built with PyQt5, MediaPipe Pose, and advanced pose comparison algorithms, the app provides a 4-pose guided session with auto-capture, detailed feedback, voice coaching, and session export.

## ✨ Core Features

### 🎯 Guided 4-Pose Workflow
- **Wizard-style interface** with Welcome → Pose Steps → Summary screens
- **Automatic pose sequence**: Front Double Biceps → Side Chest → Back Lat Spread → Rear Double Biceps
- **5-second countdown** with visual overlay for each pose capture
- **Auto-capture and analysis** at the end of each countdown
- **Retry or Next** options after reviewing feedback

### 🎨 Apple-Style Modern UI
- **Cool blue-to-white gradient** background
- **Glassy translucent cards** with subtle depth and shadows
- **Rounded corners** (20-24px radius)
- **System fonts** (SF Pro on macOS, Segoe UI on Windows)
- **Smooth animations** for screen transitions

### 📊 Advanced Pose Comparison
- **Joint-angle analysis** with per-joint delta calculations
- **Symmetry scoring** (left-right balance)
- **Alignment scoring** (pose match accuracy)
- **Overall score** (70% alignment + 30% symmetry)
- **Actionable feedback**: "Raise left elbow 10°", "Open lats", etc.

### 🎤 Smart Voice Coaching
- **Short, specific lines** (≤8 words each)
- **Top 3 tips per pose** delivered with pacing
- **Adjustable speech rate** (1.1× normal by default)
- **Optional voice guidance** toggle in Welcome screen

### 💾 Session Persistence
- **Automatic session folders**: `static/session_{timestamp}/`
- **Per-pose captures**: `pose1_user.jpg`, `pose2_user.jpg`, etc.
- **Per-pose feedback JSON**: joint angles, deltas, scores, tips
- **Summary export**: `summary.json` + `contact_sheet.png`
- **Contact sheet**: Horizontal strip of all 4 pose captures with labels

### 📸 Real-Time Camera Feed
- **Live video preview** with pose landmarks overlay
- **Countdown overlay** (5 → 0) centered on camera pane
- **Instant feedback** after capture with annotated comparison image

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

### Starting a Session

1. **Launch the app**: `python main_ui.py`
2. **Welcome screen**:
   - Select pose sequence (default: Classic 4-Pose Flow)
   - Toggle voice guidance on/off
   - Click "Start Session"

### Completing Each Pose

3. **Pose step screen** (repeated for 4 poses):
   - View reference image and pose name on the right
   - Position yourself in the camera view (left panel)
   - Read the tips (lighting, full body visible, etc.)
   - Click **Start** to begin 5-second countdown
   - **Hold the pose** until the camera captures at 0
   - Review your **score and feedback** on the right panel
   - Choose **Retry** (redo this pose) or **Next Pose** (continue)

### Viewing Results

4. **Summary screen** (after all 4 poses):
   - See thumbnails of all 4 captured poses with scores
   - Review top 3 tips overall
   - Click **Export Session** to save summary.json + contact_sheet.png
   - Click **New Session** to start over

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
├── main_ui.py              # PyQt5 wizard UI with Apple-style design
├── pose_detector.py        # MediaPipe pose processing + capture_frame
├── pose_comparator.py      # compare_pose function + PoseComparator class
├── voice_feedback.py       # Voice system + speak_tips method
├── utils/
│   ├── __init__.py
│   ├── angle_utils.py      # Angle calculation helpers
│   ├── feedback_utils.py   # Feedback generation
│   └── image_overlay.py    # Overlay drawing + contact sheet creation
├── reference_poses/        # Reference images folder
│   ├── pose1.jpg           # Front Double Biceps
│   ├── pose2.jpg           # Side Chest
│   ├── pose3.jpg           # Back Lat Spread
│   └── pose4.jpg           # Rear Double Biceps
├── static/                 # Session data (created automatically)
│   └── session_{timestamp}/
│       ├── pose1_user.jpg
│       ├── pose1_feedback.json
│       ├── pose2_user.jpg
│       ├── pose2_feedback.json
│       ├── pose3_user.jpg
│       ├── pose3_feedback.json
│       ├── pose4_user.jpg
│       ├── pose4_feedback.json
│       ├── summary.json
│       └── contact_sheet.png
├── test_poseperfect.py     # System tests
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

## New in This Version (v2.0)

- ✅ Apple-style gradient UI with translucent cards
- ✅ 4-pose guided wizard workflow
- ✅ 5-second auto-capture countdown
- ✅ Per-pose detailed feedback with joint-angle deltas
- ✅ Session export (JSON + contact sheet image)
- ✅ Smart voice coaching with batched tips
- ✅ Modern typography and rounded corners
- ✅ Retry/Next flow for each pose

## Future Enhancements

- [ ] Additional poses (Most Muscular, Ab & Thigh, etc.)
- [ ] Progress tracking over time (trend graphs)
- [ ] Video recording and playback
- [ ] Multi-angle camera support
- [ ] Competition prep timer
- [ ] Pose transition training
- [ ] Custom pose sequences
- [ ] Export to PDF report

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