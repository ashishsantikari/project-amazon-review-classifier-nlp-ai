from __future__ import annotations
# Refactored for dynamic research synthesis support

import logging
import os

from openai import OpenAI

logger = logging.getLogger(__name__)


class BlogGenerator:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY", "")
        # Ensure 'None' string from .env is treated as None
        if not api_key or api_key.lower() == "none":
            self._client = None
        else:
            self._client = OpenAI(api_key=api_key)
            
        self._model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        logger.info("BlogGenerator initialized | openai_enabled=%s model=%s", self._client is not None, self._model)

    def generate(
        self,
        category: str,
        product: str | None,
        review: str | None,
        blog_length: int = 800,
        include_emojis: bool = True,
        include_citations: bool = True,
        target_audience: str = "General Public",
        tone: str = "Professional",
        include_checklist: bool = False,
        include_comparison: bool = False,
        include_images: bool = True,
    ):
        product_text = product or "this product"
        review_text = review or "No detailed review supplied."

        if not self._client:
            yield "🛡️ **Operational Warning**: Intelligence protocol is not fully initialized. "
            yield "Please configure your OpenAI credentials in the system settings."
            return

        # Model Selection: "gpt-4o" is the premier multimodal model from OpenAI
        active_model = "gpt-4o" if include_images else "gpt-4o"
        
        # Strategy Instructions
        word_count = f"approximately {blog_length}"
        emoji_instr = "Include relevant emojis throughout the text. 🚀⚡" if include_emojis else "DO NOT use any emojis. Keep the text strictly professional."
        cit_instr = (
            "MANDATORY: Provide GROUNDED TRUTH. Every single claim, statistic, or growth trend must be followed by a "
            "verifiable, real-world source link: [Source Name](URL). "
            "Focus on high-authority sources (e.g., Bloomberg, Statista, Gartner). "
            "Include a 'Grounded Data Sources & Strategic Citations' section at the end. Failure to cite results in a rejected report."
        ) if include_citations else "Focus on original analysis only; no formal citations needed."
        
        # Section Injections
        check_instr = "MANDATORY: Include a 'Strategic Action Plan' section with a 5-item checklist for business success." if include_checklist else ""
        comp_instr = f"MANDATORY: Include an 'Industry Comparison' section comparing {category} with two adjacent market niches." if include_comparison else ""
        img_instr = (
            "MANDATORY: You are operating in MULTI-MODAL mode. Use Unsplash Markdown syntax (`![alt text](https://images.unsplash.com/photo-...)`) "
            "to embed at least 3 high-quality relevant images. Integrate them naturally into the flow."
        ) if include_images else "DO NOT include any images or image links."

        # Switch to streaming mode for real-time word-by-word synthesize
        completion = self._client.chat.completions.create(
            model=active_model,
            temperature=0.7,
            stream=True,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional content strategist and senior market analyst. "
                        f"You write detailed, high-quality blog posts ({word_count} words). "
                        f"Target Audience: {target_audience}. "
                        f"Tone of Voice: {tone}. "
                        f"{emoji_instr} {cit_instr} {check_instr} {comp_instr} {img_instr} "
                        "Always use markdown headings (H1, H2, H3). "
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Create a PROFESSIONAL, CITED blog post for category: {category}. "
                        f"Product: {product_text}. "
                        f"Review context: {review_text}. "
                        "\n\nStructure Requirements:\n"
                        "1. 🌟 Hero Introduction.\n"
                        "2. 🔍 Product Analysis.\n"
                        "3. 💵 Revenue Trends & Market Growth: Include mandatory in-text citations.\n"
                        "4. 📊 Industry Comparison: Include data comparison if requested.\n"
                        "5. 📈 Data Sources & Verified Citations: List the specific blogs, reports, and websites referenced.\n"
                        "6. ✨ Final Verdict.\n"
                    ),
                },
            ],
        )
        
        for chunk in completion:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
