from typing import Dict, List, Tuple, Optional

class TaekwondoMoveInstructions:
    def __init__(self):
        self.moves_database = {
            "Front Stance": {
                "spoken_instructions": [
                    "Let's learn the front stance, or ap-kubi in Korean.",
                    "Step forward with your lead foot about two shoulder widths.",
                    "Your front knee should be bent at 90 degrees, directly over your ankle.",
                    "Keep your back leg straight and strong.",
                    "Distribute your weight 70 percent on the front leg, 30 percent on the back.",
                    "Keep your hips facing forward and your back straight.",
                    "Your shoulders should be level and relaxed."
                ],
                "key_points": {
                    "front_knee_angle": (80, 100),  # degrees
                    "back_knee_angle": (160, 180),  # nearly straight
                    "stance_width": 1.5,  # shoulder widths
                    "weight_distribution": (0.7, 0.3),  # front, back
                    "shoulder_alignment": "level",
                    "hip_alignment": "forward"
                },
                "common_errors": {
                    "front_knee_over_toes": "Your front knee is extending past your toes. Pull it back over your ankle.",
                    "back_leg_bent": "Straighten your back leg for better stability.",
                    "stance_too_narrow": "Widen your stance to about two shoulder widths.",
                    "leaning_forward": "Keep your upper body upright, don't lean forward.",
                    "shoulders_uneven": "Level your shoulders and keep them relaxed."
                }
            },
            "Horse Stance": {
                "spoken_instructions": [
                    "Let's practice the horse stance, or juchum-seogi.",
                    "Stand with your feet about two shoulder widths apart.",
                    "Turn your toes slightly inward, heels out.",
                    "Bend both knees equally, as if sitting on a horse.",
                    "Keep your back perfectly straight and vertical.",
                    "Your weight should be evenly distributed between both legs.",
                    "Push your knees outward and keep your thighs parallel to the ground."
                ],
                "key_points": {
                    "knee_angle": (90, 110),  # both knees
                    "stance_width": 2.0,  # shoulder widths
                    "weight_distribution": (0.5, 0.5),  # even
                    "back_alignment": "vertical",
                    "toe_angle": -15  # degrees inward
                },
                "common_errors": {
                    "knees_collapsing": "Push your knees outward, don't let them collapse inward.",
                    "leaning_forward": "Keep your back straight and vertical.",
                    "stance_too_high": "Lower your stance by bending your knees more.",
                    "feet_parallel": "Turn your toes slightly inward for better stability.",
                    "weight_uneven": "Distribute your weight evenly between both legs."
                }
            },
            "Back Stance": {
                "spoken_instructions": [
                    "Now we'll learn the back stance, or dwit-kubi.",
                    "Step back with one foot, keeping feet shoulder width apart.",
                    "Bend your back knee deeply, front knee slightly.",
                    "Put 70 percent of your weight on your back leg.",
                    "Your front foot points forward, back foot at 90 degrees.",
                    "Keep your body upright and shoulders square.",
                    "This stance is perfect for defensive movements."
                ],
                "key_points": {
                    "back_knee_angle": (90, 110),
                    "front_knee_angle": (150, 170),  # slightly bent
                    "weight_distribution": (0.3, 0.7),  # front, back
                    "foot_angle_difference": 90,  # degrees
                    "stance_length": 1.5  # shoulder widths
                },
                "common_errors": {
                    "weight_too_forward": "Shift more weight to your back leg, about 70 percent.",
                    "back_knee_straight": "Bend your back knee more for stability.",
                    "feet_in_line": "Keep your feet shoulder width apart, not in a straight line.",
                    "leaning_back": "Keep your upper body upright and centered.",
                    "front_foot_angled": "Point your front foot straight forward."
                }
            },
            "Front Kick": {
                "spoken_instructions": [
                    "Let's practice the front kick, or ap-chagi.",
                    "Start in a fighting stance with your guard up.",
                    "First, lift your knee high toward your chest.",
                    "Keep your supporting leg slightly bent for balance.",
                    "Now extend your leg forward, striking with the ball of your foot.",
                    "Pull your toes back to expose the ball of your foot.",
                    "After striking, quickly retract your leg back to the knee-up position.",
                    "Return to your starting stance with control."
                ],
                "key_points": {
                    "knee_lift_height": "chest_level",
                    "striking_surface": "ball_of_foot",
                    "hip_thrust": True,
                    "supporting_leg": "slightly_bent",
                    "retraction_speed": "fast"
                },
                "common_errors": {
                    "low_knee_lift": "Lift your knee higher before extending the kick.",
                    "kicking_with_toes": "Pull your toes back and strike with the ball of your foot.",
                    "no_hip_thrust": "Push your hips forward as you extend the kick for more power.",
                    "slow_retraction": "Retract your leg quickly after the kick.",
                    "poor_balance": "Keep your supporting leg slightly bent and core engaged."
                }
            },
            "Roundhouse Kick": {
                "spoken_instructions": [
                    "Now for the roundhouse kick, or dollyo-chagi.",
                    "Start in fighting stance with your guard up.",
                    "Lift your knee high and to the side.",
                    "Pivot on your supporting foot, turning your heel toward the target.",
                    "Rotate your hips and extend your leg in an arc.",
                    "Strike with the top of your foot or the ball of your foot.",
                    "Your knee should point at the target before you extend.",
                    "Snap the kick back quickly and return to stance."
                ],
                "key_points": {
                    "knee_lift_angle": 90,  # degrees from body
                    "hip_rotation": "full",
                    "pivot_angle": 90,  # degrees minimum
                    "striking_surface": "instep_or_ball",
                    "chamber_position": "high"
                },
                "common_errors": {
                    "no_pivot": "Pivot on your supporting foot for proper hip rotation.",
                    "low_knee": "Lift your knee higher before extending the kick.",
                    "no_hip_rotation": "Rotate your hips fully to generate power.",
                    "pushing_kick": "Snap the kick, don't push it.",
                    "dropping_guard": "Keep your hands up to protect yourself."
                }
            },
            "Side Kick": {
                "spoken_instructions": [
                    "Let's work on the side kick, or yop-chagi.",
                    "Begin in fighting stance.",
                    "Lift your knee high toward your chest.",
                    "Pivot your supporting foot so your heel faces the target.",
                    "Extend your leg sideways, pushing with your heel.",
                    "Your body should lean slightly away for balance.",
                    "Keep your kicking leg parallel to the ground.",
                    "Retract quickly and return to stance."
                ],
                "key_points": {
                    "knee_chamber": "chest_high",
                    "striking_surface": "heel",
                    "hip_alignment": "stacked",
                    "body_lean": "slight",
                    "leg_height": "parallel_to_ground"
                },
                "common_errors": {
                    "kicking_forward": "Make sure you're kicking sideways, not forward.",
                    "using_toes": "Strike with your heel, not your toes.",
                    "no_chamber": "Lift your knee to your chest before extending.",
                    "excessive_lean": "Don't lean too far, maintain your balance.",
                    "dropping_kick": "Keep the kick at target height throughout."
                }
            },
            "Low Block": {
                "spoken_instructions": [
                    "Now we'll practice the low block, or arae-makki.",
                    "Start with your blocking arm raised high, opposite arm extended forward.",
                    "Sweep your blocking arm down and across your body.",
                    "Finish with your fist one fist-width away from your thigh.",
                    "Your blocking arm should be slightly bent.",
                    "Pull your opposite hand back to your hip as you block.",
                    "The motion should be smooth and powerful."
                ],
                "key_points": {
                    "start_position": "high",
                    "end_position": "thigh_level",
                    "arm_angle": 30,  # degrees from straight
                    "distance_from_body": "one_fist",
                    "opposite_hand": "hip_chamber"
                },
                "common_errors": {
                    "blocking_too_close": "Keep the block one fist-width from your thigh.",
                    "straight_arm": "Keep a slight bend in your blocking arm.",
                    "weak_motion": "Use more power and snap in the blocking motion.",
                    "forgetting_pullback": "Pull your opposite hand back to your hip.",
                    "incorrect_angle": "The block should angle downward and outward."
                }
            },
            "Middle Block": {
                "spoken_instructions": [
                    "Let's learn the middle block, or momtong-makki.",
                    "Start with your blocking arm low and across your body.",
                    "Sweep your arm up and across to shoulder height.",
                    "Your forearm should be vertical at the finish.",
                    "Keep your elbow bent at 90 degrees.",
                    "Your fist should be at shoulder height.",
                    "Pull your opposite hand back to your hip."
                ],
                "key_points": {
                    "elbow_angle": 90,  # degrees
                    "forearm_position": "vertical",
                    "height": "shoulder_level",
                    "distance_from_body": "one_forearm",
                    "rotation": "inward"
                },
                "common_errors": {
                    "elbow_too_high": "Keep your elbow down, forearm vertical.",
                    "blocking_too_far": "Keep the block closer to your body.",
                    "wrong_height": "Block at shoulder height.",
                    "no_rotation": "Rotate your forearm inward as you block.",
                    "weak_structure": "Maintain a strong 90-degree angle at the elbow."
                }
            },
            "High Block": {
                "spoken_instructions": [
                    "Finally, the high block, or olgul-makki.",
                    "Start with your blocking arm across your body at waist level.",
                    "Sweep your arm up and forward above your head.",
                    "Finish with your forearm angled upward at 45 degrees.",
                    "Your arm should be one fist-width from your forehead.",
                    "Keep your elbow bent and strong.",
                    "Pull your opposite hand back to your hip."
                ],
                "key_points": {
                    "arm_angle": 45,  # degrees from horizontal
                    "distance_from_head": "one_fist",
                    "elbow_position": "forward",
                    "forearm_angle": "upward_slope",
                    "protection_area": "head"
                },
                "common_errors": {
                    "arm_too_straight": "Keep your elbow bent for a stronger block.",
                    "blocking_behind_head": "Keep the block in front of your forehead.",
                    "arm_too_low": "Raise the block higher to protect your head.",
                    "incorrect_angle": "Angle your forearm at 45 degrees.",
                    "weak_structure": "Maintain tension in your arm for a solid block."
                }
            }
        }
    
    def get_move_instructions(self, move_name: str) -> List[str]:
        """Get spoken instructions for a move"""
        move_name = self._normalize_move_name(move_name)
        if move_name in self.moves_database:
            return self.moves_database[move_name]["spoken_instructions"]
        return [f"Let's practice {move_name.replace('_', ' ')}"]
    
    def get_move_key_points(self, move_name: str) -> Dict:
        """Get key technical points for move analysis"""
        move_name = self._normalize_move_name(move_name)
        if move_name in self.moves_database:
            return self.moves_database[move_name]["key_points"]
        return {}
    
    def get_move_error_corrections(self, move_name: str) -> Dict[str, str]:
        """Get error corrections for a move"""
        move_name = self._normalize_move_name(move_name)
        if move_name in self.moves_database:
            return self.moves_database[move_name]["common_errors"]
        return {}
    
    def get_correction_for_error(self, move_name: str, error_key: str) -> Optional[str]:
        """Get specific correction instruction for an error"""
        corrections = self.get_move_error_corrections(move_name)
        return corrections.get(error_key)
    
    def _normalize_move_name(self, move_name: str) -> str:
        """Normalize move name for database lookup"""
        # Handle different naming conventions
        move_mapping = {
            "front_stance": "Front Stance",
            "horse_stance": "Horse Stance",
            "back_stance": "Back Stance",
            "front_kick": "Front Kick",
            "roundhouse_kick": "Roundhouse Kick",
            "side_kick": "Side Kick",
            "low_block": "Low Block",
            "middle_block": "Middle Block",
            "high_block": "High Block"
        }
        
        # Try direct mapping first
        if move_name.lower().replace(" ", "_") in move_mapping:
            return move_mapping[move_name.lower().replace(" ", "_")]
        
        # Try title case
        return move_name.title()
    
    def get_all_moves(self) -> List[str]:
        """Get list of all available moves"""
        return list(self.moves_database.keys())
    
    def get_move_sequence_instructions(self, moves: List[str]) -> List[str]:
        """Get instructions for a sequence of moves"""
        instructions = ["Let's practice a combination of moves."]
        
        for i, move in enumerate(moves, 1):
            instructions.append(f"Move {i}: {move.replace('_', ' ')}.")
            # Add brief key instruction for each move
            move_data = self.moves_database.get(self._normalize_move_name(move))
            if move_data:
                # Add the most important instruction for the move
                instructions.append(move_data["spoken_instructions"][2])  # Usually the key technique point
        
        instructions.append("Practice this sequence slowly at first, then increase your speed.")
        return instructions