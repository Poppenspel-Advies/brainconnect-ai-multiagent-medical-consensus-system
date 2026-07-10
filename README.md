# BrainConnect - AI Multi-Agent Medical Consensus System

A medical document analysis system using Fireworks AI Vision Language Models to extract structured clinical data from PDF documents.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   Backend       │────▶│  Fireworks AI   │
│   (React/Vite)  │     │   (FastAPI)     │     │  (Vision LLM)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │  PyMuPDF        │
                        │  (PDF→Images)   │
                        └─────────────────┘
```

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+
- Fireworks AI API key from https://fireworks.ai/account/api-keys

### 1. Backend Setup
```bash
cd backend
cp .env.example .env
# Edit .env and add your FIREWORKS_API_KEY

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend
python api.py
```
Backend runs at `http://localhost:8000`

### 2. Frontend Setup
```bash
# In project root
cp .env.example .env.local
# Edit .env.local if needed (VITE_API_URL)

# Install dependencies
npm install

# Run frontend
npm run dev
```
Frontend runs at `http://localhost:5173`

## Project Structure

```
brainconnect-ai-multiagent-medical-consensus-system/
├── backend/
│   ├── api.py                 # FastAPI REST endpoints
│   ├── fireworks_medical.py   # Fireworks AI integration
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment variables template
├── src/
│   ├── MedicalDocumentUploader.tsx  # Main React component
│   ├── App.tsx                        # App entry
│   ├── main.tsx                       # React root
│   └── index.css                      # Tailwind imports
├── public/                     # Static assets
├── package.json                # Frontend dependencies
├── vite.config.ts              # Vite configuration
├── tsconfig.json               # TypeScript config
└── .env.example                # Frontend env template
```

## API Endpoints

### `POST /api/analyze-medical-document`
Analyze a medical PDF document.

**Request:**
- `file` (multipart/form-data): PDF file
- `prompt` (optional): Custom analysis prompt
- `model` (optional): Fireworks model (default: `accounts/fireworks/models/kimi-k2p5`)
- `dpi` (optional): PDF render resolution (default: 200)

**Response:**
```json
{
  "success": true,
  "content": { ...structured medical data... },
  "model": "accounts/fireworks/models/kimi-k2p5",
  "pages_processed": 5,
  "usage": {
    "prompt_tokens": 1234,
    "completion_tokens": 567,
    "total_tokens": 1801
  }
}
```

### `GET /health`
Health check endpoint.

## Default Medical Prompt

The system uses a comprehensive medical extraction prompt covering:
1. Patient Demographics
2. Chief Complaint
3. History of Present Illness
4. Past Medical History
5. Medications
6. Allergies
7. Physical Exam Findings
8. Laboratory Results
9. Imaging Results
10. Assessment & Plan

Custom prompts can be provided via the UI or API.

## Fireworks Models

Supported vision models:
- `accounts/fireworks/models/kimi-k2p6` (default - strong vision capabilities)
- `accounts/fireworks/models/llama-v3p2-11b-vision-instruct`
- `accounts/fireworks/models/llama-v3p2-90b-vision-instruct`

## Development

### Backend Development
```bash
cd backend
source venv/bin/activate
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
npm run dev
```

### Type Checking
```bash
npm run build  # Runs tsc + vite build
```

## Deployment Notes

1. **Backend**: Deploy FastAPI with uvicorn/gunicorn behind nginx
2. **Frontend**: Build with `npm run build`, deploy static files
3. **Environment**: Set `FIREWORKS_API_KEY` in production environment
4. **CORS**: Configure `allow_origins` in `api.py` for production domains
5. **File Limits**: Adjust max file size in `api.py` if needed

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/fireworks-integration

# Make changes, commit
git add .
git commit -m "Add Fireworks AI medical document analysis"

# Push and create PR
git push origin feature/fireworks-integration
```

## License

MIT
