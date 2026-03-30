import json
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Credits | AI Review", page_icon="🙏", layout="centered", initial_sidebar_state="expanded")

# Rich Design System
st.markdown("""
<style>
    [data-testid="stSidebar"], [data-testid="stHeader"] { display: none !important; }
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;600;800&display=swap');
    
    .stApp {
        background: #0f172a;
        font-family: 'Outfit', sans-serif;
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
</style>
""", unsafe_allow_html=True)
st.title("🙏 Project Credits")

credits_path = Path(__file__).resolve().parents[1] / "credits.json"

try:
    payload = json.loads(credits_path.read_text(encoding="utf-8"))
except Exception as exc:
    st.error(f"Could not load credits: {exc}")
    st.stop()

project_name = payload.get("project", "AI Review Intelligence")
st.subheader(project_name)

for person in payload.get("contributors", []):
    name = person.get("name", "Unknown")
    role = person.get("role", "Contributor")
    contribution = person.get("contribution", "")
    st.markdown(f"### {name}")
    st.caption(role)
    st.write(contribution)

st.divider()
c1, c2, c3 = st.columns([1,1,1])
with c1: st.page_link("Home.py", label="⬅️ BACK: HOME", icon="🏠")
with c2: st.page_link("Home.py", label="🏠 HOME", icon="✨")
