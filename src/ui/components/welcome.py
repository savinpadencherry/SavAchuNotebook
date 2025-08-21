"""
Welcome screen component for SAVIN AI application.
Displays the landing page with feature overview and getting started guide.
"""

import streamlit as st
from typing import List, Tuple

from ..styles.theme import get_glassmorphism_card, get_gradient_text


class WelcomeScreen:
    """
    Manages the welcome screen display with animated features and getting started guide.
    """
    
    def __init__(self):
        self.features = [
            {
                "icon": "📄",
                "title": "Smart Processing",
                "description": "Upload & analyze documents with AI<br>Advanced text processing & vectorization"
            },
            {
                "icon": "🌐",
                "title": "Web Search",
                "description": "Wikipedia & web search integration<br>Real-time information retrieval"
            },
            {
                "icon": "💾",
                "title": "Chat Memory",
                "description": "Conversations saved automatically<br>Persistent chat history & context"
            }
        ]
    
    def render(self):
        """Render the complete welcome screen"""
        self._render_header()
        self._render_features()
        self._render_getting_started()
    
    def _render_header(self):
        """Render the welcome screen header"""
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h1 class="welcome-title">
                🤖 SAVIN AI
            </h1>
            <p class="welcome-subtitle">
                Intelligent Document Conversations
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_features(self):
        """Render the feature overview cards"""
        col1, col2, col3 = st.columns(3, gap="large")
        
        for i, (col, feature) in enumerate(zip([col1, col2, col3], self.features)):
            with col:
                feature_card_content = f"""
                <div class="feature-card">
                    <div>
                        <span style="font-size: 2.5rem; margin-bottom: 1rem; display: block;">{feature["icon"]}</span>
                        <h4 style="color: rgba(255,255,255,0.9); margin: 0.5rem 0; font-size: 1.1rem; font-weight: 600;">{feature["title"]}</h4>
                    </div>
                    <div>
                        <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin: 0; line-height: 1.4;">
                            {feature["description"]}
                        </p>
                    </div>
                </div>
                """
                
                st.markdown(feature_card_content, unsafe_allow_html=True)
    
    def _render_getting_started(self):
        """Render the getting started guide"""
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            getting_started_content = """
            <div class="welcome-card">
                <h3 style="margin: 0 0 1rem 0; color: rgba(255,255,255,0.9);">🚀 Get Started</h3>
                <div class="welcome-steps">
                    <strong>1.</strong> Click "+ New Chat" in sidebar<br>
                    <strong>2.</strong> Upload a document<br>
                    <strong>3.</strong> Start asking questions!
                </div>
            </div>
            """
            
            st.markdown(getting_started_content, unsafe_allow_html=True)


class FeatureShowcase:
    """
    Component for showcasing specific features with detailed descriptions.
    """
    
    @staticmethod
    def render_ai_features():
        """Render AI capabilities showcase"""
        st.markdown("### 🧠 AI Capabilities")
        
        capabilities = [
            ("📊 Document Analysis", "Intelligent text processing and semantic understanding"),
            ("🔍 Smart Search", "Context-aware information retrieval"),
            ("💬 Natural Conversations", "Human-like dialogue with document context"),
            ("📝 Summarization", "Automatic key points extraction"),
            ("❓ Q&A Generation", "Smart question creation from content")
        ]
        
        for title, description in capabilities:
            capability_card = f"""
            <div style="
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 1rem;
                margin: 0.5rem 0;
                border-left: 3px solid rgba(102, 126, 234, 0.5);
            ">
                <strong style="color: rgba(255, 255, 255, 0.9);">{title}</strong><br>
                <span style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem;">{description}</span>
            </div>
            """
            st.markdown(capability_card, unsafe_allow_html=True)
    
    @staticmethod
    def render_supported_formats():
        """Render supported file formats"""
        st.markdown("### 📄 Supported Formats")
        
        formats = [
            ("PDF", "Portable Document Format", "📕"),
            ("DOCX", "Microsoft Word Documents", "📘"),
            ("TXT", "Plain Text Files", "📄")
        ]
        
        cols = st.columns(len(formats))
        
        for col, (format_name, description, icon) in zip(cols, formats):
            with col:
                format_card = f"""
                <div style="
                    text-align: center;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 12px;
                    padding: 1.5rem;
                    margin: 0.5rem 0;
                ">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                    <strong style="color: rgba(255, 255, 255, 0.9); display: block;">{format_name}</strong>
                    <small style="color: rgba(255, 255, 255, 0.6);">{description}</small>
                </div>
                """
                st.markdown(format_card, unsafe_allow_html=True)


