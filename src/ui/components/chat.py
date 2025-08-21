"""
Chat interface components for SAVIN AI.
Provides UI components for chat display, message formatting, and input handling.
"""

import streamlit as st
import logging
from typing import Dict, List, Any, Optional
import time

from src.config.settings import UIConfig, MessageConfig

import streamlit as st
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

from ...config.settings import UIConfig, MessageConfig


class ChatInterface:
    """
    Main chat interface component for displaying conversations.
    """
    
    def __init__(self):
        self.config = UIConfig()
        self.message_config = MessageConfig()
    
    def render_chat_container(self, messages: List[Dict[str, Any]], height: Optional[int] = None):
        """
        Render the main chat message container.
        
        Args:
            messages: List of message dictionaries
            height: Container height in pixels
        """
        container_height = height or self.config.MAX_CHAT_HEIGHT
        
        chat_container = st.container(height=container_height, border=True)
        
        with chat_container:
            if messages:
                for message in messages:
                    self._render_message(message)
            else:
                self._render_empty_chat()
    
    def _render_message(self, message: Dict[str, Any]):
        """Render a single chat message"""
        role = message.get("role", "user")
        content = message.get("content", "")
        timestamp = message.get("timestamp")
        context = message.get("relevant_context")
        
        # Choose avatar based on role
        avatar = "👤" if role == "user" else "🤖"
        
        with st.chat_message(role, avatar=avatar):
            # Render message content
            st.markdown(content)
            
            # Show timestamp if available
            if timestamp:
                st.caption(f"🕒 {self._format_timestamp(timestamp)}")
            
            # Show relevant context if available (for assistant messages)
            if role == "assistant" and context:
                with st.expander("📚 Source Context", expanded=False):
                    st.text(context[:500] + "..." if len(context) > 500 else context)
    
    def _render_empty_chat(self):
        """Render empty chat state"""
        st.markdown("""
        <div style="
            text-align: center; 
            padding: 3rem 1rem; 
            color: rgba(255,255,255,0.6);
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        ">
            <h3 style="margin-bottom: 1rem; color: rgba(255,255,255,0.8);">👋 Hi there!</h3>
            <p style="margin: 0.5rem 0;">I'm your friendly AI assistant! 😊</p>
            <p style="margin: 0;">Upload a document to start our intelligent conversation 🚀</p>
        </div>
        """, unsafe_allow_html=True)
    
    def _format_timestamp(self, timestamp) -> str:
        """Format timestamp for display"""
        try:
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                dt = timestamp
            
            return dt.strftime("%H:%M")
        except:
            return ""


class InputBar:
    """
    Chat input bar component with integrated search and send functionality.
    """
    
    def __init__(self):
        self.config = UIConfig()
    
    def render(self, placeholder: str = None, disabled: bool = False, 
               key_prefix: str = "chat") -> Dict[str, Any]:
        """
        Render the input bar with search and send buttons.
        
        Args:
            placeholder: Input placeholder text
            disabled: Whether input is disabled
            key_prefix: Unique key prefix for components
            
        Returns:
            Dictionary with user input and button states
        """
        # Default placeholder
        if placeholder is None:
            placeholder = "💭 Ask about your document or search the web..."
        
        # Create columns for integrated layout
        input_col1, input_col2, input_col3, input_col4 = st.columns([6, 0.8, 0.8, 1.2], gap="small")
        
        result = {
            "user_input": "",
            "send_clicked": False,
            "wiki_clicked": False,
            "web_clicked": False
        }
        
        with input_col1:
            result["user_input"] = st.text_input(
                "chat_input", 
                placeholder=placeholder,
                label_visibility="collapsed",
                key=f"{key_prefix}_input",
                disabled=disabled
            )
        
        with input_col2:
            result["wiki_clicked"] = st.button(
                "📖", 
                help="Search Wikipedia", 
                key=f"{key_prefix}_wiki", 
                use_container_width=True,
                type="secondary"
            )
        
        with input_col3:
            result["web_clicked"] = st.button(
                "🌐", 
                help="Search DuckDuckGo", 
                key=f"{key_prefix}_web", 
                use_container_width=True,
                type="secondary"
            )
        
        with input_col4:
            result["send_clicked"] = st.button(
                "Send ➤", 
                type="primary", 
                key=f"{key_prefix}_send", 
                use_container_width=True
            )
        
        return result


class QuickPrompts:
    """
    Component for displaying quick prompt suggestions.
    """
    
    def __init__(self):
        self.message_config = MessageConfig()
    
    def render(self, prompts: Optional[List[str]] = None, 
               on_prompt_click: Optional[Callable[[str], None]] = None,
               key_prefix: str = "quick") -> Optional[str]:
        """
        Render quick prompt buttons.
        
        Args:
            prompts: List of prompt strings (uses default if None)
            on_prompt_click: Callback for when a prompt is clicked
            key_prefix: Unique key prefix for buttons
            
        Returns:
            Selected prompt text or None
        """
        prompts = prompts or self.message_config.SUGGESTED_PROMPTS
        selected_prompt = None
        
        st.markdown('<div class="prompt-suggestions">', unsafe_allow_html=True)
        
        cols = st.columns(len(prompts))
        
        for i, (col, prompt) in enumerate(zip(cols, prompts)):
            with col:
                if st.button(
                    prompt, 
                    key=f"{key_prefix}_prompt_{i}", 
                    help=f"Ask: {prompt}",
                    type="secondary"
                ):
                    selected_prompt = prompt
                    if on_prompt_click:
                        on_prompt_click(prompt)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return selected_prompt


