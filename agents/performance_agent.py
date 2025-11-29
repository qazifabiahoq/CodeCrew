"""
Performance Agent - Analyzes code efficiency and optimization opportunities
"""

from .base_agent import BaseAgent


class PerformanceAgent(BaseAgent):
    """Agent specialized in performance analysis and optimization"""
    
    def __init__(self, model: str = "mistralai/Mistral-7B-Instruct-v0.2"):
        super().__init__(
            name="Performance Agent",
            role="Analyze performance and optimization opportunities",
            icon="⚡",
            color="#ea580c",
            model=model
        )
    
    def analyze(self, code: str, language: str) -> list:
        """Analyze code for performance issues"""
        
        prompt = f"""You are an expert performance engineer reviewing {language} code for optimization opportunities.

Your job is to identify performance issues including:
- Time complexity problems (O(n²), O(n³), nested loops)
- Space complexity inefficiencies
- Redundant computations or operations
- Inefficient data structures
- Database query optimization opportunities
- Missing caching opportunities
- Unnecessary object creation
- String concatenation in loops

Code to review:
```{language}
{code[:1500]}
```

INSTRUCTIONS:
1. Analyze the code for performance bottlenecks and inefficiencies
2. For EACH issue found, respond in this EXACT format:

SEVERITY: [CRITICAL/HIGH/MEDIUM/LOW]
LINE: [line number where issue appears]
ISSUE: [one-line summary of the performance problem]
DETAIL: [explanation with complexity analysis and optimization suggestion]
---

3. Separate each finding with "---"
4. If NO performance issues are found, respond ONLY with: "NO_ISSUES_FOUND"

CRITICAL: O(n²) or worse in production loops, memory leaks
HIGH: O(n log n) opportunities, significant redundant operations
MEDIUM: Unnecessary computations, suboptimal data structures
LOW: Micro-optimizations

Include Big-O notation where relevant.

Begin analysis:"""

        try:
            response = self._call_llm(prompt)
            findings = self._parse_response(response)
            self.findings = findings
            return findings
        except Exception as e:
            print(f"Performance Agent Error: {e}")
            return []
