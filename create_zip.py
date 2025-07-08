#!/usr/bin/env python3
"""
Create deployment ZIP file for I3lani Bot
"""
import os
import zipfile
import sys

def create_deployment_zip():
    """Create ZIP file with all necessary deployment files"""
    
    # Files to include
    files_to_include = []
    exclude_patterns = ['.db', '.log', '__pycache__', '.replit', 'replit.nix', '.upm', '.tmp', '.bot_', 'uv.lock']
    
    for root, dirs, files in os.walk('.'):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.upm']]
        
        for file in files:
            filepath = os.path.join(root, file)
            # Check if file should be excluded
            should_exclude = any(pattern in filepath for pattern in exclude_patterns)
            if not should_exclude:
                files_to_include.append(filepath)
    
    # Create zip file
    with zipfile.ZipFile('i3lani-bot.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files_to_include:
            try:
                zipf.write(file, file.lstrip('./'))
            except ValueError as e:
                if "ZIP does not support timestamps before 1980" in str(e):
                    # Touch the file to update timestamp
                    import time
                    os.utime(file, (time.time(), time.time()))
                    zipf.write(file, file.lstrip('./'))
                else:
                    print(f"Skipping file {file}: {e}")
                    continue
    
    print(f'✅ Created i3lani-bot.zip with {len(files_to_include)} files')
    print('\n📁 Key files included:')
    
    # Show important files
    important_files = [
        'deployment_server.py',
        'worker.py', 
        'main_bot.py',
        'database.py',
        'handlers.py',
        'admin_system.py',
        'requirements.txt',
        'render.yaml',
        'README.md'
    ]
    
    for f in important_files:
        if f in [file.lstrip('./') for file in files_to_include]:
            print(f'  ✅ {f}')
        else:
            print(f'  ❌ {f} (missing)')
    
    print(f'\n📋 Total files: {len(files_to_include)}')
    print('🚀 Ready for deployment!')
    
    return len(files_to_include)

if __name__ == "__main__":
    create_deployment_zip()