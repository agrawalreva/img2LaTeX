# img2LaTeX AI

image-to-LaTeX conversion system using Qwen2-VL-7B vision-language model with LoRA fine-tuning.

## Setup

### Backend

```bash
cd apps/api
pip install -e .
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```bash
cd apps/web
npm install
npm run dev
```

### Development Script

```bash
# Start both backend and frontend
./start-dev.sh
```

Services:
- API: http://localhost:8000
- Web: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Usage

### Inference

Upload an image via the web UI or API:

```bash
curl -X POST "http://localhost:8000/api/infer" \
  -F "image=@path/to/equation.png"
```

### Training

1. Build dataset by correcting LaTeX outputs in Dataset page
2. Configure training parameters in Train page
3. Start training job (requires 5+ dataset pairs)
4. Monitor progress and switch to trained adapter when complete

### Evaluation

Use the Evaluate page to test model performance on sample equations with accuracy and similarity metrics.

## API Endpoints

- `POST /api/infer` - Generate LaTeX from image
- `GET /api/history` - Get inference history
- `GET /api/dataset/pairs` - List dataset pairs
- `POST /api/train` - Start training job
- `GET /api/train/{job_id}/status` - Get training status
- `POST /api/evaluate` - Evaluate model on test pairs
- `GET /api/models/current` - Get current model info
- `POST /api/models/switch` - Switch model adapter

## Configuration

Environment variables:

- `DATABASE_URL` - Database connection string
- `REDIS_URL` - Redis connection string
- `ARTIFACTS_DIR` - Training output directory
- `UPLOAD_DIR` - Uploaded images directory
- `MAX_NEW_TOKENS` - Max tokens for generation (default: 256)
- `TEMPERATURE` - Sampling temperature (default: 0.7)
- `MIN_P` - Minimum probability threshold (default: 0.1)

## Project Structure

```
apps/
  api/          # FastAPI backend
  web/          # React frontend
  worker/       # Celery worker
models/
  inference/    # Model loading and inference
  training/     # Training outputs
```
