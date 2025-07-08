#!/usr/bin/env python3
"""
Create Railway-optimized ZIP file for I3lani Bot
"""
import zipfile
import os

# Essential files for Railway deployment
railway_files = [
    'deployment_server.py',
    'worker.py',
    'main_bot.py',
    'main.py',
    'database.py',
    'handlers.py',
    'admin_system.py',
    'config.py',
    'languages.py',
    'requirements.txt',
    'railway.json',
    'README.md',
    'states.py',
    'payments.py',
    'stars_handler.py',
    'channel_manager.py',
    'admin_ui_control.py',
    'anti_fraud.py',
    'atomic_rewards.py',
    'channel_incentives.py',
    'content_moderation.py',
    'dynamic_pricing.py',
    'frequency_pricing.py',
    'gamification.py',
    'task_queue.py',
    'translation_system.py',
    'troubleshooting.py',
    'ui_components.py',
    'web3_ui.py',
    '.gitignore',
    'RAILWAY_DEPLOYMENT_GUIDE.md',
    'BACKGROUND_WORKERS_GUIDE.md',
    'DEPLOYMENT_CHECKLIST.md',
    'GITHUB_UPLOAD_GUIDE.md',
    'SECRETS_SETUP_GUIDE.md'
]

# Create ZIP file
with zipfile.ZipFile('i3lani-bot-railway.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    included_count = 0
    for file in railway_files:
        if os.path.exists(file):
            zipf.write(file)
            included_count += 1
            print(f"✅ {file}")
        else:
            print(f"❌ {file} (not found)")
    
    print(f"\n📦 Created i3lani-bot-railway.zip with {included_count} files")
    print("🚀 Optimized for Railway deployment!")