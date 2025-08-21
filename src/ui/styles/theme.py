"""
UI styling and CSS management for SAVIN AI application.
Provides centralized styling functions and CSS generation.
"""

from ..config.settings import UIConfig


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
    """Get input and form-related CSS styles"""
    return """
    /* Bottom Navigation Bar Container */
    .bottom-navbar {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(15, 15, 35, 0.95);
        backdrop-filter: blur(30px);
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1rem 2rem 1.5rem 2rem;
        z-index: 1000;
        box-shadow: 0 -8px 40px rgba(0, 0, 0, 0.3);
    }
    
    .navbar-content {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Pre-defined prompts styling */
    .prompt-suggestions {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1rem;
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .prompt-suggestions .stButton button {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 15px !important;
        padding: 0.4rem 0.8rem !important;
        color: rgba(255, 255, 255, 0.8) !important;
        font-size: 0.8rem !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(10px) !important;
        min-width: auto !important;
        height: 35px !important;
        font-weight: 400 !important;
    }
    
    .prompt-suggestions .stButton button:hover {
        background: rgba(102, 126, 234, 0.2) !important;
        border-color: rgba(102, 126, 234, 0.4) !important;
        transform: translateY(-1px) !important;
        color: white !important;
    }
    
    /* Input row container within navbar */
    .input-row-container {
        display: flex;
        align-items: center;
        gap: 1rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 35px;
        padding: 0.75rem;
        border: 2px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    /* Beautiful integrated text input */
    .stTextInput input {
        background: transparent !important;
        border: none !important;
        border-radius: 25px !important;
        color: rgba(255, 255, 255, 0.95) !important;
        padding: 1rem 1.5rem !important;
        font-size: 1.1rem !important;
        font-weight: 400 !important;
        transition: all 0.3s ease !important;
        height: 50px !important;
        flex: 1 !important;
    }
    
    .stTextInput input:focus {
        outline: none !important;
        color: white !important;
    }
    
    .stTextInput input::placeholder {
        color: rgba(255, 255, 255, 0.6) !important;
        font-weight: 300 !important;
        font-style: italic !important;
    }
    
    /* Remove default input container styling */
    .stTextInput > div > div {
        border: none !important;
        background: none !important;
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