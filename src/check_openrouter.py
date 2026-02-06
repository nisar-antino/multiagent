import requests
import os
import json

# API Key provided by user
API_KEY = "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"

def get_openrouter_models():
    url = "https://openrouter.ai/api/v1/models"
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print(f"Successfully connected to OpenRouter!")
        print(f"Total models available: {len(data['data'])}")
        print("\nTop 20 Models:")
        
        # Sort by pricing (free/cheap first) or just list popular ones
        models = data['data']
        
        # Filter/Sort logic could go here, but let's just print readable list
        for i, model in enumerate(models[:20]):
            print(f"- {model['id']} ({model['name']})")
            
        print("\n... and many more.")
        
        # Check specifically for Gemini 2.0 Flash or similar free models
        print("\nChecking for Gemini models:")
        for model in models:
            if 'gemini' in model['id'].lower():
                print(f"- {model['id']}")
                
    except Exception as e:
        print(f"Error fetching models: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    get_openrouter_models()
