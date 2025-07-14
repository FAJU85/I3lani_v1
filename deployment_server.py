#!/usr/bin/env python3
"""
Deployment server for I3lani Bot - Cloud Run compatible
This runs the Flask web server required for Cloud Run deployment
"""
import os
import sys
import logging
import threading
import asyncio
from datetime import datetime
from flask import Flask, jsonify, request

# Set environment variable to prevent duplicate Flask servers
os.environ['DISABLE_STARS_FLASK'] = '1'

# Configure logging for deployment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Flask app for Cloud Run deployment
app = Flask(__name__)
bot_started = False
bot_instance = None

@app.route('/')
def health_check():
    """Health check endpoint for Cloud Run"""
    return jsonify({
        'status': 'ok',
        'service': 'I3lani Telegram Bot',
        'bot_status': 'running' if bot_started else 'starting',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Additional health endpoint"""
    return jsonify({
        'status': 'healthy',
        'bot_running': bot_started,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint for Telegram"""
    try:
        if bot_instance:
            update = request.get_json()
            return jsonify({'status': 'processed'})
        return jsonify({'status': 'bot_not_ready'})
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status')
def status():
    """Bot status endpoint"""
    return jsonify({
        'bot_started': bot_started,
        'uptime': datetime.now().isoformat(),
        'status': 'operational' if bot_started else 'initializing'
    })

def run_bot():
    """Run bot in background thread"""
    global bot_started, bot_instance
    try:
        logger.info("Starting bot in background...")
        # Import and run the V3 main bot
        from main_bot_v3 import main as start_bot
        # Set bot_started to True when bot initialization begins
        bot_started = True
        logger.info("Bot initialization started, setting bot_started=True")
        asyncio.run(start_bot())
        logger.info("Bot started successfully")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        bot_started = False
        import traceback
        traceback.print_exc()

def main():
    """Main application entry point for Cloud Run deployment"""
    try:
        logger.info("Starting I3lani Bot deployment server...")
        
        # Get port from environment (Render sets PORT automatically)
        port = int(os.environ.get('PORT', 5001))
        logger.info(f"Configuring Flask server on 0.0.0.0:{port}")
        
        # Test port availability before starting
        import socket
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(1)
            result = test_socket.connect_ex(('127.0.0.1', port))
            test_socket.close()
            
            if result == 0:
                logger.warning(f"Port {port} appears to be in use, but continuing...")
            else:
                logger.info(f"Port {port} is available")
        except Exception as e:
            logger.info(f"Port test completed: {e}")
        
        # Start bot in background thread
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        logger.info("Bot started in background thread")
        
        # Run Flask server immediately (blocking) - this ensures port opens quickly
        logger.info(f"Starting Flask server on 0.0.0.0:{port}...")
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True, use_reloader=False)
        
    except Exception as e:
        logger.error(f"Deployment server error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()