"""
Utility functions for parsing and formatting
"""

def count_lines(code: str) -> int:
    """Count number of lines in code"""
    return len(code.strip().split('\n'))


def get_severity_color(severity: str) -> str:
    """Get color for severity level"""
    colors = {
        'CRITICAL': '#dc2626',
        'HIGH': '#ea580c',
        'MEDIUM': '#eab308',
        'LOW': '#3b82f6'
    }
    return colors.get(severity.upper(), '#6b7280')


def format_finding_html(finding: dict) -> str:
    """Format a finding as HTML"""
    color = get_severity_color(finding.get('severity', 'LOW'))
    line = finding.get('line', 'N/A')
    severity = finding.get('severity', 'UNKNOWN')
    issue = finding.get('issue', 'No description')
    detail = finding.get('detail', '')
    
    return f"""
    <div style="border-left: 4px solid {color}; padding: 12px; margin-bottom: 16px; background-color: #f8fafc; border-radius: 4px;">
        <p style="margin: 0; font-weight: 700; color: {color}; font-size: 13px;">
            [{severity}] Line {line}
        </p>
        <p style="margin: 8px 0 4px 0; color: #1e293b; font-weight: 600; font-size: 15px;">
            {issue}
        </p>
        <p style="margin: 0; color: #475569; font-size: 14px; line-height: 1.5;">
            {detail}
        </p>
    </div>
    """
