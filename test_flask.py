#!/usr/bin/env python3
"""
Test Flask server for deployment
"""
import logging
from datetime import datetime
from flask import Flask, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def health_check():
    """Health check endpoint for Cloud Run"""
    return jsonify({
        'status': 'ok',
        'service': 'I3lani Telegram Bot',
        'bot_status': 'testing',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Additional health endpoint"""
    return jsonify({
        'status': 'healthy',
        'bot_running': True,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    logger.info("Starting test Flask server...")
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True, use_reloader=False)