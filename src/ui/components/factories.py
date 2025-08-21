"""
Factory functions for creating UI component instances.
Provides centralized component instantiation for the SAVIN AI application.
"""

from .chat import (
    ChatInterface, InputBar, QuickPrompts, DocumentUploadWidget, 
    ChatStats, ProcessingStatus, MessageFormatter
)


def create_chat_interface() -> ChatInterface:
    """Create a new chat interface instance"""
    return ChatInterface()


def create_input_bar() -> InputBar:
    """Create a new input bar instance"""
    return InputBar()


def create_quick_prompts() -> QuickPrompts:
    """Create a new quick prompts instance"""
    return QuickPrompts()


def create_document_upload_widget() -> DocumentUploadWidget:
    """Create a new document upload widget instance"""
    return DocumentUploadWidget()


def create_chat_stats() -> ChatStats:
    """Create a new chat stats instance"""
    return ChatStats()


def create_processing_status() -> ProcessingStatus:
    """Create a new processing status instance"""
    return ProcessingStatus()


def create_message_formatter() -> MessageFormatter:
    """Create a new message formatter instance"""
    return MessageFormatter()