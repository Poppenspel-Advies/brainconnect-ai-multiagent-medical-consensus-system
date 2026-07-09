"""
BrainConnect Medical Document Analyzer - Fireworks AI Integration
Clean, minimal analyzer for Fireworks vision models
"""

import base64
import fitz  # PyMuPDF
import requests
import os
from typing import Optional, Dict, Any, List

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

CONSENSUS_MEDICAL_PROMPT = (
    "You are a medical AI assistant simulating a consensus conference of 3 physicians analyzing a clinical case. "
    "Provide consensus-driven differential diagnoses and personalized treatment plans.\n\n"
    "CRITICAL FORMAT REQUIREMENTS:\n"
    "1. RESPONSE MUST BE EXACTLY 4 PARAGRAPHS\n"
    "2. TITLE LINE: \"Patient: [Name] | Consensus Differential: [Diagnosis 1] | Treatment Plan: [Plan 1]\"\n"
    "3. PARAGRAPH 1: Patient history from the PDF (demographics, chief complaint, HPI, PMH, meds, allergies, exam, labs, imaging, assessment)\n"
    "4. PARAGRAPH 2: 3 physicians' consensus differential diagnoses in bullet points. Key phrases in *italics*.\n"
    "5. PARAGRAPH 3: 3 personalized treatment plans in bullet points. Key phases in *italics*.\n"
    "6. PARAGRAPH 4: Observations, next steps, future treatment suggestions.\n"
    "7. MAX 2000 words total.\n"
    "8. TONE: Polite, professional, US English, US medical standards.\n\n"
    "Extract ALL clinical data from the PDF. Do not hallucinate. If information is missing, note \"Not documented in provided records.\""
)

FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
FIREWORKS_MODEL = "accounts/fireworks/models/kimi-k2p6"
FIREWORKS_API_URL = "https://api.fireworks.ai/inference/v1/chat/completions"


def pdf_to_base64_images(pdf_bytes: bytes, dpi: int = 150) -> List[str]:
    """Convert PDF pages to base64 encoded PNG images"""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    
    for page in doc:
        pix = page.get_pixmap(dpi=dpi)
        img_bytes = pix.tobytes("png")
        images.append(base64.b64encode(img_bytes).decode("utf-8"))
    
    doc.close()
    return images


def analyze_medical_pdf(pdf_bytes: bytes, api_key: str, model: str = "accounts/fireworks/models/kimi-k2p6", dpi: int = 150, prompt: str = None) -> Dict[str, Any]:
    """
    Analyze medical PDF using Fireworks vision model
    Returns dict with success, content, model, pages_processed, usage
    """
    
    # Convert PDF to images
    images = pdf_to_base64_images(pdf_bytes, dpi=dpi)
    
    # Build content for vision model
    content = [{"type": "text", "text": prompt or CONSENSUS_MEDICAL_PROMPT}]
    
    for img in images:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{img}"}
        })
    
    # Call Fireworks API
    response = requests.post(
        "https://api.fireworks.ai/inference/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "accounts/fireworks/models/kimi-k2p6",
            "messages": [{"role": "user", "content": content}],
            "max_tokens": 4096,
            "temperature": 0.1
        },
        timeout=180
    )
    
    if response.status_code == 200:
        result = response.json()
        text = result["choices"][0]["message"]["content"]
        usage = result.get("usage", {})
        
        return {
            "success": True,
            "content": text.strip(),
            "model": "accounts/fireworks/models/kimi-k2p6",
            "pages_processed": len(images),
            "usage": {
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens")
            }
        }
    else:
        return {
            "success": False,
            "error": f"API error {response.status_code}: {response.text[:200]}"
        }


def analyze_pdf(pdf_bytes: bytes, provider: str = "fireworks") -> Dict[str, Any]:
    """Main entry point for PDF analysis"""
    api_key = os.getenv("FIREWORKS_API_KEY")
    if not api_key:
        return {"success": False, "error": "FIREWORKS_API_KEY not set in environment"}
    
    return analyze_medical_pdf(pdf_bytes, api_key=api_key)


if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python analyzer.py <pdf_path>")
        sys.exit(1)
    
    with open(sys.argv[1], "rb") as f:
        pdf_bytes = f.read()
    
    result = analyze_pdf(pdf_bytes)
    print(json.dumps(result, indent=2))