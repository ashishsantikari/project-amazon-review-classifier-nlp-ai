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
    csrf_token: str = Field(..., min_length=16, max_length=256)


class BlogResponse(BaseModel):
    blog_post: str


class CsrfResponse(BaseModel):
    csrf_token: str
    expires_in_seconds: int
