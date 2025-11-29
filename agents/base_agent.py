"""
Base Agent Class for CodeCrew
Provides foundation for all specialized code review agents
"""

from typing import Dict, List
import re
import requests
import time


class BaseAgent:
    """Base class for all CodeCrew agents"""
    
    def __init__(self, name: str, role: str, icon: str, color: str, model: str = "mistralai/Mistral-7B-Instruct-v0.2"):
        self.name = name
        self.role = role
        self.icon = icon
        self.color = color
        self.model = model
        self.api_url = f"https://api-inference.huggingface.co/models/{model}"
        self.findings: List[Dict] = []
    
    def _call_llm(self, prompt: str, max_retries: int = 3) -> str:
        """Call Hugging Face Inference API"""
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1000,
                "temperature": 0.1,
                "return_full_text": False
            }
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=45)
                
                print(f"[{self.name}] Attempt {attempt + 1}: Status {response.status_code}")
                
                if response.status_code == 503:
                    # Model is loading, wait and retry
                    error_msg = f"{self.name}: Model loading, waiting 10 seconds..."
                    print(error_msg)
                    time.sleep(10)
                    continue
                
                if response.status_code == 429:
                    # Rate limited
                    error_msg = f"{self.name}: Rate limited by Hugging Face API"
                    print(error_msg)
                    return f"ERROR: Rate limited. Please try again in a few minutes."
                    
                if response.status_code == 200:
                    result = response.json()
                    print(f"[{self.name}] Response received: {str(result)[:100]}...")
                    if isinstance(result, list) and len(result) > 0:
                        text = result[0].get('generated_text', '')
                        if text:
                            return text
                        else:
                            print(f"[{self.name}] Empty generated_text in response")
                    return ''
                else:
                    error_msg = f"{self.name} API Error {response.status_code}: {response.text[:200]}"
                    print(error_msg)
                    if attempt == max_retries - 1:
                        return f"ERROR: API returned {response.status_code}"
                    
            except requests.exceptions.Timeout:
                print(f"{self.name}: Request timeout on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                return "ERROR: Request timeout"
            except Exception as e:
                error_msg = f"{self.name} Error: {type(e).__name__}: {str(e)}"
                print(error_msg)
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                return f"ERROR: {str(e)}"
        
        return "ERROR: All retries failed"
    
    def analyze(self, code: str, language: str) -> List[Dict]:
        """
        Analyze code and return findings
        To be implemented by child classes
        """
        raise NotImplementedError("Subclasses must implement analyze()")
    
    def _parse_response(self, response: str) -> List[Dict]:
        """
        Parse LLM response into structured findings
        """
        findings = []
        
        if not response or "NO_ISSUES_FOUND" in response.upper():
            return findings
        
        # Split by separator
        blocks = response.split('---')
        
        for block in blocks:
            block = block.strip()
            if not block or len(block) < 20:
                continue
            
            finding = {}
            
            # Extract SEVERITY
            severity_match = re.search(r'SEVERITY:\s*(CRITICAL|HIGH|MEDIUM|LOW)', block, re.IGNORECASE)
            if severity_match:
                finding['severity'] = severity_match.group(1).upper()
            
            # Extract LINE
            line_match = re.search(r'LINE:\s*(\d+)', block, re.IGNORECASE)
            if line_match:
                finding['line'] = int(line_match.group(1))
            else:
                finding['line'] = None
            
            # Extract ISSUE
            issue_match = re.search(r'ISSUE:\s*(.+?)(?=DETAIL:|$)', block, re.IGNORECASE | re.DOTALL)
            if issue_match:
                finding['issue'] = issue_match.group(1).strip()
            
            # Extract DETAIL
            detail_match = re.search(r'DETAIL:\s*(.+?)$', block, re.IGNORECASE | re.DOTALL)
            if detail_match:
                finding['detail'] = detail_match.group(1).strip()
            
            # Only add if we have at least severity and issue
            if 'severity' in finding and 'issue' in finding:
                finding['agent'] = self.name
                finding['icon'] = self.icon
                finding['color'] = self.color
                findings.append(finding)
        
        return findings
    
    def get_status_message(self, status: str = "analyzing") -> str:
        """Generate status message for UI"""
        status_messages = {
            "analyzing": f"{self.icon} {self.name} analyzing...",
            "complete": f"{self.icon} {self.name} ✓ Complete",
            "error": f"{self.icon} {self.name} ✗ Error"
        }
        return status_messages.get(status, f"{self.icon} {self.name}")
