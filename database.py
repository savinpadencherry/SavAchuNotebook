import sqlite3
import json
import pickle
import os
from datetime import datetime
import uuid
from typing import List, Dict, Any, Optional

class ChatDatabase:
    """
    Local SQLite database for storing chats, messages, and vector stores
    """
    
    def __init__(self, db_path: str = "notebook_ai.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
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
        
        # Vector stores table (storing serialized FAISS indices)
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
        
        # Documents table (storing original document text)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                chat_id TEXT PRIMARY KEY,
                original_text TEXT,
                processed_chunks TEXT,
                upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_chat(self, title: str, document_name: str = None, document_type: str = None, document_size: int = None) -> str:
        """Create a new chat and return its ID"""
        chat_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chats (id, title, document_name, document_type, document_size)
            VALUES (?, ?, ?, ?, ?)
        ''', (chat_id, title, document_name, document_type, document_size))
        
        conn.commit()
        conn.close()
        return chat_id
    
    def get_all_chats(self) -> List[Dict]:
        """Get all chats ordered by most recent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, created_at, updated_at, document_name, 
                   document_type, total_chunks, is_processed
            FROM chats 
            ORDER BY updated_at DESC
        ''')
        
        chats = []
        for row in cursor.fetchall():
            chats.append({
                'id': row[0],
                'title': row[1],
                'created_at': row[2],
                'updated_at': row[3],
                'document_name': row[4],
                'document_type': row[5],
                'total_chunks': row[6],
                'is_processed': bool(row[7])
            })
        
        conn.close()
        return chats
    
    def get_chat_messages(self, chat_id: str) -> List[Dict]:
        """Get all messages for a specific chat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT role, content, timestamp, relevant_context
            FROM messages 
            WHERE chat_id = ? 
            ORDER BY timestamp ASC
        ''', (chat_id,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'role': row[0],
                'content': row[1],
                'timestamp': row[2],
                'relevant_context': row[3]
            })
        
        conn.close()
        return messages
    
    def add_message(self, chat_id: str, role: str, content: str, relevant_context: str = None):
        """Add a new message to a chat"""
        message_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO messages (id, chat_id, role, content, relevant_context)
            VALUES (?, ?, ?, ?, ?)
        ''', (message_id, chat_id, role, content, relevant_context))
        
        # Update chat's updated_at timestamp
        cursor.execute('''
            UPDATE chats SET updated_at = CURRENT_TIMESTAMP WHERE id = ?
        ''', (chat_id,))
        
        conn.commit()
        conn.close()
    
    def save_document_data(self, chat_id: str, original_text: str, processed_chunks: List[str]):
        """Save document text and processed chunks"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO documents (chat_id, original_text, processed_chunks)
            VALUES (?, ?, ?)
        ''', (chat_id, original_text, json.dumps(processed_chunks)))
        
        conn.commit()
        conn.close()
    
    def save_vector_store(self, chat_id: str, vector_store, chunks: List[str], metadata: List[Dict]):
        """Save vector store data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Serialize the FAISS vector store
        vector_data = pickle.dumps(vector_store.serialize_to_bytes())
        chunks_json = json.dumps(chunks)
        metadata_json = json.dumps(metadata)
        
        cursor.execute('''
            INSERT OR REPLACE INTO vector_stores (chat_id, vector_data, chunks_data, metadata_data)
            VALUES (?, ?, ?, ?)
        ''', (chat_id, vector_data, chunks_json, metadata_json))
        
        # Update chat processing status
        cursor.execute('''
            UPDATE chats SET is_processed = TRUE, total_chunks = ? WHERE id = ?
        ''', (len(chunks), chat_id))
        
        conn.commit()
        conn.close()
    
    def load_vector_store(self, chat_id: str):
        """Load vector store data for a chat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT vector_data, chunks_data, metadata_data
            FROM vector_stores 
            WHERE chat_id = ?
        ''', (chat_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            try:
                # Deserialize vector store
                from langchain_community.vectorstores import FAISS
                from langchain_community.embeddings import HuggingFaceEmbeddings
                
                embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    model_kwargs={'device': 'cpu', 'trust_remote_code': False},
                    encode_kwargs={'normalize_embeddings': True, 'batch_size': 4}
                )
                
                vector_data = pickle.loads(row[0])
                chunks = json.loads(row[1])
                metadata = json.loads(row[2])
                
                # Reconstruct FAISS vector store
                vector_store = FAISS.deserialize_from_bytes(
                    serialized=vector_data,
                    embeddings=embeddings
                )
                
                return vector_store, chunks, metadata
                
            except Exception as e:
                print(f"Error loading vector store: {e}")
                return None, None, None
        
        return None, None, None
    
    def get_document_data(self, chat_id: str):
        """Get document data for a chat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT original_text, processed_chunks
            FROM documents 
            WHERE chat_id = ?
        ''', (chat_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return row[0], json.loads(row[1])
        return None, None
    
    def delete_chat(self, chat_id: str):
        """Delete a chat and all associated data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # SQLite will handle cascading deletes
        cursor.execute('DELETE FROM chats WHERE id = ?', (chat_id,))
        
        conn.commit()
        conn.close()
    
    def update_chat_title(self, chat_id: str, new_title: str):
        """Update chat title"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE chats SET title = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (new_title, chat_id))
        
        conn.commit()
        conn.close()
    
    def get_chat_info(self, chat_id: str) -> Optional[Dict]:
        """Get basic chat information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, document_name, document_type, 
                   total_chunks, is_processed, created_at, updated_at
            FROM chats 
            WHERE id = ?
        ''', (chat_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'title': row[1],
                'document_name': row[2],
                'document_type': row[3],
                'total_chunks': row[4],
                'is_processed': bool(row[5]),
                'created_at': row[6],
                'updated_at': row[7]
            }
        return None
    
    def get_chat_documents(self, chat_id: str) -> List[Dict]:
        """Get all documents associated with a chat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, document_name, document_type, total_chunks, is_processed
            FROM chats 
            WHERE id = ? AND document_name IS NOT NULL
        ''', (chat_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        documents = []
        for row in rows:
            documents.append({
                'id': row[0],
                'name': row[1],
                'type': row[2],
                'chunks': row[3],
                'processed': bool(row[4])
            })
        
        return documents
    
    def remove_document(self, chat_id: str):
        """Remove document data from a chat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE chats SET 
                document_name = NULL,
                document_type = NULL, 
                document_size = NULL,
                total_chunks = 0,
                is_processed = FALSE,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (chat_id,))
        
        # Also remove vector store data
        cursor.execute('DELETE FROM vector_stores WHERE chat_id = ?', (chat_id,))
        cursor.execute('DELETE FROM documents WHERE chat_id = ?', (chat_id,))
        
        conn.commit()
        conn.close()
