from flask import Flask, request, jsonify, send_from_directory
import cv2
import numpy as np
import base64
import json
import os
from datetime import datetime
from pose_detector import TaekwondoPoseDetector
from calibration import UserCalibration
import threading
import time

app = Flask(__name__)

# Global instances
pose_detector = TaekwondoPoseDetector()
user_calibration = UserCalibration()

# Session tracking
session_data = {
    'start_time': None,
    'poses_analyzed': 0,
    'quality_scores': [],
    'errors_count': {},
    'feedback_count': {},
    'current_move': 'front_stance'
}

def reset_session():
    """Reset session tracking data"""
    global session_data
    session_data = {
        'start_time': datetime.now(),
        'poses_analyzed': 0,
        'quality_scores': [],
        'errors_count': {},
        'feedback_count': {},
        'current_move': 'front_stance'
    }

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'pose_detector_ready': pose_detector is not None,
        'calibration_status': user_calibration.is_calibrated()
    })

@app.route('/api/analyze_pose', methods=['POST'])
def analyze_pose():
    """Analyze pose from base64 encoded image"""
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        image_data = base64.b64decode(data['image'].split(',')[1])
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Analyze pose
        analysis = pose_detector.detect_pose(frame)
        
        # Update session data
        if session_data['start_time'] is None:
            reset_session()
        
        session_data['poses_analyzed'] += 1
        
        if analysis['pose_detected']:
            session_data['quality_scores'].append(analysis['pose_quality'])
            
            # Count errors and feedback
            for error in analysis.get('errors', []):
                session_data['errors_count'][error] = session_data['errors_count'].get(error, 0) + 1
            
            for feedback in analysis.get('feedback', []):
                session_data['feedback_count'][feedback] = session_data['feedback_count'].get(feedback, 0) + 1
        
        # Add session info to response
        analysis['session_info'] = get_session_summary()
        
        return jsonify(analysis)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze_move', methods=['POST'])
def analyze_move():
    """Analyze specific Taekwondo move"""
    try:
        data = request.json
        if not data or 'image' not in data or 'move' not in data:
            return jsonify({'error': 'Missing image or move data'}), 400
        
        # Decode image
        image_data = base64.b64decode(data['image'].split(',')[1])
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Basic pose analysis
        analysis = pose_detector.detect_pose(frame)
        
        if not analysis['pose_detected']:
            return jsonify({'error': 'No pose detected'}), 400
        
        # Analyze specific move
        move_name = data['move'].lower()
        session_data['current_move'] = move_name
        
        move_analysis = {}
        landmarks = analysis['landmarks']
        
        if move_name == 'front_stance':
            move_analysis = pose_detector.analyze_front_stance(landmarks, frame)
        elif move_name == 'roundhouse_kick':
            move_analysis = pose_detector.analyze_roundhouse_kick(landmarks, frame)
        else:
            move_analysis = {'feedback': [], 'errors': [f'Move analysis not implemented for {move_name}']}
        
        # Combine analyses
        combined_analysis = {
            'pose_detected': True,
            'pose_quality': analysis['pose_quality'],
            'general_feedback': analysis.get('feedback', []),
            'general_errors': analysis.get('errors', []),
            'move_feedback': move_analysis.get('feedback', []),
            'move_errors': move_analysis.get('errors', []),
            'move_name': move_name
        }
        
        return jsonify(combined_analysis)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calibration/start', methods=['POST'])
def start_calibration():
    """Start calibration process"""
    try:
        result = user_calibration.start_calibration_sequence(pose_detector)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calibration/step', methods=['POST'])
def calibration_step():
    """Process calibration step"""
    try:
        data = request.json
        if not data or 'image' not in data or 'step' not in data:
            return jsonify({'error': 'Missing image or step data'}), 400
        
        # Decode image
        image_data = base64.b64decode(data['image'].split(',')[1])
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Detect pose
        analysis = pose_detector.detect_pose(frame)
        
        if not analysis['pose_detected']:
            return jsonify({'error': 'No pose detected for calibration'})
        
        # Process calibration step
        step = data['step']
        frame_dimensions = (frame.shape[1], frame.shape[0])  # (width, height)
        
        if step == 1:
            result = user_calibration.capture_neutral_pose(analysis['landmarks'], frame_dimensions)
        elif step == 2:
            result = user_calibration.capture_t_pose(analysis['landmarks'], frame_dimensions)
        elif step == 3:
            result = user_calibration.capture_front_stance(analysis['landmarks'], frame_dimensions)
        else:
            return jsonify({'error': 'Invalid calibration step'})
        
        # Finalize if needed
        if result.get('next_action') == 'finalize_calibration':
            final_result = user_calibration.finalize_calibration()
            result.update(final_result)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calibration/status', methods=['GET'])
