"""
Vector store management for SAVIN AI application.
Handles vector embeddings, storage, and retrieval operations.
"""

import tempfile
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from ..config.settings import AIConfig
from .exceptions import VectorStoreError


# Configure logging
logger = logging.getLogger(__name__)


class VectorStoreManager:
    """
    Manages vector store operations including creation, persistence, and retrieval.
    Uses ChromaDB with HuggingFace embeddings for semantic search.
    """
    
    def __init__(self):
        self.config = AIConfig()
        self.embeddings = self._create_embeddings()
    
    def _create_embeddings(self) -> HuggingFaceEmbeddings:
        """Create optimized HuggingFace embeddings model"""
        try:
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={
                    'device': 'cpu',
                    'trust_remote_code': False
                },
                encode_kwargs={
                    'normalize_embeddings': True,
                    'batch_size': self.config.BATCH_SIZE
                }
            )
            
            logger.info("Created HuggingFace embeddings model")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to create embeddings model: {e}")
            raise VectorStoreError(f"Embeddings initialization failed: {str(e)}")
    
    def create_vector_store(self, chunks: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> Chroma:
        """
        Create a vector store from text chunks.
        
        Args:
            chunks: List of text chunks to vectorize
            metadatas: Optional metadata for each chunk
            
        Returns:
            Configured Chroma vector store
            
        Raises:
            VectorStoreError: If vector store creation fails
        """
        if not chunks:
            raise VectorStoreError("No chunks provided for vector store creation")
        
        try:
            # Generate metadata if not provided
            if metadatas is None:
                metadatas = self._generate_metadata(chunks)
            
            # Ensure metadata list matches chunks list
            if len(metadatas) != len(chunks):
                logger.warning("Metadata count doesn't match chunks count, regenerating")
                metadatas = self._generate_metadata(chunks)
            
            # Create temporary directory for ChromaDB
            temp_dir = tempfile.mkdtemp()
            persist_directory = os.path.join(temp_dir, "chroma_db")
            
            # Create vector store
            vector_store = Chroma.from_texts(
                texts=chunks,
                embedding=self.embeddings,
                metadatas=metadatas,
                persist_directory=persist_directory
            )
            
            logger.info(f"Created vector store with {len(chunks)} chunks")
            return vector_store
            
        except Exception as e:
            logger.error(f"Vector store creation failed: {e}")
            raise VectorStoreError(f"Failed to create vector store: {str(e)}")
    
    def _generate_metadata(self, chunks: List[str]) -> List[Dict[str, Any]]:
        """Generate metadata for chunks"""
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            metadata = {
                "chunk_id": i,
                "chunk_length": len(chunk),
                "chunk_preview": chunk[:100] + "..." if len(chunk) > 100 else chunk,
                "chunk_position": self._get_chunk_position(i, len(chunks)),
                "word_count": len(chunk.split()),
                "has_numbers": any(char.isdigit() for char in chunk),
                "has_punctuation": any(char in ".,!?;:" for char in chunk)
            }
            metadatas.append(metadata)
        
        return metadatas
    
    def _get_chunk_position(self, index: int, total_chunks: int) -> str:
        """Determine chunk position in document"""
        third = total_chunks // 3
        if index < third:
            return "start"
        elif index < 2 * third:
            return "middle"
        else:
            return "end"
    
    def search_similar(self, vector_store: Chroma, query: str, k: int = 3) -> List[Tuple[str, float]]:
        """
        Search for similar chunks in vector store.
        
        Args:
            vector_store: Vector store to search
            query: Search query
            k: Number of results to return
            
        Returns:
            List of (chunk_text, similarity_score) tuples
        """
        try:
            results = vector_store.similarity_search_with_score(query, k=k)
            return [(doc.page_content, score) for doc, score in results]
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            raise VectorStoreError(f"Vector search failed: {str(e)}")
    
    def get_retriever(self, vector_store: Chroma, search_type: str = "similarity") -> Any:
        """
        Get a retriever from the vector store.
        
        Args:
            vector_store: Vector store to create retriever from
            search_type: Type of search ("similarity" or "mmr")
            
        Returns:
            Configured retriever
        """
        try:
            search_kwargs = {
                "k": self.config.SEARCH_K,
                "fetch_k": self.config.SEARCH_FETCH_K,
                "lambda_mult": self.config.SEARCH_LAMBDA
            }
            
            retriever = vector_store.as_retriever(
                search_type=search_type,
                search_kwargs=search_kwargs
            )
            
            logger.info(f"Created {search_type} retriever")
            return retriever
            
        except Exception as e:
            logger.error(f"Retriever creation failed: {e}")
            raise VectorStoreError(f"Failed to create retriever: {str(e)}")


class VectorStoreCache:
    """
    In-memory cache for vector stores to improve performance.
    """
    
    def __init__(self, max_size: int = 10):
        self.cache: Dict[str, Chroma] = {}
        self.max_size = max_size
        self.access_order: List[str] = []
    
    def get(self, key: str) -> Optional[Chroma]:
        """Get vector store from cache"""
        if key in self.cache:
            # Move to end of access order
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def put(self, key: str, vector_store: Chroma):
        """Put vector store in cache with LRU eviction"""
        # Remove if already exists
        if key in self.cache:
            self.access_order.remove(key)
        
        # Add to cache
        self.cache[key] = vector_store
        self.access_order.append(key)
        
        # Evict oldest if over limit
        while len(self.cache) > self.max_size:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]
    
    def remove(self, key: str) -> bool:
        """Remove vector store from cache"""
        if key in self.cache:
            del self.cache[key]
            self.access_order.remove(key)
            return True
        return False
    
    def clear(self):
        """Clear all cached vector stores"""
        self.cache.clear()
        self.access_order.clear()
    
    def size(self) -> int:
        """Get current cache size"""
        return len(self.cache)


