#!/usr/bin/env python3
"""
Startup script for Karaokefy Web Application
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import flask
        import yt_dlp
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def main():
    print("🎤 Starting Karaokefy Web Application...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Activate virtual environment if needed
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment not detected")
        print("   Make sure you're running this in the karaokefy_venv environment")
    
    # Start the Flask app
    print("🌐 Starting web server...")
    print("📱 Open your browser and go to: http://localhost:8080")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=8080)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 