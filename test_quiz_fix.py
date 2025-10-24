#!/usr/bin/env python3
"""
Test script to verify quiz generation is working
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_quiz_generation():
    """Test quiz generation directly"""
    print("🧪 Testing Quiz Generation Fix")
    print("=" * 40)
    
    try:
        from chatbot.hybrid_ai_service import get_hybrid_service
        
        # Test different stages
        stages = ["preconception", "prenatal", "birth", "postnatal"]
        
        for stage in stages:
            print(f"\n📝 Testing {stage} stage...")
            
            service = get_hybrid_service("together")
            result = service.generate_quiz_questions(stage, "test_user")
            
            print(f"  Result type: {type(result)}")
            print(f"  Result length: {len(result) if isinstance(result, list) else 'N/A'}")
            
            if isinstance(result, list) and len(result) > 0:
                print(f"  ✅ {stage}: Generated {len(result)} questions")
                print(f"  Sample question: {result[0].get('question', 'No question')[:50]}...")
            else:
                print(f"  ❌ {stage}: No questions generated")
        
        print("\n🎯 Quiz Generation Test Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Testing Quiz Generation Fix")
    print("=" * 50)
    
    test_quiz_generation()
