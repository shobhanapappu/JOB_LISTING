#!/usr/bin/env python3
"""
Simple Job Automation GUI Launcher
This script launches the simplified but modern GUI application.
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from job_automation_gui_simple import main
    print("🚀 Starting Simple Job Automation GUI...")
    print("✨ Features: Modern UI, Real-time Statistics, Clean Design")
    main()
except ImportError as e:
    print(f"❌ Error importing required modules: {e}")
    print("📦 Please make sure all dependencies are installed:")
    print("pip install -r requirements.txt")
    input("Press Enter to exit...")
except Exception as e:
    print(f"❌ Error starting simple GUI: {e}")
    input("Press Enter to exit...") 