"""
Style Agent - Ensures code quality, readability, and best practices
"""

from .base_agent import BaseAgent


class StyleAgent(BaseAgent):
    """Agent specialized in code quality and style"""
    
    def __init__(self, model: str = "mistralai/Mistral-7B-Instruct-v0.2"):
        super().__init__(
            name="Style Agent",
            role="Ensure code quality and best practices",
            icon="✨",
            color="#7c3aed",
            model=model
        )
    
    def analyze(self, code: str, language: str) -> list:
        """Analyze code for style and quality issues"""
        
        prompt = f"""You are an expert code quality reviewer analyzing {language} code for style and best practices.

Your job is to identify quality issues including:
- Naming conventions (variables, functions, classes)
- Function/method length (>50 lines is typically too long)
- Code duplication (DRY principle violations)
- Missing or inadequate documentation
- Design pattern opportunities
- Language-specific idioms and conventions
- Code readability and clarity
- Single Responsibility Principle violations
- Magic numbers or hardcoded values

Code to review:
```{language}
{code[:1500]}
```

INSTRUCTIONS:
1. Review the code for style, quality, and best practice violations
2. For EACH issue found, respond in this EXACT format:

SEVERITY: [HIGH/MEDIUM/LOW]
LINE: [line number where issue appears]
ISSUE: [one-line summary of the quality issue]
DETAIL: [explanation and improvement suggestion]
---

3. Separate each finding with "---"
4. If NO style issues are found, respond ONLY with: "NO_ISSUES_FOUND"

HIGH: Severe readability issues, major principle violations
MEDIUM: Naming problems, documentation gaps
LOW: Formatting inconsistencies, minor style preferences

Focus on impactful improvements, not nitpicks.

Begin analysis:"""

        try:
            response = self._call_llm(prompt)
            findings = self._parse_response(response)
            self.findings = findings
            return findings
        except Exception as e:
            print(f"Style Agent Error: {e}")
            return []
