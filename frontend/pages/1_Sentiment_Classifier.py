import os
import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Sentiment Classifier", page_icon="🧾", layout="centered")
st.title("Sentiment Classifier")
st.write("Paste a product review from Amazon, Yelp, Google, or any source.")

with st.expander("How to copy a clean review"):
    st.markdown(
        """
        1. Select only the review text, not star icons.
        2. Remove usernames or URLs if possible.
        3. Keep at least one full sentence for better predictions.
        """
    )

review_text = st.text_area("Review Text", height=180, placeholder="Paste review here...")

@st.cache_data(ttl=60)
def get_sentiment_models():
    try:
        resp = requests.get(f"{API_BASE_URL}/models", timeout=5)
        if resp.status_code == 200:
            models_config = resp.json()
            return {k: v.get("fallback_name", k) for k, v in models_config.items() if v.get("task") == "sentiment"}
    except requests.RequestException:
        pass
    return {"ashish": "facebookai/roberta-base-sentiment-ashish-lora", "roberta_reference": "roberta_reference_model"}

sentiment_models = get_sentiment_models()

model_option = st.selectbox(
    "Sentiment Model",
    options=list(sentiment_models.keys()),
    format_func=lambda x: sentiment_models[x],
    index=0,
)

if st.button("Predict Sentiment", type="primary", use_container_width=True):
    if not review_text.strip():
        st.warning("Please provide review text.")
    else:
        try:
            with st.spinner("Analyzing sentiment..."):
                response = requests.post(
                    f"{API_BASE_URL}/predict/sentiment",
                    json={"text": review_text, "sentiment_model": model_option},
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()

            st.success("✨ Prediction Complete")
            
            # Format the sentiment with an emoji
            raw_sentiment = data.get("sentiment", "unknown").lower()
            sentiment_emoji = {"positive": "😊", "neutral": "😐", "negative": "😠"}.get(raw_sentiment, "🔍")
            display_sentiment = f"{sentiment_emoji} {raw_sentiment.title()}"
            
            # Display metrics side-by-side
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Sentiment", display_sentiment)
            with col2:
                st.metric("Confidence", f"{data.get('confidence', 0):.1%}")
                
            with st.expander("Model Details", expanded=False):
                st.caption(f"**Loaded Model**: `{data.get('model', 'unknown')}`")
                st.caption(f"**Requested Option**: `{model_option}`")

            st.session_state["last_review_text"] = review_text
            st.session_state["last_sentiment"] = raw_sentiment

            st.markdown("---")
            st.write("### Ready for more insights?")
            st.write("Now that we know the sentiment, let's see what category this fits into.")
            if st.button("Go To Category Classifier"):
                st.switch_page("pages/2_Category_Classifier.py")

        except requests.RequestException as exc:
            st.error(f"API call failed: {exc}")
