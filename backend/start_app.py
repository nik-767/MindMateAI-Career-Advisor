#!/usr/bin/env python3
"""
Complete startup script for the Career Advisor App
This script ensures everything is properly configured and starts the app
"""
import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("🔍 Checking dependencies...")
    try:
        import flask
        import flask_cors
        import psycopg2
        import requests
        import dotenv
        print("   ✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"   ❌ Missing dependency: {e}")
        print("   📦 Installing dependencies...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print("   ✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("   ❌ Failed to install dependencies")
            return False

def check_files():
    """Check if all required files exist."""
    print("📁 Checking required files...")
    required_files = [
        "app.py",
        "database.py", 
        "index.html",
        "script.js",
        "styles.css",
        "data/roles.json",
        ".env"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"   ❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("   ✅ All required files present")
        return True

def create_env_file():
    """Create .env file if it doesn't exist or is incomplete."""
    print("⚙️ Setting up environment configuration...")
    
    env_content = """# Database Configuration
DB_NAME=career_advisor
DB_USER=postgres
DB_PASS=password
DB_HOST=localhost
DB_PORT=5432

# API Keys (leave empty if not needed)
GEMINI_API_KEY=
BACKEND_API_KEY=your_backend_api_key_here
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("   ✅ Created .env file")
    else:
        print("   ✅ .env file already exists")

def start_app():
    """Start the Flask application."""
    print("🚀 Starting Career Advisor App...")
    print("=" * 50)
    print("📱 The app will be available at:")
    print("   • http://localhost:5000")
    print("   • http://127.0.0.1:5000")
    print("=" * 50)
    print("💡 Tips:")
    print("   • Enter skills like: Python, SQL, JavaScript, React")
    print("   • Choose a domain (optional) for more targeted results")
    print("   • Click 'Analyze Skills' to see your career matches")
    print("=" * 50)
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(2)
        try:
            webbrowser.open('http://localhost:5000')
        except:
            pass
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start the Flask app
    try:
        from app import app
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting app: {e}")
        return False
    
    return True

def main():
    """Main function to run the complete setup and start process."""
    print("🎯 Career Advisor App - Complete Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: Please run this script from the project directory")
        print("   Make sure app.py is in the current directory")
        return False
    
    # Run all checks and setup
    if not check_dependencies():
        return False
    
    if not check_files():
        return False
    
    create_env_file()
    
    print("\n✅ All checks passed! Starting the app...")
    time.sleep(1)
    
    return start_app()

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)
    else:
        print("\n🎉 App started successfully!")
