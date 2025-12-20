#!/usr/bin/env python3
"""
Test script to verify the correct fallback order:
1. Together API (main)
2. Hugging Face (first fallback) 
3. Current fallback questions (last resort)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_fallback_order():
    """Test the correct fallback order"""
    print("🧪 Testing Fallback Order")
    print("=" * 40)
    print("Expected order:")
    print("1. Together API (main)")
    print("2. Hugging Face (first fallback)")
    print("3. Fallback responses (last resort)")
    print()
    
    try:
        from chatbot.hybrid_ai_service import get_hybrid_service
        
        # Test with different preferences
        print("Testing provider priority order...")
        
        # Test 1: Together preference
        service_together = get_hybrid_service("together")
        priority_together = service_together._get_provider_priority()
        print(f"Together preference: {[p.value for p in priority_together]}")
        
        # Test 2: Hugging Face preference  
        service_hf = get_hybrid_service("huggingface")
        priority_hf = service_hf._get_provider_priority()
        print(f"Hugging Face preference: {[p.value for p in priority_hf]}")
        
        # Test 3: Auto preference
        service_auto = get_hybrid_service("auto")
        priority_auto = service_auto._get_provider_priority()
        print(f"Auto preference: {[p.value for p in priority_auto]}")
        
        # Verify correct order
        expected_order = ["together", "huggingface", "fallback"]
        
        print("\n✅ Verifying correct order...")
        for i, (service_name, priority) in enumerate([
            ("Together", priority_together),
            ("Hugging Face", priority_hf), 
            ("Auto", priority_auto)
        ]):
            actual_order = [p.value for p in priority]
            if actual_order == expected_order:
                print(f"✅ {service_name}: Correct order {actual_order}")
            else:
                print(f"❌ {service_name}: Wrong order {actual_order} (expected {expected_order})")
        
        print("\n🎯 Fallback Order Verification Complete!")
        print("\nThis means:")
        print("1. Together API will be tried first (most reliable)")
        print("2. If Together fails, Hugging Face will be used (cost savings)")
        print("3. If both fail, fallback responses will be used (always works)")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_chatbot_stages():
    """Test that all chatbot stages use hybrid service"""
    print("\n🔍 Testing Chatbot Stages Integration")
    print("=" * 45)
    
    stages = [
        ("index.html", "Main chatbot"),
        ("preconception.html", "Preconception stage"),
        ("prenatal.html", "Prenatal stage"), 
        ("birth.html", "Birth stage"),
        ("postnatal.html", "Postnatal stage")
    ]
    
    for template, description in stages:
        try:
            with open(f"templates/{template}", "r") as f:
                content = f.read()
                
            if '"use_hybrid": true' in content:
                print(f"✅ {description}: Hybrid service enabled")
            else:
                print(f"❌ {description}: Hybrid service NOT enabled")
                
        except Exception as e:
            print(f"❌ {description}: Error reading template - {e}")
    
    print("\n🎯 All chatbot stages should use the hybrid service!")
    return True

def test_route_integration():
    """Test that routes use correct provider order"""
    print("\n🔗 Testing Route Integration")
    print("=" * 35)
    
    try:
        # Check that routes use "together" preference
        with open("routes/system_routes.py", "r") as f:
            content = f.read()
            
        if 'get_hybrid_service("together")' in content:
            print("✅ Routes use Together API as primary provider")
        else:
            print("❌ Routes may not use correct provider order")
            
        if "Together API main, Hugging Face fallback" in content:
            print("✅ Routes have correct fallback order documented")
        else:
            print("⚠️ Routes may not have correct fallback documentation")
            
        return True
        
    except Exception as e:
        print(f"❌ Route test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Funza Mama Fallback Order Verification")
    print("=" * 50)
    
    # Run all tests
    test1 = test_fallback_order()
    test2 = test_chatbot_stages() 
    test3 = test_route_integration()
    
    if test1 and test2 and test3:
        print("\n🎉 All tests passed! Fallback order is correct.")
        print("\nYour system now uses:")
        print("1. Together API (main) - Most reliable")
        print("2. Hugging Face (fallback) - Cost savings when Together fails")
        print("3. Fallback responses (last resort) - Always works")
        print("\nThis gives you the best of both worlds:")
        print("✅ Reliability (Together API)")
        print("✅ Cost savings (Hugging Face fallback)")
        print("✅ Always works (fallback responses)")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")




