import os
import time
import uuid
import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Blog Post", page_icon="📝", layout="centered")
st.title("Blog Post Generator")

if "client_id" not in st.session_state:
    st.session_state["client_id"] = str(uuid.uuid4())
if "csrf_token" not in st.session_state:
    st.session_state["csrf_token"] = ""
if "csrf_expire_at" not in st.session_state:
    st.session_state["csrf_expire_at"] = 0
if "blog_cooldown_until" not in st.session_state:
    st.session_state["blog_cooldown_until"] = 0


def ensure_csrf_token() -> None:
    now = time.time()
    if st.session_state["csrf_token"] and now < st.session_state["csrf_expire_at"]:
        return

    response = requests.get(f"{API_BASE_URL}/csrf-token", timeout=20)
    response.raise_for_status()
    data = response.json()
    ttl = int(data.get("expires_in_seconds", 300))
    st.session_state["csrf_token"] = data["csrf_token"]
    st.session_state["csrf_expire_at"] = now + max(ttl - 10, 30)


try:
    ensure_csrf_token()
except requests.RequestException as exc:
    st.error(f"Could not initialize secure form token: {exc}")

category_seed = st.session_state.get("last_category", "general")
review_seed = st.session_state.get("last_review_text", "")

with st.form("blog_form", clear_on_submit=False):
    category = st.text_input("Category", value=category_seed)
    product = st.text_input("Product", value="")
    review = st.text_area("Review Context", value=review_seed, height=160)
    submitted = st.form_submit_button("Generate Blog")

if submitted:
    now = time.time()
    if now < st.session_state["blog_cooldown_until"]:
        wait = int(st.session_state["blog_cooldown_until"] - now) + 1
        st.warning(f"Please wait {wait}s before another request.")
    else:
        try:
            ensure_csrf_token()
            with st.spinner("Writing your blog post..."):
                response = requests.post(
                    f"{API_BASE_URL}/generate/blog",
                    headers={
                        "x-csrf-token": st.session_state["csrf_token"],
                        "x-client-id": st.session_state["client_id"],
                    },
                    json={
                        "category": category,
                        "product": product,
                        "review": review,
                        "csrf_token": st.session_state["csrf_token"],
                    },
                    timeout=60,
                )

            if response.status_code == 429:
                st.session_state["blog_cooldown_until"] = time.time() + 60
                st.error(response.json().get("detail", "Rate limit reached."))
            else:
                response.raise_for_status()
                data = response.json()
                st.session_state["blog_cooldown_until"] = time.time() + 10
                st.success("✨ Blog post generated successfully!")
                
                st.markdown("### 📝 Your Generated Post")
                with st.container(border=True):
                    st.write(data.get("blog_post", "No output"))
                    
                st.markdown("---")
                st.caption("You can copy this text and use it for your product strategy or social media.")
        except requests.RequestException as exc:
            st.error(f"Generation failed: {exc}")
