"""
SAVIN AI - Main Application Entry Point
Intelligent Document Chat Assistant with Modern Architecture

This is the main entry point for the refactored SAVIN AI application.
All components are now properly organized into focused modules.
"""

# Apply startup optimizations first
import startup_optimization
startup_optimization.suppress_streamlit_warnings()

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
from src.utils.performance import (
    SessionStateManager, 
    preload_models, 
    optimize_streamlit_performance,
    performance_timer
)


class SavinAIApp:
    """
    Main application class that coordinates all components.
    
    This class serves as the central orchestrator for the SAVIN AI application,
    managing the lifecycle, configuration, and coordination of all components
    including:
    - Streamlit configuration and setup
    - UI components and controllers  
    - Database connections and data management
    - AI processing components
    - Performance optimization
    
    The class follows a clean separation of concerns with proper initialization
    and error handling throughout.
    """
    
    def __init__(self):
        """
        Initialize the application with proper component setup.
        
        This method sets up the application in the correct order:
        1. Load configuration settings
        2. Configure Streamlit environment
        3. Initialize all controllers and components
        """
        logger.info("🚀 Initializing SAVIN AI Application...")
        
        # Load configuration settings
        self.app_config = AppConfig()
        logger.info("✅ Configuration loaded successfully")
        
        # Setup Streamlit environment
        self._setup_streamlit()
        logger.info("✅ Streamlit environment configured")
        
        # Initialize all controllers and components
        self._initialize_controllers()
        logger.info("✅ Application initialization complete")
    
    def _setup_streamlit(self):
        """
        Configure Streamlit page settings and environment.
        
        This method handles:
        - Performance optimizations for better user experience
        - Session state initialization with default values
        - Page configuration with proper metadata
        - CSS styling and theme loading
        """
        logger.info("🎨 Setting up Streamlit environment...")
        
        # Apply performance optimizations first for better UX
        optimize_streamlit_performance()
        logger.info("⚡ Performance optimizations applied")
        
        # Initialize session state with safe defaults
        SessionStateManager.initialize_defaults()
        logger.info("💾 Session state initialized")
        
        # Configure Streamlit page with proper settings
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
        logger.info("📱 Streamlit page configuration set")
        
        # Load CSS styles for enhanced UI appearance
        st.markdown(get_complete_css(), unsafe_allow_html=True)
        logger.info("🎨 CSS styles loaded")
    
    def _initialize_controllers(self):
        """
        Initialize application controllers and components.
        
        This method handles the initialization of all application controllers
        with proper error handling and caching for performance. Controllers
        include:
        - Application controller (main UI coordination)
        - Message handlers (user input processing)
        - Database connections and repositories
        - AI processing components
        
        Uses session state caching to avoid unnecessary re-initialization
        on Streamlit reruns.
        """
        try:
            logger.info("🔧 Initializing application controllers...")
            
            # Use session state to avoid reinitializing controllers on reruns
            if 'controllers_initialized' not in st.session_state:
                with performance_timer("Initializing application controllers"):
                    # Preload AI models and dependencies for better performance
                    logger.info("🤖 Preloading AI models...")
                    preload_models()
                    
                    # Create main application controller
                    logger.info("🏗️ Creating application controller...")
                    self.app_controller = create_application_controller()
                    
                    # Create message handlers for user interactions
                    logger.info("📨 Creating message handlers...")
                    self.message_handlers = create_message_handlers(self.app_controller)
                    
                    # Wire up message handlers with the app controller
                    # This creates a clean separation of concerns where:
                    # - App controller handles UI coordination
                    # - Message handlers process user inputs and interactions
                    logger.info("🔗 Connecting handlers to controller...")
                    self.app_controller._process_document_upload = self.message_handlers.process_document_upload
                    self.app_controller._process_user_message = self.message_handlers.process_user_message
                    self.app_controller._process_wikipedia_search = self.message_handlers.process_wikipedia_search
                    self.app_controller._process_web_search = self.message_handlers.process_web_search
                    self.app_controller._clear_document = self.message_handlers.clear_document
                    
                    # Cache controllers in session state for performance
                    # This prevents re-initialization on every Streamlit rerun
                    st.session_state.controllers_initialized = True
                    st.session_state.app_controller = self.app_controller
                    st.session_state.message_handlers = self.message_handlers
                    
                    logger.info("✅ Application controllers initialized successfully")
            else:
                # Use cached controllers from session state
                # This provides significant performance improvement by avoiding
                # re-initialization of expensive components
                self.app_controller = st.session_state.app_controller
                self.message_handlers = st.session_state.message_handlers
                logger.info("⚡ Using cached application controllers")
            
        except Exception as e:
            # Handle initialization errors gracefully with proper logging
            logger.error(f"❌ Controller initialization failed: {e}")
            st.error(f"🚨 Application initialization failed: {e}")
            st.error("Please check the logs for detailed error information.")
            st.stop()
    
    def run(self):
        """
        Main application run method that starts the UI.
        
        This method delegates the main application execution to the
        app controller, which handles all UI rendering and user interactions.
        Includes proper error handling to gracefully manage runtime errors.
        """
        try:
            logger.info("🚀 Starting application UI...")
            self.app_controller.run()
        except Exception as e:
            logger.error(f"❌ Application runtime error: {e}")
            st.error(f"🚨 An error occurred while running the application: {e}")
            st.error("Please refresh the page or check the logs for more information.")


def main():
    """
    Main application entry point.
    
    This function serves as the primary entry point for the SAVIN AI application.
    It creates and runs the main application instance with comprehensive error
    handling and helpful troubleshooting information for users.
    
    The function handles:
    - Application instance creation
    - Startup error handling
    - User-friendly error messages with troubleshooting steps
    - Proper logging for debugging
    """
    logger.info("🌟 SAVIN AI Application Starting...")
    
    try:
        # Create and run the main application instance
        app = SavinAIApp()
        app.run()
        
    except ImportError as e:
        # Handle missing dependencies specifically
        logger.error(f"❌ Missing dependencies: {e}")
        st.error("🚨 Missing Dependencies!")
        st.markdown("""
        ### 📦 Installation Required
        
        Please install all required dependencies:
        
        ```bash
        pip install -r requirements.txt
        ```
        
        If you're using conda:
        
        ```bash
        conda install --file requirements.txt
        ```
        """)
        
    except Exception as e:
        # Handle all other startup errors
        logger.error(f"❌ Application startup failed: {e}")
        st.error(f"🚨 Application failed to start: {e}")
        st.markdown("""
        ### 🔧 Troubleshooting Guide
        
        **Common Solutions:**
        
        1. **Install Dependencies:**
           ```bash
           pip install -r requirements.txt
           ```
        
        2. **Start AI Backend:**
           ```bash
           ollama serve
           ```
        
        3. **Install AI Model:**
           ```bash
           ollama pull gemma3:270m
           ```
        
        4. **Check Logs:**
           - Look at `app.log` for detailed error information
           - Check console output for additional details
        
        5. **Verify Environment:**
           - Python 3.8+ required
           - Sufficient disk space available
           - Network connection for AI models
        
        **Still Having Issues?**
        
        - 🐛 [Report a bug](https://github.com/savinpadencherry/notebook-ai/issues)
        - 💬 [Get help](https://github.com/savinpadencherry/notebook-ai/discussions)
        - 📚 [Read documentation](https://github.com/savinpadencherry/notebook-ai/wiki)
        """)


if __name__ == "__main__":
    """
    """
    main()