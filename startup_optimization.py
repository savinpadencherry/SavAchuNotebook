"""
Startup optimization for SAVIN AI Streamlit application.
Pre-configures environment and reduces initialization overhead.
"""

import warnings
import logging
import os

def configure_startup_environment():
    """Configure environment for optimal startup performance"""
    
    # Suppress deprecation and future warnings
    warnings.filterwarnings('ignore', category=FutureWarning)
    warnings.filterwarnings('ignore', category=DeprecationWarning)
    warnings.filterwarnings('ignore', message='.*deprecated.*')
    warnings.filterwarnings('ignore', message='.*LangChain.*')
    
    # Optimize logging
    logging.getLogger('sentence_transformers').setLevel(logging.WARNING)
    logging.getLogger('transformers').setLevel(logging.WARNING)
    logging.getLogger('langchain').setLevel(logging.WARNING)
    logging.getLogger('chromadb').setLevel(logging.WARNING)
    
    # Set environment variables for better performance
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'  # Avoid tokenizer warnings
    os.environ['TRANSFORMERS_VERBOSITY'] = 'error'
    os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
    
    # Streamlit configuration
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
def suppress_streamlit_warnings():
    """Suppress Streamlit warnings that occur during initialization"""
    import streamlit as st
    
    # Disable Streamlit warnings about running without context
    if hasattr(st, '_set_log_level'):
        st._set_log_level('WARNING')
    
    # Configure session state handling
    if hasattr(st, '_config'):
        try:
            st._config.set_option('global.suppressDeprecationWarnings', True)
            st._config.set_option('global.showWarningOnDirectExecution', False)
        except:
            pass  # Some configurations might not be available

# Apply optimizations when module is imported
configure_startup_environment()
