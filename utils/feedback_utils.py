from typing import Dict, List, Tuple, Optional
import random
from .angle_utils import (
    calculate_angle_between_points,
    calculate_body_alignment_score,
    calculate_stance_width_score,
    calculate_knee_alignment_score,
    normalize_coordinates
)

class FeedbackGenerator:
    """Generate contextual feedback for Taekwondo poses"""
    
    def __init__(self):
        self.feedback_templates = {
            'positive': [
                "Excellent {aspect}!",
                "Great {aspect}!",
                "Perfect {aspect}!",
                "Outstanding {aspect}!",
                "Well done with your {aspect}!"
            ],
            'improvement': [
                "Work on your {aspect}",
                "Focus on improving {aspect}",
                "Try to enhance your {aspect}",
                "Pay attention to your {aspect}",
                "Keep practicing your {aspect}"
            ],
            'correction': [
                "{specific_instruction}",
                "Remember to {specific_instruction}",
                "Try to {specific_instruction}",
                "Focus on {specific_instruction}"
            ]
        }
        
        self.move_specific_feedback = {
            'front_stance': {
                'key_aspects': ['leg positioning', 'weight distribution', 'posture'],
                'common_errors': {
                    'narrow_stance': "Widen your stance for better stability",
                    'straight_back_leg': "Bend your back leg slightly",
                    'forward_lean': "Keep your torso upright",
                    'uneven_shoulders': "Level your shoulders"
                }
            },
            'horse_stance': {
                'key_aspects': ['thigh parallel', 'back straight', 'weight distribution'],
                'common_errors': {
                    'high_stance': "Lower your body, thighs should be parallel to ground",
                    'forward_lean': "Keep your back straight and vertical",
                    'feet_angle': "Point your feet forward, not outward"
                }
            },
            'roundhouse_kick': {
                'key_aspects': ['knee lift', 'hip rotation', 'balance'],
                'common_errors': {
                    'low_knee': "Lift your knee higher toward the target",
                    'no_hip_rotation': "Rotate your hips for more power",
                    'poor_balance': "Keep your standing leg stable",
                    'slow_retraction': "Snap your leg back quickly after the kick"
                }
            }
        }
    
    def generate_comprehensive_feedback(self, 
                                      landmarks, 
                                      frame_dimensions: Tuple[int, int],
                                      move_type: str = 'general',
                                      user_level: str = 'beginner') -> Dict:
        """
        Generate comprehensive feedback for a pose
        
        Args:
            landmarks: MediaPipe pose landmarks
            frame_dimensions: (width, height) of the frame
            move_type: Type of move being performed
            user_level: User skill level (beginner, intermediate, advanced)
        
        Returns:
            Dictionary containing feedback, scores, and suggestions
        """
        w, h = frame_dimensions
        coords = normalize_coordinates(landmarks, w, h)
        
        # Calculate various scores
        scores = self._calculate_all_scores(coords, move_type)
        
        # Generate feedback based on scores
        feedback = self._generate_feedback_from_scores(scores, move_type, user_level)
        
        # Get move-specific analysis
        move_analysis = self._analyze_specific_move(coords, move_type)
        
        return {
            'overall_score': self._calculate_overall_score(scores),
            'individual_scores': scores,
            'positive_feedback': feedback['positive'],
            'improvement_areas': feedback['improvements'],
            'specific_corrections': feedback['corrections'],
            'move_analysis': move_analysis,
            'difficulty_level': self._assess_difficulty_level(scores),
            'progression_suggestion': self._get_progression_suggestion(scores, user_level)
        }
    
    def _calculate_all_scores(self, coords: Dict, move_type: str) -> Dict[str, float]:
        """Calculate all relevant pose scores"""
        scores = {}
        
        # Basic alignment scores
        scores['body_alignment'] = calculate_body_alignment_score(
            coords['left_shoulder'], coords['right_shoulder'],
            coords['left_hip'], coords['right_hip']
        )
        
        # Stance width (using shoulder width as reference)
        shoulder_width = abs(coords['left_shoulder'][0] - coords['right_shoulder'][0])
        scores['stance_width'] = calculate_stance_width_score(
            coords['left_ankle'], coords['right_ankle'], 
            shoulder_width, move_type
        )
        
        # Knee alignment scores
        scores['left_knee_alignment'] = calculate_knee_alignment_score(
            coords['left_knee'], coords['left_ankle']
        )
        scores['right_knee_alignment'] = calculate_knee_alignment_score(
            coords['right_knee'], coords['right_ankle']
        )
        
        # Move-specific scores
        if move_type == 'front_stance':
            scores.update(self._score_front_stance(coords))
        elif move_type == 'horse_stance':
            scores.update(self._score_horse_stance(coords))
        elif move_type == 'roundhouse_kick':
            scores.update(self._score_roundhouse_kick(coords))
        
        return scores
    
    def _score_front_stance(self, coords: Dict) -> Dict[str, float]:
        """Score front stance specific aspects"""
        scores = {}
        
        # Determine which leg is forward
        left_forward = coords['left_ankle'][1] > coords['right_ankle'][1]
        
        if left_forward:
            front_leg_angle = calculate_angle_between_points(
                coords['left_hip'], coords['left_knee'], coords['left_ankle']
            )
            back_leg_angle = calculate_angle_between_points(
                coords['right_hip'], coords['right_knee'], coords['right_ankle']
            )
        else:
            front_leg_angle = calculate_angle_between_points(
                coords['right_hip'], coords['right_knee'], coords['right_ankle']  
            )
            back_leg_angle = calculate_angle_between_points(
                coords['left_hip'], coords['left_knee'], coords['left_ankle']
            )
        
        # Front leg should be relatively straight (160-180 degrees)
        scores['front_leg_straightness'] = max(0, 100 - abs(170 - front_leg_angle) * 2)
        
        # Back leg should be bent (120-150 degrees)
        scores['back_leg_bend'] = max(0, 100 - abs(135 - back_leg_angle) * 3)
        
        return scores
    
    def _score_horse_stance(self, coords: Dict) -> Dict[str, float]:
        """Score horse stance specific aspects"""
        scores = {}
        
        # Both legs should be bent equally
        left_leg_angle = calculate_angle_between_points(
            coords['left_hip'], coords['left_knee'], coords['left_ankle']
        )
        right_leg_angle = calculate_angle_between_points(
            coords['right_hip'], coords['right_knee'], coords['right_ankle']
        )
        
        # Target angle around 90-110 degrees for deep horse stance
        target_angle = 100
        scores['left_leg_bend'] = max(0, 100 - abs(target_angle - left_leg_angle) * 2)
        scores['right_leg_bend'] = max(0, 100 - abs(target_angle - right_leg_angle) * 2)
        
        # Leg symmetry
        angle_difference = abs(left_leg_angle - right_leg_angle)
        scores['leg_symmetry'] = max(0, 100 - angle_difference * 5)
        
        return scores
    
    def _score_roundhouse_kick(self, coords: Dict) -> Dict[str, float]:
        """Score roundhouse kick specific aspects"""
        scores = {}
        
        # Determine kicking leg (higher knee)
        left_knee_height = coords['left_hip'][1] - coords['left_knee'][1]
        right_knee_height = coords['right_hip'][1] - coords['right_knee'][1]
        
        if left_knee_height > right_knee_height:
            # Left leg is kicking
            kicking_knee = coords['left_knee']
            kicking_hip = coords['left_hip']
            standing_leg_angle = calculate_angle_between_points(
                coords['right_hip'], coords['right_knee'], coords['right_ankle']
            )
        else:
            # Right leg is kicking
            kicking_knee = coords['right_knee']
            kicking_hip = coords['right_hip']
            standing_leg_angle = calculate_angle_between_points(
                coords['left_hip'], coords['left_knee'], coords['left_ankle']
            )
        
        # Knee lift score (knee should be at or above hip level)
        knee_lift_score = min(100, max(0, left_knee_height * 2))
        scores['knee_lift'] = knee_lift_score
        
        # Standing leg stability (should be straight)
        scores['standing_leg_stability'] = max(0, 100 - abs(170 - standing_leg_angle) * 2)
        
        return scores
    
    def _generate_feedback_from_scores(self, scores: Dict, move_type: str, user_level: str) -> Dict:
        """Generate categorized feedback from scores"""
        feedback = {
            'positive': [],
            'improvements': [],
            'corrections': []
        }
        
        # Set thresholds based on user level
        thresholds = {
            'beginner': {'good': 60, 'excellent': 80},
            'intermediate': {'good': 70, 'excellent': 85},
            'advanced': {'good': 80, 'excellent': 90}
        }
        
        good_threshold = thresholds[user_level]['good']
        excellent_threshold = thresholds[user_level]['excellent']
        
        # Analyze each score
        for aspect, score in scores.items():
            aspect_name = aspect.replace('_', ' ')
            
            if score >= excellent_threshold:
                feedback['positive'].append(
                    random.choice(self.feedback_templates['positive']).format(aspect=aspect_name)
                )
            elif score >= good_threshold:
                feedback['improvements'].append(
                    f"Good {aspect_name}, try to maintain it throughout"
                )
            else:
                correction = self._get_specific_correction(aspect, score, move_type)
                feedback['corrections'].append(correction)
        
        return feedback
    
    def _get_specific_correction(self, aspect: str, score: float, move_type: str) -> str:
        """Get specific correction for an aspect"""
        corrections = {
            'body_alignment': "Keep your shoulders level and hips square",
            'stance_width': "Adjust your stance width - check your feet positioning",
            'left_knee_alignment': "Align your left knee over your ankle",
            'right_knee_alignment': "Align your right knee over your ankle",
            'front_leg_straightness': "Keep your front leg straighter",
            'back_leg_bend': "Bend your back leg more for stability",
            'knee_lift': "Lift your kicking knee higher",
            'standing_leg_stability': "Keep your standing leg strong and stable"
        }
        
        return corrections.get(aspect, f"Work on improving your {aspect.replace('_', ' ')}")
    
    def _analyze_specific_move(self, coords: Dict, move_type: str) -> Dict:
        """Provide move-specific analysis"""
        if move_type not in self.move_specific_feedback:
            return {'analysis': 'General pose analysis completed'}
        
        move_data = self.move_specific_feedback[move_type]
        analysis = {
            'move_type': move_type,
            'key_aspects_checked': move_data['key_aspects'],
            'specific_observations': []
        }
        
        # Add move-specific observations
        if move_type == 'front_stance':
            # Check stance depth
            stance_depth = abs(coords['left_ankle'][1] - coords['right_ankle'][1])
            if stance_depth < 50:
                analysis['specific_observations'].append("Increase your stance depth")
            else:
                analysis['specific_observations'].append("Good stance depth")
        
        elif move_type == 'roundhouse_kick':
            # Check hip rotation (simplified)
            hip_level_diff = abs(coords['left_hip'][1] - coords['right_hip'][1])
            if hip_level_diff > 20:
                analysis['specific_observations'].append("Good hip rotation detected")
            else:
                analysis['specific_observations'].append("Try to rotate your hips more")
        
        return analysis
    
    def _calculate_overall_score(self, scores: Dict) -> float:
        """Calculate weighted overall score"""
        if not scores:
            return 0
        
        # Weight different aspects
        weights = {
            'body_alignment': 0.25,
            'stance_width': 0.20,
            'left_knee_alignment': 0.15,
            'right_knee_alignment': 0.15,
            'front_leg_straightness': 0.10,
            'back_leg_bend': 0.10,
            'knee_lift': 0.20,
            'standing_leg_stability': 0.15
        }
        
        weighted_sum = 0
        total_weight = 0
        
        for aspect, score in scores.items():
            weight = weights.get(aspect, 0.05)  # Default small weight for unknown aspects
            weighted_sum += score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0
    
    def _assess_difficulty_level(self, scores: Dict) -> str:
        """Assess appropriate difficulty level based on performance"""
        avg_score = sum(scores.values()) / len(scores) if scores else 0
        
        if avg_score >= 85:
            return "Ready for advanced techniques"
        elif avg_score >= 70:
            return "Intermediate level performance"
        elif avg_score >= 50:
            return "Beginner to intermediate"
        else:
            return "Focus on fundamentals"
    
    def _get_progression_suggestion(self, scores: Dict, current_level: str) -> str:
        """Suggest next steps for progression"""
        avg_score = sum(scores.values()) / len(scores) if scores else 0
        
        suggestions = {
            'beginner': {
                'high': "Try practicing horse stance or basic kicks",
                'medium': "Continue practicing basic stances with focus on form",
                'low': "Focus on basic posture and body alignment first"
            },
            'intermediate': {
                'high': "Ready for combination techniques and sparring drills",
                'medium': "Practice advanced stances and kicks",
                'low': "Return to fundamentals and build consistency"
            },
            'advanced': {
                'high': "Focus on speed, power, and competition techniques",
                'medium': "Work on technique refinement and teaching others",
                'low': "Review fundamentals and focus on precision"
            }
        }
        
        level_key = 'high' if avg_score >= 80 else 'medium' if avg_score >= 60 else 'low'
        return suggestions[current_level][level_key]

