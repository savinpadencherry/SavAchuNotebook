"""
Document processing utilities for SAVIN AI application.
Handles text extraction, chunking, and preprocessing from various document formats.
"""

import io
import logging
from typing import List, Optional, Tuple
from pypdf import PdfReader
import docx
from langchain.text_splitter import RecursiveCharacterTextSplitter

from ..config.settings import AIConfig, FileConfig
from .exceptions import DocumentProcessingError


# Configure logging
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Handles document text extraction and processing for various file formats.
    Supports PDF, DOCX, and TXT files with intelligent text chunking.
    """
    
    def __init__(self):
        self.ai_config = AIConfig()
        self.file_config = FileConfig()
        self.text_splitter = self._create_text_splitter()
    
    def _create_text_splitter(self) -> RecursiveCharacterTextSplitter:
        """Create optimized text splitter for document chunking"""
        return RecursiveCharacterTextSplitter(
            chunk_size=self.ai_config.CHUNK_SIZE,
            chunk_overlap=self.ai_config.CHUNK_OVERLAP,
            length_function=len,
            separators=[
                "\n\n\n",    # Triple newlines (major sections)
                "\n\n",      # Double newlines (paragraphs)  
                "\n",        # Single newlines (lines)
                ": ",        # Colons (important for structured docs)
                ". ",        # Sentences
                "! ",        # Exclamations
                "? ",        # Questions
                "; ",        # Semi-colons
                ", ",        # Commas
                " ",         # Spaces
                ""           # Characters
            ]
        )
    
    def extract_text(self, file) -> Tuple[str, str]:
        """
        Extract text from uploaded document file.
        
        Args:
            file: Streamlit uploaded file object
            
        Returns:
            Tuple of (extracted_text, file_type)
            
        Raises:
            DocumentProcessingError: If extraction fails
        """
        if not file:
            raise DocumentProcessingError("No file provided")
        
        file_extension = file.name.split('.')[-1].lower()
        
        if file_extension not in self.file_config.ALLOWED_TYPES:
            raise DocumentProcessingError(
                f"Unsupported file type: {file_extension}. "
                f"Supported types: {', '.join(self.file_config.ALLOWED_TYPES)}"
            )
        
        # Check file size
        if file.size > self.file_config.MAX_FILE_SIZE * 1024 * 1024:
            raise DocumentProcessingError(
                f"File size ({file.size / 1024 / 1024:.1f}MB) exceeds "
                f"maximum allowed size ({self.file_config.MAX_FILE_SIZE}MB)"
            )
        
        try:
            if file_extension == 'pdf':
                text = self._extract_from_pdf(file)
            elif file_extension == 'docx':
                text = self._extract_from_docx(file)
            elif file_extension == 'txt':
                text = self._extract_from_txt(file)
            else:
                raise DocumentProcessingError(f"Unsupported file type: {file_extension}")
            
            if not text or not text.strip():
                raise DocumentProcessingError("No text content found in document")
            
            # Check text length
            if len(text) > self.file_config.MAX_TEXT_LENGTH:
                logger.warning(f"Text length ({len(text)}) exceeds maximum, truncating")
                text = text[:self.file_config.MAX_TEXT_LENGTH]
            
            logger.info(f"Successfully extracted {len(text)} characters from {file.name}")
            return text.strip(), file_extension
            
        except Exception as e:
            logger.error(f"Text extraction failed for {file.name}: {e}")
            raise DocumentProcessingError(f"Failed to extract text from {file.name}: {str(e)}")
    
    def _extract_from_pdf(self, file) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PdfReader(io.BytesIO(file.read()))
            text = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                    continue
            
            return text
            
        except Exception as e:
            raise DocumentProcessingError(f"PDF processing failed: {str(e)}")
    
    def _extract_from_docx(self, file) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(io.BytesIO(file.read()))
            text = ""
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n"
            
            # Extract text from tables if present
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            text += cell.text + "\n"
            
            return text
            
        except Exception as e:
            raise DocumentProcessingError(f"DOCX processing failed: {str(e)}")
    
    def _extract_from_txt(self, file) -> str:
        """Extract text from TXT file"""
        try:
            # Try different encodings
            encodings = [self.file_config.ENCODING, 'utf-8', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    file.seek(0)  # Reset file pointer
                    content = file.getvalue()
                    if isinstance(content, bytes):
                        text = content.decode(encoding)
                    else:
                        text = content
                    return text
                except UnicodeDecodeError:
                    continue
            
            raise DocumentProcessingError("Could not decode text file with any supported encoding")
            
        except Exception as e:
            raise DocumentProcessingError(f"TXT processing failed: {str(e)}")
    
    def create_chunks(self, text: str) -> List[str]:
        """
        Split text into meaningful chunks preserving context and structure.
        
        Args:
            text: Input text to be chunked
            
        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []
        
        try:
            # Clean and prepare text
            cleaned_text = self._clean_text(text)
            
            # Split into chunks
            raw_chunks = self.text_splitter.split_text(cleaned_text)
            
            # Filter and enhance chunks
            meaningful_chunks = self._filter_and_enhance_chunks(raw_chunks)
            
            # Limit number of chunks if needed
            if len(meaningful_chunks) > self.ai_config.MAX_CHUNKS:
                meaningful_chunks = self._sample_chunks(meaningful_chunks, self.ai_config.MAX_CHUNKS)
            
            logger.info(f"Created {len(meaningful_chunks)} chunks from {len(text)} characters")
            return meaningful_chunks
            
        except Exception as e:
            logger.error(f"Text chunking failed: {e}")
            raise DocumentProcessingError(f"Failed to create text chunks: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text while preserving structure"""
        # Remove excessive whitespace but preserve paragraph breaks
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            cleaned_line = ' '.join(line.split())  # Remove extra spaces
            cleaned_lines.append(cleaned_line)
        
        # Rejoin lines and normalize paragraph breaks
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Replace multiple newlines with double newlines
        import re
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
        
        return cleaned_text.strip()
    
    def _filter_and_enhance_chunks(self, chunks: List[str]) -> List[str]:
        """Filter out low-quality chunks and enhance with context"""
        meaningful_chunks = []
        
        for i, chunk in enumerate(chunks):
            chunk = chunk.strip()
            
            # Skip very short or empty chunks
            if len(chunk) < 20:
                continue
            
            # Skip chunks with no alphanumeric content
            if not any(c.isalnum() for c in chunk):
                continue
            
            # Add context for short chunks to improve understanding
            if len(chunk) < 200 and i > 0:
                prev_chunk = chunks[i-1].strip()
                if prev_chunk and len(prev_chunk) > 50:
                    # Add context prefix if not already overlapping
                    context = prev_chunk[-50:]
                    if not chunk.startswith(context[-30:]):
                        chunk = f"[Context: ...{context}] {chunk}"
            
            meaningful_chunks.append(chunk)
        
        return meaningful_chunks
    
    def _sample_chunks(self, chunks: List[str], max_chunks: int) -> List[str]:
        """Sample chunks across document to maintain diversity"""
        if len(chunks) <= max_chunks:
            return chunks
        
        # Calculate step size to sample evenly across document
        step = len(chunks) / max_chunks
        sampled_chunks = []
        
        for i in range(max_chunks):
            index = int(i * step)
            if index < len(chunks):
                sampled_chunks.append(chunks[index])
        
        return sampled_chunks
    
    def get_document_stats(self, text: str, chunks: List[str]) -> dict:
        """Get statistics about processed document"""
        return {
            'original_length': len(text),
            'total_chunks': len(chunks),
            'average_chunk_size': sum(len(chunk) for chunk in chunks) // len(chunks) if chunks else 0,
            'min_chunk_size': min(len(chunk) for chunk in chunks) if chunks else 0,
            'max_chunk_size': max(len(chunk) for chunk in chunks) if chunks else 0,
            'total_processed_length': sum(len(chunk) for chunk in chunks)
        }


# Factory function
def create_document_processor() -> DocumentProcessor:
    """Create a new document processor instance"""
    return DocumentProcessor()


# Convenience functions for backward compatibility
def get_document_text(file):
    """Extract text from document file (backward compatibility)"""
    processor = create_document_processor()
    text, _ = processor.extract_text(file)
    return text


def get_text_chunks(text: str) -> List[str]:
    """Create text chunks from text (backward compatibility)"""
    processor = create_document_processor()
    return processor.create_chunks(text)