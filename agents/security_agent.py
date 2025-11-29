"""
Security Agent - Identifies security vulnerabilities and risks
"""

from .base_agent import BaseAgent


class SecurityAgent(BaseAgent):
    """Agent specialized in identifying security vulnerabilities"""
    
    def __init__(self, model: str = "mistralai/Mistral-7B-Instruct-v0.2"):
        super().__init__(
            name="Security Agent",
            role="Identify security vulnerabilities and risks",
            icon="🛡️",
            color="#dc2626",
            model=model
        )
    
    def analyze(self, code: str, language: str) -> list:
        """Analyze code for security vulnerabilities"""
        
        prompt = f"""You are an expert security analyst reviewing {language} code for vulnerabilities.

Your job is to identify security issues including:
- SQL injection vulnerabilities
- Cross-Site Scripting (XSS) risks
- Hardcoded credentials or API keys
- Missing input validation
- Path traversal vulnerabilities
- Insecure deserialization
- Authentication/authorization issues
- Cryptographic weaknesses
- Command injection risks

Code to review:
```{language}
{code[:1500]}
```

INSTRUCTIONS:
1. Analyze the code thoroughly for security vulnerabilities
2. For EACH issue found, respond in this EXACT format:

SEVERITY: [CRITICAL/HIGH/MEDIUM/LOW]
LINE: [line number where issue appears]
ISSUE: [one-line summary of the vulnerability]
DETAIL: [explanation of the risk and how to fix it]
---

3. Separate each finding with "---"
4. If NO security issues are found, respond ONLY with: "NO_ISSUES_FOUND"

CRITICAL: Code execution, SQL injection, authentication bypass
HIGH: Data exposure, XSS, missing validation on sensitive operations
MEDIUM: Weak encryption, information disclosure
LOW: Missing security headers, verbose error messages

Begin analysis:"""

        try:
            response = self._call_llm(prompt)
            findings = self._parse_response(response)
            self.findings = findings
            return findings
        except Exception as e:
            print(f"Security Agent Error: {e}")
            return []
