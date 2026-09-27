import os
import csv
import time
import shutil
import requests
import sys
import re
import win32com.client
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

# ==========================================
# 0. CONFIGURATION
# ==========================================
KAGGLE_API_BASE = "https://fb00-34-121-121-14.ngrok-free.app/v1"  # UPDATE THIS EACH SESSION
VT_API_KEY      = "1011f530ade0961b2cd334a6aa9c9739e655a5828155104b1cbc7cb1e22a9dfa"                                                # YOUR VirusTotal API Key
TEMPLATE_DOCM   = os.path.abspath("blank_template.docm")
INPUT_VBA       = "demo_output.vba"
OUTPUT_DIR      = os.path.abspath("Demo_VT_Samples")
OUTPUT_CSV      = os.path.join(OUTPUT_DIR, "Demo_VT_Report.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================================
# 1. LLM INSTANCE (Obfuscator)
# ==========================================
coder_llm = ChatOpenAI(
    model="Qwen/Qwen2.5-Coder-32B-Instruct-AWQ",
    openai_api_key="empty",
    openai_api_base=KAGGLE_API_BASE,
    default_headers={"ngrok-skip-browser-warning": "true"},
    temperature=0.1
)

# ==========================================
# 2. OBFUSCATION — 3 STRATEGIES (Phase 2 style)
# ==========================================
OBFUSCATION_STRATEGIES = {
    "Random_Renaming": """You are a VBA obfuscator. Apply ONLY Strategy 1: Random Variable/Function Renaming.
    - Rename ALL variable and function names to random 6-8 character strings (e.g., xQpRmT, aJbKcL).
    - DO NOT rename: Document_Open, AutoOpen, CreateObject, WScript.Shell, MSXML2.XMLHTTP, ADODB.Stream.
    - DO NOT change logic, IP addresses, URLs, or functionality.
    - Return ONLY the raw VBA code, no explanation.""",

    "String_Concatenation": """You are a VBA obfuscator. Apply ONLY Strategy 2: String Concatenation.
    - Break ALL string literals into 2-4 character chunks joined with & operator.
    - Example: "WScript.Shell" -> "WSc" & "rip" & "t.S" & "hell"
    - DO NOT change variable names, logic, IP addresses, or functionality.
    - Return ONLY the raw VBA code, no explanation.""",

    "ASCII_Encoding": """You are a VBA obfuscator. Apply ONLY Strategy 3: ASCII Chr() Encoding.
    - Replace ALL string literals with Chr() sequences.
    - Example: "GET" -> Chr(71) & Chr(69) & Chr(84)
    - Split long Chr() chains across multiple lines using _ line continuation (VBA 1024-char limit).
    - DO NOT change logic, IP addresses, or functionality.
    - Return ONLY the raw VBA code, no explanation."""
}

def obfuscate_code(base_code: str, strategy_name: str, prompt: str) -> str:
    print(f"   [OBFUSCATOR] Applying strategy: {strategy_name}...")
    res = coder_llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=f"Obfuscate this VBA code:\n\n{base_code}")
    ])
    code = res.content.strip()
    # Strip markdown code block if present
    if "```vba" in code:
        code = code.split("```vba")[1].split("```")[0].strip()
    elif "```" in code:
        code = code.split("```")[1].split("```")[0].strip()
    return code

# ==========================================
# 3. INJECT VBA INTO .DOCM (from Validate_Obfuscated_VT.py)
# ==========================================
def inject_vba(vba_code: str, output_path: str) -> bool:
    shutil.copy(TEMPLATE_DOCM, output_path)
    word = None
    doc = None
    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = False
        doc = word.Documents.Open(output_path)
        doc.VBProject.VBComponents("ThisDocument").CodeModule.AddFromString(vba_code)
        doc.Save()
        return True
    except Exception as e:
        print(f"[ERROR] VBA injection failed: {e}")
        return False
    finally:
        try:
            if doc: doc.Close(SaveChanges=False)
        except: pass
        try:
            if word: word.Quit()
        except: pass

