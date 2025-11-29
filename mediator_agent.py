"""
Mediator Agent - Synthesizes all findings and creates prioritized recommendations
"""

from .base_agent import BaseAgent
from typing import Dict, List


class MediatorAgent(BaseAgent):
    """Agent that synthesizes findings from all other agents"""
    
    def __init__(self, model: str = "llama3.1"):
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
        
        Args:
            all_findings: Dictionary mapping agent names to their findings
            
        Returns:
            Dictionary containing synthesized report
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
        
        # Generate natural language summary
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
        """Generate a natural language summary using LLM"""
        
        # Format findings for LLM
        findings_text = ""
        for i, finding in enumerate(combined[:15], 1):  # Limit to top 15 for token efficiency
            findings_text += f"{i}. [{finding.get('severity', 'N/A')}] {finding.get('agent', 'Unknown')}: {finding.get('issue', 'No description')} (Line {finding.get('line', 'N/A')})\n"
        
        prompt = f"""You are a senior engineering lead synthesizing code review feedback from multiple specialized agents.

FINDINGS SUMMARY:
- Total Issues: {len(combined)}
- Critical: {by_severity.get('CRITICAL', 0)}
- High: {by_severity.get('HIGH', 0)}
- Medium: {by_severity.get('MEDIUM', 0)}
- Low: {by_severity.get('LOW', 0)}

TOP FINDINGS:
{findings_text}

Your task:
Create a concise, actionable summary for the developer. Structure it as:

1. **Overall Assessment**: One sentence on code health
2. **Immediate Action Required** (if any Critical/High): Top 2-3 must-fix items
3. **Important Improvements** (if any Medium): Key quality improvements
4. **Nice to Have** (if any Low): Optional enhancements

Keep it:
- Professional but friendly
- Specific and actionable
- Concise (max 150 words)
- Encouraging where appropriate

Write the summary:"""

        try:
            summary = self.llm.invoke(prompt)
            return summary.strip()
        except Exception as e:
            print(f"Mediator Agent Error: {e}")
            # Fallback summary
            return self._create_fallback_summary(by_severity, len(combined))
    
    def _create_fallback_summary(self, by_severity: Dict, total: int) -> str:
        """Create a simple fallback summary if LLM fails"""
        critical = by_severity.get('CRITICAL', 0)
        high = by_severity.get('HIGH', 0)
        
        if critical > 0:
            return f"Found {total} issues including {critical} critical security or performance problems that need immediate attention."
        elif high > 0:
            return f"Found {total} issues including {high} high-priority items that should be addressed soon."
        else:
            return f"Found {total} minor issues. Consider addressing these to improve code quality."
