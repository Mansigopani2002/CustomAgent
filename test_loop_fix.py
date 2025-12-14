import io
import contextlib
import unittest.mock
import sys
from main import run_agent

def test_loop_handling():
    print("\n--- Testing Loop Handling for 'What is the capital of France?' ---")
    
    # Capture stdout
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        # Mock input() to always return 'y'
        with unittest.mock.patch('builtins.input', return_value='y'):
             # Using asyncio.run inside main.py, so we just call the wrapper
             run_agent("What is the capital of France?")
    
    output = f.getvalue()
    
    # Check for Duplicate detection message if it happened
    loop_detected = "Duplicate tool call detected" in output
    print(f"Loop Detected mechanism triggered: {loop_detected}")
    
    # Check for final answer
    if "Answer: Paris" in output or "Answer: The capital of France is Paris" in output:
        print("RESULT: PASS - Correct Answer Found")
        return True
    else:
        print("RESULT: FAIL - Correct Answer NOT Found")
        print("Last 500 chars of output:")
        print(output[-500:])
        return False

if __name__ == "__main__":
    test_loop_handling()
