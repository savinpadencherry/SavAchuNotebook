"""
Database management for SAVIN AI application.
Handles SQLite database operations, chat storage, and data persistence.
"""

import sqlite3
import logging
import json
import os
import threading
from contextlib import contextmanager
from typing import Dict, List, Any, Optional, Tuple
import pickle
import time
from datetime import datetime, timedelta

from src.config.settings import DatabaseConfig

import sqlite3
import json
import pickle
import os
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager

from .models import ChatModel, MessageModel, DocumentModel, VectorStoreModel, MessageRole
from ..config.settings import DatabaseConfig


# Configure logging
logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database-related errors"""
    pass


class ChatDatabase:
    """
    Local SQLite database manager for storing chats, messages, and vector stores.
    Provides thread-safe operations with proper connection management.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database with optional custom path"""
        self.db_path = db_path or DatabaseConfig.DB_PATH
        self.timeout = DatabaseConfig.DB_TIMEOUT
        self._ensure_database_exists()
        
    def _ensure_database_exists(self):
        """Ensure database file and tables exist"""
        try:
            with self._get_connection() as conn:
                self._create_tables(conn)
                logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise DatabaseError(f"Database initialization failed: {e}")
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper error handling"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=self.timeout)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise DatabaseError(f"Database operation failed: {e}")
        finally:
            if conn:
                conn.close()
    
    def _create_tables(self, conn: sqlite3.Connection):
        """Create all required database tables"""
        cursor = conn.cursor()
        
        # Chats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                document_name TEXT,
                document_type TEXT,
                document_size INTEGER,
                total_chunks INTEGER DEFAULT 0,
                is_processed BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                chat_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                relevant_context TEXT,
                FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
            )
        ''')
        
        # Vector stores table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vector_stores (
                chat_id TEXT PRIMARY KEY,
                vector_data BLOB,
                chunks_data TEXT,
                metadata_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
            )
        ''')
        
        # Documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                chat_id TEXT PRIMARY KEY,
                original_text TEXT,
                processed_chunks TEXT,
                upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_name TEXT,
                file_type TEXT,
                file_size INTEGER,
                FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chats_updated ON chats(updated_at DESC)')
        
        conn.commit()


class ChatRepository:
    """Repository class for chat-related database operations"""
    
    def __init__(self, database: ChatDatabase):
        self.db = database
    
    def create_chat(self, title: str, document_name: Optional[str] = None, 
                   document_type: Optional[str] = None, document_size: Optional[int] = None) -> str:
        """Create a new chat and return its ID"""
        chat_id = str(uuid.uuid4())
        
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO chats (id, title, document_name, document_type, document_size)
                VALUES (?, ?, ?, ?, ?)
            ''', (chat_id, title, document_name, document_type, document_size))
            conn.commit()
            
        logger.info(f"Created new chat: {chat_id}")
        return chat_id
    
    def get_all_chats(self) -> List[Dict[str, Any]]:
        """Get all chats ordered by most recent"""
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, created_at, updated_at, document_name, 
                       document_type, total_chunks, is_processed
                FROM chats 
                ORDER BY updated_at DESC
            ''')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_chat_info(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific chat"""
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, created_at, updated_at, document_name,
                       document_type, document_size, total_chunks, is_processed
                FROM chats 
                WHERE id = ?
            ''', (chat_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_chat_title(self, chat_id: str, new_title: str) -> bool:
        """Update chat title"""
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE chats 
                SET title = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (new_title, chat_id))
            conn.commit()
            
            return cursor.rowcount > 0
    
    def delete_chat(self, chat_id: str) -> bool:
        """Delete a chat and all associated data"""
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM chats WHERE id = ?', (chat_id,))
            conn.commit()
            
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Deleted chat: {chat_id}")
            
            return deleted


class MessageRepository:
    """Repository class for message-related database operations"""
    
    def __init__(self, database: ChatDatabase):
        self.db = database
    
    def add_message(self, chat_id: str, role: str, content: str, 
                   relevant_context: Optional[str] = None) -> str:
        """Add a new message to a chat"""
        message_id = str(uuid.uuid4())
        
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            
            # Insert message
            cursor.execute('''
                INSERT INTO messages (id, chat_id, role, content, relevant_context)
                VALUES (?, ?, ?, ?, ?)
            ''', (message_id, chat_id, role, content, relevant_context))
            
            # Update chat timestamp
            cursor.execute('''
                UPDATE chats SET updated_at = CURRENT_TIMESTAMP WHERE id = ?
            ''', (chat_id,))
            
            conn.commit()
        
        return message_id
    
    def get_chat_messages(self, chat_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a specific chat"""
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, role, content, timestamp, relevant_context
                FROM messages 
                WHERE chat_id = ? 
                ORDER BY timestamp ASC
            ''', (chat_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_messages_by_chat(self, chat_id: str) -> int:
        """Delete all messages for a specific chat"""
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM messages WHERE chat_id = ?', (chat_id,))
            conn.commit()
            
            return cursor.rowcount


class DocumentRepository:
    """Repository class for document-related database operations"""
    
    def __init__(self, database: ChatDatabase):
        self.db = database
    
    def save_document_data(self, chat_id: str, original_text: str, processed_chunks: List[str],
                          file_name: Optional[str] = None, file_type: Optional[str] = None,
                          file_size: Optional[int] = None):
        """Save document text and processed chunks"""
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO documents 
                (chat_id, original_text, processed_chunks, file_name, file_type, file_size)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (chat_id, original_text, json.dumps(processed_chunks), 
                 file_name, file_type, file_size))
            conn.commit()
    
    def get_document_data(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get document data for a chat"""
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT original_text, processed_chunks, upload_timestamp,
                       file_name, file_type, file_size
                FROM documents 
                WHERE chat_id = ?
            ''', (chat_id,))
            
            row = cursor.fetchone()
            if row:
                data = dict(row)
                data['processed_chunks'] = json.loads(data['processed_chunks'])
                return data
            
            return None
    
    def remove_document(self, chat_id: str) -> bool:
        """Remove document data for a chat"""
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM documents WHERE chat_id = ?', (chat_id,))
            conn.commit()
            
            return cursor.rowcount > 0


class VectorStoreRepository:
    """Repository class for vector store database operations"""
    
    def __init__(self, database: ChatDatabase):
        self.db = database
    
    def save_vector_store(self, chat_id: str, vector_store: Any, chunks: List[str], 
                         metadata: List[Dict[str, Any]]):
        """Save vector store data"""
        try:
            vector_data = pickle.dumps(vector_store.serialize_to_bytes())
        except Exception as e:
            logger.error(f"Failed to serialize vector store: {e}")
            raise DatabaseError(f"Vector store serialization failed: {e}")
        
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            
            # Save vector store
            cursor.execute('''
                INSERT OR REPLACE INTO vector_stores 
                (chat_id, vector_data, chunks_data, metadata_data)
                VALUES (?, ?, ?, ?)
            ''', (chat_id, vector_data, json.dumps(chunks), json.dumps(metadata)))
            
            # Update chat processing status
            cursor.execute('''
                UPDATE chats 
                SET is_processed = TRUE, total_chunks = ? 
                WHERE id = ?
            ''', (len(chunks), chat_id))
            
            conn.commit()
    
    def load_vector_store(self, chat_id: str) -> Optional[Tuple[Any, List[str], List[Dict[str, Any]]]]:
        """Load vector store data for a chat"""
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT vector_data, chunks_data, metadata_data
                FROM vector_stores 
                WHERE chat_id = ?
            ''', (chat_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            try:
                vector_data = pickle.loads(row['vector_data'])
                chunks = json.loads(row['chunks_data'])
                metadata = json.loads(row['metadata_data'])
                
                return vector_data, chunks, metadata
            except Exception as e:
                logger.error(f"Failed to deserialize vector store: {e}")
                return None
    
    def delete_vector_store(self, chat_id: str) -> bool:
        """Delete vector store for a chat"""
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM vector_stores WHERE chat_id = ?', (chat_id,))
            conn.commit()
            
            return cursor.rowcount > 0


# Factory function for creating database instances
def create_database(db_path: Optional[str] = None) -> ChatDatabase:
    """Create a new database instance"""
    return ChatDatabase(db_path)


# Factory functions for repositories
def create_chat_repository(database: ChatDatabase) -> ChatRepository:
    """Create a chat repository instance"""
    return ChatRepository(database)


def create_message_repository(database: ChatDatabase) -> MessageRepository:
    """Create a message repository instance"""
    return MessageRepository(database)


def create_document_repository(database: ChatDatabase) -> DocumentRepository:
    """Create a document repository instance"""
    return DocumentRepository(database)


def create_vector_store_repository(database: ChatDatabase) -> VectorStoreRepository:
    """Create a vector store repository instance"""
    return VectorStoreRepository(database)