class VectorStoreSerializer:
    """
    Handles serialization and deserialization of vector stores for persistence.
    """
    
    @staticmethod
    def serialize_vector_store(vector_store: Chroma) -> bytes:
        """
        Serialize vector store to bytes.
        
        Args:
            vector_store: Vector store to serialize
            
        Returns:
            Serialized vector store as bytes
        """
        try:
            return vector_store.serialize_to_bytes()
        except Exception as e:
            logger.error(f"Vector store serialization failed: {e}")
            raise VectorStoreError(f"Failed to serialize vector store: {str(e)}")
    
    @staticmethod
    def deserialize_vector_store(data: bytes, embeddings: HuggingFaceEmbeddings) -> Chroma:
        """
        Deserialize vector store from bytes.
        
        Args:
            data: Serialized vector store data
            embeddings: Embeddings model to use
            
        Returns:
            Deserialized vector store
        """
        try:
            # This would need to be implemented based on ChromaDB's deserialization API
            # For now, we'll raise a not implemented error
            raise NotImplementedError("Vector store deserialization not yet implemented")
        except Exception as e:
            logger.error(f"Vector store deserialization failed: {e}")
            raise VectorStoreError(f"Failed to deserialize vector store: {str(e)}")


# Global cache instance
_vector_store_cache = VectorStoreCache()


# Factory functions
def create_vector_store_manager() -> VectorStoreManager:
    """Create a new vector store manager instance"""
    return VectorStoreManager()


def get_vector_store_cache() -> VectorStoreCache:
    """Get the global vector store cache instance"""
    return _vector_store_cache


def create_vector_store_serializer() -> VectorStoreSerializer:
    """Create a new vector store serializer instance"""
    return VectorStoreSerializer()


# Backward compatibility functions
def get_vector_store(chunks: List[str]) -> Chroma:
    """Create vector store from chunks (backward compatibility)"""
    manager = create_vector_store_manager()
    return manager.create_vector_store(chunks)


def get_optimized_embeddings() -> HuggingFaceEmbeddings:
    """Get optimized embeddings model (backward compatibility)"""
    manager = create_vector_store_manager()
    return manager.embeddings