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

# Enhanced CSS with animations for landing page
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
    
    /* Landing page animations */
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
    
    /* Integrated search icons styling */
    .search-icon-btn {
        padding: 0.5rem;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.2);
        background: rgba(255,255,255,0.1);
        color: white;
        font-size: 1.2rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .search-icon-btn:hover {
        background: rgba(255,255,255,0.2);
        transform: scale(1.05);
    }
    
    /* Chat input styling */
    .stTextInput input {
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 12px;
        color: white;
        padding: 0.75rem 1rem;
    }
    
    .stTextInput input::placeholder {
        color: rgba(255,255,255,0.6);
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
    if 'current_chat_id' not in st.session_state:
        st.session_state.current_chat_id = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'vectorstore' not in st.session_state:
        st.session_state.vectorstore = None
    if 'conversation' not in st.session_state:
        st.session_state.conversation = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'relevant_context' not in st.session_state:
        st.session_state.relevant_context = ""
    if 'show_new_chat_dialog' not in st.session_state:
        st.session_state.show_new_chat_dialog = False

init_session_state()

def load_chat_data(chat_id: str):
    """Load chat messages and vector store from database"""
    messages = db.get_chat_messages(chat_id)
    st.session_state.chat_history = [{"role": msg["role"], "content": msg["content"]} for msg in messages]
    
    # Load vector store if exists
    vector_data = db.load_vector_store(chat_id)
    if vector_data:
        st.session_state.vectorstore = vector_data['vector_store']
        st.session_state.conversation = get_conversation_chain(st.session_state.vectorstore)

def save_message_to_db(chat_id: str, role: str, content: str, context: str = None):
    """Save message to database"""
    db.add_message(chat_id, role, content, context)

# Helper functions for the new integrated interface
def process_user_message(user_input: str, has_document: bool):
    """Process user message with intelligent routing and friendly responses"""
    if not st.session_state.current_chat_id:
        return
    
    # Add user message to chat
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    save_message_to_db(st.session_state.current_chat_id, "user", user_input)
    
    if has_document and "conversation" in st.session_state and st.session_state.conversation:
        # Document-based response
        with st.spinner("🧠 Analyzing your document..."):
            try:
                response = st.session_state.conversation({"question": user_input})
                ai_response = response['answer']
                source_docs = response.get('source_documents', [])
                
                # Store relevant context for display
                if source_docs:
                    st.session_state.relevant_context = "\\n\\n".join([doc.page_content for doc in source_docs[:2]])
                
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                save_message_to_db(st.session_state.current_chat_id, "assistant", ai_response, st.session_state.relevant_context)
                
            except Exception as e:
                error_msg = f"""😅 **Oops!** I encountered a small hiccup while analyzing your document.

• **Error:** {str(e)}
• **Suggestion:** Try rephrasing your question or upload a different document 📄

I'm here to help - let's try again! 💪"""
                
                st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
                save_message_to_db(st.session_state.current_chat_id, "assistant", error_msg)
    else:
        # No document - provide helpful guidance
        guidance_msg = f"""🤗 **Hi there!** I'd love to help you with: "{user_input}"

Since you haven't uploaded a document yet, here's how I can assist:

• **📤 Upload a document** → I'll analyze it and give you detailed, context-aware answers
• **📖 Use Wikipedia search** → Click the 📖 button to search Wikipedia 
• **🌐 Use web search** → Click the 🌐 button to search the internet with DuckDuckGo

Just click one of the search buttons next to the text field and I'll help you find the information you need! 😊✨"""
        
        st.session_state.chat_history.append({"role": "assistant", "content": guidance_msg})
        save_message_to_db(st.session_state.current_chat_id, "assistant", guidance_msg)
    
    st.rerun()

def process_wikipedia_search(query: str):
    """Process Wikipedia search with context integration"""
    if not query.strip():
        return
    
    # Add user query
    st.session_state.chat_history.append({"role": "user", "content": f"🔍 Search Wikipedia: {query}"})
    save_message_to_db(st.session_state.current_chat_id, "user", f"Wikipedia search: {query}")
    
    with st.spinner("📖 Searching Wikipedia..."):
        try:
            results = web_search.search_wikipedia(query, max_results=3)
            
            if results:
                search_context = ""
                for i, result in enumerate(results, 1):
                    search_context += f"Article {i}: {result['title']}\\n{result['summary']}\\n\\n"
                
                # Enhanced response with context
                has_document = st.session_state.vectorstore is not None
                if has_document and "conversation" in st.session_state:
                    enhanced_prompt = f"""Based on both my document knowledge and this Wikipedia information, please provide a comprehensive answer about: {query}

Wikipedia Context:
{search_context}

User Question: {query}"""
                    
                    try:
                        response = st.session_state.conversation({"question": enhanced_prompt})
                        ai_response = f"""🌟 **Great question!** Here's what I found combining your document with Wikipedia:

{response['answer']}

📖 **Wikipedia Sources:**
"""
                        for result in results:
                            ai_response += f"• [{result['title']}]({result['url']}) 🔗\\n"
                        
                    except:
                        ai_response = f"""📖 **Here's what I found on Wikipedia about: {query}**

"""
                        for i, result in enumerate(results, 1):
                            ai_response += f"**{i}. {result['title']} 🌟**\\n• {result['summary']}\\n• 🔗 [Read more]({result['url']})\\n\\n"
                        
                        ai_response += "💡 **Want more detailed analysis?** Upload a document and I can combine this information with your document content! 📄✨"
                else:
                    ai_response = f"""📖 **Here's what I found on Wikipedia about: {query}**

"""
                    for i, result in enumerate(results, 1):
                        ai_response += f"**{i}. {result['title']} 🌟**\\n• {result['summary']}\\n• 🔗 [Read more]({result['url']})\\n\\n"
                    
                    ai_response += "💡 **Want deeper analysis?** Upload a document and I can combine this Wikipedia information with your document content! 📄✨"
                
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                save_message_to_db(st.session_state.current_chat_id, "assistant", ai_response, search_context)
            else:
                no_results_msg = f"""😅 **Sorry!** I couldn't find Wikipedia articles about "{query}".

• **Try different keywords** 🔄
• **Use more specific terms** 🎯  
• **Or try web search instead** 🌐

I'm here to help - let's try another search! 💪"""
                
                st.session_state.chat_history.append({"role": "assistant", "content": no_results_msg})
                save_message_to_db(st.session_state.current_chat_id, "assistant", no_results_msg)
                
        except Exception as e:
            error_msg = f"""😅 **Oops!** Wikipedia search encountered an issue.

• **Error:** {str(e)}
• **Suggestion:** Try a different search term or use web search 🌐

I'm still here to help! 😊"""
            
            st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
            save_message_to_db(st.session_state.current_chat_id, "assistant", error_msg)
    
    st.rerun()

def process_web_search(query: str):
    """Process DuckDuckGo web search with context integration"""
    if not query.strip():
        return
    
    # Add user query
    st.session_state.chat_history.append({"role": "user", "content": f"🌐 Search Web: {query}"})
    save_message_to_db(st.session_state.current_chat_id, "user", f"Web search: {query}")
    
    with st.spinner("🌐 Searching the web..."):
        try:
            results = web_search.search_duckduckgo(query, max_results=3)
            
            if results:
                search_context = ""
                for i, result in enumerate(results, 1):
                    search_context += f"Website {i}: {result['title']}\\n{result['summary']}\\n\\n"
                
                # Enhanced response with context
                has_document = st.session_state.vectorstore is not None
                if has_document and "conversation" in st.session_state:
                    enhanced_prompt = f"""Based on both my document knowledge and this web search information, please provide a comprehensive answer about: {query}

Web Search Context:
{search_context}

User Question: {query}"""
                    
                    try:
                        response = st.session_state.conversation({"question": enhanced_prompt})
                        ai_response = f"""🌟 **Excellent question!** Here's what I found combining your document with web search:

{response['answer']}

🌐 **Web Sources:**
"""
                        for result in results:
                            ai_response += f"• [{result['title']}]({result['url']}) 🔗\\n"
                        
                    except:
                        ai_response = f"""🌐 **Here's what I found on the web about: {query}**

"""
                        for i, result in enumerate(results, 1):
                            ai_response += f"**{i}. {result['title']} 🌟**\\n• {result['summary']}\\n• 🔗 [Visit website]({result['url']})\\n\\n"
                        
                        ai_response += "💡 **Want deeper analysis?** Upload a document and I can combine this web information with your document content! 📄✨"
                else:
                    ai_response = f"""🌐 **Here's what I found on the web about: {query}**

"""
                    for i, result in enumerate(results, 1):
                        ai_response += f"**{i}. {result['title']} 🌟**\\n• {result['summary']}\\n• 🔗 [Visit website]({result['url']})\\n\\n"
                    
                    ai_response += "💡 **Want deeper analysis?** Upload a document and I can combine this web information with your document content! 📄✨"
                
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                save_message_to_db(st.session_state.current_chat_id, "assistant", ai_response, search_context)
            else:
                no_results_msg = f"""😅 **Sorry!** I couldn't find web results for "{query}".

• **Try different keywords** 🔄
• **Use more specific terms** 🎯  
• **Or try Wikipedia search instead** 📖

I'm here to help - let's try another search! 💪"""
                
                st.session_state.chat_history.append({"role": "assistant", "content": no_results_msg})
                save_message_to_db(st.session_state.current_chat_id, "assistant", no_results_msg)
                
        except Exception as e:
            error_msg = f"""😅 **Oops!** Web search encountered an issue.

• **Error:** {str(e)}
• **Suggestion:** Try a different search term or use Wikipedia search 📖

I'm still here to help! 😊"""
            
            st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
            save_message_to_db(st.session_state.current_chat_id, "assistant", error_msg)
    
    st.rerun()

def process_document_upload(uploaded_file):
    """Process document upload with automatic processing"""
    if not uploaded_file or st.session_state.get('processing', False):
        return
    
    st.session_state.processing = True
    
    try:
        # Processing with friendly feedback
        with st.status("🚀 Processing your document...", expanded=True) as status:
            st.write("📖 Reading document content...")
            document_text = get_document_text(uploaded_file)
            
            st.write("✂️ Breaking into smart chunks...")
            text_chunks = get_text_chunks(document_text)
            
            st.write("🧠 Creating knowledge vectors...")
            vector_store = get_vector_store(text_chunks)
            st.session_state.vectorstore = vector_store
            st.session_state.conversation = get_conversation_chain(vector_store)
            
            st.write("💾 Saving to database...")
            db.save_document_data(st.session_state.current_chat_id, document_text, text_chunks)
            
            metadatas = []
            for i, chunk in enumerate(text_chunks):
                metadatas.append({
                    "chunk_id": i,
                    "chunk_length": len(chunk),
                    "chunk_preview": chunk[:100] + "..." if len(chunk) > 100 else chunk,
                })
            
            db.save_vector_store(st.session_state.current_chat_id, vector_store, text_chunks, metadatas)
            
            # Update chat title with document name
            doc_name = uploaded_file.name.split('.')[0]
            db.update_chat_title(st.session_state.current_chat_id, f"📄 {doc_name}")
            
            status.update(label="✅ Document processed successfully!", state="complete", expanded=False)
        
        # Add welcome message after processing
        welcome_msg = f"""🎉 **Perfect!** I've successfully processed your document: **{uploaded_file.name}**

📊 **Processing Summary:**
• **Chunks created:** {len(text_chunks)} intelligent segments
• **Document length:** {len(document_text):,} characters
• **Status:** ✅ Ready for intelligent chat!

💭 **Now you can ask me anything about your document!** Try questions like:
• "What are the key points?" 🎯
• "Summarize this document" 📝  
• "Explain the main concepts" 💡

I'm excited to help you explore your document! 😊🚀"""
        
        st.session_state.chat_history.append({"role": "assistant", "content": welcome_msg})
        save_message_to_db(st.session_state.current_chat_id, "assistant", welcome_msg)
        
        st.balloons()
        
    except Exception as e:
        error_msg = f"""😅 **Oops!** I had trouble processing your document.

• **Error:** {str(e)}
• **Suggestion:** Try a different document format (PDF, DOCX, TXT) 📄
• **File size:** Should be under 15MB 📏

Don't worry - I'm still here to help! Try uploading another document. 💪"""
        
        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
        save_message_to_db(st.session_state.current_chat_id, "assistant", error_msg)
    
    finally:
        st.session_state.processing = False
        st.rerun()

def clear_document():
    """Remove document and reset vectorstore"""
    if st.session_state.current_chat_id:
        db.remove_document(st.session_state.current_chat_id)
        
    # Clear session state
    for key in ['vectorstore', 'conversation', 'relevant_context']:
        if key in st.session_state:
            del st.session_state[key]
    
    # Add friendly removal message
    removal_msg = """📄 **Document removed!** 

• Your document has been successfully cleared 🗑️
• You can now upload a new document 📤
• Web search is still available anytime! 🌐

Ready for your next document! 😊"""
    
    st.session_state.chat_history.append({"role": "assistant", "content": removal_msg})
    save_message_to_db(st.session_state.current_chat_id, "assistant", removal_msg)
    st.rerun()

# Create Sidebar with chat management
with st.sidebar:
    # Custom sidebar header with gradient
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
    chats = db.get_all_chats()
    
    if chats:
        for chat in chats[:10]:  # Show last 10 chats
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(
                    f"📄 {chat['title'][:25]}{'...' if len(chat['title']) > 25 else ''}",
                    key=f"chat_{chat['id']}",
                    use_container_width=True
                ):
                    st.session_state.current_chat_id = chat['id']
                    load_chat_data(chat['id'])
                    st.rerun()
            
            with col2:
                if st.button("🗑️", key=f"delete_{chat['id']}", help="Delete chat"):
                    db.delete_chat(chat['id'])
                    if st.session_state.current_chat_id == chat['id']:
                        st.session_state.current_chat_id = None
                        st.session_state.chat_history = []
                    st.rerun()
    else:
        st.info("No chats yet. Create your first chat!")

# New Chat Dialog
if st.session_state.show_new_chat_dialog:
    with st.container():
        st.markdown("### Create New Chat")
        chat_title = st.text_input("Chat Title", placeholder="Enter chat title...", key="new_chat_title")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Create", type="primary", use_container_width=True):
                if chat_title.strip():
                    new_chat_id = db.create_chat(chat_title.strip())
                    st.session_state.current_chat_id = new_chat_id
                    st.session_state.chat_history = []
                    st.session_state.show_new_chat_dialog = False
                    st.rerun()
        
        with col2:
            if st.button("Cancel", use_container_width=True):
                st.session_state.show_new_chat_dialog = False
                st.rerun()

# Main Content Area - Redesigned with all requirements
if st.session_state.current_chat_id:
    # Get chat info for display
    chat_info = db.get_chat_info(st.session_state.current_chat_id)
    chat_title = chat_info.get('title', 'New Chat') if chat_info else 'New Chat'
    
    # Document status
    has_document = st.session_state.vectorstore is not None
    
    # Main layout: Chat interface with integrated upload sidebar
    col1, col2 = st.columns([3, 1], gap="large")
    
    with col1:
        # REQUIREMENT 2b: Chat title as conversation header (removed separate container)
        st.markdown(f"### 💬 {chat_title}")
        
        if has_document:
            st.success("📄 Document processed - Ready for intelligent chat!")
        else:
            st.info("📤 Upload a document below to enable AI-powered document analysis")
        
        # Chat Messages Container
        chat_container = st.container(height=450, border=True)
        with chat_container:
            if st.session_state.chat_history:
                for message in st.session_state.chat_history:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
            else:
                st.markdown("""
                <div style="text-align: center; padding: 3rem 1rem; color: rgba(255,255,255,0.6);">
                    <h3 style="margin-bottom: 1rem;">👋 Hi there!</h3>
                    <p style="margin: 0.5rem 0;">I'm your friendly AI assistant! 😊</p>
                    <p style="margin: 0;">Upload a document to start our intelligent conversation 🚀</p>
                </div>
                """, unsafe_allow_html=True)
        
        # REQUIREMENT 2d & 2e: Integrated search icons in text field (Perplexity-style)
        st.markdown("---")
        
        # Input container with integrated search icons
        input_col1, input_col2, input_col3, input_col4 = st.columns([4, 0.6, 0.6, 0.8])
        
        with input_col1:
            # Text field behavior based on document status
            if has_document:
                placeholder = "Ask about your document or search the web..."
                disabled = False
            else:
                placeholder = "Upload a document first, or use web search..."
                disabled = False  # Allow web search even without document
            
            user_input = st.text_input(
                "chat_input", 
                placeholder=placeholder,
                label_visibility="collapsed",
                key="main_chat_input",
                disabled=disabled
            )
        
        with input_col2:
            # Wikipedia search icon - integrated like Perplexity
            wiki_clicked = st.button("📖", help="Search Wikipedia", key="wiki_btn", use_container_width=True)
        
        with input_col3:
            # Web search icon - integrated like Perplexity  
            web_clicked = st.button("🌐", help="Search Web (DuckDuckGo)", key="web_btn", use_container_width=True)
        
        with input_col4:
            # Send button
            send_clicked = st.button("Send ➤", type="primary", key="send_btn", use_container_width=True)
    
    with col2:
        # REQUIREMENT 2c: Simplified single document upload with auto-processing
        st.markdown("#### 📤 Document Upload")
        
        # Show current document status
        if has_document and chat_info and chat_info.get('document_name'):
            st.success(f"✅ **{chat_info['document_name']}**")
            st.caption(f"📊 {chat_info.get('total_chunks', 0)} text chunks processed")
            
            if st.button("🗑️ Remove Document", use_container_width=True, key="remove_doc"):
                clear_document()
                st.rerun()
        else:
            # Document upload area
            uploaded_file = st.file_uploader(
                "Drop your document here",
                type=["pdf", "docx", "txt"],
                help="Supported: PDF, Word, Text files (max 15MB)",
                label_visibility="collapsed"
            )
            
            if uploaded_file is not None:
                st.success(f"📎 **{uploaded_file.name}** ready!")
                st.caption(f"Size: {uploaded_file.size:,} bytes")
                
                # Auto-process button
                if st.button("🚀 Process & Enable Chat", type="primary", use_container_width=True):
                    process_document_upload(uploaded_file)
        
        # Quick start prompts when no chat history
        if not st.session_state.chat_history and has_document:
            st.markdown("---")
            st.markdown("#### 💡 Try asking:")
            
            quick_prompts = [
                "📝 Summarize this document",
                "🔍 What are the key points?", 
                "💭 Explain the main concepts"
            ]
            
            for prompt in quick_prompts:
                if st.button(prompt, key=f"quick_{prompt[:5]}", use_container_width=True):
                    process_user_message(prompt.replace("📝 ", "").replace("🔍 ", "").replace("💭 ", ""), has_document)
        
        # Chat statistics
        if st.session_state.chat_history:
            st.markdown("---")
            st.markdown("#### 📊 Chat Stats")
            st.metric("Messages", len(st.session_state.chat_history))
            if has_document:
                st.metric("Document", "✅ Loaded")
            else:
                st.metric("Document", "❌ None")
    
    # REQUIREMENT 2d & 2e: Process integrated search and chat input
    if user_input and (send_clicked or wiki_clicked or web_clicked):
        if wiki_clicked:
            # Wikipedia search with context integration
            process_wikipedia_search(user_input)
        elif web_clicked:
            # DuckDuckGo search with context integration
            process_web_search(user_input)
        else:
            # Regular document chat or web search routing
            if has_document:
                process_user_message(user_input, True)
            else:
                # No document - guide to web search
                guidance_msg = """🤗 **Hi there!** I'd love to help you with that question!

Since you haven't uploaded a document yet, here are your options:

• **📤 Upload a document** → I'll analyze it and give you detailed, context-aware answers
• **📖 Click Wikipedia button** → I'll search Wikipedia for relevant information  
• **🌐 Click Web Search button** → I'll search the web using DuckDuckGo

Just click one of the search buttons above and I'll help you find the information you need! 😊"""
                
                st.session_state.chat_history.append({"role": "assistant", "content": guidance_msg})
                save_message_to_db(st.session_state.current_chat_id, "assistant", guidance_msg)
                st.rerun()

else:
    # REQUIREMENT 1a & 1b: Enhanced Welcome Screen with animations
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="font-size: 2.5rem; font-weight: 300; margin: 0; 
                   background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), #667eea); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   animation: slideInUp 1s ease;">
            🤖 SAVIN AI
        </h1>
        <p style="font-size: 1.1rem; color: rgba(255,255,255,0.8); margin: 0.5rem 0 1.5rem 0;
                  animation: slideInUp 1.2s ease;">
            Intelligent Document Conversations
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Animated feature overview with improved spacing and container content
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <span style="font-size: 2.5rem; margin-bottom: 1rem; display: block;">📄</span>
            <h4 style="color: rgba(255,255,255,0.9); margin: 0.5rem 0; font-size: 1.1rem; font-weight: 600;">Smart Processing</h4>
            <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin: 0; line-height: 1.4;">
                Upload & analyze documents with AI<br>Advanced text processing & vectorization
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <span style="font-size: 2.5rem; margin-bottom: 1rem; display: block;">🌐</span>
            <h4 style="color: rgba(255,255,255,0.9); margin: 0.5rem 0; font-size: 1.1rem; font-weight: 600;">Web Search</h4>
            <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin: 0; line-height: 1.4;">
                Wikipedia & web search integration<br>Real-time information retrieval
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <span style="font-size: 2.5rem; margin-bottom: 1rem; display: block;">💾</span>
            <h4 style="color: rgba(255,255,255,0.9); margin: 0.5rem 0; font-size: 1.1rem; font-weight: 600;">Chat Memory</h4>
            <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin: 0; line-height: 1.4;">
                Conversations saved automatically<br>Persistent chat history & context
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick start guide
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background: rgba(102, 126, 234, 0.1); border-radius: 15px; padding: 2rem; text-align: center;
                    animation: slideInUp 1.5s ease;">
            <h3 style="margin: 0 0 1rem 0; color: rgba(255,255,255,0.9);">🚀 Get Started</h3>
            <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0; line-height: 1.6;">
                <strong>1.</strong> Click "+ New Chat" in sidebar<br>
                <strong>2.</strong> Upload a document<br>
                <strong>3.</strong> Start asking questions!
            </p>
        </div>
        """, unsafe_allow_html=True)
