"""
Utility modules for Taekwondo.AI

This package contains utility functions for pose analysis, angle calculations,
and feedback generation for the Taekwondo training application.
"""

from .angle_utils import (
    calculate_angle_between_points,
    calculate_slope_angle,
    calculate_distance,
    calculate_body_alignment_score,
    calculate_stance_width_score,
    calculate_knee_alignment_score,
    normalize_coordinates
)

from .feedback_utils import (
    FeedbackGenerator,
    generate_session_summary
)

__all__ = [
    'calculate_angle_between_points',
    'calculate_slope_angle', 
    'calculate_distance',
    'calculate_body_alignment_score',
    'calculate_stance_width_score',
    'calculate_knee_alignment_score',
    'normalize_coordinates',
    'FeedbackGenerator',
    'generate_session_summary'
]