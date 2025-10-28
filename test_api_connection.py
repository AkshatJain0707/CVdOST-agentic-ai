#!/usr/bin/env python3
"""
Quick API connection test - verify backend is working
Run this AFTER starting the backend server
"""

import requests
import json
import time

API_URL = "http://localhost:8000/api/analyze"
HEALTH_URL = "http://localhost:8000/api/health"

print("=" * 60)
print("🧪 Resumate API Connection Test")
print("=" * 60)

# Test 1: Health check
print("\n1️⃣  Testing health endpoint...")
try:
    response = requests.get(HEALTH_URL, timeout=5)
    if response.status_code == 200:
        print("   ✅ Health check: OK")
        print(f"   Response: {response.json()}")
    else:
        print(f"   ❌ Health check failed: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("   ❌ Cannot connect to backend!")
    print("   Make sure backend is running:")
    print("      uvicorn backend.main:app --reload")
    exit(1)

# Test 2: Test with sample data
print("\n2️⃣  Testing analysis endpoint...")

sample_resume = """
JOHN DOE
john@example.com | 555-1234

EXPERIENCE
Senior Software Engineer at TechCorp (2020-2023)
- Led team of 5 engineers
- Improved API performance by 40%
- Developed microservices architecture

SKILLS
Python, JavaScript, AWS, Docker, PostgreSQL
"""

sample_jd = """
Senior Software Engineer - TechCorp

Requirements:
- 5+ years of software development experience
- Proficiency in Python and JavaScript
- Experience with AWS and Docker
- Leadership experience preferred

Responsibilities:
- Design and implement scalable systems
- Lead technical initiatives
- Mentor junior developers
"""

# Create test file
import tempfile
import os

with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
    f.write(sample_resume)
    resume_path = f.name

try:
    with open(resume_path, 'rb') as resume_file:
        files = {'resume_file': resume_file}
        data = {
            'job_description': sample_jd,
            'target_role': 'Senior Software Engineer'
        }
        
        print("   Sending request...")
        start = time.time()
        response = requests.post(API_URL, files=files, data=data, timeout=120)
        elapsed = time.time() - start
        
        print(f"   Response time: {elapsed:.2f}s")
        print(f"   Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n   ✅ Analysis successful!")
            
            # Display summary
            print("\n   📊 Results Summary:")
            if result.get('status') == 'success':
                ats_score = result.get('ats', {}).get('ats', {}).get('final_score', 'N/A')
                print(f"      ATS Score: {ats_score}%")
                
                suggestions = result.get('ats', {}).get('ats', {}).get('suggestions', [])
                if suggestions:
                    print(f"      Suggestions: {len(suggestions)} recommendations")
                    for i, s in enumerate(suggestions[:3], 1):
                        print(f"         {i}. {s[:60]}...")
            else:
                print(f"      Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"\n   ❌ Analysis failed!")
            print(f"   Error: {response.text}")
            
finally:
    os.unlink(resume_path)

print("\n" + "=" * 60)
print("✅ Tests complete!")
print("=" * 60)
print("\nNext steps:")
print("  1. Open Streamlit UI: streamlit run frontend.py")
print("  2. Go to Dashboard Overview")
print("  3. Upload resume and paste job description")
print("  4. Click 'Analyze Resume'")