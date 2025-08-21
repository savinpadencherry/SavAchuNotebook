"""
Data models and schemas for SAVIN AI application.
Defines the structure and validation for data entities.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class MessageRole(Enum):
    """Enumeration for message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class FileType(Enum):
    """Enumeration for supported file types"""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"


@dataclass
class ChatModel:
    """Data model for chat conversations"""
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    document_name: Optional[str] = None
    document_type: Optional[str] = None
    document_size: Optional[int] = None
    total_chunks: int = 0
    is_processed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            'document_name': self.document_name,
            'document_type': self.document_type,
            'document_size': self.document_size,
            'total_chunks': self.total_chunks,
            'is_processed': self.is_processed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatModel':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            title=data['title'],
            created_at=datetime.fromisoformat(data['created_at']) if isinstance(data['created_at'], str) else data['created_at'],
            updated_at=datetime.fromisoformat(data['updated_at']) if isinstance(data['updated_at'], str) else data['updated_at'],
            document_name=data.get('document_name'),
            document_type=data.get('document_type'),
            document_size=data.get('document_size'),
            total_chunks=data.get('total_chunks', 0),
            is_processed=data.get('is_processed', False)
        )


@dataclass
class MessageModel:
    """Data model for chat messages"""
    id: str
    chat_id: str
    role: MessageRole
    content: str
    timestamp: datetime
    relevant_context: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'role': self.role.value if isinstance(self.role, MessageRole) else self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            'relevant_context': self.relevant_context
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MessageModel':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            chat_id=data['chat_id'],
            role=MessageRole(data['role']) if isinstance(data['role'], str) else data['role'],
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']) if isinstance(data['timestamp'], str) else data['timestamp'],
            relevant_context=data.get('relevant_context')
        )


@dataclass
class DocumentModel:
    """Data model for processed documents"""
    chat_id: str
    original_text: str
    processed_chunks: List[str]
    upload_timestamp: datetime
    file_name: Optional[str] = None
    file_type: Optional[FileType] = None
    file_size: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'chat_id': self.chat_id,
            'original_text': self.original_text,
            'processed_chunks': self.processed_chunks,
            'upload_timestamp': self.upload_timestamp.isoformat() if isinstance(self.upload_timestamp, datetime) else self.upload_timestamp,
            'file_name': self.file_name,
            'file_type': self.file_type.value if isinstance(self.file_type, FileType) else self.file_type,
            'file_size': self.file_size
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentModel':
        """Create from dictionary"""
        return cls(
            chat_id=data['chat_id'],
            original_text=data['original_text'],
            processed_chunks=data['processed_chunks'],
            upload_timestamp=datetime.fromisoformat(data['upload_timestamp']) if isinstance(data['upload_timestamp'], str) else data['upload_timestamp'],
            file_name=data.get('file_name'),
            file_type=FileType(data['file_type']) if data.get('file_type') else None,
            file_size=data.get('file_size')
        )


@dataclass
class VectorStoreModel:
    """Data model for vector store data"""
    chat_id: str
    vector_data: bytes
    chunks_data: List[str]
    metadata_data: List[Dict[str, Any]]
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'chat_id': self.chat_id,
            'vector_data': self.vector_data,
            'chunks_data': self.chunks_data,
            'metadata_data': self.metadata_data,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VectorStoreModel':
        """Create from dictionary"""
        return cls(
            chat_id=data['chat_id'],
            vector_data=data['vector_data'],
            chunks_data=data['chunks_data'],
            metadata_data=data['metadata_data'],
            created_at=datetime.fromisoformat(data['created_at']) if isinstance(data['created_at'], str) else data['created_at']
        )


@dataclass
class SearchResult:
    """Data model for search results"""
    title: str
    url: str
    summary: str
    score: Optional[float] = None
    source: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'url': self.url,
            'summary': self.summary,
            'score': self.score,
            'source': self.source
        }


@dataclass
class ProcessingStatus:
    """Data model for document processing status"""
    chat_id: str
    status: str
    progress: float
    message: str
    timestamp: datetime
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'chat_id': self.chat_id,
            'status': self.status,
            'progress': self.progress,
            'message': self.message,
            'timestamp': self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            'error': self.error
        }


# Type aliases for common data structures
ChatList = List[ChatModel]
MessageList = List[MessageModel]
SearchResultList = List[SearchResult]
ChunkList = List[str]
MetadataList = List[Dict[str, Any]]