class DocumentUploadWidget:
    """
    Component for document upload with status display.
    """
    
    def render(self, has_document: bool = False, document_info: Optional[Dict[str, Any]] = None,
               on_upload: Optional[Callable] = None, on_remove: Optional[Callable] = None) -> Any:
        """
        Render document upload widget.
        
        Args:
            has_document: Whether a document is currently loaded
            document_info: Information about the loaded document
            on_upload: Callback for file upload
            on_remove: Callback for document removal
            
        Returns:
            Uploaded file object or None
        """
        st.markdown("#### 📤 Document Upload")
        
        if has_document and document_info:
            # Show current document status
            doc_name = document_info.get('document_name', 'Unknown Document')
            chunks = document_info.get('total_chunks', 0)
            
            st.success(f"✅ **{doc_name}**")
            st.caption(f"📊 {chunks} text chunks processed")
            
            if st.button("🗑️ Remove Document", use_container_width=True, key="remove_doc"):
                if on_remove:
                    on_remove()
                return None
        else:
            # Show upload interface
            uploaded_file = st.file_uploader(
                "Drop your document here",
                type=["pdf", "docx", "txt"],
                help="Supported: PDF, Word, Text files (max 15MB)",
                label_visibility="collapsed"
            )
            
            if uploaded_file is not None:
                st.success(f"📎 **{uploaded_file.name}** ready!")
                st.caption(f"Size: {uploaded_file.size:,} bytes")
                
                if on_upload:
                    on_upload(uploaded_file)
            
            return uploaded_file
        
        return None


class ChatStats:
    """
    Component for displaying chat statistics and information.
    """
    
    @staticmethod
    def render(message_count: int = 0, has_document: bool = False, 
               document_info: Optional[Dict[str, Any]] = None):
        """
        Render chat statistics.
        
        Args:
            message_count: Number of messages in chat
            has_document: Whether a document is loaded
            document_info: Document information
        """
        st.markdown("#### 📊 Chat Stats")
        
        # Message count
        st.metric("Messages", message_count)
        
        # Document status
        if has_document:
            st.metric("Document", "✅ Loaded")
            
            if document_info:
                chunks = document_info.get('total_chunks', 0)
                if chunks > 0:
                    st.metric("Text Chunks", chunks)
        else:
            st.metric("Document", "❌ None")


class ProcessingStatus:
    """
    Component for showing processing status and progress.
    """
    
    @staticmethod
    def show_processing(message: str = "Processing...", progress: Optional[float] = None) -> st.status:
        """
        Show processing status with optional progress.
        
        Args:
            message: Status message
            progress: Progress value (0.0 to 1.0)
            
        Returns:
            Streamlit status object
        """
        status = st.status(f"🚀 {message}", expanded=True)
        
        if progress is not None:
            status.progress(progress)
        
        return status
    
    @staticmethod
    def show_thinking_animation(steps: List[str], container=None):
        """
        Show AI thinking animation with steps.
        
        Args:
            steps: List of thinking step messages
            container: Streamlit container (uses st if None)
        """
        if container is None:
            container = st
        
        progress_bar = container.progress(0)
        status_container = container.empty()
        
        for i, step in enumerate(steps):
            status_container.markdown(
                f"""<div style='
                    text-align: center; 
                    padding: 10px; 
                    background: rgba(255,255,255,0.1); 
                    border-radius: 10px; 
                    margin: 5px 0;
                '>{step}</div>""", 
                unsafe_allow_html=True
            )
            progress_bar.progress((i + 1) / len(steps))
            
            # In a real implementation, you'd add time.sleep() here
            # but we'll leave that to the calling code
        
        return progress_bar, status_container


class MessageFormatter:
    """
    Utility class for formatting different types of messages.
    """
    
    @staticmethod
    def format_search_query(query: str, search_type: str) -> str:
        """Format search query message"""
        icons = {"wikipedia": "📖", "web": "🌐", "combined": "🔍"}
        icon = icons.get(search_type, "🔍")
        return f"{icon} Search: {query}"
    
    @staticmethod
    def format_document_processed(filename: str, chunks: int) -> str:
        """Format document processed message"""
        return f"""🎉 **Perfect!** I've successfully processed your document: **{filename}**

📊 **Processing Summary:**
• **Chunks created:** {chunks} intelligent segments
• **Status:** ✅ Ready for intelligent chat!

💭 **Now you can ask me anything about your document!** Try questions like:
• "What are the key points?" 🎯
• "Summarize this document" 📝  
• "Explain the main concepts" 💡

I'm excited to help you explore your document! 😊🚀"""
    
    @staticmethod
    def format_error_message(error_type: str, error_details: str) -> str:
        """Format error message"""
        return f"""😅 **Oops! Something went wrong**

🎯 **What happened:**
• {error_type} error occurred
• Details: {error_details}

💡 **What you can try:**
• Check your internet connection 🌐
• Try rephrasing your question 🔄
• Upload a different document if needed 📄
• Restart the application if problems persist 🔄

🤗 **Don't worry!** I'm still here to help you. Let's try again! 💪"""


# Factory functions
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