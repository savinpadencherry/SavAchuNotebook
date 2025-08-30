# FIXED: settings.py - Optimized for Better RAG Performance

"""
Optimized configuration settings for enhanced RAG performance.
"""

import os
from typing import Dict, List, Any

class AppConfig:
    """Main application configuration"""
    APP_TITLE = "SAVIN AI - Document Intelligence"
    APP_ICON = "🤖"
    APP_DESCRIPTION = "Intelligent Document Chat Assistant powered by Advanced AI"
    PAGE_TITLE = "SAVIN AI - Document Intelligence"
    PAGE_ICON = "🤖"
    LAYOUT = "wide"
    INITIAL_SIDEBAR_STATE = "expanded"
    HELP_URL = "https://github.com/savinpadencherry/notebook-ai"
    BUG_REPORT_URL = "https://github.com/savinpadencherry/notebook-ai/issues"

class UIConfig:
    """UI and styling configuration"""
    ANIMATION_SPEED = 200
    GRADIENT_ANIMATION_DURATION = "10s"
    SLIDE_ANIMATION_DURATION = "0.8s"
    PRIMARY_COLOR = "#667eea"
    SECONDARY_COLOR = "#764ba2"
    ACCENT_COLOR = "#f093fb"
    ERROR_COLOR = "#f5576c"
    SUCCESS_COLOR = "#4facfe"
    MAX_CHAT_HEIGHT = 500
    SIDEBAR_WIDTH = 300
    MAX_CONTENT_WIDTH = 1200

class AIConfig:
    """OPTIMIZED AI configuration for better RAG performance"""
    
    # LLM settings - OPTIMIZED
    AI_MODEL = "qwen2.5:0.5b-instruct"  # Changed from gemma3:270m
    AI_TEMPERATURE = 0.1  # Lower temperature for more consistent, factual responses
    AI_MAX_TOKENS = 512   # Increased for better responses
    
    # Text processing - OPTIMIZED for better chunking
    CHUNK_SIZE = 800      # Reduced from 1500 for better precision
    CHUNK_OVERLAP = 150   # Optimized overlap for context continuity
    MAX_CHUNKS = 100      # Reduced from 200 to avoid information overload
    
    # Vector search settings - OPTIMIZED for accuracy
    SEARCH_TYPE = "similarity"  # Changed from MMR for more precise results
    SEARCH_K = 5          # Reduced from 12 for more focused results
    SEARCH_FETCH_K = 15   # Reduced from 50 to minimize noise
    SEARCH_LAMBDA = 0.7   # Increased for more diverse results when using MMR
    
    # Performance settings
    BATCH_SIZE = 4
    NUM_THREADS = 2       # Reduced for stability on lower-end devices
    
    # NEW: Anti-hallucination settings
    ENABLE_STRICT_CONTEXT = True
    CONTEXT_RELEVANCE_THRESHOLD = 0.2
    MAX_CONTEXT_LENGTH = 2000
    ENABLE_RESPONSE_VALIDATION = True

class DatabaseConfig:
    """Database configuration"""
    DB_PATH = "notebook_ai.db"
    DB_TIMEOUT = 30.0
    MAX_CONNECTIONS = 10
    AUTO_BACKUP = True
    BACKUP_INTERVAL_HOURS = 24
    MAX_BACKUPS = 7

class FileConfig:
    """File handling configuration"""
    ALLOWED_TYPES = ["pdf", "docx", "txt"]
    MAX_FILE_SIZE = 15  # MB
    MAX_TEXT_LENGTH = 1000000  # characters
    ENCODING = "utf-8"

class SearchConfig:
    """Web search configuration"""
    MAX_SEARCH_RESULTS = 3
    SEARCH_TIMEOUT = 10  # seconds
    WIKIPEDIA_SENTENCES = 3
    WIKIPEDIA_AUTO_SUGGEST = True
    DUCKDUCKGO_REGION = "us-en"
    DUCKDUCKGO_SAFE_SEARCH = "moderate"

class CacheConfig:
    """Caching configuration"""
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 0
    REDIS_PASSWORD = None
    VECTOR_CACHE_TTL = 3600  # 1 hour
    SEARCH_CACHE_TTL = 1800  # 30 minutes
    MAX_MEMORY_CACHE_SIZE = 100  # MB