# ==========================================
# 4. VIRUSTOTAL SCAN (from Validate_Obfuscated_VT.py)
# ==========================================
def vt_upload(file_path: str):
    headers = {"x-apikey": VT_API_KEY}
    with open(file_path, "rb") as f:
        res = requests.post("https://www.virustotal.com/api/v3/files",
                            headers=headers, files={"file": f}, timeout=60)
    if res.status_code == 200:
        return res.json()["data"]["id"]
    print(f"[ERROR] VT Upload failed: {res.status_code} {res.text}")
    return None

def vt_poll(analysis_id: str) -> dict:
    headers = {"x-apikey": VT_API_KEY}
    url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
    print("   [VT] Polling analysis status", end="", flush=True)
    for _ in range(30):  # max 10 minutes
        time.sleep(20)
        print(".", end="", flush=True)
        res = requests.get(url, headers=headers, timeout=60)
        if res.status_code == 200:
            data = res.json()
            if data["data"]["attributes"]["status"] == "completed":
                print(" Done!")
                stats = data["data"]["attributes"]["stats"]
                file_hash = data.get("meta", {}).get("file_info", {}).get("sha256", analysis_id.split("-")[0])
                return stats, file_hash
    print(" [TIMEOUT]")
    return None, None

def vt_behavior(file_hash: str) -> dict:
    headers = {"x-apikey": VT_API_KEY}
    url = f"https://www.virustotal.com/api/v3/files/{file_hash}/behavior_mitre_trees"
    print("   [VT] Fetching MITRE behavior...", end="", flush=True)
    for _ in range(15):  # wait up to 5 min
        res = requests.get(url, headers=headers, timeout=60)
        if res.status_code == 200:
            print(" Done!")
            detected = {}
            for sandbox in res.json().get("data", []):
                for tactic in sandbox.get("attributes", {}).get("tactics", []):
                    for tech in tactic.get("techniques", []):
                        tid = tech.get("id")
                        if tid:
                            detected[tid] = tech.get("name", "")
            return detected
        elif res.status_code == 404:
            print(".", end="", flush=True)
            time.sleep(20)
        else:
            break
    print(" [NOT AVAILABLE]")
    return {}

