"""
Custom exceptions for SAVIN AI application.
Provides structured error handling with specific exception types.
"""


class SAVINAIException(Exception):
    """Base exception for SAVIN AI application"""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
        super().__init__(message)
    
    def to_dict(self) -> dict:
        """Convert exception to dictionary"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class DocumentProcessingError(SAVINAIException):
    """Exception raised for document processing errors"""
    pass


class VectorStoreError(SAVINAIException):
    """Exception raised for vector store operations"""
    pass


class AIProcessingError(SAVINAIException):
    """Exception raised for AI/LLM processing errors"""
    pass


class DatabaseError(SAVINAIException):
    """Exception raised for database operations"""
    pass


class SearchError(SAVINAIException):
    """Exception raised for web search operations"""
    pass


class ConfigurationError(SAVINAIException):
    """Exception raised for configuration-related errors"""
    pass


class ValidationError(SAVINAIException):
    """Exception raised for data validation errors"""
    pass


class CacheError(SAVINAIException):
    """Exception raised for caching operations"""
    pass