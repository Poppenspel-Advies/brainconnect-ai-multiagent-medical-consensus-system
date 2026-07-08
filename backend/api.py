"""
FastAPI Backend for BrainConnect - Fireworks AI Integration
Provides REST endpoints for medical document analysis
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import os
import json

from fireworks_medical import FireworksMedicalAnalyzer, DEFAULT_MEDICAL_PROMPT

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
    model: Optional[str] = "accounts/fireworks/models/kimi-k2p5"
    dpi: Optional[int] = 200


class AnalysisResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    model: Optional[str] = None
    pages_processed: Optional[int] = None
    usage: Optional[dict] = None
    error: Optional[str] = None


# Global analyzer instance (initialized on startup)
analyzer: Optional[FireworksMedicalAnalyzer] = None


@app.on_event("startup")
async def startup_event():
    """Initialize Fireworks analyzer on startup"""
    global analyzer
    api_key = os.getenv("FIREWORKS_API_KEY")
    if api_key:
        analyzer = FireworksMedicalAnalyzer(api_key=api_key)
    else:
        print("WARNING: FIREWORKS_API_KEY not set. API will return errors until configured.")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "BrainConnect Medical Analysis API",
        "fireworks_configured": analyzer is not None
    }


@app.post("/api/analyze-medical-document", response_model=AnalysisResponse)
async def analyze_medical_document(
    file: UploadFile = File(...),
    prompt: Optional[str] = Form(None),
    model: Optional[str] = Form("accounts/fireworks/models/kimi-k2p5"),
    dpi: Optional[int] = Form(200)
):
    """
    Analyze a medical PDF document using Fireworks Vision Model
    
    - **file**: PDF file to analyze
    - **prompt**: Custom analysis prompt (optional, uses default medical prompt)
    - **model**: Fireworks model to use (default: kimi-k2p5)
    - **dpi**: PDF rendering resolution (default: 200)
    """
    if not analyzer:
        raise HTTPException(
            status_code=503,
            detail="Fireworks API not configured. Set FIREWORKS_API_KEY environment variable."
        )
    
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
        # Update model if different
        if model != analyzer.model:
            analyzer.model = model
        
        # Analyze document
        result = analyzer.analyze_medical_document_bytes(
            pdf_bytes=pdf_bytes,
            prompt=prompt or DEFAULT_MEDICAL_PROMPT,
            dpi=dpi
        )
        
        return AnalysisResponse(**result)
        
    except Exception as e:
        return AnalysisResponse(
            success=False,
            error=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)