#!/usr/bin/env python3
"""
Simple test script to verify OpenAI API connection
"""

import os
import openai
from dotenv import load_dotenv

def test_openai_connection():
    """Test OpenAI API connection"""
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set your API key using one of these methods:")
        print("1. Export in terminal: export OPENAI_API_KEY='your-key-here'")
        print("2. Create a .env file with: OPENAI_API_KEY=your-key-here")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Set API key
    openai.api_key = api_key
    
    try:
        print("🔄 Testing OpenAI API connection...")
        
        # Make a simple API call
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'user', 'content': 'Hello, this is a test message. Please respond with "API connection successful!"'}
            ],
            max_tokens=20
        )
        
        print("✅ OpenAI API connection successful!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except openai.error.AuthenticationError as e:
        print(f"❌ Authentication error: {e}")
        print("Please check your API key is correct")
        return False
        
    except openai.error.RateLimitError as e:
        print(f"❌ Rate limit error: {e}")
        print("You've exceeded your API quota. Please check your billing.")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_openai_connection() 