"""
Multilingual embedding service (GPU). Exposes POST /embed, GET /health, and Salad probes.
Default: paraphrase-multilingual-mpnet-base-v2 (768d). Override MODEL_NAME for another 768d model.
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

MODEL_NAME = os.environ.get(
    "MODEL_NAME",
    "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
)
MAX_TEXT_LENGTH = int(os.environ.get("MAX_TEXT_LENGTH", "512"))

model = None


def get_model():
    global model
    if model is None:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(MODEL_NAME)
    return model


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_model()
    yield


app = FastAPI(title="Embedding Service (GPU)", lifespan=lifespan)


class EmbedRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1, max_length=100)


class EmbedResponse(BaseModel):
    embeddings: list[list[float]]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/started")
def started():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    return {"status": "ok"}


@app.get("/live")
def live():
    return {"status": "ok"}


@app.post("/embed", response_model=EmbedResponse)
def embed(request: EmbedRequest):
    try:
        encoder = get_model()
        truncated = [t[:MAX_TEXT_LENGTH] if len(t) > MAX_TEXT_LENGTH else t for t in request.texts]
        embeddings = encoder.encode(truncated, convert_to_numpy=True)
        return EmbedResponse(embeddings=[e.tolist() for e in embeddings])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
