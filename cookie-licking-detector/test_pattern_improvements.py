#!/usr/bin/env python3
"""
Test improved pattern matching with complex/hesitant questions
"""
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.pattern_matcher import ClaimPatternMatcher

def test_improved_patterns():
    matcher = ClaimPatternMatcher()
    
    # Test cases that should be detected as claims (questions)
    hesitant_questions = [
        "Can I maybe possibly work on this perhaps?",
        "Could I potentially work on this issue?",
        "Would it be okay if I work on this?",
        "Is it alright if I take this one?",
        "Do you mind if I work on this?",
        "Am I allowed to work on this?",
        "Can I maybe help with this issue?",
        "Maybe can I work on this?",
        "Perhaps could I take this?",
    ]
    
    # Test cases that should NOT be detected as claims
    non_claims = [
        "This is a great issue!",
        "Thanks for the explanation.",
        "What does this error mean?",
        "How do I reproduce this bug?",
        "Maybe this is related to #123?",
    ]
    
    print("=== Testing Improved Pattern Matching ===\n")
    
    print("🔍 Testing Hesitant Questions (should be detected as claims):")
    for question in hesitant_questions:
        result = matcher.analyze_comment(question)
        is_claim = result.get('is_claim', False)
        confidence = result.get('final_score', 0)
        detected_patterns = result.get('detected_patterns', [])
        
        status = "✅" if is_claim else "❌"
        print(f"{status} '{question}' -> {is_claim} (confidence: {confidence}%)")
        
        if detected_patterns:
            for pattern in detected_patterns:
                print(f"    Pattern: {pattern['type'].value} ({pattern['confidence']}%)")
    
    print(f"\n🚫 Testing Non-Claims (should NOT be detected as claims):")
    for text in non_claims:
        result = matcher.analyze_comment(text)
        is_claim = result.get('is_claim', False)
        confidence = result.get('final_score', 0)
        
        status = "✅" if not is_claim else "❌"
        print(f"{status} '{text}' -> {is_claim} (confidence: {confidence}%)")
    
    print(f"\n📊 Pattern Analysis:")
    print(f"Hesitant questions detected: {sum(1 for q in hesitant_questions if matcher.analyze_comment(q).get('is_claim', False))}/{len(hesitant_questions)}")
    print(f"Non-claims correctly rejected: {sum(1 for t in non_claims if not matcher.analyze_comment(t).get('is_claim', False))}/{len(non_claims)}")

if __name__ == "__main__":
    test_improved_patterns()