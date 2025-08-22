"""
Redis-based vector caching system for SAVIN AI
Provides lightning-fast vector operations and caching
"""
import time
import pickle
import hashlib
import json
from typing import Dict, List, Any, Optional
import streamlit as st

# Redis import with fallback
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️ Redis not available - install with: pip install redis")

try:
    import config
except ImportError:
    class config:
        REDIS_HOST = "localhost"
        REDIS_PORT = 6379
        REDIS_DB = 0
        VECTOR_CACHE_TTL = 3600  # 1 hour
        ENABLE_REDIS_CACHE = True

class VectorCacheManager:
    """Redis-based vector store caching for ultra-fast responses"""
    
    def __init__(self):
        """Initialize Redis connection"""
        self.redis_client = None
        self.enabled = config.ENABLE_REDIS_CACHE and REDIS_AVAILABLE
        
        if self.enabled:
            try:
                self.redis_client = redis.Redis(
                    host=config.REDIS_HOST,
                    port=config.REDIS_PORT,
                    db=config.REDIS_DB,
                    decode_responses=False  # Keep binary for pickle
                )
                # Test connection
                self.redis_client.ping()
                print("✅ Redis cache connected successfully")
            except Exception as e:
                print(f"⚠️ Redis cache unavailable: {e}")
                self.enabled = False
                self.redis_client = None
    
    def _get_document_hash(self, document_text: str) -> str:
        """Generate unique hash for document content"""
        return hashlib.sha256(document_text.encode()).hexdigest()[:16]
    
    def _get_cache_key(self, doc_hash: str, cache_type: str) -> str:
        """Generate cache key for Redis"""
        return f"savin_ai:{cache_type}:{doc_hash}"
    
    def cache_vector_store(self, document_text: str, vector_store, chunks: List[str], metadata: List[Dict]) -> bool:
        """Cache vector store with Redis"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            doc_hash = self._get_document_hash(document_text)
            
            # Cache vector store
            vector_key = self._get_cache_key(doc_hash, "vectors")
            vector_data = pickle.dumps({
                'vector_store': vector_store.serialize_to_bytes(),
                'chunks': chunks,
                'metadata': metadata,
                'timestamp': time.time()
            })
            
            self.redis_client.setex(
                vector_key, 
                config.VECTOR_CACHE_TTL, 
                vector_data
            )
            
            # Cache document text for reference
            text_key = self._get_cache_key(doc_hash, "text")
            self.redis_client.setex(
                text_key, 
                config.VECTOR_CACHE_TTL, 
                document_text.encode()
            )
            
            return True
            
        except Exception as e:
            print(f"⚠️ Error caching vectors: {e}")
            return False
    
    def get_cached_vector_store(self, document_text: str):
        """Retrieve cached vector store"""
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            doc_hash = self._get_document_hash(document_text)
            vector_key = self._get_cache_key(doc_hash, "vectors")
            
            cached_data = self.redis_client.get(vector_key)
            if cached_data:
                data = pickle.loads(cached_data)
                
                # Reconstruct vector store from cached bytes
                from langchain_community.vectorstores import FAISS
                from utils import get_optimized_embeddings
                
                embeddings = get_optimized_embeddings()
                vector_store = FAISS.deserialize_from_bytes(
                    data['vector_store'], 
                    embeddings
                )
                
                return {
                    'vector_store': vector_store,
                    'chunks': data['chunks'],
                    'metadata': data['metadata'],
                    'from_cache': True
                }
        
        except Exception as e:
            print(f"⚠️ Error retrieving cached vectors: {e}")
        
        return None
    
    def cache_search_results(self, query: str, search_type: str, results: List[Dict]) -> bool:
        """Cache web search results"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            query_hash = hashlib.sha256(query.encode()).hexdigest()[:12]
            cache_key = f"savin_ai:search:{search_type}:{query_hash}"
            
            cache_data = {
                'results': results,
                'timestamp': time.time(),
                'query': query
            }
            
            self.redis_client.setex(
                cache_key,
                1800,  # 30 minutes for search results
                pickle.dumps(cache_data)
            )
            
            return True
            
        except Exception as e:
            print(f"⚠️ Error caching search results: {e}")
            return False
    
    def get_cached_search_results(self, query: str, search_type: str) -> Optional[List[Dict]]:
        """Retrieve cached search results"""
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            query_hash = hashlib.sha256(query.encode()).hexdigest()[:12]
            cache_key = f"savin_ai:search:{search_type}:{query_hash}"
            
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                data = pickle.loads(cached_data)
                return data['results']
        
        except Exception as e:
            print(f"⚠️ Error retrieving cached search: {e}")
        
        return None
    
    def clear_cache(self, pattern: str = "savin_ai:*") -> int:
        """Clear cache entries matching pattern"""
        if not self.enabled or not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
            
        except Exception as e:
            print(f"⚠️ Error clearing cache: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.enabled or not self.redis_client:
            return {"status": "disabled"}
        
        try:
            info = self.redis_client.info()
            vector_keys = len(self.redis_client.keys("savin_ai:vectors:*"))
            search_keys = len(self.redis_client.keys("savin_ai:search:*"))
            
            return {
                "status": "active",
                "used_memory": info.get("used_memory_human", "N/A"),
                "total_keys": info.get("db0", {}).get("keys", 0),
                "vector_cache_count": vector_keys,
                "search_cache_count": search_keys,
                "uptime": info.get("uptime_in_seconds", 0)
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}

# Global cache manager instance
cache_manager = VectorCacheManager()

@st.cache_resource
def get_cache_manager():
    """Get cached instance of VectorCacheManager"""
    return cache_manager

# Enhanced vector store creation with caching
def get_cached_vector_store(document_text: str, chunks: List[str]):
    """Create or retrieve cached vector store"""
    cache_mgr = get_cache_manager()
    
    # Try to get from cache first
    cached_result = cache_mgr.get_cached_vector_store(document_text)
    if cached_result:
        st.success("⚡ Using cached vectors - lightning fast!")
        return cached_result['vector_store']
    
    # Create new vector store
    st.info("🔄 Creating new vector store...")
    from utils import get_vector_store
    
    vector_store = get_vector_store(chunks)
    
    # Cache for future use
    metadata = [{"chunk_id": i, "length": len(chunk)} for i, chunk in enumerate(chunks)]
    cache_mgr.cache_vector_store(document_text, vector_store, chunks, metadata)
    
    return vector_store

# Enhanced web search with caching
def get_cached_web_search(query: str, search_type: str = "combined"):
    """Get cached web search results"""
    cache_mgr = get_cache_manager()
    
    # Try cache first
    cached_results = cache_mgr.get_cached_search_results(query, search_type)
    if cached_results:
        return cached_results
    
    # Perform new search
    from web_search import WebSearchManager
    web_search = WebSearchManager()
    
    if search_type == "wikipedia":
        results = web_search.search_wikipedia(query)
    elif search_type == "duckduckgo":
        results = web_search.search_duckduckgo(query)
    else:
        results = web_search.combined_search(query)
    
    # Cache results
    cache_mgr.cache_search_results(query, search_type, results)
    
    return results
