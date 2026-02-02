"""
Configuration management.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Validate required environment variables
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY or GOOGLE_API_KEY == 'your_api_key_here':
    print("\n" + "="*60)
    print("ERROR: GOOGLE_API_KEY not configured!")
    print("="*60)
    print("\nPlease follow these steps:")
    print("1. Visit: https://aistudio.google.com/app/apikey")
    print("2. Sign in and create an API key")
    print("3. Copy the .env.template file to .env")
    print("4. Replace 'your_api_key_here' with your actual API key")
    print("\nExample .env file:")
    print("  GOOGLE_API_KEY=AIza... (your actual key)")
    print("="*60 + "\n")
    raise ValueError("GOOGLE_API_KEY not configured in .env file")

# Database configuration
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'database': os.getenv('MYSQL_DATABASE', 'gst_db'),
    'user': os.getenv('MYSQL_USER', 'gst_user'),
    'password': os.getenv('MYSQL_PASSWORD', 'gstpassword123')
}

# Rate limiting
MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_REQUESTS_PER_MINUTE', 60))

# Paths
DATA_DIR = Path(__file__).parent.parent / 'data'
VECTOR_STORE_PATH = DATA_DIR / 'vector_store'
GST_RULES_PATH = DATA_DIR / 'gst_rules'
