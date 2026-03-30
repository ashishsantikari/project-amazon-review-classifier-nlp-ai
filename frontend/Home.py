import streamlit as st
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

st.set_page_config(page_title="Intelligence | AI Review", page_icon="🚀", layout="centered", initial_sidebar_state="expanded")

# Vibrant Glossy Design System
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;600;800&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        font-family: 'Outfit', sans-serif;
    }
    .block-container {
        max-width: 800px !important;
        padding-top: 5rem !important;
    }
    h1, h2, h3 {
        background: linear-gradient(to right, #60a5fa, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    .stButton>button {
        background: linear-gradient(to right, #3b82f6, #8b5cf6);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        transition: 0.3s;
    }
    .stButton>button:hover {
        opacity: 0.9;
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.title("🚀 Next-Gen Review Intelligence")
st.markdown("<h3 style='text-align: center; -webkit-text-fill-color: #cbd5e1; font-weight:400;'>Harness transformer-powered insights to turn raw feedback into strategy.</h3>", unsafe_allow_html=True)

st.markdown("---")

# KPI Cards using native Streamlit layout
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.info("⚡ **180ms Latency**", icon="⚡")
        st.caption("Average prediction latency with warm model cache. Fast and reliable feedback processing.")

with col2:
    with st.container(border=True):
        st.success("🧠 **Transformer Native**", icon="🧠")
        st.caption("PyTorch sequence classification pipelines seamlessly integrated via Docker volumes.")

with col3:
    with st.container(border=True):
        st.warning("📈 **Decision Ready**", icon="📈")
        st.caption("Sentiment insights, rapid categorization, and context-aware blog generation all in one flow.")

st.markdown("<br>", unsafe_allow_html=True)

# Main action links
st.markdown("### 🛠️ Select Intelligence Protocol")
c1, c2, c3 = st.columns(3)
with c1:
    st.page_link("pages/1_Sentiment_Classifier.py", label="🎭 SENTIMENT", icon="✨")
    st.caption("Multi-model emotional intelligence extraction.")
with c2:
    st.page_link("pages/2_Category_Classifier.py", label="🎲 CATEGORY", icon="✨")
    st.caption("Automated market niche classification.")
with c3:
    st.page_link("pages/3_Research_Post.py", label="📝 RESEARCH", icon="✨")
    st.caption("Live market search & blog synthesis.")

st.markdown("---")
f1, f2 = st.columns([1, 1])
with f2: st.page_link("pages/4_Credits.py", label="🛡️ View Credits", icon="🙏")
with f1: st.caption("Intelligence Orchestrated with Streamlit | PyTorch | LangChain")
