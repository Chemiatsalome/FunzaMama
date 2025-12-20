"""
Setup script for Hugging Face local models
This script helps you set up and test Hugging Face models as an alternative to Together API
"""

import os
import sys
import subprocess
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'transformers',
        'torch',
        'huggingface_hub',
        'accelerate'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            logger.warning(f"❌ {package} is missing")
    
    if missing_packages:
        logger.info(f"Missing packages: {missing_packages}")
        return False
    
    return True

def install_requirements():
    """Install required packages"""
    logger.info("Installing required packages...")
    
    packages = [
        'transformers>=4.30.0',
        'torch>=2.0.0',
        'huggingface_hub>=0.15.0',
        'accelerate>=0.20.0'
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            logger.info(f"✅ Installed {package}")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def setup_huggingface_auth():
    """Setup Hugging Face authentication"""
    logger.info("Setting up Hugging Face authentication...")
    
    # Check if already authenticated
    try:
        from huggingface_hub import whoami
        user_info = whoami()
        logger.info(f"✅ Already authenticated as: {user_info['name']}")
        return True
    except Exception:
        logger.info("Not authenticated. Please run: huggingface-cli login")
        logger.info("You can get a token from: https://huggingface.co/settings/tokens")
        return False

def test_model_loading():
    """Test if the model can be loaded"""
    logger.info("Testing model loading...")
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
        
        model_name = "meta-llama/Llama-3.2-1B"
        
        logger.info(f"Loading tokenizer for {model_name}...")
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        
        logger.info(f"Loading model for {model_name}...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
            trust_remote_code=True
        )
        
        logger.info("✅ Model loaded successfully!")
        
        # Test a simple generation
        logger.info("Testing text generation...")
        test_prompt = "What is maternal health?"
        inputs = tokenizer(test_prompt, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                max_new_tokens=50,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        logger.info(f"✅ Test generation successful: {response[:100]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Model loading failed: {e}")
        return False

def create_test_script():
    """Create a test script to verify the setup"""
    test_script = """
#!/usr/bin/env python3
'''
Test script for Hugging Face integration
Run this to test if everything is working correctly
'''

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot.huggingface_integration import get_hf_model

def test_quiz_generation():
    print("Testing quiz generation...")
    
    model = get_hf_model()
    
    # Test each stage
    stages = ["preconception", "prenatal", "birth", "postnatal"]
    
    for stage in stages:
        print(f"\\nTesting {stage} stage...")
        try:
            result = model.generate_quiz_questions(stage)
            if "error" in result:
                print(f"❌ Error in {stage}: {result['error']}")
            else:
                print(f"✅ {stage} generated {len(result)} questions")
                if result:
                    print(f"   Sample question: {result[0]['question'][:50]}...")
        except Exception as e:
            print(f"❌ Exception in {stage}: {e}")
    
    # Test teaching facts
    print("\\nTesting teaching facts...")
    for stage in stages:
        try:
            facts = model.generate_teaching_facts(stage)
            print(f"✅ {stage} facts: {len(facts)} items")
            if facts:
                print(f"   Sample fact: {facts[0][:50]}...")
        except Exception as e:
            print(f"❌ Exception in {stage} facts: {e}")

if __name__ == "__main__":
    test_quiz_generation()
"""
    
    with open("test_huggingface.py", "w") as f:
        f.write(test_script)
    
    logger.info("✅ Created test_huggingface.py")
    logger.info("Run 'python test_huggingface.py' to test the setup")

def main():
    """Main setup function"""
    logger.info("🚀 Setting up Hugging Face local models for Funza Mama")
    logger.info("=" * 60)
    
    # Step 1: Check requirements
    logger.info("Step 1: Checking requirements...")
    if not check_requirements():
        logger.info("Installing missing packages...")
        if not install_requirements():
            logger.error("❌ Failed to install requirements")
            return False
    
    # Step 2: Setup authentication
    logger.info("\\nStep 2: Setting up authentication...")
    if not setup_huggingface_auth():
        logger.warning("⚠️ Please run 'huggingface-cli login' and get a token")
        logger.info("Token URL: https://huggingface.co/settings/tokens")
        logger.info("Then run this script again")
        return False
    
    # Step 3: Test model loading
    logger.info("\\nStep 3: Testing model loading...")
    if not test_model_loading():
        logger.error("❌ Model loading failed. Check your setup.")
        return False
    
    # Step 4: Create test script
    logger.info("\\nStep 4: Creating test script...")
    create_test_script()
    
    logger.info("\\n🎉 Setup completed successfully!")
    logger.info("\\nNext steps:")
    logger.info("1. Run 'python test_huggingface.py' to test the setup")
    logger.info("2. Update your routes to use the hybrid service")
    logger.info("3. Monitor performance and costs")
    
    return True

if __name__ == "__main__":
    main()

