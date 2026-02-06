
import os
import sys
# Ensure src is in path
sys.path.insert(0, '/app')

from langchain_google_genai import GoogleGenerativeAIEmbeddings
import logging


def list_available_models():
    api_key = os.getenv('GOOGLE_API_KEY')
    print(f"Testing with API Key: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")
    
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    
    print("\nListing available models:")
    try:
        for m in genai.list_models():
            if 'embedContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_available_models()

