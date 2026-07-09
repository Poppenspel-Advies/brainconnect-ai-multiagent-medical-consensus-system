#!/usr/bin/env python3
"""
BrainConnect Local Test Script
Run this on YOUR machine with VPN connected.
"""
import os
import sys
import base64
import requests
import json

# ============================================================
# CONFIGURATION - CHANGE THESE IF NEEDED
# ============================================================
GEMINI_API_KEY = "AIzaSyBeC8PeH7wE03kATqO3QRqg-hiPozX6DIw"  # Your key
TEST_PDF = "test_patient_james_anderson.pdf"  # Must be in same folder
# ============================================================

def test_gemini_direct():
    """Test 1: Direct Gemini API call"""
    print("\n" + "="*60)
    print("TEST 1: Direct Gemini API")
    print("="*60)
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": "Reply with exactly: GEMINI WORKS"}]
        }]
    }
    
    try:
        r = requests.post(url, json=payload, timeout=30)
        if r.status_code == 200:
            result = r.json()
            text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            print(f"✅ PASS: {text.strip()}")
            return True
        else:
            print(f"❌ FAIL: HTTP {r.status_code}")
            print(f"   Response: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_gemini_vision():
    """Test 2: Gemini Vision with PDF"""
    print("\n" + "="*60)
    print("TEST 2: Gemini Vision (PDF -> Images)")
    print("="*60)
    
    if not os.path.exists(TEST_PDF):
        print(f"⚠️  SKIP: {TEST_PDF} not found")
        return False
    
    try:
        import fitz  # PyMuPDF
        
        # Convert first page to base64
        doc = fitz.open(TEST_PDF)
        page = doc[0]
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        doc.close()
        
        print(f"   PDF pages: {len(doc)}")
        print(f"   Image size: {len(img_bytes)} bytes")
        
        # Call Gemini Vision
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": "Extract patient name, chief complaint, and key diagnosis from this medical document. Be concise."},
                    {"inline_data": {"mime_type": "image/png", "data": img_b64}}
                ]
            }]
        }
        
        r = requests.post(url, json=payload, timeout=60)
        
        if r.status_code == 200:
            result = r.json()
            text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            print(f"✅ PASS: Vision response ({len(text)} chars)")
            print(f"   Preview: {text[:200]}...")
            return True
        else:
            print(f"❌ FAIL: HTTP {r.status_code}")
            print(f"   Response: {r.text[:300]}")
            return False
            
    except ImportError:
        print("⚠️  SKIP: PyMuPDF not installed (pip install pymupdf)")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_backend_health():
    """Test 3: Backend API (if running locally)"""
    print("\n" + "="*60)
    print("TEST 3: Backend Health (http://localhost:8000)")
    print("="*60)
    
    try:
        r = requests.get("http://localhost:8000/health", timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(f"✅ PASS: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ FAIL: HTTP {r.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️  SKIP: Backend not running (start with: cd backend && python api.py)")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_full_pipeline():
    """Test 4: Full upload pipeline"""
    print("\n" + "="*60)
    print("TEST 4: Full Upload Pipeline (Backend)")
    print("="*60)
    
    if not os.path.exists(TEST_PDF):
        print(f"⚠️  SKIP: {TEST_PDF} not found")
        return False
    
    try:
        with open(TEST_PDF, "rb") as f:
            files = {"file": (TEST_PDF, f, "application/pdf")}
            data = {"model": "gemini-1.5-flash"}
            
            r = requests.post(
                "http://localhost:8000/api/analyze-medical-document",
                files=files,
                data=data,
                timeout=120
            )
        
        if r.status_code == 200:
            result = r.json()
            if result.get("success"):
                content = result.get("content", "")
                print(f"✅ PASS: Full pipeline works!")
                print(f"   Model: {result.get('model')}")
                print(f"   Pages: {result.get('pages_processed')}")
                print(f"   Tokens: {result.get('usage', {}).get('total_tokens')}")
                print(f"   Preview: {content[:300]}...")
                return True
            else:
                print(f"❌ FAIL: {result.get('error')}")
                return False
        else:
            print(f"❌ FAIL: HTTP {r.status_code}")
            print(f"   Response: {r.text[:300]}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("\n" + "🔬"*30)
    print("  BrainConnect Local Test Suite")
    print("  Run with VPN ON")
    print("🔬"*30)
    
    results = []
    
    # Run tests
    results.append(("Gemini Direct", test_gemini_direct()))
    results.append(("Gemini Vision", test_gemini_vision()))
    results.append(("Backend Health", test_backend_health()))
    results.append(("Full Pipeline", test_full_pipeline()))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL/SKIP"
        print(f"  {name}: {status}")
    
    passed_count = sum(1 for _, p in results if p)
    print(f"\n  Total: {passed_count}/{len(results)} tests passed")
    
    if passed_count >= 2:
        print("\n🎉 Core API works! Ready for hackathon demo.")
    else:
        print("\n⚠️  Check VPN / API key / backend status")
    
    sys.exit(0 if passed_count >= 2 else 1)