class QuickStartGuide:
    """
    Component for displaying a detailed quick start guide.
    """
    
    def render(self):
        """Render the quick start guide"""
        st.markdown("### 🚀 Quick Start Guide")
        
        steps = [
            {
                "number": "1",
                "title": "Create New Chat",
                "description": "Click the '+ New Chat' button in the sidebar to start a new conversation",
                "icon": "💬"
            },
            {
                "number": "2", 
                "title": "Upload Document",
                "description": "Drag and drop or select a PDF, DOCX, or TXT file to analyze",
                "icon": "📤"
            },
            {
                "number": "3",
                "title": "Start Chatting",
                "description": "Ask questions about your document or use the quick prompt buttons",
                "icon": "🗣️"
            },
            {
                "number": "4",
                "title": "Explore Features",
                "description": "Use Wikipedia and web search for additional context and information",
                "icon": "🌟"
            }
        ]
        
        for step in steps:
            step_card = f"""
            <div style="
                display: flex;
                align-items: center;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 1rem;
                margin: 1rem 0;
                border-left: 4px solid rgba(102, 126, 234, 0.7);
            ">
                <div style="
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    margin-right: 1rem;
                    flex-shrink: 0;
                ">
                    {step["number"]}
                </div>
                <div style="flex-grow: 1;">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.2rem; margin-right: 0.5rem;">{step["icon"]}</span>
                        <strong style="color: rgba(255, 255, 255, 0.9);">{step["title"]}</strong>
                    </div>
                    <p style="color: rgba(255, 255, 255, 0.7); margin: 0; font-size: 0.9rem;">
                        {step["description"]}
                    </p>
                </div>
            </div>
            """
            
            st.markdown(step_card, unsafe_allow_html=True)


class TipsAndTricks:
    """
    Component for displaying helpful tips and tricks.
    """
    
    @staticmethod
    def render():
        """Render tips and tricks section"""
        st.markdown("### 💡 Tips & Tricks")
        
        tips = [
            {
                "icon": "🎯",
                "title": "Specific Questions",
                "tip": "Ask specific questions for more targeted and useful responses"
            },
            {
                "icon": "📝",
                "title": "Use Quick Prompts",
                "tip": "Try the suggested prompt buttons for common document analysis tasks"
            },
            {
                "icon": "🔍",
                "title": "Combine Sources",
                "tip": "Upload a document and use web search for comprehensive analysis"
            },
            {
                "icon": "💾",
                "title": "Chat History",
                "tip": "Your conversations are automatically saved - resume anytime!"
            },
            {
                "icon": "🔄",
                "title": "Rephrase Questions",
                "tip": "If you don't get the answer you want, try rephrasing your question"
            }
        ]
        
        for tip in tips:
            tip_card = f"""
            <div style="
                display: flex;
                align-items: flex-start;
                background: rgba(255, 255, 255, 0.03);
                border-radius: 8px;
                padding: 1rem;
                margin: 0.75rem 0;
            ">
                <span style="font-size: 1.5rem; margin-right: 1rem; flex-shrink: 0;">{tip["icon"]}</span>
                <div>
                    <strong style="color: rgba(255, 255, 255, 0.9); display: block; margin-bottom: 0.25rem;">
                        {tip["title"]}
                    </strong>
                    <span style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem;">
                        {tip["tip"]}
                    </span>
                </div>
            </div>
            """
            
            st.markdown(tip_card, unsafe_allow_html=True)


# Factory functions
def create_welcome_screen() -> WelcomeScreen:
    """Create a new welcome screen instance"""
    return WelcomeScreen()


def create_feature_showcase() -> FeatureShowcase:
    """Create a new feature showcase instance"""
    return FeatureShowcase()


def create_quick_start_guide() -> QuickStartGuide:
    """Create a new quick start guide instance"""
    return QuickStartGuide()


def create_tips_and_tricks() -> TipsAndTricks:
    """Create a new tips and tricks instance"""
    return TipsAndTricks()