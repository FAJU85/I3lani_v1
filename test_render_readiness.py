#!/usr/bin/env python3
"""
Test if your bot is ready for Render deployment
"""
import os
import sys

def check_files():
    """Check if all required files exist"""
    print("🔍 Checking required files...")
    
    required_files = [
        'deployment_server.py',
        'main_bot.py',
        'config.py',
        'database.py',
        'handlers.py',
        'requirements.txt'
    ]
    
    all_good = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING!")
            all_good = False
    
    return all_good

def check_deployment_server():
    """Check deployment server configuration"""
    print("\n🔍 Checking deployment_server.py...")
    
    with open('deployment_server.py', 'r') as f:
        content = f.read()
        
    checks = [
        ('PORT environment variable', 'os.environ.get' in content and 'PORT' in content),
        ('0.0.0.0 binding', '0.0.0.0' in content),
        ('Flask app', 'Flask(__name__)' in content),
        ('Health endpoints', "'/health'" in content)
    ]
    
    all_good = True
    for name, passed in checks:
        if passed:
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - NOT FOUND!")
            all_good = False
    
    return all_good

def check_requirements():
    """Check requirements.txt"""
    print("\n🔍 Checking requirements.txt...")
    
    required_packages = [
        'aiogram',
        'flask',
        'psycopg2-binary',
        'python-dotenv',
        'requests'
    ]
    
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read().lower()
        
        all_good = True
        for package in required_packages:
            if package in content:
                print(f"✅ {package}")
            else:
                print(f"❌ {package} - MISSING!")
                all_good = False
        
        return all_good
    except FileNotFoundError:
        print("❌ requirements.txt not found!")
        return False

def main():
    print("🚀 Render Deployment Readiness Check\n")
    
    files_ok = check_files()
    server_ok = check_deployment_server()
    requirements_ok = check_requirements()
    
    print("\n📋 Summary:")
    if files_ok and server_ok and requirements_ok:
        print("✅ Your bot is ready for Render deployment!")
        print("\n🎯 Next steps:")
        print("1. Push your code to GitHub/GitLab")
        print("2. Create a PostgreSQL database on Render")
        print("3. Deploy your bot following RENDER_DEPLOYMENT_GUIDE.md")
        print("\n💡 Render gives you FREE hosting with PostgreSQL!")
    else:
        print("❌ Some issues need to be fixed before deployment")
        print("Please fix the issues above and run this test again")
        sys.exit(1)

if __name__ == "__main__":
    main()