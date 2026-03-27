# Specialized Agent Task Board

Use this board to run independent feature streams in parallel.

## Agent: REST API Specialist
Status: Done
- Implemented FastAPI contracts in backend app
- Added sentiment and category prediction endpoints
- Added blog generation endpoint wired to OpenAI client

## Agent: Security Specialist
Status: Done
- Implemented CSRF token issuance and validation
- Added secure form/header token matching for blog endpoint
- Added per-client rate limiter to reduce overload/cost risk

## Agent: ML Runtime Specialist
Status: Done
- Added lazy model loading from mounted model volume
- Added idle model unload logic after 3 minutes inactivity
- Added fallback heuristics when model artifacts are absent

## Agent: Streamlit UX Specialist
Status: Done
- Built marketing-focused landing page with CTA
- Built sentiment flow page with user guidance
- Built category flow page with rolling dice animation component
- Built blog generation page with secure form flow and cooldown
- Built JSON-driven credits page

## Agent: Docker Specialist
Status: Done
- Added backend Dockerfile
- Added frontend Dockerfile
- Added docker-compose orchestration with model volume mount

## Agent: Manual Validation Specialist
Status: Pending
- Bring stack up with Docker Compose
- Verify endpoint flows and UI navigation
- Verify CSRF and rate limiting under repeated blog requests
- Verify model unload after 3+ minutes idle
