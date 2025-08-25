"""
UI styling and CSS management for SAVIN AI application.
Provides centralized styling functions and CSS generation.
"""

from src.config.settings import UIConfig


def get_base_styles() -> str:
    """Get base CSS styles for the application"""
    config = UIConfig()
    
    return f"""
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Base styling */
    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    /* Hide Streamlit elements */
    #MainMenu {{visibility: hidden;}}
    .stDeployButton {{display:none;}}
    footer {{visibility: hidden;}}
    .stAppHeader {{display: none;}}
    
    /* Modern gradient background */
    .stApp {{
        background: linear-gradient(135deg, 
            {config.PRIMARY_COLOR} 0%, 
            {config.SECONDARY_COLOR} 25%, 
            {config.ACCENT_COLOR} 50%, 
            {config.ERROR_COLOR} 75%, 
            {config.SUCCESS_COLOR} 100%
        );
        background-size: 300% 300%;
        animation: gradientShift {config.GRADIENT_ANIMATION_DURATION} ease infinite;
    }}
    
    @keyframes gradientShift {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    """


def get_animation_styles() -> str:
    """Get animation-related CSS styles"""
    config = UIConfig()
    
    return f"""
    /* Landing page animations */
    @keyframes slideInUp {{
        from {{
            opacity: 0;
            transform: translateY(30px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    @keyframes brain-pulse {{
        0%, 100% {{ transform: scale(1); }}
        50% {{ transform: scale(1.1); }}
    }}
    
    @keyframes aurora {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    
    /* Thinking animation */
    .thinking-container {{
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }}
    
    .thinking-icon {{
        display: inline-block;
        font-size: 1.5rem;
        animation: brain-pulse 2.5s ease-in-out infinite;
        margin-right: 0.75rem;
    }}
    
    /* Feature card animations */
    .feature-card {{
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 2rem 1.5rem;
        text-align: center;
        height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.3s ease;
        animation: slideInUp {config.SLIDE_ANIMATION_DURATION} ease;
        margin: 1rem 0;
    }}
    
    .feature-card:hover {{
        transform: translateY(-5px);
        background: rgba(255,255,255,0.08);
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }}
    
    .feature-card:nth-child(1) {{ animation-delay: 0.1s; }}
    .feature-card:nth-child(2) {{ animation-delay: 0.2s; }}
    .feature-card:nth-child(3) {{ animation-delay: 0.3s; }}
    """


def get_layout_styles() -> str:
    """Get layout-related CSS styles"""
    config = UIConfig()
    
    return f"""
    /* Main content container */
    .main .block-container {{
        padding: 2rem 1rem;
        max-width: {config.MAX_CONTENT_WIDTH}px;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        margin: 1rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 180px !important;
    }}
    
    /* Sidebar styling */
    .css-1d391kg {{
        background: rgba(15, 15, 35, 0.95);
        backdrop-filter: blur(25px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        width: {config.SIDEBAR_WIDTH}px;
    }}
    
    /* Sidebar header */
    .sidebar-header {{
        text-align: center;
        padding: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1rem;
    }}
    
    .sidebar-title {{
        font-size: 1.5rem;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.9);
        margin: 0;
        background: linear-gradient(135deg, {config.PRIMARY_COLOR}, {config.SECONDARY_COLOR});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    .sidebar-subtitle {{
        font-size: 0.8rem;
        color: rgba(255, 255, 255, 0.6);
        margin: 0.5rem 0 0 0;
        font-weight: 300;
    }}
    
    /* Chat container */
    .chat-container {{
        height: {config.MAX_CHAT_HEIGHT}px;
        overflow-y: auto;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    """


