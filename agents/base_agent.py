"""
Base Agent Class for CodeCrew
Provides foundation for all specialized code review agents
"""

from typing import Dict, List, Optional
from langchain_community.llms import Ollama
import re


class BaseAgent:
    """Base class for all CodeCrew agents"""
    
    def __init__(self, name: str, role: str, icon: str, color: str, model: str = "llama3.1"):
        self.name = name
        self.role = role
        self.icon = icon
        self.color = color
        self.llm = Ollama(model=model, temperature=0.1)
        self.findings: List[Dict] = []
    
    def analyze(self, code: str, language: str) -> List[Dict]:
        """
        Analyze code and return findings
        To be implemented by child classes
        """
        raise NotImplementedError("Subclasses must implement analyze()")
    
    def _parse_response(self, response: str) -> List[Dict]:
        """
        Parse LLM response into structured findings
        Expected format:
        SEVERITY: CRITICAL
        LINE: 23
        ISSUE: SQL injection vulnerability
        DETAIL: User input directly concatenated into SQL query...
        ---
        """
        findings = []
        
        if "NO_ISSUES_FOUND" in response.upper():
            return findings
        
        # Split by separator
        blocks = response.split('---')
        
        for block in blocks:
            block = block.strip()
            if not block:
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
