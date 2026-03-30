# 🚀 Next-Gen Review Intelligence Dashboard

A high-performance, unified AI market intelligence platform designed to transform raw consumer feedback into actionable strategic reports. This dashboard leverages local Transformer models and OpenAI synthesis to provide real-time sentiment analysis, market classification, and deep research deep dives.

---

## 🌟 Key Features

### 🎭 Multi-Model Sentiment Intelligence
Extract emotional intent using a variety of specialized models:
- **Custom LoRA Adapters**: Fine-tuned PEFT models for niche sentiment accuracy.
- **Full RoBERTa Pipelines**: High-precision local sequence classification.
- **Model Lifecycle Management**: Lazy loading and automatic unloading of idle models (180s timeout) to optimize memory.

### 🎲 Strategic Market Categorization
Automated niche classification with a dynamic, synchronized UI:
- **Heuristic & Transformer Backends**: Fallback logic for resilient classification.
- **Visual Feedback**: Real-time category matching with "Dice" randomization indicators.

### 📝 Live Research Synthesis (Streaming)
Refactored, streaming-first intelligence reports:
- **Deep Market Discovery**: Word-by-word streaming of market trends and revenue snapshots using LangChain.
- **Strategic Mega-Reports**: Multi-modal blog generation with mandatory "Grounded Truth" citations and embedded Unsplash imagery.
- **Real-time Word Streaming**: Powered by `st.write_stream` for zero perceived latency.

### 🛡️ Dashboard Protocol
- **Vibrant Glossy UI**: Bespoke CSS-driven design system with aura animations and glassmorphism.
- **State-Driven Workflow**: Seamless transitions from Sentiment → Category → Deep Research.
- **JSON Credits Engine**: Dynamic attribution and asset tracking via `credits.json`.

---

## 📂 Repository Layout

- `frontend/`: The core Streamlit application logic, UI components, and styles.
- `models/`: Persistent directory for local `.bin` / `.safetensors` model artifacts and adapters.
- `docker-compose.yml`: Modern orchestration with `env_file` and optimized volumes.

---

## 🐳 Run With Docker (Optimized Build)

The stack is containerized with a **Multi-Stage Dockerfile** for maximum build efficiency and minimal runtime footprint.

1.  **Configure Credentials**:
    Ensure your `frontend/.env` is populated (see `.env.example` for reference).
    ```env
    OPENAI_API_KEY=your_key_here
    OPENAI_MODEL=gpt-4o-mini
    ```

2.  **Start the Intelligence Stack**:
    ```bash
    docker-compose up --build
    ```

3.  **Access the Dashboard**:
    - **Main Interface**: http://localhost:8501

---

## 🛠️ Local Development

Ensure you have [uv](https://github.com/astral-sh/uv) installed for lightning-fast dependency management.

### Setup
```bash
cd frontend
uv sync
```

### Execution
```bash
streamlit run Home.py
```

---

## ⚙️ Core Technology Stack

- **Frontend**: Streamlit 1.44+, Custom HSL Design Tokens.
- **LLM Orchestration**: LangChain 0.3+, OpenAI API (Streaming Mode).
- **ML Engine**: PyTorch, HuggingFace Transformers, PEFT (LoRA).
- **Package Management**: `uv`.
- **Infrastructure**: Docker Multi-stage Builds.
