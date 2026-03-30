import sys
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Category Classifier", page_icon="🎲", layout="centered", initial_sidebar_state="expanded")

# Logic Imports
sys.path.append(str(Path(__file__).resolve().parent.parent))
from logic.model_manager import ModelManager
from logic.styles import apply_shared_styles, navigation_footer, apply_aura_animation

# --- CONFIG & INITIALIZATION ---
def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent

@st.cache_resource
def get_model_manager():
    root = get_project_root() / "models"
    return ModelManager(model_root=str(root))

model_manager = get_model_manager()

apply_shared_styles()

st.title("🎲 Category Classifier")
st.write("Automatically classify text into market niches using deep learning.")

# --- INPUT SECTION ---
review_text = st.text_area("Analyze Review", value=st.session_state.get("shared_review_text", ""), height=150, placeholder="Paste your product review here...")
st.session_state["shared_review_text"] = review_text

if st.button("🚀 EXECUTE CLASSIFICATION", type="primary", use_container_width=True):
    if not review_text.strip():
        st.warning("Please enter a review.")
    else:
        apply_aura_animation()
        with st.status("🌌 Classifying Market Niche...", expanded=True) as status:
            category, confidence, m_name = model_manager.category_predict(review_text)
            st.session_state["category_result"] = {"category": category, "confidence": confidence, "model": m_name}
            status.update(label="Classification Complete", state="complete")

# --- RESULTS ---
if "category_result" in st.session_state:
    c = st.session_state["category_result"]
    st.markdown(f"### Market Niche: `{c['category'].title()}`")
    st.write(f"**Confidence**: {c['confidence']:.1%}")
    st.caption(f"**Model**: {c['model']}")
    
    st.markdown("---")
    st.markdown("### 🛠️ Research Configuration")
    
    # 1. Strategy Row 1
    c1, c2 = st.columns([2, 1])
    with c1:
        blog_length = st.slider("Blog Length (words)", 300, 3000, 1000, 100)
    with c2:
        include_emojis = st.checkbox("Include Emojis", value=True)
        include_citations = st.checkbox("Include Citations", value=True)
        include_images = st.checkbox("Include Images", value=True)
        
    # 2. Audience & Tone
    a1, a2 = st.columns(2)
    with a1:
        target_audience = st.selectbox("Target Audience", ["General Public", "Business Executives", "Tech Specialists", "Investors"])
    with a2:
        tone = st.selectbox("Report Tone", ["Professional", "Casual", "Inspirational", "Provocative", "Cynical"])
        
    # 3. Section Injection
    ch1, ch2 = st.columns(2)
    with ch1:
        include_checklist = st.checkbox("Add Strategic Checklist", value=False)
    with ch2:
        include_comparison = st.checkbox("Add Industry Comparison", value=False)
        
    if st.button("🚀 Perform Deep Research", type="primary", use_container_width=True):
        st.session_state["research_params"] = {
            "product_name": None, # Omitted per user request
            "category_name": c['category'].title(),
            "blog_length": blog_length,
            "include_emojis": include_emojis,
            "include_citations": include_citations,
            "include_images": include_images,
            "target_audience": target_audience,
            "tone": tone,
            "include_checklist": include_checklist,
            "include_comparison": include_comparison,
            "review_context": st.session_state.get("shared_review_text", "")
        }
        # Clear previous results to force fresh generation
        if "research_post_results" in st.session_state:
            del st.session_state["research_post_results"]
        st.switch_page("pages/3_Research_Post.py")

navigation_footer()
