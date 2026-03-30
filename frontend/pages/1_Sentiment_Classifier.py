import sys
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Sentiment Classifier", page_icon="🎭", layout="centered", initial_sidebar_state="expanded")

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

@st.cache_data(ttl=600)
def get_available_models():
    try:
        models = model_manager.models_config
        return [k for k, v in models.items() if v.get("task") == "sentiment"]
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return ["ashish", "jesus", "roberta_reference"]

available_models = get_available_models()

st.title("🎭 Sentiment Classifier")
st.write("Extract emotional intelligence from text using advanced transformer models.")

# --- INPUT SECTION ---
review_text = st.text_area("Analyze Review", value=st.session_state.get("shared_review_text", ""), height=150, placeholder="Paste your product review here...")
st.session_state["shared_review_text"] = review_text

st.markdown("### 🛠️ Configuration")
selected_models = st.multiselect(
    "Models to Compare",
    options=available_models,
    default=["ashish"]
)

if st.button("🚀 EXECUTE CLASSIFICATION", type="primary", use_container_width=True):
    if not review_text.strip():
        st.warning("Please enter a review.")
    elif not selected_models:
        st.warning("Please select at least one sentiment model.")
    else:
        apply_aura_animation()
        with st.status("🌌 Extracting Emotional Intelligence...", expanded=True) as status:
            try:
                sent_results = []
                for m in selected_models:
                    sentiment, confidence, m_name = model_manager.sentiment_predict(review_text, model_option=m)
                    sent_results.append({"sentiment": sentiment, "confidence": confidence, "model": m_name})
                
                st.session_state["sentiment_results"] = sent_results
                status.update(label="Classification Complete", state="complete")
            except RuntimeError as e:
                status.update(label="Classification Failed", state="error")
                st.error(f"**Model Error**: {e}")
            except Exception as e:
                status.update(label="Critical System Error", state="error")
                st.error(f"**Unexpected Error**: {e}")

# --- RESULTS ---
if "sentiment_results" in st.session_state:
    st.markdown("## 📊 Results")
    cols = st.columns(len(st.session_state["sentiment_results"]))
    for idx, s in enumerate(st.session_state["sentiment_results"]):
        with cols[idx]:
            st.metric(s["model"].upper(), s["sentiment"].upper(), f"{s['confidence']:.1%}")

    st.markdown("---")
    st.page_link("pages/2_Category_Classifier.py", label="Switch to Category Classifier", icon="🎲", use_container_width=True)

navigation_footer()
