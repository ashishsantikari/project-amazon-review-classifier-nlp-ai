import json
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Credits", page_icon="🙏", layout="centered")
st.title("Credits")
st.write("This page is fully controlled by JSON.")

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
