#!/usr/bin/env python3
"""
Test script to verify pattern matching logic works with real comment text
"""
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_pattern_matching():
    """Test pattern matching with real comment examples"""
    from app.services.pattern_matcher import pattern_matcher
    
    # Test cases with real GitHub comment examples
    test_cases = [
        # Direct claims (should be 95% confidence)
        ("I'll take this!", True, 95),
        ("I'll work on this issue", True, 95),
        ("I can handle this one", True, 95),
        ("Let me work on this", True, 95),
        ("I got this", True, 95),
        
        # Assignment requests (should be 90% confidence) 
        ("Please assign this to me", True, 90),
        ("Can you assign this to me?", True, 90),
        ("I want to work on this", True, 90),
        ("I'd like to take this issue", True, 90),
        
        # Questions (should be 70% confidence)
        ("Can I work on this?", True, 70),
        ("Is this available?", True, 70),
        ("Is anyone working on this?", True, 70),
        ("May I take this issue?", True, 70),
        
        # Non-claims (should be below 75% threshold)
        ("This looks interesting", False, 0),
        ("Great issue!", False, 0),
        ("I have the same problem", False, 0),
        ("Thanks for reporting this", False, 0),
        ("Any updates on this?", False, 0),
        
        # Progress updates (should reset timers but not create claims)
        ("Working on this now", False, 0),  # Progress update, not a new claim
        ("Made some progress on this", False, 0),
        ("Submitted a PR for this", False, 0),
    ]
    
    print("🧪 Testing Pattern Matching Logic...")
    print("=" * 50)
    
    all_passed = True
    
    for i, (comment_text, expected_claim, expected_confidence) in enumerate(test_cases):
        try:
            result = pattern_matcher.analyze_comment(comment_text)
            
            is_claim = result.get('is_claim', False)
            confidence = result.get('final_score', 0)
            detected_patterns = result.get('detected_patterns', [])
            
            # Check if result matches expectation
            if is_claim == expected_claim:
                if expected_claim and abs(confidence - expected_confidence) <= 5:  # Allow 5% tolerance
                    status = "✅ PASS"
                elif not expected_claim:
                    status = "✅ PASS"
                else:
                    status = f"❌ FAIL (confidence {confidence} != {expected_confidence})"
                    all_passed = False
            else:
                status = f"❌ FAIL (claim {is_claim} != {expected_claim})"
                all_passed = False
            
            print(f"Test {i+1:2d}: {status}")
            print(f"   Text: '{comment_text}'")
            print(f"   Expected: Claim={expected_claim}, Confidence={expected_confidence}%")
            print(f"   Actual:   Claim={is_claim}, Confidence={confidence}%")
            if detected_patterns:
                pattern_types = [p['type'].value for p in detected_patterns]
                print(f"   Patterns: {pattern_types}")
            print()
            
        except Exception as e:
            print(f"Test {i+1:2d}: ❌ ERROR - {e}")
            print(f"   Text: '{comment_text}'")
            print()
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 All pattern matching tests PASSED!")
        return True
    else:
        print("💥 Some pattern matching tests FAILED!")
        return False

if __name__ == "__main__":
    success = test_pattern_matching()
    sys.exit(0 if success else 1)