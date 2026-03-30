from pydantic import BaseModel, Field
from typing import Literal


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=3, max_length=5000)


class SentimentPredictRequest(BaseModel):
    text: str = Field(..., min_length=3, max_length=5000)
    sentiment_model: Literal["ashish", "roberta_reference", "jesus"] = "ashish"


class SentimentResponse(BaseModel):
    sentiment: str
    confidence: float
    model: str


class CategoryResponse(BaseModel):
    category: str
    confidence: float
    model: str


class BlogRequest(BaseModel):
    category: str = Field(..., min_length=2, max_length=100)
    product: str | None = Field(default=None, max_length=200)
    review: str | None = Field(default=None, max_length=5000)
    blog_length: int = Field(default=800, ge=100, le=3500)
    include_emojis: bool = Field(default=True)
    include_citations: bool = Field(default=True)
    target_audience: str = Field(default="General Public", max_length=50)
    tone: str = Field(default="Professional", max_length=50)
    include_checklist: bool = Field(default=False)
    include_comparison: bool = Field(default=False)
    csrf_token: str = Field(..., min_length=16, max_length=256)


class BlogResponse(BaseModel):
    blog_post: str


class CsrfResponse(BaseModel):
    csrf_token: str
    expires_in_seconds: int


class ResearchRequest(BaseModel):
    product: str | None = Field(default=None, max_length=200)
    category: str | None = Field(default=None, max_length=100)
    csrf_token: str = Field(..., min_length=16, max_length=256)


class ResearchResponse(BaseModel):
    research_results: str
