#!/usr/bin/env python3
"""
Test script to verify Flask server starts correctly for Cloud Run deployment
"""
import os
import sys
import time
import requests
import threading
import logging
from deployment_server import app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_flask_server():
    """Test Flask server startup"""
    try:
        # Test that Flask app can be created and health endpoints work
        logger.info("Testing Flask app creation...")
        
        # Test health endpoint
        with app.test_client() as client:
            response = client.get('/')
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'ok'
            assert data['service'] == 'I3lani Telegram Bot'
            logger.info("✅ Health endpoint test passed")
            
            # Test /health endpoint
            response = client.get('/health')
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'healthy'
            logger.info("✅ /health endpoint test passed")
            
            # Test /status endpoint
            response = client.get('/status')
            assert response.status_code == 200
            data = response.get_json()
            assert 'bot_started' in data
            assert 'status' in data
            logger.info("✅ /status endpoint test passed")
        
        logger.info("✅ All Flask server tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Flask server test failed: {e}")
        return False

def test_server_startup():
    """Test that Flask server can start on port 5001"""
    try:
        # Start server in thread
        port = 5001
        server_thread = threading.Thread(
            target=lambda: app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False),
            daemon=True
        )
        server_thread.start()
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Test server is responding
        response = requests.get(f'http://localhost:{port}/health', timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        
        logger.info("✅ Flask server startup test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Flask server startup test failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting deployment tests...")
    
    # Run Flask app tests
    if not test_flask_server():
        sys.exit(1)
    
    # Run server startup test
    if not test_server_startup():
        sys.exit(1)
    
    logger.info("✅ All deployment tests passed!")
    print("Deployment server is ready for Cloud Run!")