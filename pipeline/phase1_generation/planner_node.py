"""
PLANNER Node - Phase 1 of VBA Macro Generation Pipeline
NT230.Q22.ANTT | Võ Duy Hiếu

Generates a Cyber Kill Chain plan based on MITRE ATT&CK TTP combo.
Temperature: 0.7 (creative planning)
"""

import json
from typing import Dict


PLANNER_PROMPT = """You are a cybersecurity researcher analyzing malware behavior patterns.
Given the following MITRE ATT&CK techniques, generate a Cyber Kill Chain execution plan
for a VBA macro that demonstrates these behaviors in an isolated lab environment.

Techniques:
- Execution: {execution_ttp} ({execution_desc})
- Discovery: {discovery_ttp} ({discovery_desc})
- C2/Exfil: {c2_ttp} ({c2_desc})

Generate a step-by-step technical plan. Be specific about VBA API calls and Windows APIs.
Output as JSON with keys: steps[], vba_apis[], windows_apis[], risk_level.
"""


def run_planner(ttp_combo: Dict, llm_client) -> Dict:
    """
    Runs the PLANNER node to generate a kill chain plan.
    
    Args:
        ttp_combo: Dict with execution, discovery, c2 TTP details
        llm_client: Initialized LLM client (Qwen-32B)
    
    Returns:
        Dict: Kill chain plan with steps and API lists
    """
    prompt = PLANNER_PROMPT.format(**ttp_combo)
    
    response = llm_client.chat(
        model="qwen-32b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1024
    )
    
    plan = json.loads(response.choices[0].message.content)
    return plan


if __name__ == "__main__":
    # Example TTP combo
    sample_ttp = {
        "execution_ttp": "T1059.001",
        "execution_desc": "PowerShell - bypass ExecutionPolicy, hidden window",
        "discovery_ttp": "T1082",
        "discovery_desc": "System Information Discovery",
        "c2_ttp": "T1071.001",
        "c2_desc": "Web Protocol C2 over HTTP"
    }
    print("PLANNER Node - Sample TTP:", sample_ttp["execution_ttp"])
