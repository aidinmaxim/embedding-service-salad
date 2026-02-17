# GPU-only image for SaladCloud. Base has PyTorch with CUDA 12.1.
FROM pytorch/pytorch:2.4.1-cuda12.1-cudnn9-runtime

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Pre-download model at build time for faster startup on Salad
ENV MODEL_NAME=sentence-transformers/paraphrase-multilingual-mpnet-base-v2
ENV SENTENCE_TRANSFORMERS_HOME=/app/cache
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('$MODEL_NAME')"

EXPOSE 8001
# Salad requires --host * for IPv6
CMD ["uvicorn", "main:app", "--host", "*", "--port", "8001"]
