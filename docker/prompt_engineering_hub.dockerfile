# Advanced Prompt Engineering Service
# Intelligent prompt optimization and management
# Author: Fahed Mlaiel (mlaiel@live.de) - IA Prompt Engineer Role

FROM python:3.11-slim AS base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Prompt Engineering Hub - Advanced prompt optimization"
LABEL version="1.0.0"

# Install dependencies for prompt engineering
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install prompt engineering and AI libraries
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    # AI API clients
    openai \
    anthropic \
    google-generativeai \
    cohere \
    # Prompt engineering frameworks
    langchain \
    prompttools \
    guidance \
    # Text processing
    transformers \
    tokenizers \
    # Prompt optimization
    optuna \
    hyperopt \
    # Template engines
    jinja2 \
    mustache \
    # NLP utilities
    spacy \
    nltk \
    textstat \
    # Async processing
    asyncio \
    aiohttp \
    # Data analysis
    pandas \
    numpy \
    matplotlib \
    seaborn \
    # Caching
    redis \
    # Web framework
    fastapi \
    uvicorn \
    # Testing
    pytest \
    pytest-asyncio

# Download NLP resources
RUN python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"

# Copy prompt engineering source code
COPY ./prompt_engineering/ ./engineering/
COPY ./ai_services/common/ ./common/

# Security: Create prompt engineer user
RUN groupadd --gid 1000 promptengineer && \
    useradd --uid 1000 --gid promptengineer --shell /bin/bash --create-home promptengineer

# Create prompt engineering directories
RUN mkdir -p \
    /app/templates \
    /app/optimizations \
    /app/experiments \
    /app/cache \
    /app/logs \
    /app/metrics \
    /app/datasets \
    && chown -R promptengineer:promptengineer /app \
    && chmod 755 /app

# Copy template library
COPY ./prompt_engineering/templates/ /app/templates/
COPY ./prompt_engineering/experiments/ /app/experiments/

# Cleanup
RUN rm -rf /var/lib/apt/lists/* \
    /tmp/* \
    /var/tmp/* \
    && find /app -name "*.pyc" -delete

# Switch to prompt engineer user
USER promptengineer

# Prompt engineering environment variables
ENV PYTHONPATH=/app \
    SERVICE_NAME=prompt_engineering_hub \
    TEMPLATE_CACHE_SIZE=500 \
    OPTIMIZATION_RUNS=100 \
    A_B_TEST_ENABLED=true \
    PERFORMANCE_TRACKING=true \
    AUTO_OPTIMIZATION=true

# Health check for prompt engineering service
HEALTHCHECK --interval=30s --timeout=15s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8000/prompts/health').raise_for_status()" || exit 1

EXPOSE 8000

# Start prompt engineering hub
CMD ["python3", "-m", "uvicorn", "engineering.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1", \
     "--log-level", "info"]