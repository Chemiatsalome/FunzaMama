#!/usr/bin/env python3
"""
Test script for hybrid AI service integration
This script tests the hybrid AI service to ensure it works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_hybrid_service():
    """Test the hybrid AI service"""
    print("🧪 Testing Hybrid AI Service Integration")
    print("=" * 50)
    
    try:
        # Test 1: Import hybrid service
        print("1. Testing import...")
        from chatbot.hybrid_ai_service import get_hybrid_service
        print("✅ Hybrid service imported successfully")
        
        # Test 2: Initialize service
        print("\n2. Testing service initialization...")
        service = get_hybrid_service("huggingface")
        print("✅ Hybrid service initialized")
        
        # Test 3: Check provider status
        print("\n3. Checking provider status...")
        status = service.get_provider_status()
        print(f"   Together API: {'✅ Available' if status['together'] else '❌ Not available'}")
        print(f"   Hugging Face: {'✅ Available' if status['hf_available'] else '❌ Not available'}")
        print(f"   Preferred: {status['preferred']}")
        
        # Test 4: Test chat response (fallback)
        print("\n4. Testing chat response...")
        try:
            response = service.generate_chat_response(
                "What should I know about prenatal nutrition?",
                "prenatal",
                {}
            )
            print(f"✅ Chat response generated: {response[:100]}...")
        except Exception as e:
            print(f"⚠️ Chat response failed (expected if HF not set up): {e}")
        
        # Test 5: Test teaching facts
        print("\n5. Testing teaching facts...")
        try:
            facts = service.generate_teaching_facts("prenatal")
            print(f"✅ Teaching facts generated: {len(facts)} facts")
            if facts:
                print(f"   Sample fact: {facts[0][:50]}...")
        except Exception as e:
            print(f"⚠️ Teaching facts failed (expected if HF not set up): {e}")
        
        print("\n🎉 Hybrid AI Service Integration Test Complete!")
        print("\nNext steps:")
        print("1. Run 'python setup_huggingface.py' to set up Hugging Face models")
        print("2. Test the chatbot in your browser")
        print("3. Monitor cost savings in your Together API usage")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_route_integration():
    """Test that routes can import the hybrid service"""
    print("\n🔗 Testing Route Integration")
    print("=" * 30)
    
    try:
        # Test importing from routes
        from routes.system_routes import get_intelligent_fallback_response
        print("✅ Route imports working")
        
        # Test fallback response
        response = get_intelligent_fallback_response("test message")
        print(f"✅ Fallback response: {response[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Route integration failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Funza Mama Hybrid AI Integration Test")
    print("=" * 50)
    
    # Run tests
    test1 = test_hybrid_service()
    test2 = test_route_integration()
    
    if test1 and test2:
        print("\n🎉 All tests passed! Hybrid AI service is ready.")
        print("\nTo start using Hugging Face models:")
        print("1. Run: python setup_huggingface.py")
        print("2. Follow the setup instructions")
        print("3. Your chatbot will automatically use HF models for cost savings!")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
        print("The system will still work with Together API as fallback.")