class MessageConfig:
    """Enhanced messaging configuration with better prompts"""
    
    # Enhanced quick prompts for better user experience
    SUGGESTED_PROMPTS = [
        "📝 Summarize this document",
        "🔍 What are the key points?",
        "💡 Explain the main concepts",
        "❓ What does this document say about [topic]?",
        "🎯 Extract important insights",
        "📊 What are the main findings?",
        "🔗 How does this relate to [concept]?",
        "⚡ Give me a quick overview"
    ]
    
    # Context-specific prompts
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
    
    # Enhanced error messages
    ERROR_MESSAGES = {
        "file_too_large": "File size exceeds {max_size}MB limit. Please use a smaller file.",
        "unsupported_format": "Unsupported file format. Please use PDF, DOCX, or TXT files.",
        "processing_error": "Error processing document: {error}",
        "ai_error": "AI processing error: {error}",
        "search_error": "Search error: {error}",
        "database_error": "Database error: {error}",
        "context_not_found": "I cannot find information about '{query}' in the provided document.",
        "hallucination_detected": "I cannot provide a reliable answer based on the document content. Please try rephrasing your question."
    }
    
    # Success messages
    SUCCESS_MESSAGES = {
        "document_processed": "✅ Document processed successfully! Ready for intelligent chat.",
        "document_removed": "📄 Document removed successfully.",
        "chat_created": "💬 New chat created successfully.",
        "message_saved": "Message saved to chat history.",
        "context_validated": "✅ Response validated against document content."
    }

class RAGConfig:
    """NEW: Specific RAG optimization settings"""
    
    # Chunk quality settings
    MIN_CHUNK_LENGTH = 30
    MAX_CHUNK_LENGTH = 1000
    MIN_MEANINGFUL_WORDS = 3
    MIN_ALPHA_RATIO = 0.3
    
    # Context validation settings
    KEYWORD_OVERLAP_THRESHOLD = 0.2
    SIMILARITY_THRESHOLD = 0.8
    MAX_CONTEXT_CHUNKS = 3
    
    # Response validation settings
    ENABLE_HALLUCINATION_DETECTION = True
    HALLUCINATION_KEYWORDS = [
        "quantum computing",
        "google deepseek",
        "artificial intelligence can be built",
        "they have demonstrated"
    ]
    
    # Retrieval optimization
    ENABLE_CHUNK_SCORING = True
    PREFER_COMPLETE_SENTENCES = True
    ENABLE_CONTEXT_COMPRESSION = True

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
        "messages": MessageConfig.__dict__,
        "rag": RAGConfig.__dict__
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

def get_rag_config() -> RAGConfig:
    """Get RAG configuration instance"""
    return RAGConfig()

# Environment-based configuration overrides
def load_env_config():
    """Load configuration from environment variables"""
    if os.getenv("AI_MODEL"):
        AIConfig.AI_MODEL = os.getenv("AI_MODEL")
    
    if os.getenv("DB_PATH"):
        DatabaseConfig.DB_PATH = os.getenv("DB_PATH")
    
    if os.getenv("CHUNK_SIZE"):
        try:
            AIConfig.CHUNK_SIZE = int(os.getenv("CHUNK_SIZE"))
        except ValueError:
            pass
    
    if os.getenv("SEARCH_K"):
        try:
            AIConfig.SEARCH_K = int(os.getenv("SEARCH_K"))
        except ValueError:
            pass
    
    if os.getenv("AI_TEMPERATURE"):
        try:
            AIConfig.AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE"))
        except ValueError:
            pass

# Load environment overrides on import
load_env_config()

# Validation function
def validate_config():
    """Validate configuration settings"""
    errors = []
    
    if AIConfig.CHUNK_SIZE <= 0:
        errors.append("CHUNK_SIZE must be positive")
    
    if AIConfig.CHUNK_OVERLAP >= AIConfig.CHUNK_SIZE:
        errors.append("CHUNK_OVERLAP must be less than CHUNK_SIZE")
    
    if AIConfig.SEARCH_K <= 0:
        errors.append("SEARCH_K must be positive")
    
    if not (0 <= AIConfig.AI_TEMPERATURE <= 2):
        errors.append("AI_TEMPERATURE must be between 0 and 2")
    
    if errors:
        raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    return True

# Validate on import
try:
    validate_config()
except ValueError as e:
    print(f"Configuration warning: {e}")

# Export optimized settings for easy access
OPTIMIZED_SETTINGS = {
    "model": AIConfig.AI_MODEL,
    "chunk_size": AIConfig.CHUNK_SIZE,
    "chunk_overlap": AIConfig.CHUNK_OVERLAP,
    "search_k": AIConfig.SEARCH_K,
    "temperature": AIConfig.AI_TEMPERATURE,
    "search_type": AIConfig.SEARCH_TYPE,
    "max_chunks": AIConfig.MAX_CHUNKS
}