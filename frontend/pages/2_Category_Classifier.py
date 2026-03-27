import os
import requests
import streamlit as st
import streamlit.components.v1 as components

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Category Classifier", page_icon="🎲", layout="centered")
st.title("Category Classifier")

seed_text = st.session_state.get("last_review_text", "")
review_text = st.text_area(
    "Review Text",
    value=seed_text,
    height=180,
    placeholder="Paste or edit review text...",
)


def show_dice_animation() -> None:
    components.html(
        """
        <div style="display:flex;justify-content:center;align-items:center;padding:8px;">
          <div class="dice">🎲</div>
        </div>
        <style>
          .dice {
            font-size: 56px;
            animation: roll 0.9s infinite linear;
            filter: drop-shadow(0 6px 8px rgba(0,0,0,0.2));
          }
          @keyframes roll {
            from { transform: rotate(0deg) scale(1); }
            50% { transform: rotate(180deg) scale(1.15); }
            to { transform: rotate(360deg) scale(1); }
          }
        </style>
        """,
        height=90,
    )


if st.button("Predict Category", type="primary", use_container_width=True):
    if not review_text.strip():
        st.warning("Please provide review text.")
    else:
        anim_slot = st.empty()
        with anim_slot:
            show_dice_animation()

        try:
            response = requests.post(
                f"{API_BASE_URL}/predict/category",
                json={"text": review_text},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            anim_slot.empty()
            st.success("✨ Categorization Complete")
            
            # Display metrics side-by-side
            col1, col2 = st.columns(2)
            raw_category = str(data.get("category", "unknown"))
            with col1:
                st.metric("Category", f"🏷️ {raw_category.title()}")
            with col2:
                st.metric("Confidence", f"{data.get('confidence', 0):.1%}")
                
            with st.expander("Model Details", expanded=False):
                st.caption(f"**Loaded Model**: `{data.get('model', 'unknown')}`")

            st.session_state["last_review_text"] = review_text
            st.session_state["last_category"] = raw_category

            st.markdown("---")
            st.write("### Leverage these insights")
            st.write("Generate a tailored blog post responding to this review and category.")
            if st.button("Generate Blog Post"):
                st.switch_page("pages/3_Blog_Post.py")

        except requests.RequestException as exc:
            anim_slot.empty()
            st.error(f"API call failed: {exc}")
