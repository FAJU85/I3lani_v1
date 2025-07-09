#!/usr/bin/env python3
"""
Simple ZIP creator for I3lani Bot
"""
import zipfile
import os

# Essential files to include
files_to_zip = [
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
    'render.yaml',
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
    'Dockerfile',
    'cloudbuild.yaml',
    '.gitignore',
    'RENDER_DEPLOYMENT_GUIDE.md',
    'CLOUD_RUN_DEPLOYMENT_GUIDE.md',
    'RAILWAY_DEPLOYMENT_GUIDE.md',
    'BACKGROUND_WORKERS_GUIDE.md',
    'DEPLOYMENT_CHECKLIST.md',
    'GITHUB_UPLOAD_GUIDE.md',
    'SECRETS_SETUP_GUIDE.md',
    'railway.json',
    'render-deploy.json',
    'ONE_CLICK_DEPLOY.md'
]

# Create ZIP file
with zipfile.ZipFile('i3lani-bot.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    included_count = 0
    for file in files_to_zip:
        if os.path.exists(file):
            zipf.write(file)
            included_count += 1
            print(f"✅ {file}")
        else:
            print(f"❌ {file} (not found)")
    
    print(f"\n📦 Created i3lani-bot.zip with {included_count} files")
    print("🚀 Ready for deployment!")