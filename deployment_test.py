#!/usr/bin/env python3
"""
Comprehensive deployment test to verify all fixes are working
"""
import time
import requests
import json
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_flask_server():
    """Test Flask server endpoints"""
    logger.info("Testing Flask server endpoints...")
    
    endpoints = [
        {'url': 'http://localhost:5001/', 'expected_status': 'ok'},
        {'url': 'http://localhost:5001/health', 'expected_status': 'healthy'},
        {'url': 'http://localhost:5001/status', 'expected_status': 'operational'}
    ]
    
    all_passed = True
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint['url'], timeout=5)
            if response.status_code == 200:
                data = response.json()
                if endpoint['expected_status'] in str(data):
                    logger.info(f"✅ {endpoint['url']} - OK")
                else:
                    logger.error(f"❌ {endpoint['url']} - Unexpected response: {data}")
                    all_passed = False
            else:
                logger.error(f"❌ {endpoint['url']} - Status {response.status_code}")
                all_passed = False
        except Exception as e:
            logger.error(f"❌ {endpoint['url']} - Error: {e}")
            all_passed = False
    
    return all_passed

def test_webhook_endpoint():
    """Test webhook endpoint"""
    logger.info("Testing webhook endpoint...")
    
    try:
        test_payload = {"test": "webhook"}
        response = requests.post(
            'http://localhost:5001/webhook',
            json=test_payload,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        if response.status_code == 200:
            logger.info("✅ Webhook endpoint - OK")
            return True
        else:
            logger.error(f"❌ Webhook endpoint - Status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Webhook endpoint - Error: {e}")
        return False

def test_bot_status():
    """Test bot status via health endpoint"""
    logger.info("Testing bot status...")
    
    try:
        response = requests.get('http://localhost:5001/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('bot_running') is True:
                logger.info("✅ Bot is running - OK")
                return True
            else:
                logger.error(f"❌ Bot is not running - Status: {data}")
                return False
        else:
            logger.error(f"❌ Health check failed - Status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return False

def test_port_availability():
    """Test port binding"""
    logger.info("Testing port 5001 availability...")
    
    try:
        response = requests.get('http://localhost:5001/', timeout=2)
        if response.status_code == 200:
            logger.info("✅ Port 5001 is properly bound - OK")
            return True
        else:
            logger.error(f"❌ Port 5001 not responding properly - Status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Port 5001 error: {e}")
        return False

def main():
    """Run all deployment tests"""
    logger.info("🚀 Starting deployment tests...")
    
    tests = [
        ("Port Availability", test_port_availability),
        ("Flask Server", test_flask_server),
        ("Webhook Endpoint", test_webhook_endpoint),
        ("Bot Status", test_bot_status)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))
        time.sleep(1)  # Small delay between tests
    
    # Summary
    logger.info("\n📊 Test Results Summary:")
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        logger.info("\n🎉 All deployment tests passed! Ready for Cloud Run deployment.")
        return True
    else:
        logger.error("\n❌ Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)