def generate_session_summary(session_scores: List[Dict], session_duration: float) -> Dict:
    """Generate comprehensive session summary"""
    if not session_scores:
        return {'message': 'No poses analyzed in this session'}
    
    # Calculate averages
    all_scores = [score.get('overall_score', 0) for score in session_scores]
    avg_score = sum(all_scores) / len(all_scores)
    
    # Track improvement
    if len(all_scores) >= 5:
        first_half = all_scores[:len(all_scores)//2]
        second_half = all_scores[len(all_scores)//2:]
        improvement = sum(second_half)/len(second_half) - sum(first_half)/len(first_half)
    else:
        improvement = 0
    
    # Find most common feedback
    all_corrections = []
    all_positives = []
    
    for score_data in session_scores:
        all_corrections.extend(score_data.get('specific_corrections', []))
        all_positives.extend(score_data.get('positive_feedback', []))
    
    return {
        'session_duration_minutes': round(session_duration, 1),
        'poses_analyzed': len(session_scores),
        'average_score': round(avg_score, 1),
        'improvement_trend': round(improvement, 1),
        'performance_level': _classify_performance(avg_score),
        'most_common_correction': _most_common_item(all_corrections),
        'most_common_success': _most_common_item(all_positives),
        'next_session_focus': _get_next_focus(avg_score, all_corrections)
    }

def _classify_performance(avg_score: float) -> str:
    """Classify overall performance level"""
    if avg_score >= 85:
        return "Excellent"
    elif avg_score >= 70:
        return "Good" 
    elif avg_score >= 55:
        return "Fair"
    else:
        return "Needs Improvement"

def _most_common_item(items: List[str]) -> Optional[str]:
    """Find most common item in a list"""
    if not items:
        return None
    
    from collections import Counter
    return Counter(items).most_common(1)[0][0]

def _get_next_focus(avg_score: float, corrections: List[str]) -> str:
    """Suggest focus for next session"""
    if avg_score >= 80:
        return "Try more advanced techniques and combinations"
    elif corrections:
        most_common = _most_common_item(corrections)
        return f"Focus on: {most_common}"
    else:
        return "Continue practicing basic stances and form"