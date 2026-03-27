from __future__ import annotations

import logging
import os

from openai import OpenAI

logger = logging.getLogger(__name__)


class BlogGenerator:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY", "")
        self._client = OpenAI(api_key=api_key) if api_key else None
        self._model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        logger.info("BlogGenerator initialized | openai_enabled=%s model=%s", self._client is not None, self._model)

    def generate(self, category: str, product: str | None, review: str | None) -> str:
        product_text = product or "this product"
        review_text = review or "No detailed review supplied."

        if not self._client:
            return (
                f"## Spotlight: {product_text}\n\n"
                f"This item falls under **{category}**. Based on the review, it appears to deliver solid value. "
                "Top highlights include usability, reliability, and strong feature fit for everyday users.\n\n"
                "### Why this category matters\n"
                "Products in this category often balance convenience, quality, and long-term utility.\n\n"
                f"### Review signal\n{review_text}\n\n"
                "### Final take\n"
                "If you are looking for a dependable option in this category, this is worth exploring."
            )

        completion = self._client.responses.create(
            model=self._model,
            temperature=0.7,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You write concise, engaging blog posts about products and categories. "
                        "Use markdown headings and practical, friendly tone."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Create a blog post about category: {category}. "
                        f"Product: {product_text}. "
                        f"Review context: {review_text}. "
                        "Include top features, who it is good for, and a final recommendation."
                    ),
                },
            ],
        )
        return completion.output_text
