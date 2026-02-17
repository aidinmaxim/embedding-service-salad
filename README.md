# Embedding Service (GPU) for SaladCloud

Multilingual embedding service for search (e.g. Meilisearch hybrid search). Same API contract as the backend expects; **GPU-only** image for deployment on [SaladCloud](https://docs.salad.com/container-engine/tutorials/quickstart).

- **POST /embed** — `{"texts": ["s1", "s2", ...]}` → `{"embeddings": [[...], [...]]}` (768 dimensions, up to 100 texts per request).
- **GET /health**, **GET /started**, **GET /ready**, **GET /live** — for health checks and Salad probes.

## Build

Requires a Docker environment that can build the image (no GPU needed for build; the base image is pre-built with CUDA).

```bash
docker build -t your-registry/embedding-salad:gpu .
```

Push to your registry (Docker Hub, GHCR, etc.):

```bash
docker push your-registry/embedding-salad:gpu
```

## Local run (with GPU)

If you have an NVIDIA GPU and [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html):

```bash
docker run --gpus all -p 8001:8001 your-registry/embedding-salad:gpu
```

Then: `curl http://localhost:8001/health` and `curl -X POST http://localhost:8001/embed -H "Content-Type: application/json" -d '{"texts":["test"]}'`.

## Deploy on SaladCloud

1. **Push the image** to a registry Salad can pull from (Docker Hub, GHCR, etc.). Images up to 35 GB (compressed) are supported.

2. **Create a Container Group** in the [SaladCloud Portal](https://portal.salad.com):
   - **Image**: `your-registry/embedding-salad:gpu`
   - **Replicas**: 1 or more
   - **Hardware**: **GPU required** — select one or more GPUs in the Hardware section. CPU/RAM as needed (e.g. 2 vCPU, 4 GB RAM).

3. **Add Container Gateway**:
   - **Port**: `8001`
   - **Load balancing**: **Least Connections** (recommended for embedding workloads).

4. **Health Probes** (Salad lifecycle):
   - **Startup** (`/started`): Initial Delay `0`, Period `1s`, Timeout `1s`, Success Threshold `1`, Failure Threshold `5`.
   - **Liveness** (`/live`): Failure Threshold `3`.
   - **Readiness** (`/ready`): controls when the instance receives traffic.

5. **Deploy** and note the Container Gateway URL (e.g. `https://xxx.salad.cloud`).

6. **Backend config**: In your app (e.g. meindeal-backend), set:
   ```env
   EMBEDDING_SERVICE_URL=https://<your-gateway>.salad.cloud
   ```
   No port in URL if the gateway serves HTTPS on 443.

## Environment

- `MODEL_NAME` — sentence-transformers model (default: `paraphrase-multilingual-mpnet-base-v2`, 768d).
- `MAX_TEXT_LENGTH` — max characters per text, truncation (default: `512`).

## Reference

- [Salad Quickstart](https://docs.salad.com/container-engine/tutorials/quickstart)
- [Salad Health Probes](https://docs.salad.com/container-engine/explanation/infrastructure-platform/health-probes)
