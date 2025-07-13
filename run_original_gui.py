#!/usr/bin/env python3
"""
Original Job Automation GUI Launcher
This script launches the original GUI application with proper formatting.
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from job_automation_gui import main
    print("🚀 Starting Original Job Automation GUI...")
    print("✨ Features: Clean Design, Real-time Statistics, Progress Tracking")
    main()
except ImportError as e:
    print(f"❌ Error importing required modules: {e}")
    print("📦 Please make sure all dependencies are installed:")
    print("pip install -r requirements.txt")
    input("Press Enter to exit...")
except Exception as e:
    print(f"❌ Error starting original GUI: {e}")
    input("Press Enter to exit...") 