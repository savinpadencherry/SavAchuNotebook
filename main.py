"""
SAVIN AI - Main Application Entry Point
Intelligent Document Chat Assistant with Modern Architecture

This is the main entry point for the refactored SAVIN AI application.
All components are now properly organized into focused modules.
"""

import streamlit as st
import logging
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import organized modules
from src.config.settings import AppConfig
from src.ui.styles.theme import get_complete_css
from src.ui.app_controller import create_application_controller
from src.ui.message_handlers import create_message_handlers


class SavinAIApp:
    """
    Main application class that coordinates all components.
    Manages the application lifecycle and streamlit configuration.
    """
    
    def __init__(self):
        """Initialize the application"""
        self.app_config = AppConfig()
        self._setup_streamlit()
        self._initialize_controllers()
    
    def _setup_streamlit(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title=self.app_config.PAGE_TITLE,
            page_icon=self.app_config.PAGE_ICON,
            layout=self.app_config.LAYOUT,
            initial_sidebar_state=self.app_config.INITIAL_SIDEBAR_STATE,
            menu_items={
                'Get Help': self.app_config.HELP_URL,
                'Report a bug': self.app_config.BUG_REPORT_URL,
                'About': f"# {self.app_config.APP_TITLE}\n{self.app_config.APP_DESCRIPTION}"
            }
        )
        
        # Load CSS styles
        st.markdown(get_complete_css(), unsafe_allow_html=True)
    
    def _initialize_controllers(self):
        """Initialize application controllers"""
        try:
            self.app_controller = create_application_controller()
            self.message_handlers = create_message_handlers(self.app_controller)
            
            # Set up message handlers for the app controller
            self.app_controller._process_document_upload = self.message_handlers.process_document_upload
            self.app_controller._process_user_message = self.message_handlers.process_user_message
            self.app_controller._process_wikipedia_search = self.message_handlers.process_wikipedia_search
            self.app_controller._process_web_search = self.message_handlers.process_web_search
            self.app_controller._clear_document = self.message_handlers.clear_document
            
            logger.info("Application controllers initialized successfully")
            
        except Exception as e:
            logger.error(f"Controller initialization failed: {e}")
            st.error(f"Application initialization failed: {e}")
            st.stop()
    
    def run(self):
        """Main application run method"""
        try:
            self.app_controller.run()
        except Exception as e:
            logger.error(f"Application error: {e}")
            st.error(f"An error occurred: {e}")


def main():
    """Main application entry point"""
    try:
        app = SavinAIApp()
        app.run()
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        st.error(f"Application failed to start: {e}")
        st.markdown("""
        ### 🔧 Troubleshooting
        
        1. Check that all dependencies are installed: `pip install -r requirements.txt`
        2. Ensure Ollama is running: `ollama serve`
        3. Verify the AI model is available: `ollama pull gemma2:2b`
        4. Check the logs for detailed error information
        
        If problems persist, please create an issue on GitHub.
        """)


if __name__ == "__main__":
    main()


def main():
    """Main application entry point"""
    try:
        app = SavinAIApp()
        app.run()
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        st.error(f"Application failed to start: {e}")
        st.markdown("""
        ### 🔧 Troubleshooting
        
        1. Check that all dependencies are installed: `pip install -r requirements.txt`
        2. Ensure Ollama is running: `ollama serve`
        3. Verify the AI model is available: `ollama pull gemma2:2b`
        4. Check the logs for detailed error information
        
        If problems persist, please create an issue on GitHub.
        """)


if __name__ == "__main__":
    main()