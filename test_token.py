#!/usr/bin/env python3
"""Test token loading"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get token from different sources
env_token = os.getenv('BOT_TOKEN')
print(f"Token from environment: {env_token}")

# Test with direct import
try:
    from config import BOT_TOKEN
    print(f"Token from config.py: {BOT_TOKEN}")
except Exception as e:
    print(f"Error loading from config: {e}")

# Test API call
import requests

if env_token:
    url = f"https://api.telegram.org/bot{env_token}/getMe"
    response = requests.get(url)
    print(f"\nAPI test result: {response.json()}")