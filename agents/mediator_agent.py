"""
Mediator Agent - Synthesizes all findings and creates prioritized recommendations
"""

from .base_agent import BaseAgent
from typing import Dict, List


class MediatorAgent(BaseAgent):
    """Agent that synthesizes findings from all other agents"""
    
    def __init__(self, model: str = "mistralai/Mistral-7B-Instruct-v0.2"):
        super().__init__(
            name="Mediator Agent",
            role="Synthesize findings and prioritize actions",
            icon="🎯",
            color="#0891b2",
            model=model
        )
    
    def synthesize(self, all_findings: Dict[str, List[Dict]]) -> Dict:
        """
        Synthesize all agent findings into a prioritized action plan
        """
        # Combine all findings
        combined = []
        total_by_agent = {}
        
        for agent_name, findings in all_findings.items():
            total_by_agent[agent_name] = len(findings)
            for finding in findings:
                combined.append(finding)
        
        # If no findings, return early
        if not combined:
            return {
                'all_findings': [],
                'summary': "Excellent! No issues found. The code looks good!",
                'total_issues': 0,
                'by_severity': {},
                'by_agent': total_by_agent,
                'priority_1': [],
                'priority_2': [],
                'priority_3': []
            }
        
        # Sort by severity
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        combined.sort(key=lambda x: severity_order.get(x.get('severity', 'LOW'), 99))
        
        # Count by severity
        by_severity = {}
        for finding in combined:
            severity = finding.get('severity', 'UNKNOWN')
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        # Categorize into priorities
        priority_1 = [f for f in combined if f.get('severity') in ['CRITICAL', 'HIGH']]
        priority_2 = [f for f in combined if f.get('severity') == 'MEDIUM']
        priority_3 = [f for f in combined if f.get('severity') == 'LOW']
        
        # Generate summary
        summary = self._generate_summary(combined, by_severity, priority_1, priority_2, priority_3)
        
        return {
            'all_findings': combined,
            'summary': summary,
            'total_issues': len(combined),
            'by_severity': by_severity,
            'by_agent': total_by_agent,
            'priority_1': priority_1,
            'priority_2': priority_2,
            'priority_3': priority_3
        }
    
    def _generate_summary(self, combined: List[Dict], by_severity: Dict, 
                         priority_1: List, priority_2: List, priority_3: List) -> str:
        """Generate a natural language summary"""
        
        # Format findings for LLM
        findings_text = ""
        for i, finding in enumerate(combined[:10], 1):
            findings_text += f"{i}. [{finding.get('severity', 'N/A')}] {finding.get('agent', 'Unknown')}: {finding.get('issue', 'No description')}\n"
        
        prompt = f"""You are a senior engineering lead synthesizing code review feedback.

FINDINGS SUMMARY:
- Total Issues: {len(combined)}
- Critical: {by_severity.get('CRITICAL', 0)}
- High: {by_severity.get('HIGH', 0)}
- Medium: {by_severity.get('MEDIUM', 0)}
- Low: {by_severity.get('LOW', 0)}

TOP FINDINGS:
{findings_text}

Create a concise summary (max 100 words):
1. Overall Assessment: One sentence on code health
2. Immediate Action: Top must-fix items if Critical/High exist
3. Important Improvements: Key quality improvements if Medium exist

Be professional, specific, and encouraging.

Summary:"""

        try:
            summary = self._call_llm(prompt)
            if summary and len(summary) > 20:
                return summary.strip()
            else:
                return self._create_fallback_summary(by_severity, len(combined))
        except Exception as e:
            print(f"Mediator Agent Error: {e}")
            return self._create_fallback_summary(by_severity, len(combined))
    
    def _create_fallback_summary(self, by_severity: Dict, total: int) -> str:
        """Create a simple fallback summary if LLM fails"""
        critical = by_severity.get('CRITICAL', 0)
        high = by_severity.get('HIGH', 0)
        medium = by_severity.get('MEDIUM', 0)
        
        if critical > 0:
            return f"Found {total} issues including {critical} critical security or performance problems that need immediate attention. Address these before deployment."
        elif high > 0:
            return f"Found {total} issues including {high} high-priority items that should be addressed soon to improve code quality and security."
        elif medium > 0:
            return f"Found {total} issues, mostly medium severity. Consider addressing these to improve code quality and maintainability."
        else:
            return f"Found {total} minor issues. These are optional improvements that could enhance code quality."
