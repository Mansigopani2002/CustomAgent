import io
import sys
import contextlib
import unittest.mock
from main import run_agent

def run_test_query(query, expected_keywords):
    print(f"\n--- Testing Query: '{query}' ---")
    
    # Capture stdout
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        # Mock input() to always return 'y' to continue if timeout occurs
        with unittest.mock.patch('builtins.input', return_value='y'):
            run_agent(query)
    output = f.getvalue()
    
    # Analyze output
    # Check if web_search was used
    tool_used = "[web_search]" in output
    
    # Extract Answer
    answer = ""
    if "Answer:" in output:
        answer = output.split("Answer:", 1)[1].strip()
    else:
        # Fallback extraction similar to main.py
        lines = output.splitlines()
        if lines:
            answer = lines[-1] # Valid for simple cases
            
    print(f"Tool Used: {tool_used}")
    print(f"Full Answer: {answer[:200]}..." if len(answer) > 200 else f"Full Answer: {answer}")
    
    # Verify keywords
    missing_keywords = [k for k in expected_keywords if k.lower() not in answer.lower()]
    
    if not missing_keywords:
        print("RESULT: PASS")
        return True
    else:
        print(f"RESULT: FAIL - Missing keywords: {missing_keywords}")
        print("Debug Output (last 500 chars):")
        print(output[-500:])
        return False

def main():
    tests = [
        ("What is the capital of France?", ["Paris"]),
        ("Who is the CEO of Google?", ["Sundar", "Pichai"]),
        ("Who wrote the book '1984'?", ["George", "Orwell"]),
        ("What is the currency of Japan?", ["Yen"]),
    ]
    
    passed = 0
    for query, keywords in tests:
        if run_test_query(query, keywords):
            passed += 1
            
    print(f"\nTotal Passed: {passed}/{len(tests)}")

if __name__ == "__main__":
    main()
