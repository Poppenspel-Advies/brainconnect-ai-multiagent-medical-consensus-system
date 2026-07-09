"""
BrainConnect Medical Document Analyzer - Hugging Face Inference API Integration

Analyzes medical PDF documents using Hugging Face vision models (LLaVA, Qwen-VL, etc.).
Free tier: 30,000 requests/month, no region restrictions.
"""

import base64
import fitz  # PyMuPDF
import requests
import os
from typing import Optional, Dict, Any, List
import json
import time
from dotenv import load_dotenv

# Load .env file
load_dotenv()


CONSENSUS_MEDICAL_PROMPT = """You are a medical AI assistant simulating a consensus conference of 3 physicians analyzing a clinical case. 
Provide consensus-driven differential diagnoses and personalized treatment plans.

CRITICAL FORMAT REQUIREMENTS:
1. RESPONSE MUST BE EXACTLY 4 PARAGRAPHS
2. TITLE LINE: "Patient: [Name] | Consensus Differential: [Diagnosis 1] | Treatment Plan: [Plan 1]"
3. PARAGRAPH 1: Patient history from the PDF (demographics, chief complaint, HPI, PMH, meds, allergies, exam, labs, imaging, assessment)
4. PARAGRAPH 2: 3 physicians' consensus differential diagnoses in bullet points. Key phrases in *italics*.
5. PARAGRAPH 3: 3 personalized treatment plans in bullet points. Key phases in *italics*.
6. PARAGRAPH 4: Observations, next steps, future treatment suggestions.
7. MAX 2000 words total.
8. TONE: Polite, professional, US English, US medical standards.

Extract ALL clinical data from the PDF. Do not hallucinate. If information is missing, note "Not documented in provided records."""  # noqa: E501


# Recommended free vision models on Hugging Face
HF_VISION_MODELS = {
    "llava-1.5-7b": "llava-hf/llava-1.5-7b-hf",
    "llava-1.5-13b": "llava-hf/llava-1.5-13b-hf", 
    "llava-next-7b": "llava-hf/llava-v1.6-mistral-7b-hf",
    "llava-next-13b": "llava-hf/llava-v1.6-vicuna-13b-hf",
    "qwen-vl": "Qwen/Qwen-VL-Chat",
    "idefics2-8b": "HuggingFaceM4/idefics2-8b",
    "bakllava": "llava-hf/bakllava-7b-hf",
}


class HFMedicalAnalyzer:
    """
    Analyzes medical PDF documents using Hugging Face Inference API vision models.
    
    Usage:
        analyzer = HFMedicalAnalyzer(api_key="hf_...")
        result = analyzer.analyze_medical_document("path/to/document.pdf")
        print(result["content"])
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: str = "llava-1.5-7b",
        timeout: int = 120
    ):
        """
        Initialize the analyzer.
        
        Args:
            api_key: Hugging Face API token (defaults to HF_API_KEY env var)
            model: Model key from HF_VISION_MODELS (default: llava-1.5-7b)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.getenv("HF_API_KEY")
        if not self.api_key:
            raise ValueError("Hugging Face API key required. Set HF_API_KEY env var or pass api_key parameter.")
        
        self.model_key = model
        self.model_id = HF_VISION_MODELS.get(model, model)
        self.timeout = timeout
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_id}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def pdf_pages_to_base64(self, pdf_path: str, dpi: int = 200) -> List[str]:
        """Convert PDF pages to base64 encoded PNG images."""
        doc = fitz.open(pdf_path)
        images = []
        
        for page_num, page in enumerate(doc):
            pix = page.get_pixmap(dpi=dpi)
            img_bytes = pix.tobytes("png")
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
            images.append(img_b64)
        
        doc.close()
        return images
    
    def pdf_bytes_to_base64(self, pdf_bytes: bytes, dpi: int = 200) -> List[str]:
        """Convert PDF bytes to base64 encoded PNG images."""
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        images = []
        
        for page_num, page in enumerate(doc):
            pix = page.get_pixmap(dpi=dpi)
            img_bytes = pix.tobytes("png")
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
            images.append(img_b64)
        
        doc.close()
        return images
    
    def _call_hf_api(self, images_b64: List[str], prompt: str) -> Dict[str, Any]:
        """Call Hugging Face Inference API with images and prompt."""
        
        # Build payload for vision models (LLaVA format)
        content = []
        content.append({"type": "text", "text": prompt})
        
        for img_b64 in images_b64:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{img_b64}"}
            })
        
        payload = {
            "inputs": [
                {"role": "user", "content": content}
            ],
            "parameters": {
                "max_new_tokens": 2048,
                "temperature": 0.1,
                "top_p": 0.9,
                "return_full_text": False
            }
        }
        
        # Handle model loading (first request may take longer)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    # Handle different response formats
                    if isinstance(result, list) and len(result) > 0:
                        text = result[0].get("generated_text", "")
                    elif isinstance(result, dict):
                        text = result.get("generated_text", result.get("generated_text", ""))
                    else:
                        text = str(result)
                    
                    return {
                        "success": True,
                        "content": text.strip(),
                        "model": self.model_id,
                        "pages_processed": len(images_b64)
                    }
                
                elif response.status_code == 503:
                    # Model loading - wait and retry
                    wait_time = 10 * (attempt + 1)
                    print(f"Model loading, waiting {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                    
                else:
                    error_msg = f"HF API error {response.status_code}: {response.text[:200]}"
                    return {"success": False, "error": error_msg}
                    
            except requests.exceptions.Timeout:
                return {"success": False, "error": "Request timeout"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Max retries exceeded - model may be loading"}
    
    def analyze_medical_document(
        self,
        pdf_path: str,
        prompt: Optional[str] = None,
        dpi: int = 200
    ) -> Dict[str, Any]:
        """Analyze a medical PDF document from file path."""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        page_images = self.pdf_pages_to_base64(pdf_path, dpi=dpi)
        return self._call_hf_api(page_images, prompt or CONSENSUS_MEDICAL_PROMPT)
    
    def analyze_medical_document_bytes(
        self,
        pdf_bytes: bytes,
        prompt: Optional[str] = None,
        dpi: int = 200
    ) -> Dict[str, Any]:
        """Analyze a medical PDF document from bytes."""
        page_images = self.pdf_bytes_to_base64(pdf_bytes, dpi=dpi)
        return self._call_hf_api(page_images, prompt or CONSENSUS_MEDICAL_PROMPT)


# Convenience function
def analyze_pdf_with_hf(
    pdf_path: str,
    api_key: Optional[str] = None,
    prompt: Optional[str] = None,
    model: str = "llava-1.5-7b",
    dpi: int = 200
) -> Dict[str, Any]:
    analyzer = HFMedicalAnalyzer(api_key=api_key, model=model)
    return analyzer.analyze_medical_document(
        pdf_path=pdf_path,
        prompt=prompt or CONSENSUS_MEDICAL_PROMPT,
        dpi=dpi
    )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python hf_medical.py <pdf_path> [api_key]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    api_key = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result = analyze_pdf_with_hf(pdf_path, api_key)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)