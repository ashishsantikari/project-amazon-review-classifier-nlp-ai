import streamlit as st

st.set_page_config(page_title="AI Review Intelligence", page_icon="🚀", layout="wide")

# Hero Section
st.title("🚀 Next-Gen Review Intelligence")
st.subheader(
    "Harness transformer-powered sentiment and category intelligence to turn "
    "raw feedback into actionable product strategy."
)

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

# Main action button
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    if st.button("Get Started — Try the Sentiment Classifier", type="primary", use_container_width=True):
        st.switch_page("pages/1_Sentiment_Classifier.py")

st.markdown("---")
st.caption("Built with Streamlit, FastAPI, and Transformers for robust AI orchestration.")
