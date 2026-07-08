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


DEFAULT_MEDICAL_PROMPT = """You are a medical AI assistant analyzing clinical documents for physicians.
Extract and structure the following information from the provided medical document:

1. **Patient Demographics**: Age, sex, relevant identifiers (anonymized)
2. **Chief Complaint**: Primary reason for visit/encounter
3. **History of Present Illness**: Key symptoms, timeline, progression, severity
4. **Past Medical History**: Relevant conditions, surgeries, hospitalizations
5. **Medications**: Current medications with doses if available
6. **Allergies**: Known drug/allergy reactions
7. **Physical Exam Findings**: Vital signs, relevant positive/negative findings
8. **Laboratory Results**: Key values with reference ranges, flag abnormalities
9. **Imaging Results**: Radiology findings, impressions
10. **Assessment & Plan**: Working diagnoses, differential, treatment plan, follow-up

Format as clear, structured JSON. For missing sections, include with "Not documented" value.
Be precise and clinical. Do not speculate beyond the document content."""


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
        model: str = "accounts/fireworks/models/kimi-k2p5"
    ):
        """
        Initialize the analyzer.
        
        Args:
            api_key: Fireworks API key (defaults to FIREWORKS_API_KEY env var)
            model: Fireworks model to use (default: kimi-k2p5 vision model)
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
            prompt: Custom analysis prompt (uses default medical prompt if None)
            dpi: PDF rendering resolution
            
        Returns:
            Dict with analysis results
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        page_images = self.pdf_pages_to_base64(pdf_path, dpi=dpi)
        
        return self._analyze_images(page_images, prompt or DEFAULT_MEDICAL_PROMPT)
    
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
            prompt: Custom analysis prompt (uses default medical prompt if None)
            dpi: PDF rendering resolution
            
        Returns:
            Dict with analysis results
        """
        page_images = self.pdf_bytes_to_base64(pdf_bytes, dpi=dpi)
        
        return self._analyze_images(page_images, prompt or DEFAULT_MEDICAL_PROMPT)
    
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
        
        # Try to parse as JSON if structured
        parsed_content = None
        try:
            parsed_content = json.loads(message_content)
        except json.JSONDecodeError:
            # If not JSON, keep as string
            pass
        
        return {
            "success": True,
            "content": parsed_content if parsed_content else message_content,
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
    model: str = "accounts/fireworks/models/kimi-k2p5",
    dpi: int = 200
) -> Dict[str, Any]:
    """
    Convenience function to analyze a medical PDF with Fireworks.
    
    Args:
        pdf_path: Path to PDF file
        api_key: Fireworks API key (uses env var if not provided)
        prompt: Custom prompt (uses default medical prompt if None)
        model: Fireworks model to use
        dpi: PDF rendering resolution
        
    Returns:
        Dict with analysis results
    """
    analyzer = FireworksMedicalAnalyzer(api_key=api_key, model=model)
    return analyzer.analyze_medical_document(
        pdf_path=pdf_path,
        prompt=prompt or DEFAULT_MEDICAL_PROMPT,
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