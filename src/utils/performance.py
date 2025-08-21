"""
Performance optimization utilities for SAVIN AI.
Provides caching, lazy loading, and performance monitoring.
"""

import streamlit as st
import logging
import functools
import time
from typing import Any, Callable, Dict, Optional, List
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class PerformanceCache:
    """Singleton cache for expensive operations"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._cache = {}
            self._embeddings_model = None
            self._llm_model = None
            self._initialized = True
    
    def get_embeddings_model(self):
        """Get cached embeddings model"""
        if self._embeddings_model is None:
            with performance_timer("Loading embeddings model"):
                import warnings
                warnings.filterwarnings('ignore', category=FutureWarning)
                warnings.filterwarnings('ignore', message='.*deprecated.*')
                
                from langchain_community.embeddings import HuggingFaceEmbeddings
                from src.config.settings import AIConfig
                
                self._embeddings_model = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': False}
                )
                logger.info("Embeddings model loaded and cached")
        return self._embeddings_model
    
    def get_llm_model(self):
        """Get cached LLM model"""
        if self._llm_model is None:
            with performance_timer("Loading LLM model"):
                import warnings
                warnings.filterwarnings('ignore', category=FutureWarning)
                warnings.filterwarnings('ignore', message='.*deprecated.*')
                
                from langchain_community.llms import Ollama
                from src.config.settings import AIConfig
                
                self._llm_model = Ollama(
                    model=AIConfig.AI_MODEL,
                    temperature=AIConfig.AI_TEMPERATURE,
                    num_predict=AIConfig.AI_MAX_TOKENS,
                )
                logger.info(f"LLM model {AIConfig.AI_MODEL} loaded and cached")
        return self._llm_model
    
    def cache_result(self, key: str, result: Any):
        """Cache a result with the given key"""
        self._cache[key] = result
    
    def get_cached_result(self, key: str) -> Optional[Any]:
        """Get cached result by key"""
        return self._cache.get(key)
    
    def clear_cache(self):
        """Clear all cached results"""
        self._cache.clear()
        logger.info("Performance cache cleared")


# Global cache instance
_performance_cache = PerformanceCache()


@contextmanager
def performance_timer(operation_name: str):
    """Context manager for timing operations"""
    start_time = time.time()
    logger.info(f"Starting: {operation_name}")
    try:
        yield
    finally:
        elapsed = time.time() - start_time
        logger.info(f"Completed: {operation_name} in {elapsed:.2f} seconds")


def cache_expensive_operation(cache_key: str = None, ttl: int = 3600):
    """Decorator to cache expensive operations"""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key if not provided
            key = cache_key or f"{func.__name__}_{str(args)}_{str(kwargs)}"
            
            # Try to get from cache
            cached_result = _performance_cache.get_cached_result(key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {key}")
                return cached_result
            
            # Execute function and cache result
            with performance_timer(f"Computing {func.__name__}"):
                result = func(*args, **kwargs)
                _performance_cache.cache_result(key, result)
                logger.debug(f"Cached result for {key}")
                return result
        
        return wrapper
    return decorator


@st.cache_resource(show_spinner=False)
def get_cached_embeddings_model():
    """Streamlit cached embeddings model - optimized"""
    with performance_timer("Loading embeddings model"):
        return _performance_cache.get_embeddings_model()


@st.cache_resource(show_spinner=False)
def get_cached_llm_model():
    """Streamlit cached LLM model - optimized"""
    with performance_timer("Loading LLM model"):
        return _performance_cache.get_llm_model()


@st.cache_data(ttl=3600)
def cache_document_processing(_file_content: bytes, filename: str) -> Dict[str, Any]:
    """Cache document processing results"""
    # This will be implemented by the document processor
    pass


@st.cache_data(ttl=1800)
def cache_web_search(query: str, search_type: str = "web") -> List[Dict[str, Any]]:
    """Cache web search results"""
    # This will be implemented by the web search module
    pass


def lazy_load_component(component_name: str):
    """Decorator for lazy loading UI components"""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if f"loaded_{component_name}" not in st.session_state:
                with st.spinner(f"Loading {component_name}..."):
                    result = func(*args, **kwargs)
                    st.session_state[f"loaded_{component_name}"] = True
                    return result
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator


class SessionStateManager:
    """Manages Streamlit session state efficiently"""
    
    @staticmethod
    def initialize_defaults():
        """Initialize default session state values"""
        defaults = {
            'performance_cache_initialized': False,
            'models_loaded': False,
            'current_chat_id': None,
            'chat_history': [],
            'vectorstore': None,
            'conversation': None,
            'processing': False,
            'relevant_context': "",
            'show_new_chat_dialog': False,
            'last_activity': time.time()
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    @staticmethod
    def update_activity():
        """Update last activity timestamp"""
        st.session_state.last_activity = time.time()
    
    @staticmethod
    def is_session_expired(timeout_seconds: int = 3600) -> bool:
        """Check if session has expired"""
        if 'last_activity' not in st.session_state:
            return True
        return time.time() - st.session_state.last_activity > timeout_seconds


def preload_models():
    """Preload models in background - optimized for speed"""
    if not st.session_state.get('models_loaded', False):
        # Use a more subtle loading indicator
        placeholder = st.empty()
        placeholder.info("🚀 Loading AI models...")
        
        try:
            # Load models without blocking UI
            get_cached_embeddings_model()
            get_cached_llm_model()
            
            st.session_state.models_loaded = True
            placeholder.empty()  # Remove loading message immediately
            
        except Exception as e:
            placeholder.error(f"Failed to load models: {e}")
            logger.error(f"Model loading failed: {e}")


def optimize_streamlit_performance():
    """Apply Streamlit performance optimizations"""
    # Configure Streamlit for better performance
    if hasattr(st, '_config'):
        st._config.set_option('server.runOnSave', False)
        st._config.set_option('server.allowRunOnSave', False)
    
    # Hide Streamlit elements that cause recomputation
    hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display:none;}
        .stApp > header {display: none;}
        
        /* Reduce recomputation triggers */
        .main .block-container {
            padding-top: 1rem;
        }
        
        /* Cache-friendly styling */
        .element-container {
            will-change: auto;
        }
        
        /* Reduce visual lag */
        .stSpinner > div {
            border-width: 2px;
        }
        </style>
    """
    
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# Performance monitoring
class PerformanceMonitor:
    """Monitor application performance"""
    
    def __init__(self):
        self.start_time = time.time()
        self.operation_times = {}
    
    def log_operation(self, operation: str, duration: float):
        """Log operation duration"""
        if operation not in self.operation_times:
            self.operation_times[operation] = []
        self.operation_times[operation].append(duration)
        
        if len(self.operation_times[operation]) > 100:
            # Keep only last 100 measurements
            self.operation_times[operation] = self.operation_times[operation][-100:]
    
    def get_average_time(self, operation: str) -> float:
        """Get average time for an operation"""
        times = self.operation_times.get(operation, [])
        return sum(times) / len(times) if times else 0.0
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            'uptime': time.time() - self.start_time,
            'operation_averages': {
                op: self.get_average_time(op) 
                for op in self.operation_times.keys()
            },
            'total_operations': sum(len(times) for times in self.operation_times.values())
        }


# Global performance monitor
_performance_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor"""
    return _performance_monitor
