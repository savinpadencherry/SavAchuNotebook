#!/usr/bin/env python3
"""
Demo script to showcase the improved UI
"""

import streamlit as st
import time

st.set_page_config(
    page_title="SAVIN AI - UI Demo",
    page_icon="🧠",
    layout="wide"
)

# Add our custom CSS
st.markdown("""
<style>
@keyframes aurora {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes brain-pulse {
    0%, 100% { 
        transform: scale(1) rotate(0deg);
        opacity: 0.8;
    }
    25% { 
        transform: scale(1.05) rotate(1deg);
        opacity: 1;
    }
    50% { 
        transform: scale(1.1) rotate(0deg);
        opacity: 0.9;
    }
    75% { 
        transform: scale(1.05) rotate(-1deg);
        opacity: 1;
    }
}

.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 30%, #16213e 60%, #0f3460 100%);
    background-size: 400% 400%;
    animation: aurora 15s ease infinite;
}

.thinking-container {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
    border: 1px solid rgba(102, 126, 234, 0.2);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
}

.thinking-icon {
    display: inline-block;
    font-size: 1.5rem;
    animation: brain-pulse 2.5s ease-in-out infinite;
    margin-right: 0.75rem;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 SAVIN AI - UI Improvements Demo")

st.markdown("## ✨ Enhanced Thinking Animation")

if st.button("Demo Thinking Process", type="primary"):
    with st.container():
        st.markdown("""
        <div class='thinking-container'>
            <div style='display: flex; align-items: center; justify-content: center;'>
                <span class='thinking-icon'>🧠</span>
                <span style='color: rgba(255,255,255,0.9); font-weight: 500;'>AI is processing your question...</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        progress = st.progress(0)
        status = st.empty()
        
        steps = [
            "Understanding your question",
            "Searching document content", 
            "Analyzing relevant information",
            "Synthesizing response",
            "Finalizing answer"
        ]
        
        for i, step in enumerate(steps):
            status.markdown(f"""
            <div style='text-align: center; color: rgba(255,255,255,0.8); 
                       font-size: 0.875rem; margin: 0.5rem 0; font-weight: 400;'>
                {step}...
            </div>
            """, unsafe_allow_html=True)
            progress.progress((i + 1) / len(steps))
            time.sleep(1)
        
        status.empty()
        st.success("✅ Process completed!")

st.markdown("---")
st.markdown("## 🎨 Professional Welcome Design")

st.markdown("""
<div style='
    background: rgba(255, 255, 255, 0.02);
    backdrop-filter: blur(25px) saturate(150%);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 3rem 2rem;
    text-align: center;
    margin: 2rem 0;
'>
    <div style='
        font-size: 2.5rem;
        font-weight: 300;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(102, 126, 234, 0.8) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
    '>SAVIN AI</div>
    
    <p style='color: rgba(255,255,255,0.75); font-size: 1.1rem; margin-bottom: 2.5rem; font-weight: 300;'>
        Intelligent document conversations powered by advanced AI
    </p>
    
    <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin: 2.5rem 0;'>
        <div style='
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 1.5rem 1rem;
        '>
            <div style='font-size: 2rem; margin-bottom: 0.75rem; opacity: 0.8;'>📄</div>
            <div style='font-weight: 500; color: rgba(255, 255, 255, 0.95); margin-bottom: 0.5rem;'>Document Processing</div>
            <div style='color: rgba(255, 255, 255, 0.65); font-size: 0.875rem;'>Upload and analyze documents with intelligent chunking</div>
        </div>
        
        <div style='
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 1.5rem 1rem;
        '>
            <div style='font-size: 2rem; margin-bottom: 0.75rem; opacity: 0.8;'>🧠</div>
            <div style='font-weight: 500; color: rgba(255, 255, 255, 0.95); margin-bottom: 0.5rem;'>AI Conversations</div>
            <div style='color: rgba(255, 255, 255, 0.65); font-size: 0.875rem;'>Ask questions and get contextual answers</div>
        </div>
        
        <div style='
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 1.5rem 1rem;
        '>
            <div style='font-size: 2rem; margin-bottom: 0.75rem; opacity: 0.8;'>💾</div>
            <div style='font-weight: 500; color: rgba(255, 255, 255, 0.95); margin-bottom: 0.5rem;'>Persistent Memory</div>
            <div style='color: rgba(255, 255, 255, 0.65); font-size: 0.875rem;'>Resume conversations without re-uploading</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.info("The UI has been completely revamped with professional animations, minimalist design, and elegant visual effects that avoid looking like advertisements.")