def get_input_styles() -> str:
    """Get input and form-related CSS styles - Enhanced unified navbar design"""
    return """
    /* Fixed Bottom Navigation Container - Premium Floating Design */
    .bottom-navbar-container {
        position: fixed !important;
        bottom: 24px !important;
        left: 24px !important;
        right: 24px !important;
        z-index: 9999 !important;
        
        /* Premium glassmorphism floating card with enhanced effects */
        background: linear-gradient(135deg, 
            rgba(15, 15, 35, 0.92) 0%, 
            rgba(25, 25, 45, 0.88) 50%,
            rgba(15, 15, 35, 0.92) 100%) !important;
        backdrop-filter: blur(32px) saturate(200%) contrast(120%) !important;
        border: 2px solid transparent !important;
        border-radius: 28px !important;
        
        /* Premium gradient border */
        background-clip: padding-box !important;
        position: relative !important;
    }
    
    /* Animated gradient border */
    .bottom-navbar-container::before {
        content: '' !important;
        position: absolute !important;
        top: -2px !important;
        left: -2px !important;
        right: -2px !important;
        bottom: -2px !important;
        border-radius: 28px !important;
        background: linear-gradient(45deg, 
            rgba(102, 126, 234, 0.3) 0%,
            rgba(118, 75, 162, 0.3) 25%,
            rgba(240, 147, 251, 0.3) 50%,
            rgba(245, 87, 108, 0.3) 75%,
            rgba(79, 172, 254, 0.3) 100%
        ) !important;
        z-index: -1 !important;
        animation: borderGlow 3s ease-in-out infinite alternate !important;
    }
    
    @keyframes borderGlow {
        0% { opacity: 0.3; }
        100% { opacity: 0.7; }
    }
        
        /* Enhanced floating shadow */
        box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        
        padding: 1.5rem !important;
        pointer-events: auto !important;
        
        /* Smooth animation for appearance */
        animation: slideUpFloat 0.6s ease-out !important;
    }

    @keyframes slideUpFloat {
        from {
            opacity: 0;
            transform: translateY(100px) scale(0.95);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    /* Content wrapper for better organization */
    .navbar-content-wrapper {
        max-width: 1000px !important;
        margin: 0 auto !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 1rem !important;
    }

    /* Quick actions styling */
    .bottom-navbar-container h3,
    .bottom-navbar-container .markdown-text-container strong {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 0.9rem !important;
        margin-bottom: 0.5rem !important;
        text-align: center !important;
    }

    /* Main input container - premium chatbot design inspired by ChatGPT/Claude */
    .input-row-container {
        display: flex !important;
        align-items: center !important;
        gap: 0.75rem !important;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%) !important;
        border: 2px solid transparent !important;
        border-radius: 24px !important;
        padding: 0.5rem !important;
        backdrop-filter: blur(20px) !important;
        position: relative !important;
        
        /* Premium gradient border effect */
        background-clip: padding-box !important;
        box-shadow: 
            inset 0 1px 0 rgba(255, 255, 255, 0.15),
            0 8px 32px rgba(102, 126, 234, 0.2),
            0 4px 16px rgba(0, 0, 0, 0.1) !important;
        
        /* Hover effect for premium feel */
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .input-row-container:hover {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.08) 100%) !important;
        box-shadow: 
            inset 0 1px 0 rgba(255, 255, 255, 0.2),
            0 12px 40px rgba(102, 126, 234, 0.3),
            0 6px 20px rgba(0, 0, 0, 0.15) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Animated gradient border effect */
    .input-row-container::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        border-radius: 24px !important;
        padding: 2px !important;
        background: linear-gradient(45deg, 
            rgba(102, 126, 234, 0.6) 0%,
            rgba(118, 75, 162, 0.6) 25%,
            rgba(240, 147, 251, 0.6) 50%,
            rgba(245, 87, 108, 0.6) 75%,
            rgba(79, 172, 254, 0.6) 100%
        ) !important;
        mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0) !important;
        mask-composite: xor !important;
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0) !important;
        -webkit-mask-composite: xor !important;
        opacity: 0 !important;
        transition: opacity 0.4s ease !important;
    }
    
    .input-row-container:focus-within::before {
        opacity: 1 !important;
    }

    /* Premium text input styling - ChatGPT inspired */
    .bottom-navbar-container .stTextInput > div > div {
        border: none !important;
        background: transparent !important;
        border-radius: 20px !important;
    }

    .bottom-navbar-container .stTextInput input {
        background: transparent !important;
        border: none !important;
        color: rgba(255, 255, 255, 0.95) !important;
        padding: 1rem 1.25rem !important;
        font-size: 1.1rem !important;
        font-weight: 400 !important;
        line-height: 1.5 !important;
        outline: none !important;
        border-radius: 20px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }

    .bottom-navbar-container .stTextInput input::placeholder {
        color: rgba(255, 255, 255, 0.6) !important;
        font-style: normal !important;
        font-weight: 400 !important;
        letter-spacing: 0.01em !important;
    }

    .bottom-navbar-container .stTextInput input:focus {
        background: rgba(255, 255, 255, 0.08) !important;
        color: rgba(255, 255, 255, 1) !important;
        transform: scale(1.01) !important;
    }

    /* Premium action buttons - Modern chatbot style */
    .bottom-navbar-container .stButton > button {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.08) 100%) !important;
        border: 1.5px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 16px !important;
        color: rgba(255, 255, 255, 0.95) !important;
        height: 48px !important;
        min-width: 48px !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        backdrop-filter: blur(15px) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    /* Hover effect for search buttons */
    .bottom-navbar-container .stButton > button:hover {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.18) 0%, rgba(255, 255, 255, 0.12) 100%) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
        transform: translateY(-2px) scale(1.05) !important;
        box-shadow: 
            0 8px 25px rgba(102, 126, 234, 0.25),
            0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Active state */
    .bottom-navbar-container .stButton > button:active {
        transform: translateY(0) scale(0.98) !important;
    }

    /* Premium primary send button - ChatGPT inspired */
    .bottom-navbar-container .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%) !important;
        border: 2px solid rgba(102, 126, 234, 0.4) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0 1.5rem !important;
        box-shadow: 
            0 8px 32px rgba(102, 126, 234, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    /* Primary button hover with premium effect */
    .bottom-navbar-container .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 50%, #e084f0 100%) !important;
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 
            0 12px 40px rgba(102, 126, 234, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
        border-color: rgba(102, 126, 234, 0.6) !important;
    }
    
    /* Shimmer effect for primary button */
    .bottom-navbar-container .stButton > button[kind="primary"]::after {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: -100% !important;
        width: 100% !important;
        height: 100% !important;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent) !important;
        transition: left 0.6s !important;
    }
    
    .bottom-navbar-container .stButton > button[kind="primary"]:hover::after {
        left: 100% !important;
    }

    /* Quick action buttons - secondary style */
    .bottom-navbar-container .stButton > button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        color: rgba(255, 255, 255, 0.8) !important;
        font-size: 0.85rem !important;
        padding: 0.4rem 0.8rem !important;
        border-radius: 8px !important;
    }

    .bottom-navbar-container .stButton > button[kind="secondary"]:hover {
        background: rgba(102, 126, 234, 0.2) !important;
        color: rgba(255, 255, 255, 0.95) !important;
    }

    /* Ensure main content doesn't hide behind the floating navbar */
    .main .block-container {
        padding-bottom: 160px !important;
    }

    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .bottom-navbar-container {
            bottom: 10px !important;
            left: 10px !important;
            right: 10px !important;
            padding: 1rem !important;
        }
        
        .input-row-container {
            gap: 0.3rem !important;
            padding: 0.2rem !important;
        }
        
        .bottom-navbar-container .stTextInput input {
            font-size: 0.9rem !important;
            padding: 0.6rem 0.8rem !important;
        }
        
        .bottom-navbar-container .stButton > button {
            height: 38px !important;
            font-size: 0.8rem !important;
        }
    }
    """