def calibration_status():
    """Get calibration status"""
    try:
        return jsonify({
            'calibrated': user_calibration.is_calibrated(),
            'data': user_calibration.get_calibration_data(),
            'thresholds': user_calibration.get_personalized_feedback_thresholds()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calibration/reset', methods=['POST'])
def reset_calibration():
    """Reset calibration data"""
    try:
        user_calibration.reset_calibration()
        return jsonify({'success': True, 'message': 'Calibration reset successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/start', methods=['POST'])
def start_session():
    """Start a new training session"""
    reset_session()
    return jsonify({
        'success': True,
        'message': 'New training session started',
        'start_time': session_data['start_time'].isoformat()
    })

@app.route('/api/session/summary', methods=['GET'])
def get_session_summary():
    """Get current session summary"""
    if session_data['start_time'] is None:
        return jsonify({'error': 'No active session'})
    
    duration_minutes = (datetime.now() - session_data['start_time']).total_seconds() / 60
    
    summary = {
        'duration_minutes': round(duration_minutes, 1),
        'poses_analyzed': session_data['poses_analyzed'],
        'avg_quality': round(np.mean(session_data['quality_scores']) if session_data['quality_scores'] else 0, 1),
        'quality_trend': calculate_quality_trend(),
        'most_common_error': get_most_common_error(),
        'most_common_feedback': get_most_common_feedback(),
        'current_move': session_data['current_move'],
        'improvement_suggestions': get_improvement_suggestions()
    }
    
    return jsonify(summary)

def calculate_quality_trend():
    """Calculate if quality is improving, declining, or stable"""
    scores = session_data['quality_scores']
    if len(scores) < 5:
        return 'insufficient_data'
    
    recent_scores = scores[-5:]
    earlier_scores = scores[-10:-5] if len(scores) >= 10 else scores[:-5]
    
    if not earlier_scores:
        return 'insufficient_data'
    
    recent_avg = np.mean(recent_scores)
    earlier_avg = np.mean(earlier_scores)
    
    if recent_avg > earlier_avg + 5:
        return 'improving'
    elif recent_avg < earlier_avg - 5:
        return 'declining'
    else:
        return 'stable'

def get_most_common_error():
    """Get the most common error in the session"""
    if not session_data['errors_count']:
        return None
    
    return max(session_data['errors_count'].items(), key=lambda x: x[1])[0]

def get_most_common_feedback():
    """Get the most common positive feedback"""
    if not session_data['feedback_count']:
        return None
    
    return max(session_data['feedback_count'].items(), key=lambda x: x[1])[0]

def get_improvement_suggestions():
    """Generate improvement suggestions based on session data"""
    suggestions = []
    
    # Quality-based suggestions
    avg_quality = np.mean(session_data['quality_scores']) if session_data['quality_scores'] else 0
    
    if avg_quality < 50:
        suggestions.append("Focus on basic posture and alignment")
    elif avg_quality < 70:
        suggestions.append("Work on maintaining consistent form")
    elif avg_quality < 85:
        suggestions.append("Fine-tune your technique for better precision")
    else:
        suggestions.append("Excellent form! Try advancing to more complex moves")
    
    # Error-based suggestions
    most_common_error = get_most_common_error()
    if most_common_error:
        error_suggestions = {
            "keep shoulders level": "Practice shoulder alignment exercises",
            "widen your stance": "Work on stance width consistency",
            "align left knee over ankle": "Focus on left leg positioning",
            "align right knee over ankle": "Focus on right leg positioning",
            "lift kicking knee higher": "Strengthen hip flexors and practice knee lifts",
            "rotate hips more for power": "Practice hip rotation drills"
        }
        
        if most_common_error in error_suggestions:
            suggestions.append(error_suggestions[most_common_error])
    
    return suggestions

@app.route('/api/capture_photo', methods=['POST'])
def capture_photo():
    """Save a pose photo with landmarks"""
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode image
        image_data = base64.b64decode(data['image'].split(',')[1])
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Analyze pose and draw landmarks
        analysis = pose_detector.detect_pose(frame)
        if analysis['pose_detected']:
            frame = pose_detector.draw_pose_landmarks(frame, analysis['landmarks'])
        
        # Create static directory if it doesn't exist
        os.makedirs('static/captures', exist_ok=True)
        
        # Save image
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"pose_capture_{timestamp}.jpg"
        filepath = os.path.join('static/captures', filename)
        
        cv2.imwrite(filepath, frame)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'pose_detected': analysis['pose_detected'],
            'pose_quality': analysis.get('pose_quality', 0)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/moves', methods=['GET'])
def get_available_moves():
    """Get list of available Taekwondo moves"""
    moves = {
        'stances': [
            {'id': 'front_stance', 'name': 'Front Stance', 'difficulty': 'beginner'},
            {'id': 'horse_stance', 'name': 'Horse Stance', 'difficulty': 'beginner'},
            {'id': 'back_stance', 'name': 'Back Stance', 'difficulty': 'intermediate'}
        ],
        'kicks': [
            {'id': 'front_kick', 'name': 'Front Kick', 'difficulty': 'beginner'},
            {'id': 'roundhouse_kick', 'name': 'Roundhouse Kick', 'difficulty': 'intermediate'},
            {'id': 'side_kick', 'name': 'Side Kick', 'difficulty': 'intermediate'}
        ],
        'blocks': [
            {'id': 'low_block', 'name': 'Low Block', 'difficulty': 'beginner'},
            {'id': 'middle_block', 'name': 'Middle Block', 'difficulty': 'beginner'},
            {'id': 'high_block', 'name': 'High Block', 'difficulty': 'beginner'}
        ]
    }
    
    return jsonify(moves)

@app.route('/api/move_instructions/<move_id>', methods=['GET'])
def get_move_instructions(move_id):
    """Get detailed instructions for a specific move"""
    instructions = {
        'front_stance': {
            'name': 'Front Stance',
            'description': 'A fundamental forward-facing stance used in many techniques.',
            'key_points': [
                'Step forward with one foot',
                'Front leg should be relatively straight',
                'Back leg bent for stability',
                'Weight distributed evenly',
                'Keep shoulders level and facing forward'
            ],
            'common_mistakes': [
                'Stance too narrow',
                'Leaning too far forward',
                'Back leg too straight',
                'Uneven shoulder alignment'
            ]
        },
        'roundhouse_kick': {
            'name': 'Roundhouse Kick',
            'description': 'A circular kick using the top of the foot or shin.',
            'key_points': [
                'Lift knee high toward target',
                'Rotate hips for power',
                'Strike with top of foot',
                'Maintain balance on standing leg',
                'Retract leg quickly after strike'
            ],
            'common_mistakes': [
                'Not lifting knee high enough',
                'Insufficient hip rotation',
                'Poor balance on standing leg',
                'Slow retraction'
            ]
        }
    }
    
    if move_id not in instructions:
        return jsonify({'error': 'Move not found'}), 404
    
    return jsonify(instructions[move_id])

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Background cleanup task
def cleanup_old_captures():
    """Clean up old capture files"""
    while True:
        try:
            captures_dir = 'static/captures'
            if os.path.exists(captures_dir):
                now = time.time()
                for filename in os.listdir(captures_dir):
                    filepath = os.path.join(captures_dir, filename)
                    if os.path.isfile(filepath):
                        # Delete files older than 7 days
                        if now - os.path.getmtime(filepath) > 7 * 24 * 3600:
                            os.remove(filepath)
        except Exception as e:
            print(f"Error in cleanup task: {e}")
        
        # Wait 24 hours before next cleanup
        time.sleep(24 * 3600)

if __name__ == '__main__':
    # Start cleanup task in background
    cleanup_thread = threading.Thread(target=cleanup_old_captures, daemon=True)
    cleanup_thread.start()
    
    # Run Flask app
    app.run(debug=True, host='127.0.0.1', port=5000, threaded=True)