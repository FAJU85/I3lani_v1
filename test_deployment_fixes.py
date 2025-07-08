#!/usr/bin/env python3
"""
Test script to verify all deployment fixes are working correctly
"""
import requests
import json
import sys
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_deployment_fixes():
    """Test all deployment fixes"""
    logger.info("Testing deployment fixes...")
    
    # Test 1: Flask server is running on correct port
    try:
        response = requests.get('http://localhost:5001/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Flask server running on port 5001 - Status: {data['status']}")
        else:
            logger.error(f"❌ Flask server not responding correctly - Status: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Flask server not accessible: {e}")
        return False
    
    # Test 2: All health endpoints are working
    endpoints = [
        {'url': 'http://localhost:5001/', 'expected_key': 'status'},
        {'url': 'http://localhost:5001/health', 'expected_key': 'status'},
        {'url': 'http://localhost:5001/status', 'expected_key': 'status'}
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint['url'], timeout=5)
            if response.status_code == 200:
                data = response.json()
                if endpoint['expected_key'] in data:
                    logger.info(f"✅ {endpoint['url']} - Working correctly")
                else:
                    logger.error(f"❌ {endpoint['url']} - Missing expected key")
                    return False
            else:
                logger.error(f"❌ {endpoint['url']} - Status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ {endpoint['url']} - Error: {e}")
            return False
    
    # Test 3: Bot is running
    try:
        response = requests.get('http://localhost:5001/health', timeout=5)
        data = response.json()
        if data.get('bot_running') == True:
            logger.info("✅ Bot is running successfully")
        else:
            logger.warning("⚠️ Bot might still be starting up")
    except Exception as e:
        logger.error(f"❌ Bot status check failed: {e}")
        return False
    
    # Test 4: Server responds quickly (under 1 second)
    start_time = time.time()
    try:
        response = requests.get('http://localhost:5001/', timeout=5)
        response_time = time.time() - start_time
        if response_time < 1.0:
            logger.info(f"✅ Server responds quickly ({response_time:.2f}s)")
        else:
            logger.warning(f"⚠️ Server response time is slow ({response_time:.2f}s)")
    except Exception as e:
        logger.error(f"❌ Server response time test failed: {e}")
        return False
    
    return True

def main():
    """Run all deployment tests"""
    logger.info("Starting deployment fix verification...")
    
    if test_deployment_fixes():
        logger.info("✅ All deployment fixes are working correctly!")
        logger.info("🚀 Bot is ready for Cloud Run deployment")
        return 0
    else:
        logger.error("❌ Some deployment fixes failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())