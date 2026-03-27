# Project Plan

## Scope
Build a monorepo app with Streamlit frontend and FastAPI backend supporting:
- Landing page
- Sentiment classifier
- Category classifier
- Blog post generation
- JSON-driven credits page

## Architecture
- Frontend: Streamlit multipage app
- Backend: FastAPI REST API
- Models: Mounted from a Docker volume (`/models`)
- LLM: OpenAI endpoint for blog generation

## API Contract

### GET /health
Returns service status.

### GET /csrf-token
Returns a short-lived CSRF token for blog form submission.

### POST /predict/sentiment
Request:
```json
{
  "text": "I love this product"
}
```
Response:
```json
{
  "sentiment": "positive",
  "confidence": 0.97,
  "model": "sentiment-transformer-v1"
}
```

### POST /predict/category
Request:
```json
{
  "text": "Battery life is excellent and camera is great"
}
```
Response:
```json
{
  "category": "electronics",
  "confidence": 0.9,
  "model": "category-transformer-v1"
}
```

### POST /generate/blog
Request:
```json
{
  "category": "electronics",
  "product": "Smartphone X",
  "review": "Battery life is excellent",
  "csrf_token": "token"
}
```
Headers:
- `x-csrf-token`: must match body token
- `x-client-id`: stable client id for rate limiting

Response:
```json
{
  "blog_post": "..."
}
```

## Security & Cost Controls
- CSRF token required for blog generation.
- Per-client rate limiting on blog endpoint.
- OpenAI key only on backend via environment variable.
- Input length guardrails and clear API error messages.

## Model Lifecycle
- Models are lazy-loaded from `/models`.
- Last usage time tracked per model.
- Background sweeper unloads models not used for 3+ minutes.

## Deployment
- Docker Compose runs both services.
- Mounted volumes:
  - `./models:/models`

## Manual Validation Checklist
- Landing CTA navigates to Sentiment page.
- Sentiment prediction works.
- Category prediction works with dice animation.
- Blog post generation works with CSRF token.
- Rate limiting blocks excessive blog requests.
- Credits page renders from JSON.
- Idle models are unloaded after 3 minutes.
