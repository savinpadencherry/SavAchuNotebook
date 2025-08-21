# NoteBook AI Configuration - Optimized for Performance & Quality
# Customize these settings to personalize your experience

# AI Model Settings - Optimized for structured responses
AI_MODEL = "gemma2:2b"  # Lightweight but capable model
AI_TEMPERATURE = 0.2    # Balanced creativity for structured responses
AI_MAX_TOKENS = 1024    # Longer responses for comprehensive answers

# Document Processing - Optimized for better context
CHUNK_SIZE = 800        # Larger chunks for better context retention
CHUNK_OVERLAP = 100     # Increased overlap for continuity
MAX_CHUNKS = 20         # More chunks for comprehensive analysis

# Vector Search Settings - Enhanced for quality
SEARCH_TYPE = "mmr"     # Maximum Marginal Relevance for diverse results
SEARCH_K = 4            # More chunks for comprehensive answers
SEARCH_FETCH_K = 15     # More candidates for better selection
SEARCH_LAMBDA = 0.5     # Balanced relevance vs diversity

# UI Settings - Optimized for single-view experience
APP_TITLE = "SAVIN AI"
APP_ICON = "🤖"
THEME_COLOR = "#667eea"
ANIMATION_SPEED = 150   # Faster animations for responsiveness

# Database Settings
DB_NAME = "notebook_ai.db"
AUTO_BACKUP = True      # Automatically backup database

# Performance Settings - Optimized for speed
BATCH_SIZE = 6          # Increased batch size for faster processing
NUM_THREADS = 6         # More threads for parallel processing
ENABLE_GPU = False      # Use GPU if available (requires CUDA)

# File Upload Settings
MAX_FILE_SIZE = 15      # Increased max file size to 15MB
ALLOWED_TYPES = ["pdf", "docx", "txt"]

# Advanced Settings - Lightning fast responses
DEBUG_MODE = False      # Disable debug for speed
CACHE_EMBEDDINGS = True # Cache embedding model for faster startup
AUTO_TITLE = True       # Auto-generate chat titles
LIGHTWEIGHT_MODE = True # Enable lightweight optimizations

# REQUIREMENT 5: Redis Vector Caching for ultra-fast responses
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None   # Set if Redis requires authentication
VECTOR_CACHE_TTL = 3600 # Cache vectors for 1 hour
SEARCH_CACHE_TTL = 1800 # Cache search results for 30 minutes
ENABLE_REDIS_CACHE = True # Enable Redis caching system
