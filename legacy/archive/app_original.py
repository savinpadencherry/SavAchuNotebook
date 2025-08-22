import streamlit as st
import time
import uuid
from datetime import datetime
from utils import (get_document_text, get_text_chunks, get_vector_store, 
                  get_conversation_chain, show_thinking_process, generate_chat_title)
from database import ChatDatabase
from web_search import WebSearchManager, SUGGESTED_PROMPTS

try:
    import config
except ImportError:
    # Default config if file not found
    class config:
        APP_TITLE = "SAVIN AI"
        APP_ICON = "🧠"
        ANIMATION_SPEED = 200

# Configure page with better settings
st.set_page_config(
    page_title="SAVIN AI - Document Intelligence",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/savinpadencherry/notebook-ai',
        'Report a bug': "https://github.com/savinpadencherry/notebook-ai/issues",
        'About': "# SAVIN AI\nIntelligent Document Chat Assistant powered by Advanced AI"
    }
)

# Inject custom CSS for intuitive, modern UI
def load_css():
    st.markdown("""
    <style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Base styling */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stAppHeader {display: none;}
    
    /* Modern gradient background */
    .stApp {
        background: linear-gradient(135deg, 
            #667eea 0%, 
            #764ba2 25%, 
            #f093fb 50%, 
            #f5576c 75%, 
            #4facfe 100%
        );
        background-size: 300% 300%;
        animation: gradientShift 10s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Main content container */
    .main .block-container {
        padding: 2rem 1rem;
        max-width: 100%;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        margin: 1rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(15, 15, 35, 0.95);
        backdrop-filter: blur(25px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Custom sidebar header */
    .sidebar-header {
        text-align: center;
        padding: 2rem 1rem 1.5rem 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1.5rem;
    }
    
    .sidebar-title {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .sidebar-subtitle {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.85rem;
        margin: 0.5rem 0 0 0;
        font-weight: 400;
    }
    
    /* New Chat Button - Intuitive Plus Design */
    .new-chat-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        color: white;
        font-weight: 500;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .new-chat-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
    }
    
    .plus-icon {
        font-size: 1.2rem;
        font-weight: bold;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.2);
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* Chat list styling */
    .chat-item {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .chat-item:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(102, 126, 234, 0.3);
        transform: translateX(5px);
    }
    
    .chat-item.active {
        background: rgba(102, 126, 234, 0.2);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    .chat-title {
        color: rgba(255, 255, 255, 0.9);
        font-weight: 500;
        font-size: 0.9rem;
        margin: 0;
        line-height: 1.4;
    }
    
    .chat-meta {
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.75rem;
        margin-top: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .delete-btn {
        background: rgba(244, 67, 54, 0.2);
        border: 1px solid rgba(244, 67, 54, 0.3);
        color: rgba(244, 67, 54, 0.9);
        border-radius: 6px;
        padding: 0.25rem 0.5rem;
        font-size: 0.75rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .delete-btn:hover {
        background: rgba(244, 67, 54, 0.3);
        border-color: rgba(244, 67, 54, 0.5);
    }
    
    /* Main content styling */
    .main-content {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .welcome-screen {
        text-align: center;
        padding: 3rem 2rem;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 2rem auto;
        max-width: 800px;
    }
    
    .welcome-title {
        font-size: 3rem;
        font-weight: 300;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), #667eea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .welcome-subtitle {
        color: rgba(255, 255, 255, 0.8);
        font-size: 1.2rem;
        margin-bottom: 3rem;
        font-weight: 300;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 2rem 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .feature-card:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(102, 126, 234, 0.3);
        transform: translateY(-5px);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .feature-title {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    /* Chat container - Enhanced */
    .chat-container {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        padding: 1rem !important;
        max-height: 500px !important;
        overflow-y: auto !important;
    }
    
    /* Modern chat input styling */
    .stChatInput {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 25px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        padding: 0.75rem 1.5rem !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stChatInput input {
        background: transparent !important;
        border: none !important;
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 1rem !important;
        outline: none !important;
    }
    
    .stChatInput input::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Chat message styling */
    [data-testid="chatMessage"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 15px !important;
        margin: 0.75rem 0 !important;
        padding: 1rem 1.5rem !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    
    [data-testid="chatMessage"][data-testid*="user"] {
        background: rgba(102, 126, 234, 0.1) !important;
        border-color: rgba(102, 126, 234, 0.2) !important;
        margin-left: 20% !important;
    }
    
    [data-testid="chatMessage"][data-testid*="assistant"] {
        background: rgba(255, 255, 255, 0.03) !important;
        margin-right: 20% !important;
    }
    
    /* Enhanced expander styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
        color: rgba(255, 255, 255, 0.9) !important;
        font-weight: 500 !important;
    }
    
    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
        padding: 1rem !important;
    }
    
    /* Web search button styling */
    .web-search-btn {
        background: linear-gradient(135deg, #4285f4 0%, #34a853 25%, #fbbc05 50%, #ea4335 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        margin-left: 0.5rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 10px rgba(66, 133, 244, 0.3) !important;
    }
    
    .web-search-btn:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 15px rgba(66, 133, 244, 0.4) !important;
    }
    
    /* Prompt suggestions */
    .prompt-suggestions {
        display: flex !important;
        gap: 0.5rem !important;
        flex-wrap: wrap !important;
        margin-bottom: 1rem !important;
    }
    
    .prompt-chip {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 20px !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.85rem !important;
        color: rgba(255, 255, 255, 0.8) !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
    }
    
    .prompt-chip:hover {
        background: rgba(102, 126, 234, 0.2) !important;
        border-color: rgba(102, 126, 234, 0.4) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Form elements */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
        color: rgba(255, 255, 255, 0.9) !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* File uploader - Fixed container */
    .stFileUploader {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 2px dashed rgba(102, 126, 234, 0.4) !important;
        border-radius: 15px !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
    }
    
    .stFileUploader > div {
        padding: 1rem !important;
    }
    
    .stFileUploader label {
        color: rgba(255, 255, 255, 0.8) !important;
        font-weight: 500 !important;
    }
    
    .stFileUploader [data-testid="stFileUploaderDropzone"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border-radius: 12px !important;
        padding: 2rem 1rem !important;
        text-align: center !important;
    }
    
    .stFileUploader [data-testid="stFileUploaderDropzoneInstructions"] {
        color: rgba(255, 255, 255, 0.7) !important;
        font-size: 0.9rem !important;
    }
    
    /* Progress bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        height: 6px !important;
        border-radius: 3px !important;
    }
    
    /* Text styling */
    h1, h2, h3, h4, h5, h6 {
        color: rgba(255, 255, 255, 0.9) !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    p {
        color: rgba(255, 255, 255, 0.8) !important;
    }
    
    /* Thinking animation */
    .thinking-bubble {
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 20px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.8; }
        50% { opacity: 1; }
    }
    
    .thinking-icon {
        font-size: 1.5rem;
        animation: spin 2s linear infinite;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.5);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(102, 126, 234, 0.7);
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize the CSS
load_css()

# Initialize database, web search, and session state
@st.cache_resource
def init_database():
    return ChatDatabase()

@st.cache_resource
def init_web_search():
    return WebSearchManager()

db = init_database()
web_search = init_web_search()

# Initialize session state
def init_session_state():
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = {}
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "relevant_context" not in st.session_state:
        st.session_state.relevant_context = ""
    if "show_new_chat_dialog" not in st.session_state:
        st.session_state.show_new_chat_dialog = False
    if "processing" not in st.session_state:
        st.session_state.processing = False

init_session_state()

def load_chat_data(chat_id: str):
    """Load chat data from database"""
    messages = db.get_chat_messages(chat_id)
    st.session_state.chat_history = [
        {"role": msg["role"], "content": msg["content"]} 
        for msg in messages
    ]
    
    vector_store, chunks, metadata = db.load_vector_store(chat_id)
    if vector_store:
        st.session_state.vector_store = vector_store
        st.session_state.conversation = get_conversation_chain(vector_store)
    
    st.session_state.current_chat_id = chat_id

def create_new_chat():
    """Create a new chat"""
    st.session_state.show_new_chat_dialog = True

def save_message_to_db(chat_id: str, role: str, content: str, context: str = None):
    """Save message to database"""
    if chat_id:
        db.add_message(chat_id, role, content, context)

# Create Sidebar with intuitive design
with st.sidebar:
    # Custom sidebar header
    st.markdown("""
    <div class="sidebar-header">
        <div class="sidebar-title">🤖 SAVIN AI</div>
        <div class="sidebar-subtitle">Document Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Intuitive New Chat Button
    if st.button("+ New Chat", key="new_chat_btn", type="primary", use_container_width=True):
        create_new_chat()
    
    # Chat List Section
    st.markdown("### 💬 Recent Chats")
    
    chats = db.get_all_chats()
    
    if chats:
        for chat in chats:
            is_active = chat['id'] == st.session_state.current_chat_id
            
            # Create chat item
            chat_class = "chat-item active" if is_active else "chat-item"
            
            col1, col2 = st.columns([4, 1])
            
            with col1:
                if st.button(
                    f"📄 {chat['title'][:30]}..." if len(chat['title']) > 30 else f"📄 {chat['title']}",
                    key=f"chat_{chat['id']}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary"
                ):
                    load_chat_data(chat['id'])
                    st.rerun()
            
            with col2:
                if st.button("🗑️", key=f"delete_{chat['id']}", help="Delete chat"):
                    db.delete_chat(chat['id'])
                    if st.session_state.current_chat_id == chat['id']:
                        st.session_state.current_chat_id = None
                        st.session_state.chat_history = []
                        st.session_state.relevant_context = ""
                    st.rerun()
            
            # Show document info
            if chat['document_name']:
                st.caption(f"📎 {chat['document_name']}")
            if chat['is_processed']:
                st.caption(f"✅ {chat['total_chunks']} chunks processed")
                
            st.markdown("---")
    else:
        st.info("No chats yet. Click '+ New Chat' to get started!")

# New Chat Dialog with better UX
if st.session_state.show_new_chat_dialog:
    st.markdown("---")
    with st.form("new_chat_form", clear_on_submit=True):
        st.subheader("📝 Create New Chat")
        chat_title = st.text_input(
            "Chat Title", 
            placeholder="Enter a descriptive title for your new chat...",
            help="Give your chat a meaningful name to easily find it later"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("✨ Create Chat", type="primary", use_container_width=True):
                if chat_title.strip():
                    new_chat_id = db.create_chat(chat_title.strip())
                    st.session_state.current_chat_id = new_chat_id
                    st.session_state.chat_history = []
                    st.session_state.relevant_context = ""
                    st.session_state.show_new_chat_dialog = False
                    st.success(f"✅ Created new chat: {chat_title}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Please enter a chat title")
        
        with col2:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                st.session_state.show_new_chat_dialog = False
                st.rerun()

def create_new_chat():
    """Create a new chat and set it as current"""
    new_chat_id = str(uuid.uuid4())
    chat_title = f"New Chat {datetime.now().strftime('%H:%M')}"
    
    # Create in database
    db.create_chat(chat_title)
    
    # Set as current chat
    st.session_state.current_chat_id = new_chat_id
    st.session_state.chat_messages[new_chat_id] = []
    
    return new_chat_id

def save_message_to_db(chat_id: str, role: str, content: str, context: str = None):
    """Save a message to the database"""
    try:
        db.add_message(chat_id, role, content, context)
    except Exception as e:
        print(f"Error saving message to DB: {e}")

# Helper functions for web search integration
def process_user_message(user_input: str, has_document: bool):
    """Process user message with intelligent routing"""
    if not st.session_state.current_chat_id:
        return
    
    # Add user message to chat
    if st.session_state.current_chat_id not in st.session_state.chat_messages:
        st.session_state.chat_messages[st.session_state.current_chat_id] = []
    
    st.session_state.chat_messages[st.session_state.current_chat_id].append({
        "role": "user", 
        "content": user_input
    })
    save_message_to_db(st.session_state.current_chat_id, "user", user_input)
    
    # Generate response
    try:
        with st.spinner("🤔 Analyzing..."):
            if has_document and st.session_state.conversation:
                # Document-based response
                response = st.session_state.conversation({"question": user_input})
                ai_response = response['answer']
            else:
                # Web-enhanced response
                search_results = web_search.combined_search(user_input, include_wikipedia=True, include_web=True)
                if search_results:
                    context = web_search.create_search_context(search_results)
                    ai_response = f"🌐 **Web Search Results:**\n\n{web_search.format_search_results(search_results)}"
                else:
                    ai_response = "I couldn't find relevant information. Please try rephrasing your question or upload a document."
        
        # Add AI response
        st.session_state.chat_messages[st.session_state.current_chat_id].append({
            "role": "assistant", 
            "content": ai_response
        })
        save_message_to_db(st.session_state.current_chat_id, "assistant", ai_response)
        st.rerun()
        
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")

def process_wikipedia_search(query: str):
    """Process Wikipedia search and add to chat"""
    if not st.session_state.current_chat_id:
        return
    
    with st.spinner("📖 Searching Wikipedia..."):
        results = web_search.search_wikipedia(query, max_results=3)
        if results:
            formatted_results = web_search.format_search_results(results)
            
            if st.session_state.current_chat_id not in st.session_state.chat_messages:
                st.session_state.chat_messages[st.session_state.current_chat_id] = []
            
            st.session_state.chat_messages[st.session_state.current_chat_id].append({
                "role": "user", 
                "content": f"📖 Search Wikipedia: {query}"
            })
            st.session_state.chat_messages[st.session_state.current_chat_id].append({
                "role": "assistant", 
                "content": formatted_results
            })
            
            save_message_to_db(st.session_state.current_chat_id, "user", f"Wikipedia: {query}")
            save_message_to_db(st.session_state.current_chat_id, "assistant", formatted_results)
            st.rerun()

def process_web_search(query: str):
    """Process web search and add to chat"""
    if not st.session_state.current_chat_id:
        return
    
    with st.spinner("🌐 Searching web..."):
        results = web_search.search_duckduckgo(query, max_results=5)
        if results:
            formatted_results = web_search.format_search_results(results)
            
            if st.session_state.current_chat_id not in st.session_state.chat_messages:
                st.session_state.chat_messages[st.session_state.current_chat_id] = []
            
            st.session_state.chat_messages[st.session_state.current_chat_id].append({
                "role": "user", 
                "content": f"🌐 Search web: {query}"
            })
            st.session_state.chat_messages[st.session_state.current_chat_id].append({
                "role": "assistant", 
                "content": formatted_results
            })
            
            save_message_to_db(st.session_state.current_chat_id, "user", f"Web: {query}")
            save_message_to_db(st.session_state.current_chat_id, "assistant", formatted_results)
            st.rerun()

def process_web_search_query(prompt: str):
    """Process quick start prompts with web search"""
    if not st.session_state.current_chat_id:
        return
    
    with st.spinner("🔍 Getting information..."):
        results = web_search.combined_search(prompt, include_wikipedia=True, include_web=True)
        if results:
            formatted_results = web_search.format_search_results(results)
            
            if st.session_state.current_chat_id not in st.session_state.chat_messages:
                st.session_state.chat_messages[st.session_state.current_chat_id] = []
            
            st.session_state.chat_messages[st.session_state.current_chat_id].append({
                "role": "user", 
                "content": prompt
            })
            st.session_state.chat_messages[st.session_state.current_chat_id].append({
                "role": "assistant", 
                "content": formatted_results
            })
            
            save_message_to_db(st.session_state.current_chat_id, "user", prompt)
            save_message_to_db(st.session_state.current_chat_id, "assistant", formatted_results)
            st.rerun()

def process_document_upload(uploaded_file):
    """Process document upload and enable chat"""
    if not st.session_state.current_chat_id:
        return
    
    if uploaded_file.size <= config.MAX_FILE_SIZE * 1024 * 1024:
        with st.spinner("🔄 Processing document..."):
            try:
                # Extract and process document
                raw_text = get_document_text(uploaded_file)
                if raw_text:
                    text_chunks = get_text_chunks(raw_text)
                    vectorstore = get_vector_store(text_chunks)
                    
                    # Store in session and database
                    st.session_state.vectorstore = vectorstore
                    st.session_state.conversation = get_conversation_chain(vectorstore)
                    
                    # Save to database
                    db.save_document_data(st.session_state.current_chat_id, raw_text, text_chunks)
                    
                    # Update chat title with document name
                    doc_name = uploaded_file.name.split('.')[0]
                    db.update_chat_title(st.session_state.current_chat_id, f"{doc_name} Chat")
                    
                    st.success("✅ Document processed! Chat enabled.")
                    st.rerun()
                else:
                    st.error("❌ Could not extract text from document")
            except Exception as e:
                st.error(f"❌ Error processing document: {str(e)}")
    else:
        st.error(f"❌ File too large. Maximum size: {config.MAX_FILE_SIZE}MB")

def clear_document():
    """Clear current document and vectors"""
    if st.session_state.current_chat_id:
        st.session_state.vectorstore = None
        st.session_state.conversation = None
        db.remove_document(st.session_state.current_chat_id)
        st.success("🗑️ Document cleared")
        st.rerun()

# Enhanced helper functions for web search integration
def process_user_message(user_input: str, has_document: bool):
    """Process user message with intelligent routing"""
    if not st.session_state.current_chat_id:
        return
    
    # Add user message to chat
    if st.session_state.current_chat_id not in st.session_state.chat_messages:
        st.session_state.chat_messages[st.session_state.current_chat_id] = []
    
    st.session_state.chat_messages[st.session_state.current_chat_id].append({
        "role": "user", 
        "content": user_input
    })
    save_message_to_db(st.session_state.current_chat_id, "user", user_input)
    
    # Generate response with web enhancement
    try:
        with st.spinner("🤔 Analyzing..."):
            if has_document and st.session_state.conversation:
                # Document-based response
                response = st.session_state.conversation.invoke({"query": user_input})
                ai_response = response['result']
            else:
                # Web-enhanced response
                search_results = web_search.combined_search(user_input, include_wikipedia=True, include_web=True)
                if search_results:
                    context = web_search.create_search_context(search_results)
                    # Use AI to generate response with web context
                    from langchain_community.llms import Ollama
                    llm = Ollama(model=config.AI_MODEL, temperature=0.3)
                    enhanced_prompt = f"""Based on this web search information, provide a comprehensive answer to: {user_input}

Web Search Context:
{context}

Please provide a well-structured, informative response with emojis and clear formatting."""
                    
                    ai_response = llm.invoke(enhanced_prompt)
                else:
                    ai_response = "I couldn't find relevant information. Please try rephrasing your question or upload a document."
        
        # Add AI response
        st.session_state.chat_messages[st.session_state.current_chat_id].append({
            "role": "assistant", 
            "content": ai_response
        })
        save_message_to_db(st.session_state.current_chat_id, "assistant", ai_response)
        st.rerun()
        
    except Exception as e:
        st.error(f"⚠️ Error processing message: {str(e)}")

def process_wikipedia_search(query: str):
    """Process Wikipedia search and add to chat"""
    if not st.session_state.current_chat_id:
        return
    
    with st.spinner("🔍 Searching Wikipedia..."):
        results = web_search.search_wikipedia(query, max_results=3)
        if results:
            # Use AI to synthesize Wikipedia results
            context = web_search.create_search_context(results)
            from langchain_community.llms import Ollama
            llm = Ollama(model=config.AI_MODEL, temperature=0.2)
            
            synthesis_prompt = f"""Based on these Wikipedia search results, provide a comprehensive answer to: {query}

Wikipedia Context:
{context}

Please provide a well-structured response with:
🎯 **Key Answer**
📋 **Detailed Explanation** 
💡 **Key Insights**
🔗 **Sources**: List the Wikipedia articles used"""
            
            ai_response = llm.invoke(synthesis_prompt)
            
            if st.session_state.current_chat_id not in st.session_state.chat_messages:
                st.session_state.chat_messages[st.session_state.current_chat_id] = []
            
            st.session_state.chat_messages[st.session_state.current_chat_id].append({
                "role": "user", 
                "content": f"📖 Search Wikipedia: {query}"
            })
            st.session_state.chat_messages[st.session_state.current_chat_id].append({
                "role": "assistant", 
                "content": ai_response
            })
            
            save_message_to_db(st.session_state.current_chat_id, "user", f"Wikipedia: {query}")
            save_message_to_db(st.session_state.current_chat_id, "assistant", ai_response)
            st.rerun()

def process_web_search(query: str):
    """Process web search and add to chat"""
    if not st.session_state.current_chat_id:
        return
    
    with st.spinner("🌐 Searching web..."):
        results = web_search.search_duckduckgo(query, max_results=5)
        if results:
            context = web_search.create_search_context(results)
            from langchain_community.llms import Ollama
            llm = Ollama(model=config.AI_MODEL, temperature=0.2)
            
            synthesis_prompt = f"""Based on these web search results, provide a comprehensive answer to: {query}

Web Search Context:
{context}

Please provide a well-structured response with:
🎯 **Key Answer**
📋 **Detailed Analysis** 
💡 **Key Insights**
🔗 **Sources**: List the key websites referenced"""
            
            ai_response = llm.invoke(synthesis_prompt)
            
            if st.session_state.current_chat_id not in st.session_state.chat_messages:
                st.session_state.chat_messages[st.session_state.current_chat_id] = []
            
            st.session_state.chat_messages[st.session_state.current_chat_id].append({
                "role": "user", 
                "content": f"🌐 Search web: {query}"
            })
            st.session_state.chat_messages[st.session_state.current_chat_id].append({
                "role": "assistant", 
                "content": ai_response
            })
            
            save_message_to_db(st.session_state.current_chat_id, "user", f"Web: {query}")
            save_message_to_db(st.session_state.current_chat_id, "assistant", ai_response)
            st.rerun()

def process_web_search_query(prompt: str):
    """Process quick start prompts with web search"""
    if not st.session_state.current_chat_id:
        return
    
    # Use combined search for quick prompts
    with st.spinner("🔍 Getting information..."):
        results = web_search.combined_search(prompt, include_wikipedia=True, include_web=True)
        if results:
            context = web_search.create_search_context(results)
            from langchain_community.llms import Ollama
            llm = Ollama(model=config.AI_MODEL, temperature=0.2)
            
            ai_response = f"""🌐 **Web Search Results for: {prompt}**

{web_search.format_search_results(results)}"""
            
            if st.session_state.current_chat_id not in st.session_state.chat_messages:
                st.session_state.chat_messages[st.session_state.current_chat_id] = []
            
            st.session_state.chat_messages[st.session_state.current_chat_id].append({
                "role": "user", 
                "content": prompt
            })
            st.session_state.chat_messages[st.session_state.current_chat_id].append({
                "role": "assistant", 
                "content": ai_response
            })
            
            save_message_to_db(st.session_state.current_chat_id, "user", prompt)
            save_message_to_db(st.session_state.current_chat_id, "assistant", ai_response)
            st.rerun()

def process_document_upload(uploaded_file):
    """Process document upload and enable chat"""
    if not st.session_state.current_chat_id:
        return
    
    if uploaded_file.size <= config.MAX_FILE_SIZE * 1024 * 1024:
        with st.spinner("🔄 Processing document..."):
            try:
                # Extract and process document
                raw_text = get_document_text(uploaded_file)
                if raw_text:
                    text_chunks = get_text_chunks(raw_text)
                    vectorstore = get_vector_store(text_chunks)
                    
                    # Store in session and database
                    st.session_state.vectorstore = vectorstore
                    st.session_state.conversation = get_conversation_chain(vectorstore)
                    
                    # Save to database (vectors only, not PDF to save space)
                    db.save_document_data(st.session_state.current_chat_id, raw_text, text_chunks)
                    
                    # Update chat title with document name
                    doc_name = uploaded_file.name.split('.')[0]
                    db.update_chat_title(st.session_state.current_chat_id, f"{doc_name} Chat")
                    
                    st.success("✅ Document processed! Chat enabled.")
                    st.rerun()
                else:
                    st.error("❌ Could not extract text from document")
            except Exception as e:
                st.error(f"❌ Error processing document: {str(e)}")
    else:
        st.error(f"❌ File too large. Maximum size: {config.MAX_FILE_SIZE}MB")

def clear_document():
    """Clear current document and vectors"""
    if st.session_state.current_chat_id:
        st.session_state.vectorstore = None
        st.session_state.conversation = None
        db.remove_document(st.session_state.current_chat_id)
        st.success("🗑️ Document cleared")
        st.rerun()

# Main Content Area - COMPLETELY RESTRUCTURED per user requirements
if st.session_state.current_chat_id:
    # Load chat data if not already loaded
    if st.session_state.current_chat_id not in st.session_state.get('loaded_chats', set()):
        load_chat_data(st.session_state.current_chat_id)
        if 'loaded_chats' not in st.session_state:
            st.session_state.loaded_chats = set()
        st.session_state.loaded_chats.add(st.session_state.current_chat_id)
    
    # Get chat info for display
    chat_info = db.get_chat_info(st.session_state.current_chat_id)
    chat_title = chat_info.get('title', 'New Chat') if chat_info else 'New Chat'
    
    # REQUIREMENT 3: Use chat title instead of "Conversation" - NO MORE FIR CONTAINER!
    st.markdown(f"### 💬 {chat_title}")
    
    # Document status - compact display
    has_document = st.session_state.vectorstore is not None
    if has_document:
        st.success("📄 Document loaded - Chat enabled!")
    else:
        st.info("📤 Upload a document to enable document chat (web search always available)")
    
    # REQUIREMENT 1: Remove FIR container, fix layout for single view
    col1, col2 = st.columns([2, 1], gap="medium")
    
    with col1:
        # Chat interface - Main focus area
        st.markdown("### 💬 Conversation")
        
        # Compact chat container - optimized height
        chat_container = st.container(height=500, border=True)
        with chat_container:
            if st.session_state.chat_history:
                for message in st.session_state.chat_history:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
            else:
                st.markdown("""
                <div style="text-align: center; padding: 2rem 1rem; color: rgba(255,255,255,0.6);">
                    <h3 style="margin-bottom: 0.75rem;">👋 Welcome!</h3>
                    <p style="margin: 0;">Upload a document or use web search to get started</p>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        # Compact sidebar with all controls
        
        # 1. Quick Prompt Suggestions (3 clean prompts)
        if not st.session_state.chat_history:
            st.markdown("**💡 Quick Start**")
            clean_prompts = [
                "📝 Summarize this document", 
                "🔍 Explain key concepts",
                "💡 Answer my questions"
            ]
            
            for i, prompt in enumerate(clean_prompts):
                if st.button(prompt, key=f"clean_prompt_{i}", use_container_width=True):
                    st.session_state.selected_prompt = prompt.replace("� ", "").replace("� ", "").replace("💡 ", "")
        
        # 2. Document Management
        with st.expander("📄 Document Library", expanded=True):
            # Show existing documents
            chat_documents = db.get_chat_documents(st.session_state.current_chat_id) if st.session_state.current_chat_id else []
            
            if chat_documents:
                st.markdown("**📚 Stored Documents:**")
                for doc in chat_documents:
                    col_doc, col_del = st.columns([4, 1])
                    with col_doc:
                        st.caption(f"📎 {doc['name']} ({doc['chunks']} chunks)")
                    with col_del:
                        if st.button("🗑️", key=f"del_doc_{doc['id']}", help="Remove document"):
                            # Remove document logic here
                            pass
            
            # Upload new document
            uploaded_file = st.file_uploader(
                "Add Document", 
                type=["pdf", "docx", "txt"],
                help="PDF, Word, or Text files"
            )
            
            if uploaded_file is not None:
                st.success(f"📎 {uploaded_file.name}")
                if st.button("� Process", type="primary", use_container_width=True):
                    if not st.session_state.processing:
                        st.session_state.processing = True
                        
                        with st.status("Processing...", expanded=False) as status:
                            # Processing logic
                            document_text = get_document_text(uploaded_file)
                            text_chunks = get_text_chunks(document_text)
                            vector_store = get_vector_store(text_chunks)
                            st.session_state.vector_store = vector_store
                            st.session_state.conversation = get_conversation_chain(vector_store)
                            
                            # Save to database
                            db.save_document_data(st.session_state.current_chat_id, document_text, text_chunks)
                            
                            metadatas = []
                            for i, chunk in enumerate(text_chunks):
                                metadatas.append({
                                    "chunk_id": i,
                                    "chunk_length": len(chunk),
                                    "chunk_preview": chunk[:100],
                                })
                            
                            db.save_vector_store(st.session_state.current_chat_id, vector_store, text_chunks, metadatas)
                            db.update_chat_title(st.session_state.current_chat_id, f"{uploaded_file.name.split('.')[0]}")
                            
                            status.update(label="✅ Ready!", state="complete")
                        
                        st.session_state.processing = False
                        st.balloons()
                        st.rerun()
        
        # 3. Separate Web Search Buttons
        st.markdown("**🌐 Web Search**")
        
        search_query = st.text_input(
            "Search query", 
            placeholder="Enter search terms...",
            key="compact_search_input"
        )
        
        col_wiki, col_duck = st.columns(2)
        with col_wiki:
            if st.button("📚 Wikipedia", use_container_width=True, help="Search Wikipedia"):
                if search_query.strip():
                    with st.spinner("Searching Wikipedia..."):
                        results = web_search.search_wikipedia(search_query, max_results=2)
                        if results:
                            search_context = web_search.format_search_results(results)
                            if st.session_state.current_chat_id:
                                st.session_state.chat_history.append({
                                    "role": "assistant", 
                                    "content": f"� **Wikipedia Results:**\n\n{search_context}"
                                })
                                save_message_to_db(st.session_state.current_chat_id, "assistant", f"Wikipedia: {search_query}", search_context)
                                st.rerun()
        
        with col_duck:
            if st.button("🦆 DuckDuckGo", use_container_width=True, help="Search Web"):
                if search_query.strip():
                    with st.spinner("Searching Web..."):
                        results = web_search.search_duckduckgo(search_query, max_results=3)
                        if results:
                            search_context = web_search.format_search_results(results)
                            if st.session_state.current_chat_id:
                                st.session_state.chat_history.append({
                                    "role": "assistant", 
                                    "content": f"🦆 **Web Results:**\n\n{search_context}"
                                })
                                save_message_to_db(st.session_state.current_chat_id, "assistant", f"Web: {search_query}", search_context)
                                st.rerun()
        
        # 4. Context Preview
        if st.session_state.relevant_context:
            with st.expander("🔍 Context", expanded=False):
                st.text_area("", value=st.session_state.relevant_context[:200] + "...", height=100, disabled=True)
        # Document upload section
        with st.expander("📄 Document Upload", expanded=True):
            uploaded_file = st.file_uploader(
                "Upload Document", 
                type=["pdf", "docx", "txt"],
                help="Supported formats: PDF, Word documents, and text files"
            )
            
            if uploaded_file is not None:
                st.success(f"📎 **{uploaded_file.name}** ready for processing")
                st.info(f"File size: {uploaded_file.size:,} bytes")
                
                if st.button("🚀 Process Document", type="primary", use_container_width=True):
                    if not st.session_state.processing:
                        st.session_state.processing = True
                        
                        # Processing with intuitive feedback
                        with st.status("Processing document...", expanded=True) as status:
                            st.write("📖 Extracting text content...")
                            document_text = get_document_text(uploaded_file)
                            
                            st.write("✂️ Creating intelligent chunks...")
                            text_chunks = get_text_chunks(document_text)
                            
                            st.write("🧠 Building knowledge vectors...")
                            vector_store = get_vector_store(text_chunks)
                            st.session_state.vector_store = vector_store
                            st.session_state.conversation = get_conversation_chain(vector_store)
                            
                            st.write("💾 Saving to database...")
                            db.save_document_data(st.session_state.current_chat_id, document_text, text_chunks)
                            
                            metadatas = []
                            for i, chunk in enumerate(text_chunks):
                                metadatas.append({
                                    "chunk_id": i,
                                    "chunk_length": len(chunk),
                                    "chunk_preview": chunk[:100],
                                })
                            
                            db.save_vector_store(st.session_state.current_chat_id, vector_store, text_chunks, metadatas)
                            db.update_chat_title(st.session_state.current_chat_id, f"{uploaded_file.name.split('.')[0]} Chat")
                            
                            status.update(label="✅ Document processed successfully!", state="complete", expanded=False)
                        
                        st.session_state.processing = False
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
        
        # Context display
        with st.expander("🔍 Relevant Context", expanded=False):
            if st.session_state.relevant_context:
                st.markdown("**Retrieved from document:**")
                st.text_area("Context", value=st.session_state.relevant_context, height=150, disabled=True)
            else:
                st.info("Context will appear here when you ask questions about your document.")

    # Compact Chat Input - Fixed at bottom
    user_input = st.chat_input(
        "💬 Ask about your document or search the web...",
        key="main_chat_input"
    )
    
    # Handle chat input
    if user_input:
        # Check if a prompt was selected
        if "selected_prompt" in st.session_state:
            user_input = st.session_state.selected_prompt
            del st.session_state.selected_prompt
        
        # Handle document chat
        if "conversation" in st.session_state and st.session_state.conversation:
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            save_message_to_db(st.session_state.current_chat_id, "user", user_input)
            
            # Lightning-fast AI response with structured output
            with st.spinner("🧠 Analyzing..."):
                try:
                    # Get AI response with enhanced context
                    retriever = st.session_state.vector_store.as_retriever(
                        search_type="mmr",
                        search_kwargs={"k": 4, "fetch_k": 12, "lambda_mult": 0.5}
                    )
                    relevant_docs = retriever.invoke(user_input)
                    
                    # Format context for enhanced responses
                    context_text = ""
                    for i, doc in enumerate(relevant_docs):
                        context_text += f"**Document Section {i+1}:**\n{doc.page_content}\n\n"
                    st.session_state.relevant_context = context_text
                    
                    # Get structured AI response
                    response_dict = st.session_state.conversation.invoke({"query": user_input})
                    answer = response_dict['result']
                    
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    save_message_to_db(st.session_state.current_chat_id, "assistant", answer, context_text)
                    
                except Exception as e:
                    error_msg = f"⚠️ **Analysis Error**\n\nI encountered an issue while processing your question: {str(e)}\n\n💡 **Suggestions:**\n• Try rephrasing your question\n• Upload a document first\n• Check if the document was processed correctly"
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
                    save_message_to_db(st.session_state.current_chat_id, "assistant", error_msg)
            
            st.rerun()
        else:
            # Helpful guidance when no document is loaded
            guidance_msg = f"""🤖 **Hi there!** 

I'd love to help answer: *"{user_input}"*

📋 **To get started:**
• Upload a document using the sidebar
• Process it to enable AI analysis  
• Then I can provide detailed, structured answers!

🌐 **Alternative:** Use the Wikipedia or DuckDuckGo buttons above to search for information about your topic."""

            st.session_state.chat_history.append({"role": "assistant", "content": guidance_msg})
            if st.session_state.current_chat_id:
                save_message_to_db(st.session_state.current_chat_id, "assistant", guidance_msg)
            st.rerun()

else:
    # COMPACT Welcome Screen for single-view experience
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="font-size: 2.5rem; font-weight: 300; margin: 0; 
                   background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), #667eea); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🤖 SAVIN AI
        </h1>
        <p style="font-size: 1.1rem; color: rgba(255,255,255,0.8); margin: 0.5rem 0 1.5rem 0;">
            Intelligent Document Conversations
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Animated feature overview with improved spacing
    st.markdown("""
    <style>
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .feature-card {
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 2rem 1rem;
        text-align: center;
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.3s ease;
        animation: slideInUp 0.8s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        background: rgba(255,255,255,0.08);
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .feature-card:nth-child(1) { animation-delay: 0.1s; }
    .feature-card:nth-child(2) { animation-delay: 0.2s; }
    .feature-card:nth-child(3) { animation-delay: 0.3s; }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .feature-title {
        color: rgba(255,255,255,0.9);
        margin: 0.5rem 0;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .feature-description {
        color: rgba(255,255,255,0.7);
        font-size: 0.9rem;
        margin: 0;
        line-height: 1.4;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📄</span>
            <h4 class="feature-title">Smart Processing</h4>
            <p class="feature-description">Upload & analyze documents with AI<br>Advanced text processing & vectorization</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🌐</span>
            <h4 class="feature-title">Web Search</h4>
            <p class="feature-description">Wikipedia & web search integration<br>Real-time information retrieval</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">💾</span>
            <h4 class="feature-title">Chat Memory</h4>
            <p class="feature-description">Conversations saved automatically<br>Persistent chat history & context</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick start guide
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background: rgba(102, 126, 234, 0.1); border-radius: 10px; padding: 1.5rem; text-align: center;">
            <h3 style="margin: 0 0 1rem 0; color: rgba(255,255,255,0.9);">🚀 Get Started</h3>
            <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0;">
                <strong>1.</strong> Click "+ New Chat" in sidebar<br>
                <strong>2.</strong> Upload a document<br>
                <strong>3.</strong> Start asking questions!
            </p>
        </div>
        """, unsafe_allow_html=True)
