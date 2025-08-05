#!/usr/bin/env python3
"""
Test script for voice instructions and stance correction system
"""

import sys
from voice_feedback import VoiceFeedback
from move_instructions import TaekwondoMoveInstructions
import time

def test_voice_system():
    print("Testing Taekwondo.AI Voice Instruction System")
    print("=" * 50)
    
    # Initialize components
    voice = VoiceFeedback()
    move_db = TaekwondoMoveInstructions()
    
    # Test 1: Check voice system
    print("\nTest 1: Voice System Check")
    if voice.test_voice():
        print("✓ Voice system is working")
    else:
        print("✗ Voice system not available")
        return False
    
    time.sleep(2)
    
    # Test 2: Test move instructions
    print("\nTest 2: Move Instructions Database")
    moves = move_db.get_all_moves()
    print(f"Found {len(moves)} moves in database")
    for move in moves[:3]:  # Test first 3 moves
        print(f"  - {move}")
        instructions = move_db.get_move_instructions(move)
        print(f"    Instructions: {len(instructions)} steps")
    
    # Test 3: Voice reading instructions
    print("\nTest 3: Voice Reading Move Instructions")
    test_move = "Front Stance"
    print(f"Testing voice for: {test_move}")
    
    instructions = move_db.get_move_instructions(test_move)
    
    # Announce the move
    voice.speak_instruction(f"Now learning {test_move}")
    time.sleep(2)
    
    # Read first 3 instructions
    for i, instruction in enumerate(instructions[:3]):
        print(f"  Speaking: {instruction[:50]}...")
        voice.speak_instruction(instruction)
        time.sleep(3)
    
    # Test 4: Correction feedback
    print("\nTest 4: Correction Feedback")
    corrections = move_db.get_move_error_corrections(test_move)
    
    for error_key, correction in list(corrections.items())[:2]:
        print(f"  Error: {error_key}")
        print(f"  Correction: {correction}")
        voice.speak_feedback(correction, priority="high")
        time.sleep(3)
    
    # Test 5: Encouragement
    print("\nTest 5: Encouragement")
    voice.speak_encouragement()
    time.sleep(3)
    
    print("\n" + "=" * 50)
    print("Voice instruction system test completed!")
    print("\nThe system can now:")
    print("1. Read move instructions when a move is selected")
    print("2. Provide real-time corrections based on pose analysis")
    print("3. Give encouragement during practice")
    
    return True

if __name__ == "__main__":
    try:
        success = test_voice_system()
        if success:
            print("\n✓ All tests passed!")
        else:
            print("\n✗ Some tests failed")
            sys.exit(1)
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)