"""
BrainConnect Medical Document Analyzer - Google Gemini Integration

Analyzes medical PDF documents using Google Gemini Vision Models (1.5 Flash/Pro).
"""

import base64
import fitz  # PyMuPDF
import google.generativeai as genai
from typing import Optional, Dict, Any, List
import os
import json


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

EXAMPLE FORMAT:
Patient: John Doe | Consensus Differential: Acute Coronary Syndrome | Treatment Plan: Immediate PCI Pathway

[Paragraph 1: Patient history...]

[Paragraph 2: 
• Dr. Smith (Cardiology): *Primary consideration* — Acute Coronary Syndrome given...
• Dr. Chen (Emergency Medicine): *Key differential* — Aortic dissection...
• Dr. Patel (Internal Medicine): *Must rule out* — Pulmonary embolism...]

[Paragraph 3:
• *Immediate stabilization*: Aspirin, P2Y12 inhibitor, anticoagulation...
• *Definitive management*: Early invasive strategy with cardiac catheterization...
• *Secondary prevention*: High-intensity statin, beta-blocker, ACE inhibitor...]

[Paragraph 4: Observations and next steps...]

Extract ALL clinical data from the PDF. Do not hallucinate. If information is missing, note "Not documented in provided records."""  # noqa: E501


class GeminiMedicalAnalyzer:
    """
    Analyzes medical PDF documents using Google Gemini Vision Models.
    
    Usage:
        analyzer = GeminiMedicalAnalyzer(api_key="your_key")
        result = analyzer.analyze_medical_document("path/to/document.pdf")
        print(result["content"])
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: str = "gemini-1.5-flash"
    ):
        """
        Initialize the analyzer.
        
        Args:
            api_key: Google AI Studio API key (defaults to GEMINI_API_KEY env var)
            model: Gemini model to use (default: gemini-1.5-flash, options: gemini-1.5-pro)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key required. Set GEMINI_API_KEY env var or pass api_key parameter.")
        
        self.model_name = model
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)
    
    def pdf_pages_to_base64(self, pdf_path: str, dpi: int = 200) -> List[str]:
        """
        Convert PDF pages to base64 encoded PNG images.
        
        Args:
            pdf_path: Path to PDF file
            dpi: Rendering resolution (default 200)
            
        Returns:
            List of base64 encoded PNG strings
        """
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
        """
        Convert PDF bytes to base64 encoded PNG images.
        
        Args:
            pdf_bytes: PDF file content as bytes
            dpi: Rendering resolution (default 200)
            
        Returns:
            List of base64 encoded PNG strings
        """
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        images = []
        
        for page_num, page in enumerate(doc):
            pix = page.get_pixmap(dpi=dpi)
            img_bytes = pix.tobytes("png")
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
            images.append(img_b64)
        
        doc.close()
        return images
    
    def analyze_medical_document(
        self,
        pdf_path: str,
        prompt: Optional[str] = None,
        dpi: int = 200
    ) -> Dict[str, Any]:
        """
        Analyze a medical PDF document from file path.
        
        Args:
            pdf_path: Path to PDF file
            prompt: Custom analysis prompt (uses consensus prompt if None)
            dpi: PDF rendering resolution
            
        Returns:
            Dict with analysis results
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        page_images = self.pdf_pages_to_base64(pdf_path, dpi=dpi)
        
        return self._analyze_images(page_images, prompt or CONSENSUS_MEDICAL_PROMPT)
    
    def analyze_medical_document_bytes(
        self,
        pdf_bytes: bytes,
        prompt: Optional[str] = None,
        dpi: int = 200
    ) -> Dict[str, Any]:
        """
        Analyze a medical PDF document from bytes (e.g., uploaded file).
        
        Args:
            pdf_bytes: PDF file content as bytes
            prompt: Custom analysis prompt (uses consensus prompt if None)
            dpi: PDF rendering resolution
            
        Returns:
            Dict with analysis results
        """
        page_images = self.pdf_bytes_to_base64(pdf_bytes, dpi=dpi)
        
        return self._analyze_images(page_images, prompt or CONSENSUS_MEDICAL_PROMPT)
    
    def _analyze_images(self, page_images: List[str], prompt: str) -> Dict[str, Any]:
        """
        Send images to Gemini for analysis.
        
        Args:
            page_images: List of base64 encoded PNG images
            prompt: Analysis prompt
            
        Returns:
            Dict with analysis results
        """
        # Build content for Gemini (text + images)
        content = [prompt]
        
        for img_b64 in page_images:
            content.append({
                "mime_type": "image/png",
                "data": base64.b64decode(img_b64)
            })
        
        # Configure generation
        generation_config = genai.types.GenerationConfig(
            temperature=0.1,
            max_output_tokens=4096,
        )
        
        # Call Gemini API
        response = self.model.generate_content(
            content,
            generation_config=generation_config
        )
        
        message_content = response.text
        
        return {
            "success": True,
            "content": message_content,
            "model": self.model_name,
            "pages_processed": len(page_images),
            "usage": {
                "prompt_tokens": response.usage_metadata.prompt_token_count if response.usage_metadata else None,
                "completion_tokens": response.usage_metadata.candidates_token_count if response.usage_metadata else None,
                "total_tokens": response.usage_metadata.total_token_count if response.usage_metadata else None
            }
        }


# Convenience function for quick analysis
def analyze_pdf_with_gemini(
    pdf_path: str,
    api_key: Optional[str] = None,
    prompt: Optional[str] = None,
    model: str = "gemini-1.5-flash",
    dpi: int = 200
) -> Dict[str, Any]:
    """
    Convenience function to analyze a medical PDF with Gemini.
    
    Args:
        pdf_path: Path to PDF file
        api_key: Gemini API key (uses env var if not provided)
        prompt: Custom prompt (uses consensus prompt if None)
        model: Gemini model to use
        dpi: PDF rendering resolution
        
    Returns:
        Dict with analysis results
    """
    analyzer = GeminiMedicalAnalyzer(api_key=api_key, model=model)
    return analyzer.analyze_medical_document(
        pdf_path=pdf_path,
        prompt=prompt or CONSENSUS_MEDICAL_PROMPT,
        dpi=dpi
    )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python gemini_medical.py <pdf_path> [api_key]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    api_key = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result = analyze_pdf_with_gemini(pdf_path, api_key)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)