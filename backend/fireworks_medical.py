"""
BrainConnect Medical Document Analyzer - Fireworks AI Integration

This module provides a clean interface to analyze medical PDF documents
using Fireworks Vision Language Models (VLMs).
"""

import base64
import fitz  # PyMuPDF
from fireworks.client import Fireworks
from typing import Optional, Dict, Any, List
import os
import json


CONSENSUS_MEDICAL_PROMPT = """You are a medical AI assistant in a consensus conference of physicians analyzing a clinical case. 
Provide consensus-driven differential diagnoses and personalized treatment plans for the Patient from the pdf passed. Include all below information only in response and no other information from the pdf.

CRITICAL FORMAT REQUIREMENTS:
1. RESPONSE MUST CONTENT EXACTLY 5 PARAGRAPHS WITH BELOW DETAILS AND NO OTHER DETAILS
2. **PARAGRAPH 1: Patient history from the PDF (demographics, chief complaint, HPI, PMH, meds, allergies, exam, labs, imaging, assessment) & lifestyle and 200 word count.
3. **PARAGRAPH 2: Physicians'  and their consensus-driven differential diagnoses in bullet points. Important phrases in *italics* and 200 word count.
4. **PARAGRAPH 3: Personalized treatment plans in bullet points. Important phases in *italics* and 200 word count.
5. **PARAGRAPH 4: Observations, next steps, future treatment suggestions with 200 word count.
6. **PARAGRAPH 5: empty paragraph.
7. TONE: Polite, professional, US English, US medical standards.

EXAMPLE FORMAT:
Patient: John Doe | Consensus Differential: Acute Coronary Syndrome | Treatment Plan: Immediate PCI Pathway

[Paragraph 1: Patient history...]

[Paragraph 2: 
• *Primary consideration* — Acute Coronary Syndrome given...
• *Key differential* — Aortic dissection...
• *Must rule out* — Pulmonary embolism...]

[Paragraph 3:
• *Immediate stabilization*: Aspirin, P2Y12 inhibitor, anticoagulation...
• *Definitive management*: Early invasive strategy with cardiac catheterization...
• *Secondary prevention*: High-intensity statin, beta-blocker, ACE inhibitor...]

[Paragraph 4: Observations and next steps...]

[PARAGRAPH 5: ]

Extract above response from the given PDF. Do not hallucinate. If information is missing, note "Not documented" in provided records. Do not repeat user request and your analysis of the patient details for the pdf in response. Do not provide details of what you need to follow strict formatting requirements in response. Do not provide details of your extract of the clinical data first in response. Do not repeat in any Paragraph what you have to include in response. Do not send your draft response, send your final response."""  # noqa: E501


class FireworksMedicalAnalyzer:
    """
    Analyzes medical PDF documents using Fireworks Vision Language Models.
    
    Usage:
        analyzer = FireworksMedicalAnalyzer(api_key="your_key")
        result = analyzer.analyze_medical_document("path/to/document.pdf")
        print(result["content"])
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: str = "accounts/fireworks/models/kimi-k2p6"
    ):
        """
        Initialize the analyzer.
        
        Args:
            api_key: Fireworks API key (defaults to FIREWORKS_API_KEY env var)
            model: Fireworks model to use (default: kimi-k2p6 vision model)
        """
        self.api_key = api_key or os.getenv("FIREWORKS_API_KEY")
        if not self.api_key:
            raise ValueError("Fireworks API key required. Set FIREWORKS_API_KEY env var or pass api_key parameter.")
        
        self.model = model
        self.client = Fireworks(api_key=self.api_key)
    
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
        Send images to Fireworks VLM for analysis.
        
        Args:
            page_images: List of base64 encoded PNG images
            prompt: Analysis prompt
            
        Returns:
            Dict with analysis results
        """
        # Build content array with text prompt and images
        content = [{"type": "text", "text": prompt}]
        
        for img_b64 in page_images:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{img_b64}"}
            })
        
        # Call Fireworks API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": content}],
            temperature=0.1,
            max_tokens=4096
        )
        
        # Extract response
        message_content = response.choices[0].message.content
        
        return {
            "success": True,
            "content": message_content,
            "model": self.model,
            "pages_processed": len(page_images),
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else None,
                "completion_tokens": response.usage.completion_tokens if response.usage else None,
                "total_tokens": response.usage.total_tokens if response.usage else None
            }
        }


# Convenience function for quick analysis
def analyze_pdf_with_fireworks(
    pdf_path: str,
    api_key: Optional[str] = None,
    prompt: Optional[str] = None,
    model: str = "accounts/fireworks/models/kimi-k2p6",
    dpi: int = 200
) -> Dict[str, Any]:
    """
    Convenience function to analyze a medical PDF with Fireworks.
    
    Args:
        pdf_path: Path to PDF file
        api_key: Fireworks API key (uses env var if not provided)
        prompt: Custom prompt (uses consensus prompt if None)
        model: Fireworks model to use
        dpi: PDF rendering resolution
        
    Returns:
        Dict with analysis results
    """
    analyzer = FireworksMedicalAnalyzer(api_key=api_key, model=model)
    return analyzer.analyze_medical_document(
        pdf_path=pdf_path,
        prompt=prompt or CONSENSUS_MEDICAL_PROMPT,
        dpi=dpi
    )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python fireworks_medical.py <pdf_path> [api_key]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    api_key = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result = analyze_pdf_with_fireworks(pdf_path, api_key)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
