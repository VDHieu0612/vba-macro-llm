import os
import csv
import time
import argparse
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# ==========================================
# COMMAND LINE ARGUMENTS
# ==========================================
parser = argparse.ArgumentParser(description="LLMalMorph Phase 2: Obfuscation Evasions Only")
parser.add_argument("--input", default="Validated_Bases.csv", help="Input CSV file containing clean bases")
parser.add_argument("--output", default="LLMalMorph_Obfuscated_Dataset.csv", help="Output filename")
args = parser.parse_args()

# ==========================================
# 0. LANGSMITH CONFIGURATION (OBSERVABILITY)
# ==========================================
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "YOUR_LANGSMITH_API_KEY_HERE")
os.environ["LANGCHAIN_PROJECT"] = "Phase2_Obfuscation"

# ==========================================
# 1. API CONFIGURATION
# ==========================================
KAGGLE_API_BASE = "https://fb00-34-121-121-14.ngrok-free.app/v1" 

coder_llm = ChatOpenAI(
    model="Qwen/Qwen2.5-Coder-32B-Instruct-AWQ",
    openai_api_key="empty",
    openai_api_base=KAGGLE_API_BASE,
    default_headers={"ngrok-skip-browser-warning": "true"},
    temperature=0.1,
    request_timeout=1200,
    max_retries=2
)

# ==========================================
# 2. OBFUSCATION STRATEGIES (BASED ON THREAT INTEL)
# ==========================================
obfuscation_strategies = [
    "Obfuscation - Random Renaming: Rename ONLY user-defined variables and custom function names (except Document_Open/AutoOpen) to short, meaningless alphanumeric strings (EXACTLY 5 to 8 characters long, e.g., xK9pQ). CRITICAL: Do NOT rename built-in VBA keywords, objects, or methods (e.g., CreateObject, Chr, Replace). Preserve all original line breaks to prevent compiler crashes.",
    "Obfuscation - String Concatenation: Break down critical strings (URLs, IPs, Commands, Object Names) into very small chunks and join them using the '&' operator (e.g., 'WSc' & 'ript').",
    "Obfuscation - ASCII Encoding: Replace characters in sensitive strings with Chr(). CRITICAL: VBA has a 1024 character limit per line and cannot handle too many '&' operators at once. You MUST split the encoded string across multiple lines using string building variables (e.g., strCmd = Chr(112) & Chr(111) \n strCmd = strCmd & Chr(119)...).",
]

def morph_malware(base_code: str, strategy: str) -> str:
    print(f"   -> Applying Obfuscation: {strategy.split(':')[0]}...")
    sys_prompt = f"""You are an Expert Malware Obfuscator. Apply this specific obfuscation technique to the provided VBA code: {strategy}
    
    CRITICAL CONSTRAINTS:
    1. DO NOT change the core functionality of the code. The execution, discovery, and C2 must still work.
    2. DO NOT change the entry point names (Document_Open or AutoOpen).
    3. Return ONLY the raw, obfuscated VBA code inside a ```vba ``` block without any conversational text or explanations.
    4. Focus heavily on the requested obfuscation technique. If it asks for Chr(), use it extensively on the payloads."""
    
    res = coder_llm.invoke([SystemMessage(content=sys_prompt), HumanMessage(content=base_code)])
    code = res.content
    if "```vba" in code:
        code = code.split("```vba")[1].split("```")[0].strip()
    return code

# ==========================================
# 3. PHASE 2 RUNNER
# ==========================================
def generate_evasions():
    input_file = args.input
    output_file = args.output
    
    if not os.path.exists(input_file):
        print(f"[ERROR] Input file '{input_file}' not found. Please check the filename.")
        return

    # Resume capabilities for evasion variants
    completed_variants = set()
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                completed_variants.add(f"{row['Combo_ID']}_{row['Evasion_Strategy']}")

    with open(input_file, 'r', encoding='utf-8') as fin, \
         open(output_file, 'a', newline='', encoding='utf-8') as fout:
        
        reader = csv.DictReader(fin)
        fieldnames = reader.fieldnames + ['Evasion_Strategy', 'Morphed_VBA_Code']
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        
        if os.stat(output_file).st_size == 0:
            writer.writeheader()

        for row in reader:
            combo_id = row['Combo_ID']
            base_code = row['Base_VBA_Code']
            
            print(f"\n[PHASE 2] Obfuscating Variants for: {combo_id}")
            
            for strat in obfuscation_strategies:
                strat_name = strat.split(':')[0]
                unique_key = f"{combo_id}_{strat_name}"
                
                # Skip previously generated variants
                if unique_key in completed_variants:
                    continue
                
                try:
                    morphed_code = morph_malware(base_code, strat)
                    
                    # Log the output row
                    out_row = row.copy()
                    out_row['Evasion_Strategy'] = strat_name
                    out_row['Morphed_VBA_Code'] = morphed_code
                    writer.writerow(out_row)
                    fout.flush()
                    
                    time.sleep(3)
                except Exception as e:
                    print(f"[ERROR] Morphing process failed for {strat_name}: {e}")

if __name__ == "__main__":
    print("Initializing Phase 2: Advanced Obfuscation Pipeline...")
    generate_evasions()

