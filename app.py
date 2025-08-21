#!/usr/bin/env python3
"""
SAVIN AI - Clean & Modular Architecture
=====================================

This is the new, refactored entry point for SAVIN AI that leverages 
the modular architecture. All components are properly organized and 
follow industry best practices.

Key Features:
- 🏗️ Modular architecture with separated concerns
- 🎨 Clean chat interface with integrated navbar
- 🔍 Web search & Wikipedia integration
- 📄 Smart document processing
- 💾 Persistent chat history
- 🚀 Optimized performance

Usage:
    streamlit run app.py

Author: SAVIN AI Team
Version: 2.0 (Refactored)
"""

import sys
import os
import logging

# Add src directory to Python path for modular imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging for better debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_application():
    """
    Main application runner that imports and executes the modular app.
    
    This function provides a clean entry point and handles any import
    errors gracefully with helpful error messages.
    """
    try:
        logger.info("🚀 Starting SAVIN AI with modular architecture...")
        
        # Import and run the modular application
        from main import main
        main()
        
    except ImportError as e:
        logger.error(f"Failed to import modular components: {e}")
        print("❌ Module Import Error!")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        print(f"❌ Application Error: {e}")
        print("Check app.log for detailed error information")
        sys.exit(1)

if __name__ == "__main__":
    """
    Entry point for the SAVIN AI application.
    
    This script serves as a clean, documented entry point that:
    1. Sets up proper logging
    2. Configures the module path for imports
    3. Handles errors gracefully
    4. Provides helpful error messages
    """
    run_application()