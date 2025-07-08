#!/usr/bin/env python3
"""
Check deployment readiness for Cloud Run
"""
import os
import requests
import time
import json

def check_environment():
    """Check environment variables"""
    print("🔍 Checking environment variables...")
    required_vars = ['BOT_TOKEN', 'DATABASE_URL', 'ADMIN_IDS']
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var} is set (starts with: {str(value)[:20]}...)")
        else:
            print(f"❌ {var} is NOT set")
    
    # Check PORT for Cloud Run
    port = os.getenv('PORT', '5001')
    print(f"✅ PORT: {port} (Cloud Run will set this)")

def check_health_endpoints():
    """Check health endpoints"""
    print("\n🔍 Checking health endpoints...")
    base_url = "http://localhost:5001"
    
    endpoints = [
        ('/', 'Main health check'),
        ('/health', 'Health endpoint'),
        ('/status', 'Status endpoint')
    ]
    
    for path, name in endpoints:
        try:
            start = time.time()
            response = requests.get(f"{base_url}{path}", timeout=2)
            elapsed = time.time() - start
            
            if response.status_code == 200:
                print(f"✅ {name} ({path}): {response.status_code} - {elapsed:.2f}s")
                print(f"   Response: {response.text[:100]}...")
            else:
                print(f"❌ {name} ({path}): {response.status_code}")
        except Exception as e:
            print(f"❌ {name} ({path}): {type(e).__name__}: {e}")

def check_deployment_file():
    """Check deployment server file"""
    print("\n🔍 Checking deployment server...")
    if os.path.exists('deployment_server.py'):
        print("✅ deployment_server.py exists")
        # Check if it binds to correct port
        with open('deployment_server.py', 'r') as f:
            content = f.read()
            if '0.0.0.0' in content:
                print("✅ Binds to 0.0.0.0 (correct for Cloud Run)")
            else:
                print("❌ Not binding to 0.0.0.0")
            
            if 'PORT' in content:
                print("✅ Uses PORT environment variable")
            else:
                print("⚠️  Hardcoded port 5001")
    else:
        print("❌ deployment_server.py NOT found")

def check_bot_status():
    """Check if bot is running"""
    print("\n🔍 Checking bot status...")
    try:
        response = requests.get("http://localhost:5001/status", timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data.get('bot_started'):
                print("✅ Bot is running")
            else:
                print("⚠️  Bot is initializing")
            print(f"   Status: {data}")
    except Exception as e:
        print(f"❌ Cannot check bot status: {e}")

def main():
    print("🚀 Cloud Run Deployment Readiness Check\n")
    
    check_environment()
    check_health_endpoints()
    check_deployment_file()
    check_bot_status()
    
    print("\n📋 Cloud Run Requirements:")
    print("✅ 1. Use deployment_server.py as entry point")
    print("✅ 2. Listen on 0.0.0.0:$PORT (default 5001)")
    print("✅ 3. Respond to health checks within 10s")
    print("✅ 4. Set all required environment variables in Cloud Run")
    print("\n⚠️  Make sure to set these in Cloud Run:")
    print("   - BOT_TOKEN (your Telegram bot token)")
    print("   - DATABASE_URL (PostgreSQL connection string)")
    print("   - ADMIN_IDS (comma-separated admin user IDs)")
    print("   - TON_WALLET_ADDRESS (for TON payments)")

if __name__ == "__main__":
    main()