import sys
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Research Post", page_icon="📝", layout="centered", initial_sidebar_state="expanded")

# Logic Imports
sys.path.append(str(Path(__file__).resolve().parent.parent))
from logic.openai_client import BlogGenerator
from logic.research import ResearchGenerator
from logic.styles import apply_shared_styles, navigation_footer, apply_aura_animation, apply_synthesis_animation

# --- CONFIG & INITIALIZATION ---
def get_blog_generator_v2():
    return BlogGenerator()

def get_research_generator():
    return ResearchGenerator()

blog_generator = get_blog_generator_v2()
research_generator = get_research_generator()

apply_shared_styles()

st.title("📝 Research Post")
st.write("Synthesize market intelligence into professional strategic reports.")

# --- STATE GUARD & AUTOMATION ---
if "research_params" not in st.session_state:
    st.warning("### ⚠️ Protocol Deviation Detected")
    st.info("Strategic intelligence synthesis requires a **Market Niche Classification** baseline. Please initiate the protocol from the Category Classifier.")
    st.page_link("pages/2_Category_Classifier.py", label="RE-INITIATE CLASSIFICATION", icon="🎲", use_container_width=True)
    st.stop()

params = st.session_state["research_params"]

# --- DYNAMIC INTELLIGENCE FEED ---
if "research_post_results" not in st.session_state:
    apply_synthesis_animation()
    display_name = params['product_name'] or params['category_name']
    
    try:
        # 1. Market Research Stream
        st.markdown(f"## 🔎 Market Discovery: `{display_name}`")
        with st.spinner("Initializing Deep Scan..."):
            research_stream = research_generator.generate(
                product=params['product_name'], 
                category=params['category_name']
            )
            research_text = st.write_stream(research_stream)
        
        st.divider()
        
        # 2. Strategic Narrative Stream
        st.markdown("## 📝 Strategic Mega-Report")
        with st.spinner("Synthesizing Narrative..."):
            blog_stream = blog_generator.generate(
                category=params['category_name'], 
                product=params['product_name'], 
                review=params['review_context'],
                blog_length=params['blog_length'],
                include_emojis=params['include_emojis'],
                include_citations=params['include_citations'],
                target_audience=params['target_audience'],
                tone=params['tone'],
                include_checklist=params['include_checklist'],
                include_comparison=params.get('include_comparison', False),
                include_images=params.get('include_images', True)
            )
            blog_text = st.write_stream(blog_stream)
        
        st.session_state["research_post_results"] = {
            "research": research_text,
            "blog": blog_text
        }
        st.rerun() # Refresh to solidify the document
        
    except Exception as e:
        st.error(f"**Strategic Error**: {e}")
        st.stop()

# --- PERSISTED RESULTS ---
else:
    res = st.session_state["research_post_results"]
    st.markdown(res["research"])
    st.divider()
    st.markdown('<div class="blog-container">', unsafe_allow_html=True)
    st.markdown(res["blog"], unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

navigation_footer()