# ==========================================
# 5. MAIN DEMO FLOW
# ==========================================
if __name__ == "__main__":
    print("=" * 60)
    print("  DEMO — OBFUSCATE + VIRUSTOTAL SCAN")
    print("=" * 60)

    # --- Guard checks ---
    if not VT_API_KEY:
        print("[ERROR] Please fill in VT_API_KEY at the top of this file.")
        sys.exit(1)
    if not os.path.exists(INPUT_VBA):
        print(f"[ERROR] '{INPUT_VBA}' not found. Run Demo_Phase1_Base_043.py first.")
        sys.exit(1)
    if not os.path.exists(TEMPLATE_DOCM):
        print(f"[ERROR] '{TEMPLATE_DOCM}' not found. A blank Word macro-enabled template is required.")
        sys.exit(1)

    # Load base VBA code
    with open(INPUT_VBA, "r", encoding="utf-8") as f:
        base_vba = f.read()

    print(f"\n[INFO] Loaded base VBA: {len(base_vba)} chars from '{INPUT_VBA}'")
    print(f"[INFO] Will apply {len(OBFUSCATION_STRATEGIES)} obfuscation strategies and submit each to VirusTotal.\n")

    results = []

    # ==========================================
    # BASELINE — upload raw (unobfuscated) file
    # ==========================================
    print(f"\n{'-'*60}")
    print("[BASELINE] Raw VBA (no obfuscation)")
    print(f"{'-'*60}")

    base_docm_path = os.path.join(OUTPUT_DIR, "demo_Baseline.docm")
    if inject_vba(base_vba, base_docm_path):
        print(f"   [SAVED] DOCM sample: {base_docm_path}")
        print("   [VT] Uploading baseline to VirusTotal...")
        base_analysis_id = vt_upload(base_docm_path)
        if base_analysis_id:
            print(f"   [VT] Analysis ID: {base_analysis_id}")
            base_stats, base_hash = vt_poll(base_analysis_id)
            if base_stats:
                base_mal   = int(base_stats.get("malicious", 0))
                base_total = base_mal + int(base_stats.get("undetected", 0))
                base_rate  = round((base_mal / base_total) * 100, 2) if base_total > 0 else 0
                time.sleep(15)
                base_ttps  = vt_behavior(base_hash)
                base_ttp_str = " | ".join([f"{k} ({v})" for k, v in base_ttps.items()])
                print(f"\n   ✅ BASELINE RESULT: {base_mal}/{base_total} engines detected ({base_rate}%)")
                print(f"   🔍 MITRE TTPs detected: {base_ttp_str or 'None'}")
                results.append({
                    "Strategy":       "Baseline (No Obfuscation)",
                    "Detected":       base_mal,
                    "Total":          base_total,
                    "Detection_Rate": base_rate,
                    "TTPs":           base_ttp_str
                })
                time.sleep(15)  # Cooldown before first obfuscated sample
    else:
        print("   [SKIP] Baseline injection failed.")

    for strategy_name, prompt in OBFUSCATION_STRATEGIES.items():
        print(f"\n{'-'*60}")
        print(f"[STRATEGY] {strategy_name}")
        print(f"{'-'*60}")

        # Step 1: Obfuscate
        morphed_code = obfuscate_code(base_vba, strategy_name, prompt)

        # Save obfuscated VBA to txt for inspection
        vba_out_path = os.path.join(OUTPUT_DIR, f"demo_{strategy_name}.vba")
        with open(vba_out_path, "w", encoding="utf-8") as f:
            f.write(morphed_code)
        print(f"   [SAVED] Obfuscated VBA: {vba_out_path}")

        # Step 2: Inject into .docm
        docm_path = os.path.join(OUTPUT_DIR, f"demo_{strategy_name}.docm")
        if not inject_vba(morphed_code, docm_path):
            print(f"   [SKIP] Injection failed for {strategy_name}")
            continue
        print(f"   [SAVED] DOCM sample: {docm_path}")

        # Step 3: Upload to VirusTotal
        print("   [VT] Uploading to VirusTotal...")
        analysis_id = vt_upload(docm_path)
        if not analysis_id:
            continue
        print(f"   [VT] Analysis ID: {analysis_id}")

        # Step 4: Poll for results
        stats, file_hash = vt_poll(analysis_id)
        if not stats:
            continue

        mal   = int(stats.get("malicious", 0))
        total = mal + int(stats.get("undetected", 0))
        rate  = round((mal / total) * 100, 2) if total > 0 else 0

        # Step 5: Fetch MITRE behavior
        time.sleep(15)
        detected_ttps = vt_behavior(file_hash)
        ttp_str = " | ".join([f"{k} ({v})" for k, v in detected_ttps.items()])

        print(f"\n   ✅ RESULT: {mal}/{total} engines detected ({rate}%)")
        print(f"   🔍 MITRE TTPs detected: {ttp_str or 'None'}")

        results.append({
            "Strategy":       strategy_name,
            "Detected":       mal,
            "Total":          total,
            "Detection_Rate": rate,
            "TTPs":           ttp_str
        })

        time.sleep(15)  # Cooldown between samples

    # ==========================================
    # FINAL SUMMARY — Console + CSV
    # ==========================================
    print(f"\n{'='*60}")
    print("  FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"{'Strategy':<28} {'Detected':>10} {'Total':>8} {'Rate':>8}")
    print("-" * 60)
    for r in results:
        print(f"{r['Strategy']:<28} {r['Detected']:>10} {r['Total']:>8} {r['Detection_Rate']:>7}%")
        print(f"   TTPs: {r['TTPs'] or 'None'}")

    # Export CSV
    csv_fieldnames = [
        "Strategy",
        "VT_Malicious_Engines",
        "VT_Total_Engines",
        "Detection_Rate",
        "VT_Detected_TTPs"
    ]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({
                "Strategy":            r["Strategy"],
                "VT_Malicious_Engines": r["Detected"],
                "VT_Total_Engines":     r["Total"],
                "Detection_Rate":       r["Detection_Rate"],
                "VT_Detected_TTPs":     r["TTPs"]
            })
    print(f"\n[INFO] CSV report saved to: {OUTPUT_CSV}")
