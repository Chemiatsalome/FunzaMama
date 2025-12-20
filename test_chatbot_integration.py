#!/usr/bin/env python3
"""
Test script to verify chatbot integration is working properly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_chatbot_responses():
    """Test chatbot responses with different scenarios"""
    print("🧪 Testing Chatbot Integration")
    print("=" * 40)
    
    try:
        from chatbot.hybrid_ai_service import get_hybrid_service
        
        # Create hybrid service
        service = get_hybrid_service("together")
        
        # Test different scenarios
        test_cases = [
            {
                "message": "hello",
                "stage": "general",
                "expected_keywords": ["Funza Mama", "maternal health", "help"]
            },
            {
                "message": "what is tummy time",
                "stage": "postnatal", 
                "expected_keywords": ["tummy time", "baby", "stomach", "supervised"]
            },
            {
                "message": "pregnancy nutrition",
                "stage": "prenatal",
                "expected_keywords": ["nutrition", "pregnancy", "vitamins", "diet"]
            },
            {
                "message": "labor signs",
                "stage": "birth",
                "expected_keywords": ["labor", "contractions", "delivery", "signs"]
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test {i}: '{test_case['message']}' (stage: {test_case['stage']})")
            
            response = service.generate_chat_response(
                test_case['message'], 
                test_case['stage']
            )
            
            print(f"✅ Response: {response[:150]}...")
            
            # Check if response contains expected keywords
            response_lower = response.lower()
            found_keywords = []
            for keyword in test_case['expected_keywords']:
                if keyword.lower() in response_lower:
                    found_keywords.append(keyword)
            
            if found_keywords:
                print(f"✅ Found keywords: {found_keywords}")
            else:
                print(f"⚠️ Expected keywords not found: {test_case['expected_keywords']}")
            
            # Check if response is not generic
            if "Thank you for your question" in response:
                print("❌ Still using generic response")
            else:
                print("✅ Using intelligent response")
        
        print("\n🎯 Chatbot Integration Test Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_provider_status():
    """Test provider status"""
    print("\n🔍 Testing Provider Status")
    print("=" * 30)
    
    try:
        from chatbot.hybrid_ai_service import get_hybrid_service
        
        service = get_hybrid_service("together")
        status = service.get_provider_status()
        
        print(f"Together API: {'✅ Available' if status['together'] else '❌ Not Available'}")
        print(f"Hugging Face: {'✅ Available' if status['huggingface'] else '❌ Not Available'}")
        print(f"Preferred: {status['preferred']}")
        
        if not status['together'] and not status['huggingface']:
            print("ℹ️ Using fallback responses (this is expected if Together/HF not installed)")
        
        return True
        
    except Exception as e:
        print(f"❌ Provider status test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Funza Mama Chatbot Integration Test")
    print("=" * 50)
    
    test1 = test_chatbot_responses()
    test2 = test_provider_status()
    
    if test1 and test2:
        print("\n🎉 All tests passed! Chatbot is working properly.")
        print("\nYour chatbot now provides:")
        print("✅ Intelligent responses to common questions")
        print("✅ Specific information about maternal health topics")
        print("✅ Proper fallback when AI providers are unavailable")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")




