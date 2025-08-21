"""
Configuration settings for SAVIN AI application.
Centralized configuration management for all application components.
"""

import os
from typing import Dict, List, Any


class AppConfig:
    """Main application configuration"""
    
    # Application metadata
    APP_TITLE = "SAVIN AI - Document Intelligence"
    APP_ICON = "🤖"
    APP_DESCRIPTION = "Intelligent Document Chat Assistant powered by Advanced AI"
    
    # Streamlit page configuration
    PAGE_TITLE = "SAVIN AI - Document Intelligence"
    PAGE_ICON = "🤖"
    LAYOUT = "wide"
    INITIAL_SIDEBAR_STATE = "expanded"
    
    # Application URLs
    HELP_URL = "https://github.com/savinpadencherry/notebook-ai"
    BUG_REPORT_URL = "https://github.com/savinpadencherry/notebook-ai/issues"


class UIConfig:
    """UI and styling configuration"""
    
    # Animation settings
    ANIMATION_SPEED = 200
    GRADIENT_ANIMATION_DURATION = "10s"
    SLIDE_ANIMATION_DURATION = "0.8s"
    
    # Color scheme
    PRIMARY_COLOR = "#667eea"
    SECONDARY_COLOR = "#764ba2"
    ACCENT_COLOR = "#f093fb"
    ERROR_COLOR = "#f5576c"
    SUCCESS_COLOR = "#4facfe"
    
    # Layout settings
    MAX_CHAT_HEIGHT = 500
    SIDEBAR_WIDTH = 300
    MAX_CONTENT_WIDTH = 1200


class AIConfig:
    """AI and model configuration"""
    
    # LLM settings
    AI_MODEL = "gemma3:270m"
    AI_TEMPERATURE = 0.1
    AI_MAX_TOKENS = 300
    
    # Text processing
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    MAX_CHUNKS = 15
    
    # Vector search settings
    SEARCH_TYPE = "mmr"
    SEARCH_K = 3
    SEARCH_FETCH_K = 12
    SEARCH_LAMBDA = 0.6
    
    # Performance settings
    BATCH_SIZE = 4
    NUM_THREADS = 4


class DatabaseConfig:
    """Database configuration"""
    
    # Database settings
    DB_PATH = "notebook_ai.db"
    DB_TIMEOUT = 30.0
    MAX_CONNECTIONS = 10
    
    # Backup settings
    AUTO_BACKUP = True
    BACKUP_INTERVAL_HOURS = 24
    MAX_BACKUPS = 7


class FileConfig:
    """File handling configuration"""
    
    # Supported file types
    ALLOWED_TYPES = ["pdf", "docx", "txt"]
    MAX_FILE_SIZE = 15  # MB
    
    # File processing
    MAX_TEXT_LENGTH = 1000000  # characters
    ENCODING = "utf-8"


class SearchConfig:
    """Web search configuration"""
    
    # Search settings
    MAX_SEARCH_RESULTS = 3
    SEARCH_TIMEOUT = 10  # seconds
    
    # Wikipedia settings
    WIKIPEDIA_SENTENCES = 3
    WIKIPEDIA_AUTO_SUGGEST = True
    
    # DuckDuckGo settings  
    DUCKDUCKGO_REGION = "us-en"
    DUCKDUCKGO_SAFE_SEARCH = "moderate"


class CacheConfig:
    """Caching configuration"""
    
    # Redis settings (if available)
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 0
    REDIS_PASSWORD = None
    
    # Cache TTL settings
    VECTOR_CACHE_TTL = 3600  # 1 hour
    SEARCH_CACHE_TTL = 1800  # 30 minutes
    
    # Memory cache settings
    MAX_MEMORY_CACHE_SIZE = 100  # MB


class MessageConfig:
    """
    User messaging and prompts configuration.
    
    This class manages all user-facing messaging including:
    - Quick prompt suggestions for common queries
    - Error messages with proper formatting
    - Success messages and notifications
    - Help text and tooltips
    """
    
    # Enhanced quick prompts for better user experience
    SUGGESTED_PROMPTS = [
        "📝 Summarize this document",
        "🔍 What are the key points?", 
        "💡 Explain the main concepts",
        "❓ Generate questions about this content",
        "🎯 Extract important insights",
        "📊 Create a table of contents",
        "🔗 Find relationships between topics",
        "⚡ Give me quick facts"
    ]
    
    # Contextual prompt suggestions based on content type
    DOCUMENT_TYPE_PROMPTS = {
        "academic": [
            "📚 What is the research methodology?",
            "🔬 What are the findings and conclusions?",
            "📖 Explain the theoretical framework"
        ],
        "business": [
            "💼 What are the business implications?", 
            "📈 Summarize financial data",
            "🎯 What are the strategic recommendations?"
        ],
        "technical": [
            "⚙️ Explain the technical implementation",
            "🛠️ What are the requirements?",
            "🔧 List the main components"
        ]
    }
    
    # Error messages
    ERROR_MESSAGES = {
        "file_too_large": "File size exceeds {max_size}MB limit. Please use a smaller file.",
        "unsupported_format": "Unsupported file format. Please use PDF, DOCX, or TXT files.",
        "processing_error": "Error processing document: {error}",
        "ai_error": "AI processing error: {error}",
        "search_error": "Search error: {error}",
        "database_error": "Database error: {error}"
    }
    
    # Success messages
    SUCCESS_MESSAGES = {
        "document_processed": "✅ Document processed successfully! Ready for intelligent chat.",
        "document_removed": "📄 Document removed successfully.",
        "chat_created": "💬 New chat created successfully.",
        "message_saved": "Message saved to chat history."
    }


def get_config() -> Dict[str, Any]:
    """Get complete configuration as dictionary"""
    return {
        "app": AppConfig.__dict__,
        "ui": UIConfig.__dict__,
        "ai": AIConfig.__dict__,
        "database": DatabaseConfig.__dict__,
        "file": FileConfig.__dict__,
        "search": SearchConfig.__dict__,
        "cache": CacheConfig.__dict__,
        "messages": MessageConfig.__dict__
    }


def get_app_config() -> AppConfig:
    """Get application configuration instance"""
    return AppConfig()


def get_ui_config() -> UIConfig:
    """Get UI configuration instance"""
    return UIConfig()


def get_ai_config() -> AIConfig:
    """Get AI configuration instance"""
    return AIConfig()


# Environment-based configuration overrides
def load_env_config():
    """Load configuration from environment variables"""
    
    # Override AI model if specified
    if os.getenv("AI_MODEL"):
        AIConfig.AI_MODEL = os.getenv("AI_MODEL")
    
    # Override database path if specified
    if os.getenv("DB_PATH"):
        DatabaseConfig.DB_PATH = os.getenv("DB_PATH")
    
    # Override Redis settings if specified
    if os.getenv("REDIS_URL"):
        import urllib.parse as urlparse
        url = urlparse.urlparse(os.getenv("REDIS_URL"))
        CacheConfig.REDIS_HOST = url.hostname
        CacheConfig.REDIS_PORT = url.port
        CacheConfig.REDIS_PASSWORD = url.password


# Load environment overrides on import
load_env_config()