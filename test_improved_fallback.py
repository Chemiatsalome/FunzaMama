#!/usr/bin/env python3
"""
Test script to verify the improved fallback responses
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_fallback_responses():
    """Test the improved fallback responses"""
    print("🧪 Testing Improved Fallback Responses")
    print("=" * 45)
    
    try:
        from chatbot.hybrid_ai_service import get_hybrid_service
        
        # Create hybrid service (will use fallback since Together/HF not available)
        service = get_hybrid_service("together")
        
        # Test different messages
        test_messages = [
            "hello",
            "what is tummy time", 
            "pregnancy nutrition",
            "exercise during pregnancy",
            "breastfeeding tips",
            "labor signs",
            "random question about health"
        ]
        
        for message in test_messages:
            print(f"\n📝 Testing: '{message}'")
            response = service.generate_chat_response(message, "general")
            print(f"✅ Response: {response[:100]}...")
            
            # Check if response is intelligent (not generic)
            if "Thank you for your question" in response:
                print("❌ Still using generic response")
            else:
                print("✅ Using intelligent fallback response")
        
        print("\n🎯 Fallback Response Test Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Improved Fallback Responses")
    print("=" * 50)
    
    test_fallback_responses()




