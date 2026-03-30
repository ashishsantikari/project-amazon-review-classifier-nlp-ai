import streamlit as st

def apply_shared_styles():
    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;600;800&display=swap');
    
    .stApp {
        background: #0f172a;
        font-family: 'Outfit', sans-serif;
        color: #e2e8e9;
    }
    .block-container {
        max-width: 800px !important;
    }
    h1, h2, h3 {
        background: linear-gradient(to right, #60a5fa, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    .stButton>button {
        background: linear-gradient(to right, #3b82f6, #8b5cf6);
        color: white; border: none; border-radius: 12px; font-weight: 600; transition: 0.3s;
    }
    
    @keyframes aura {
        0% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.2); background: #0f172a; }
        50% { box-shadow: 0 0 60px rgba(139, 92, 246, 0.4); background: #1e1b4b; }
        100% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.2); background: #0f172a; }
    }
    
    @keyframes synthesis-pulse {
        0% { background: #0f172a; opacity: 1; }
        50% { background: #1e1b4b; opacity: 0.85; }
        100% { background: #0f172a; opacity: 1; }
    }
    
    .aura-active { animation: aura 2s infinite ease-in-out; }
    
    .blog-container {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        padding: 3rem;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        line-height: 1.8;
    }
</style>
""", unsafe_allow_html=True)

def apply_aura_animation():
    st.markdown("<style>.stApp { animation: aura 2s infinite ease-in-out; }</style>", unsafe_allow_html=True)

def apply_synthesis_animation():
    st.markdown("""
    <style>
        .stApp {
            animation: synthesis-pulse 1.5s infinite ease-in-out;
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        }
    </style>
    """, unsafe_allow_html=True)

def navigation_footer():
    st.divider()
    c1, c2, c3 = st.columns([1,1,1])
    with c1: st.page_link("Home.py", label="⬅️ BACK: HOME", icon="🏠")
    with c3: st.page_link("pages/4_Credits.py", label="🛡️ CREDITS", icon="🙏")