def get_button_styles() -> str:
    """Get button-related CSS styles"""
    return """
    /* Secondary buttons integrated in navbar */
    .stButton button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.12) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 18px !important;
        color: rgba(255, 255, 255, 0.9) !important;
        padding: 0.75rem !important;
        font-size: 1.3rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
        min-width: 50px !important;
        height: 50px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    .stButton button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.18) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
        transform: scale(1.05) !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Primary send button in navbar */
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 18px !important;
        color: white !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3) !important;
        min-width: 90px !important;
        height: 50px !important;
        text-transform: none !important;
    }
    
    .stButton button[kind="primary"]:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
        transform: scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5) !important;
    }
    
    /* General button hover effects */
    .stButton button {
        transition: all 0.2s ease !important;
    }
    
    .stButton button:hover {
        transform: translateY(-1px) !important;
    }
    """


def get_welcome_screen_styles() -> str:
    """Get welcome screen specific styles"""
    return """
    /* Welcome screen styling */
    .welcome-title {
        font-size: 2.5rem;
        font-weight: 300;
        margin: 0;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), #667eea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        animation: slideInUp 1s ease;
    }
    
    .welcome-subtitle {
        font-size: 1.1rem;
        color: rgba(255,255,255,0.8);
        margin: 0.5rem 0 1.5rem 0;
        animation: slideInUp 1.2s ease;
        text-align: center;
    }
    
    .welcome-card {
        background: rgba(102, 126, 234, 0.1);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        animation: slideInUp 1.5s ease;
        margin: 2rem auto;
        max-width: 600px;
    }
    
    .welcome-steps {
        color: rgba(255,255,255,0.8);
        margin: 0.5rem 0;
        line-height: 1.6;
    }
    """


def get_search_styles() -> str:
    """Get search-related CSS styles"""
    return """
    /* Search icons styling */
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
    
    /* Search results styling */
    .search-results {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .search-result-item {
        padding: 0.75rem;
        margin: 0.5rem 0;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        border-left: 3px solid rgba(102, 126, 234, 0.5);
    }
    """


def get_complete_css() -> str:
    """Get complete CSS styling for the application"""
    return f"""
    <style>
    {get_base_styles()}
    {get_animation_styles()}
    {get_layout_styles()}
    {get_input_styles()}
    {get_button_styles()}
    {get_welcome_screen_styles()}
    {get_search_styles()}
    </style>
    """


def get_glassmorphism_card(content: str, padding: str = "2rem", border_radius: str = "15px") -> str:
    """Generate a glassmorphism card with content"""
    return f"""
    <div style="
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: {border_radius};
        padding: {padding};
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    ">
        {content}
    </div>
    """


def get_gradient_text(text: str, size: str = "1.2rem") -> str:
    """Generate gradient text styling"""
    return f"""
    <span style="
        font-size: {size};
        font-weight: 600;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    ">
        {text}
    </span>
    """


def get_status_indicator(status: str, message: str) -> str:
    """Generate status indicator with appropriate styling"""
    status_colors = {
        "success": "#4facfe",
        "error": "#f5576c", 
        "warning": "#f093fb",
        "info": "#667eea",
        "processing": "#764ba2"
    }
    
    color = status_colors.get(status, "#667eea")
    
    return f"""
    <div style="
        display: flex;
        align-items: center;
        padding: 0.75rem 1rem;
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid {color};
        border-radius: 8px;
        margin: 0.5rem 0;
    ">
        <span style="color: {color}; margin-right: 0.5rem;">●</span>
        <span style="color: rgba(255, 255, 255, 0.9);">{message}</span>
    </div>
    """