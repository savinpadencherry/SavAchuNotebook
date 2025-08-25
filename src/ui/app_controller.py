"""
Main application controller for SAVIN AI.
Handles application lifecycle and coordinates all components.
"""

import streamlit as st
import logging
from typing import Dict, Any, Optional

from src.config.settings import AppConfig, UIConfig
from ..ui.components.welcome import create_welcome_screen
from ..ui.components.factories import (
    create_chat_interface, create_quick_prompts,
    create_document_upload_widget, create_chat_stats, create_message_formatter
)
from ..ui.styles.theme import get_input_styles
from ..data.database import (
    create_database, create_chat_repository, create_message_repository,
    create_document_repository, create_vector_store_repository
)
from ..core.document_processor import create_document_processor
from ..core.ai_handler import create_ai_handler
from ..core.vector_store import create_vector_store_manager
from ..utils.web_search import create_web_search_manager
from ..core.exceptions import SAVINAIException
from ..ui.message_handlers import create_message_handlers


# Configure logging
logger = logging.getLogger(__name__)


class ApplicationController:
    """
    Main application controller that coordinates all components.
    Manages the application lifecycle and state.
    """
    
    def __init__(self):
        """Initialize the application with all required components"""
        self.app_config = AppConfig()
        self.ui_config = UIConfig()
        
        # Initialize components
        self._initialize_components()
        self._initialize_session_state()
    
    def _initialize_components(self):
        """Initialize core components (lazy load others)"""
        try:
            # Data layer - initialize immediately
            self.database = create_database()
            self.chat_repo = create_chat_repository(self.database)
            self.message_repo = create_message_repository(self.database)
            self.document_repo = create_document_repository(self.database)
            self.vector_repo = create_vector_store_repository(self.database)
            
            # Lazy initialization flags
            self._components_loaded = {
                'document_processor': False,
                'ai_handler': False,
                'vector_manager': False,
                'web_search': False
            }
            
            # UI components - initialize immediately (lightweight)
            self.welcome_screen = create_welcome_screen()
            self.chat_interface = create_chat_interface()
            self.quick_prompts = create_quick_prompts()
            self.document_widget = create_document_upload_widget()
            self.chat_stats = create_chat_stats()
            self.message_formatter = create_message_formatter()
            
            # Message handlers for processing actions
            self.message_handlers = create_message_handlers(self)
            
            logger.info("Core components initialized successfully")
            
        except Exception as e:
            logger.error(f"Component initialization failed: {e}")
            st.error(f"Application initialization failed: {e}")
            st.stop()
    
    def _get_document_processor(self):
        """Lazy load document processor"""
        if not self._components_loaded['document_processor']:
            self.document_processor = create_document_processor()
            self._components_loaded['document_processor'] = True
        return self.document_processor
    
    def _get_ai_handler(self):
        """Lazy load AI handler"""
        if not self._components_loaded['ai_handler']:
            self.ai_handler = create_ai_handler()
            self._components_loaded['ai_handler'] = True
        return self.ai_handler
    
    def _get_vector_manager(self):
        """Lazy load vector manager"""
        if not self._components_loaded['vector_manager']:
            self.vector_manager = create_vector_store_manager()
            self._components_loaded['vector_manager'] = True
        return self.vector_manager
    
    def _get_web_search(self):
        """Lazy load web search"""
        if not self._components_loaded['web_search']:
            self.web_search = create_web_search_manager()
            self._components_loaded['web_search'] = True
        return self.web_search
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state variables"""
        defaults = {
            'current_chat_id': None,
            'chat_history': [],
            'vectorstore': None,
            'conversation': None,
            'processing': False,
            'relevant_context': "",
            'show_new_chat_dialog': False
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def run(self):
        """Main application run method"""
        try:
            # Render sidebar
            self._render_sidebar()
            
            # Render main content based on current state
            if st.session_state.current_chat_id:
                self._render_chat_interface()
            else:
                self._render_welcome_screen()
            
            # Always render bottom input bar (fixed at bottom)
            if st.session_state.current_chat_id:
                has_document = bool(st.session_state.get('vectorstore'))
                self._render_bottom_input_bar(has_document)
                
        except Exception as e:
            logger.error(f"Application error: {e}")
            st.error(f"An error occurred: {e}")
    
    def _render_sidebar(self):
        """Render the application sidebar with chat management"""
        with st.sidebar:
            # Sidebar header
            st.markdown("""
            <div class="sidebar-header">
                <h1 class="sidebar-title">🤖 SAVIN AI</h1>
                <p class="sidebar-subtitle">Document Intelligence Platform</p>
            </div>
            """, unsafe_allow_html=True)
            
            # New Chat Button
            if st.button("+ New Chat", key="new_chat_btn", use_container_width=True, type="primary"):
                st.session_state.show_new_chat_dialog = True
            
            # Chat List
            st.markdown("### 💬 Recent Chats")
            self._render_chat_list()
            
            # New Chat Dialog
            if st.session_state.show_new_chat_dialog:
                self._render_new_chat_dialog()
    
    def _render_chat_list(self):
        """Render the list of existing chats"""
        try:
            chats = self.chat_repo.get_all_chats()
            
            if chats:
                for chat in chats[:10]:  # Show last 10 chats
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        chat_title = chat['title'][:25] + ('...' if len(chat['title']) > 25 else '')
                        
                        if st.button(
                            f"📄 {chat_title}",
                            key=f"chat_{chat['id']}",
                            use_container_width=True
                        ):
                            self._load_chat(chat['id'])
                    
                    with col2:
                        if st.button("🗑️", key=f"delete_{chat['id']}", help="Delete chat"):
                            self._delete_chat(chat['id'])
            else:
                st.info("No chats yet. Create your first chat!")
                
        except Exception as e:
            logger.error(f"Error rendering chat list: {e}")
            st.error("Error loading chats")
    
    def _render_new_chat_dialog(self):
        """Render dialog for creating new chat"""
        with st.container():
            st.markdown("### Create New Chat")
            chat_title = st.text_input(
                "Chat Title", 
                placeholder="Enter chat title...", 
                key="new_chat_title"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Create", type="primary", use_container_width=True):
                    if chat_title.strip():
                        self._create_new_chat(chat_title.strip())
            
            with col2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.show_new_chat_dialog = False
                    st.rerun()
    
    def _render_welcome_screen(self):
        """Render the welcome screen when no chat is selected"""
        self.welcome_screen.render()

    def _render_chat_interface(self):
        """Render the main chat interface"""
        try:
            # Get chat info
            chat_info = self.chat_repo.get_chat_info(st.session_state.current_chat_id)
            chat_title = chat_info.get('title', 'New Chat') if chat_info else 'New Chat'
            
            # Check if document is loaded
            has_document = st.session_state.vectorstore is not None
            
            # Main layout
            col1, col2 = st.columns([3, 1], gap="large")
            
            with col1:
                # Chat title
                st.markdown(f"### 💬 {chat_title}")
                
                # Status indicator
                if has_document:
                    st.success("📄 Document processed - Ready for intelligent chat!")
                else:
                    st.info("📤 Upload a document below to enable AI-powered document analysis")
                
                # Chat messages
                messages = self.message_repo.get_chat_messages(st.session_state.current_chat_id)
                self.chat_interface.render_chat_container(messages)
            
            with col2:
                # Document upload widget
                self.document_widget.render(
                    has_document=has_document,
                    document_info=chat_info,
                    on_upload=self._process_document_upload,
                    on_remove=self._clear_document
                )
                
                # Quick prompts (if document loaded and no messages)
                if has_document and not messages:
                    st.markdown("---")
                    st.markdown("#### 💡 Try asking:")
                    
                    selected_prompt = self.quick_prompts.render(
                        prompts=["📝 Summarize this document", "🔍 What are the key points?", "💭 Explain the main concepts"],
                        key_prefix="sidebar_quick"
                    )
                    
                    if selected_prompt:
                        clean_prompt = selected_prompt.replace("📝 ", "").replace("🔍 ", "").replace("💭 ", "")
                        self._process_user_message(clean_prompt, has_document)
                
                # Chat statistics
                self.chat_stats.render(
                    message_count=len(messages),
                    has_document=has_document,
                    document_info=chat_info
                )
            
            # Bottom input bar
            self._render_bottom_input_bar(has_document)
            
        except Exception as e:
            logger.error(f"Error rendering chat interface: {e}")
            st.error("Error loading chat interface")
    
    def _render_bottom_input_bar(self, has_document: bool):
        """
        Render the unified floating navigation bar with integrated text field and buttons
        """
        # Apply the CSS styles for the floating navbar
        css = get_input_styles()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        
        # Create the main floating navbar container
        st.markdown("""
        <div class="bottom-navbar-container">
            <div class="navbar-content-wrapper">
        """, unsafe_allow_html=True)
        
        # Quick prompts section (integrated within the navbar)
        if has_document:
            st.markdown("**💡 Quick Actions**")
            prompt_cols = st.columns(4, gap="small")
            prompts = ["📝 Summarize", "🔍 Key Points", "💡 Concepts", "❓ Questions"]
            
            for i, prompt in enumerate(prompts):
                with prompt_cols[i]:
                    if st.button(prompt, key=f"quick_prompt_{i}", use_container_width=True, type="secondary"):
                        prompt_text = {
                            "📝 Summarize": "Please provide a comprehensive summary of this document",
                            "🔍 Key Points": "What are the main key points and takeaways?",
                            "💡 Concepts": "Explain the main concepts and ideas presented",
                            "❓ Questions": "Generate 5 thoughtful questions based on this content"
                        }
                        self.message_handlers.process_user_message(prompt_text[prompt], has_document)
                        st.rerun()
        
        # Main unified input container
        st.markdown('<div class="input-row-container">', unsafe_allow_html=True)
        
        # Create columns for the integrated layout - text field takes most space
        input_cols = st.columns([6, 1, 1, 1.2], gap="small")
        
        # Text input field (main component) with enhanced placeholder
        with input_cols[0]:
            placeholder_text = (
                "Ask me anything about your document, or search Wikipedia & Web for insights..." 
                if has_document 
                else "Ask me anything - I'll search Wikipedia & Web to give you comprehensive answers..."
            )
            user_input = st.text_input(
                "message_input",
                placeholder=placeholder_text,
                label_visibility="collapsed",
                key="unified_message_input"
            )
        
        # Wikipedia search button with modern design
        with input_cols[1]:
            wiki_btn = st.button("🔍 Wiki", key="unified_wiki", help="Search Wikipedia for additional context", use_container_width=True)
        
        # DuckDuckGo search button with modern design
        with input_cols[2]:
            web_btn = st.button("🌐 Web", key="unified_web", help="Search the web with DuckDuckGo", use_container_width=True)
        
        # Send button (primary action) with enhanced styling
        with input_cols[3]:
            send_btn = st.button("Send ✨", key="unified_send", help="Send Message", use_container_width=True, type="primary")
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close input-row-container
        st.markdown("""
            </div>
        </div>
        """, unsafe_allow_html=True)  # Close navbar containers
        
        # Process user input based on which action was triggered
        if user_input and (send_btn or wiki_btn or web_btn):
            try:
                if wiki_btn:
                    self.message_handlers.process_wikipedia_search(user_input)
                elif web_btn:
                    self.message_handlers.process_web_search(user_input)
                else:
                    self.message_handlers.process_user_message(user_input, has_document)
                
                # Clear input field after processing
                st.session_state.unified_message_input = ""
                st.rerun()
            except Exception as e:
                logger.error(f"Error processing user input: {e}")
                st.error(f"Error processing your request: {str(e)}")

    
    def _load_chat(self, chat_id: str):
        """Load a specific chat"""
        try:
            st.session_state.current_chat_id = chat_id
            
            # Load vector store if available
            vector_data = self.vector_repo.load_vector_store(chat_id)
            if vector_data:
                st.session_state.vectorstore = vector_data[0]  # Vector store object
                st.session_state.conversation = self._get_ai_handler().create_conversation_chain(st.session_state.vectorstore)
            else:
                st.session_state.vectorstore = None
                st.session_state.conversation = None
            
            st.rerun()
            
        except Exception as e:
            logger.error(f"Error loading chat {chat_id}: {e}")
            st.error("Error loading chat")
    
    def _create_new_chat(self, title: str):
        """Create a new chat"""
        try:
            new_chat_id = self.chat_repo.create_chat(title)
            st.session_state.current_chat_id = new_chat_id
            st.session_state.chat_history = []
            st.session_state.vectorstore = None
            st.session_state.conversation = None
            st.session_state.show_new_chat_dialog = False
            st.rerun()
            
        except Exception as e:
            logger.error(f"Error creating new chat: {e}")
            st.error("Error creating chat")
    
    def _delete_chat(self, chat_id: str):
        """Delete a chat"""
        try:
            self.chat_repo.delete_chat(chat_id)
            
            if st.session_state.current_chat_id == chat_id:
                st.session_state.current_chat_id = None
                st.session_state.chat_history = []
            
            st.rerun()
            
        except Exception as e:
            logger.error(f"Error deleting chat {chat_id}: {e}")
            st.error("Error deleting chat")
    
    def _add_message(self, role: str, content: str, context: str = None):
        """Add message to current chat"""
        if st.session_state.current_chat_id:
            self.message_repo.add_message(
                st.session_state.current_chat_id,
                role,
                content,
                context
            )

    # Lightweight wrappers to delegate actions to MessageHandlers
    def _process_document_upload(self, uploaded_file):
        return self.message_handlers.process_document_upload(uploaded_file)

    def _clear_document(self):
        return self.message_handlers.clear_document()


# Factory function
def create_application_controller() -> ApplicationController:
    """Create a new application controller instance"""
    return ApplicationController()