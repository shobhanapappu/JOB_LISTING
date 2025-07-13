#!/usr/bin/env python3
"""
Job Automation GUI Launcher
This script launches the GUI application for the job listing automation tool.
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from job_automation_gui import main
    print("Starting Job Automation GUI...")
    main()
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please make sure all dependencies are installed:")
    print("pip install -r requirements.txt")
    input("Press Enter to exit...")
except Exception as e:
    print(f"Error starting GUI: {e}")
    input("Press Enter to exit...") 