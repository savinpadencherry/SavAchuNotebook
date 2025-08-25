import streamlit as st

# Simple demo to show the enhanced UI styles
st.set_page_config(page_title="SAVIN AI - Enhanced UI Demo", page_icon="🌟")

# Add the enhanced CSS styles
enhanced_css = """
<style>
/* Import modern font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Base styling */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
}

/* Hide Streamlit elements */
#MainMenu {visibility: hidden;}
.stDeployButton {display:none;}
footer {visibility: hidden;}
.stAppHeader {display: none;}

/* Premium floating navbar container */
.bottom-navbar-container {
    position: fixed !important;
    bottom: 24px !important;
    left: 24px !important;
    right: 24px !important;
    z-index: 9999 !important;
    
    background: linear-gradient(135deg, 
        rgba(15, 15, 35, 0.92) 0%, 
        rgba(25, 25, 45, 0.88) 50%,
        rgba(15, 15, 35, 0.92) 100%) !important;
    backdrop-filter: blur(32px) saturate(200%) contrast(120%) !important;
    border: 2px solid transparent !important;
    border-radius: 28px !important;
    padding: 1.5rem !important;
}

/* Enhanced input container */
.input-row-container {
    display: flex !important;
    align-items: center !important;
    gap: 0.75rem !important;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%) !important;
    border: 2px solid transparent !important;
    border-radius: 24px !important;
    padding: 0.5rem !important;
    backdrop-filter: blur(20px) !important;
}

/* Premium text input */
.stTextInput input {
    background: transparent !important;
    border: none !important;
    color: rgba(255, 255, 255, 0.95) !important;
    padding: 1rem 1.25rem !important;
    font-size: 1.1rem !important;
    border-radius: 20px !important;
}

.stTextInput input::placeholder {
    color: rgba(255, 255, 255, 0.6) !important;
}

/* Premium buttons */
.stButton > button {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.08) 100%) !important;
    border: 1.5px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 16px !important;
    color: rgba(255, 255, 255, 0.95) !important;
    height: 48px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    transform: translateY(-2px) scale(1.05) !important;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.18) 0%, rgba(255, 255, 255, 0.12) 100%) !important;
}

/* Primary button */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%) !important;
    border: 2px solid rgba(102, 126, 234, 0.4) !important;
    font-weight: 700 !important;
}
</style>
"""

st.markdown(enhanced_css, unsafe_allow_html=True)

# Main content
st.markdown("""
<div style="text-align: center; padding: 2rem; color: white;">
    <h1 style="font-size: 3rem; margin-bottom: 1rem; background: linear-gradient(135deg, #667eea, #f093fb); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        🌟 SAVIN AI Enhanced
    </h1>
    <p style="font-size: 1.2rem; opacity: 0.8; margin-bottom: 2rem;">
        Modern Chatbot Interface with Advanced RAG Capabilities
    </p>
</div>
""", unsafe_allow_html=True)

# Simulate the enhanced navbar
st.markdown('<div class="bottom-navbar-container">', unsafe_allow_html=True)

st.markdown("**💡 Enhanced Features Demo**")

col1, col2, col3, col4 = st.columns([6, 1, 1, 1.2])

with col1:
    st.text_input(
        "demo_input",
        placeholder="Ask me anything - I'll search Wikipedia & Web to give you comprehensive answers...",
        label_visibility="collapsed",
        key="demo_input"
    )

with col2:
    st.button("🔍 Wiki", key="demo_wiki", help="Search Wikipedia for additional context")

with col3:
    st.button("🌐 Web", key="demo_web", help="Search the web with DuckDuckGo")

with col4:
    st.button("Send ✨", key="demo_send", type="primary", help="Send Message")

st.markdown('</div>', unsafe_allow_html=True)

# Feature highlights
st.markdown("""
### ✨ Enhanced Features

#### 🎨 Premium UI Design
- **Glassmorphism Effects**: Modern floating interface with backdrop blur
- **Animated Gradients**: Beautiful color transitions and hover effects  
- **Premium Typography**: Inter font family for professional appearance
- **Responsive Design**: Works perfectly on all screen sizes

#### 🤖 Advanced RAG with LangChain
- **Multi-Source Intelligence**: Combines document, Wikipedia, and web search
- **Smart Synthesis**: AI-powered analysis and response generation
- **Context Awareness**: Understands relationships between information sources
- **Source Attribution**: Clear citations and transparency

#### 🔍 Intelligent Search
- **Enhanced Wikipedia**: AI synthesis of factual information
- **Smart Web Search**: DuckDuckGo integration with content analysis
- **Document Analysis**: PDF processing with external context enrichment
- **Error Resilience**: Graceful fallbacks and user-friendly messages

**Ready to revolutionize your AI chat experience!** 🚀
""")