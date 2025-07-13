#!/usr/bin/env python3
"""
Advanced Job Automation GUI Launcher
This script launches the advanced GUI application with modern styling and animations.
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from job_automation_gui_advanced import main
    print("🚀 Starting Advanced Job Automation GUI...")
    print("✨ Features: Modern UI, Smooth Animations, Real-time Statistics")
    main()
except ImportError as e:
    print(f"❌ Error importing required modules: {e}")
    print("📦 Please make sure all dependencies are installed:")
    print("pip install -r requirements.txt")
    input("Press Enter to exit...")
except Exception as e:
    print(f"❌ Error starting advanced GUI: {e}")
    input("Press Enter to exit...") 