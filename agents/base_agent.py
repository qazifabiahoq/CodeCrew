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
                
                if response.status_code == 503:
                    # Model is loading, wait and retry
                    print(f"{self.name}: Model loading, waiting...")
                    time.sleep(10)
                    continue
                    
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        return result[0].get('generated_text', '')
                    return ''
                else:
                    print(f"{self.name} API Error: {response.status_code}")
                    return ''
                    
            except Exception as e:
                print(f"{self.name} Error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                return ''
        
        return ''
    
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
