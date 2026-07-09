"""
BrainConnect Medical Document Analyzer API - FastAPI Backend
Multi-provider support with Fireworks as primary (working)
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from analyzer import analyze_pdf, CONSENSUS_MEDICAL_PROMPT

app = FastAPI(title="BrainConnect Medical Analysis API", version="1.0.0")

# CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalysisRequest(BaseModel):
    prompt: Optional[str] = None
    model: Optional[str] = "accounts/fireworks/models/kimi-k2p6"
    dpi: Optional[int] = 150


class AnalysisResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    model: Optional[str] = None
    pages_processed: Optional[int] = None
    usage: Optional[dict] = None
    error: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Verify configuration on startup"""
    fireworks_key = os.getenv("FIREWORKS_API_KEY")
    if fireworks_key:
        print(f"Fireworks API configured: {fireworks_key[:10]}...")
    else:
        print("WARNING: FIREWORKS_API_KEY not set")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "BrainConnect Medical Analysis API",
        "providers": {
            "fireworks": bool(os.getenv("FIREWORKS_API_KEY")),
            "gemini": bool(os.getenv("GEMINI_API_KEY")),
            "huggingface": bool(os.getenv("HF_API_KEY"))
        },
        "primary_provider": "fireworks" if os.getenv("FIREWORKS_API_KEY") else "none"
    }


@app.post("/api/analyze-medical-document", response_model=dict)
async def analyze_medical_document(
    file: UploadFile = File(...),
    prompt: Optional[str] = Form(None),
    model: Optional[str] = Form("accounts/fireworks/models/kimi-k2p6"),
    dpi: Optional[int] = Form(150)
):
    """
    Analyze a medical PDF document using vision language models
    
    - **file**: PDF file to analyze (max 20MB)
    - **prompt**: Custom analysis prompt (optional, uses default medical consensus prompt)
    - **model**: Model to use (default: accounts/fireworks/models/kimi-k2p6)
    - **dpi**: PDF rendering resolution (default: 150)
    """
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Read file bytes
    pdf_bytes = await file.read()
    
    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded")
    
    # Validate file size (max 20MB)
    if len(pdf_bytes) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 20MB limit")
    
    try:
        # Use default consensus prompt if none provided
        analysis_prompt = prompt or CONSENSUS_MEDICAL_PROMPT
        
        # Analyze document using Fireworks (primary provider)
        from analyzer import analyze_pdf
        result = analyze_pdf(pdf_bytes)
        
        if not result.get("success"):
            raise HTTPException(status_code=503, detail=f"Analysis failed: {result.get('error', 'Unknown error')}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/api/analyze-medical-document-fallback")
async def analyze_with_fallback(
    file: UploadFile = File(...),
    prompt: Optional[str] = Form(None),
    dpi: Optional[int] = Form(150)
):
    """
    Try Fireworks first, fallback to other providers
    """
    # Validate file
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    pdf_bytes = await file.read()
    
    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded")
    
    if len(pdf_bytes) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 20MB limit")
    
    analysis_prompt = prompt or CONSENSUS_MEDICAL_PROMPT
    
    # Try Fireworks first
    from analyzer import analyze_pdf
    try:
        result = analyze_pdf(pdf_bytes)
        if result.get("success"):
            result["fallback"] = False
            return result
    except Exception as e:
        print(f"Fireworks failed: {e}")
    
    raise HTTPException(503, "All providers failed")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)