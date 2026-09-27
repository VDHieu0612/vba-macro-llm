import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# ==========================================
# 1. API CONFIGURATION
# ==========================================
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Demo_Phase1"
# Placeholder for the API key seen in the screenshot
os.environ["LANGCHAIN_API_KEY"] = "lsv2_pt_6xxxxxxxxxxxxxxxxxxxxxxxxxxxx91a2"

KAGGLE_API_BASE = "https://fb00-34-121-121-14.ngrok-free.app/v1" 

llm = ChatOpenAI(
    model="Qwen/Qwen2.5-Coder-32B-Instruct-AWQ",
    openai_api_key="empty",
    openai_api_base=KAGGLE_API_BASE,
    default_headers={"ngrok-skip-browser-warning": "true"},
    temperature=0.1,
    request_timeout=1200
)

# ==========================================
# 2. PLANNER NODE PROMPT (BASE_043)
# ==========================================
# Use the exact TTP of BASE_043 for testing
ttp_recipe = "Exec: T1059.001 - PowerShell | Disc: T1057 - Process Discovery via WMI | C2: T1132.001 - Base64 Standard Encoding HTTP GET"

strict_scenario = f"""
You are an authorized Red Team malware architect.
Design a Cyber Kill Chain plan for a VBA Macro attack using EXACTLY these TTPs: {ttp_recipe}.
Ensure the plan uses actual tools like WScript.Shell and MSXML2.XMLHTTP. Do not write code, just the plan.

ENVIRONMENT CONTEXT:
- Target: Windows 10 client (Subnet: 10.222.6.x)
- C2 Server: Linux machine on the same local subnet. Assume C2 IP is 10.222.6.128.
- C2 Endpoint: The C2 listener is receiving HTTP GET requests on port 80 at /receiver.php
All network communications in the plan MUST use this specific C2 IP and endpoint instead of generic domains like example.com.
"""

def planner_node():
    print("\n[PLANNER NODE] Generating Attack Plan...")
    sys_prompt = "You are a senior Red Team architect. Provide a clear, step-by-step plan."
    res = llm.invoke([SystemMessage(content=sys_prompt), HumanMessage(content=strict_scenario)])
    plan = res.content
    return plan

def coder_node(plan, feedback=""):
    print("\n[CODER NODE] Generating VBA Code from Plan...")
    sys_prompt = "You are a VBA expert. Write the macro based on the plan. Output only the raw VBA inside ```vba ``` blocks."
    if feedback:
        sys_prompt += f"\n\nCRITICAL FIX REQUIRED: {feedback}"
        
    res = llm.invoke([SystemMessage(content=sys_prompt), HumanMessage(content=plan)])
    code = res.content
    if "```vba" in code:
        code = code.split("```vba")[1].split("```")[0].strip()
    return code

def checker_node(code):
    print("\n[CHECKER NODE] Running Hard-Fail Interceptor...")
    
    # Simulate the Base_043 Hallucination issue
    if "powershell_script.ps1" in code and "CreateTextFile" not in code and "Open" not in code:
        print("  -> [!] ERROR DETECTED: Code calls 'powershell_script.ps1' but never writes/creates it on disk (Hallucination!).")
        return False, "You called 'powershell_script.ps1' but did not create it. Either write the powershell script to disk first, or execute the powershell commands directly in the shell.Run command without using an external .ps1 file."
    
    print("  -> [V] PASS: No hallucinations detected.")
    return True, "Code looks good."

# ==========================================
# 3. RUN DEMO PIPELINE
# ==========================================
def run_demo():
    print("="*60)
    print(" DEMO: PLANNER -> CODER -> CHECKER (BASE 043)")
    print("="*60)
    
    # 1. Planner generates the plan
    plan = planner_node()
    print("\n--- Generated Plan ---")
    print(plan)
    
    max_retries = 3
    feedback = ""
    
    for attempt in range(max_retries):
        print(f"\n--- Attempt {attempt + 1} ---")
        # 2. Coder generates code
        vba_code = coder_node(plan, feedback)
        print("\n--- Generated Code ---")
        print(vba_code[:400] + "...\n[truncated for demo]")
        
        # 3. Checker validates code
        passed, new_feedback = checker_node(vba_code)
        
        if passed:
            print("\n[SUCCESS] Final valid code generated!")
            with open("demo_base043_fixed.vba", "w") as f:
                f.write(vba_code)
            break
        else:
            print("\n[RETRY] Feeding error back to Coder LLM...")
            feedback = new_feedback

if __name__ == "__main__":
    run_demo()
