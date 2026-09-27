import os
import csv
import time
import shutil
import requests
import win32com.client
import sys
import re
import argparse

# ==========================================
# ARGPARSE INITIALIZATION FOR PARALLEL EXECUTION
# ==========================================
parser = argparse.ArgumentParser(description="VT Evaluation Pipeline - Parallel Mode")
parser.add_argument("--key", required=True, help="VirusTotal API Key")
parser.add_argument("--input", required=True, help="Input CSV file (e.g., Chunk_1.csv)")
parser.add_argument("--output", required=True, help="Output CSV file (e.g., Result_1.csv)")
args = parser.parse_args()

VT_API_KEY = args.key
INPUT_CSV = args.input
OUTPUT_CSV = args.output
TEMPLATE_DOCM = os.path.abspath("blank_template.docm")

# Create isolated directories for each chunk to prevent file locking conflicts
chunk_name = INPUT_CSV.split('.')[0]
SAMPLES_DIR = os.path.abspath(f"Generated_Docm_Samples_{chunk_name}")

if not os.path.exists(SAMPLES_DIR):
    os.makedirs(SAMPLES_DIR)

def inject_vba(vba_code, output_path):
    """Robust Word Injection using DispatchEx"""
    shutil.copy(TEMPLATE_DOCM, output_path)
    word = None
    doc = None
    try:
        # Use DispatchEx to force a completely isolated Word instance
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = False # Suppress any Word UI popups that might cause freezing
        
        doc = word.Documents.Open(output_path)
        doc.VBProject.VBComponents("ThisDocument").CodeModule.AddFromString(vba_code)
        doc.Save()
        return True
    except Exception as e:
        print(f"\n[ERROR] Code injection failed for {output_path}: {e}")
        return False
    finally:
        # Isolate cleanup commands in separate try-except blocks to prevent chain-crashing
        try:
            if doc: 
                doc.Close(SaveChanges=False)
        except Exception:
            pass
            
        try:
            if word: 
                word.Quit()
        except Exception:
            pass

def vt_scan_and_report(file_path):
    """Upload and fetch TTPs with SMART AUTO-RETRY for 429 Daily vs Minute Limits"""
    headers = {"x-apikey": VT_API_KEY}
    
    # 1. UPLOAD PHASE
    retry_count = 0
    while True:
        with open(file_path, "rb") as f:
            res = requests.post("https://www.virustotal.com/api/v3/files", headers=headers, files={"file": f})
        
        if res.status_code == 429:
            retry_count += 1
            if retry_count > 3:
                print("\n[CRITICAL STOP] Hit 429 limit 3 times in a row. DAILY QUOTA EXCEEDED (500 req/day).")
                sys.exit(0)
            print(f" -> [WAITING] Upload limit hit. Sleeping 60s (Attempt {retry_count}/3)...")
            time.sleep(60)
            continue
        elif res.status_code == 401:
            print("\n[CRITICAL ERROR] Invalid API Key! Exiting.")
            sys.exit(1)
        elif res.status_code != 200:
            print(f"\n[ERROR] Upload failed: {res.text}")
            return None, None
        break # Success
        
    analysis_id = res.json()["data"]["id"]
    file_hash = analysis_id.split('-')[0]
    time.sleep(20) 
    stats = None
    
    # 2. POLLING PHASE
    retry_count = 0
    while True:
        report_res = requests.get(f"https://www.virustotal.com/api/v3/analyses/{analysis_id}", headers=headers)
        if report_res.status_code == 429:
            retry_count += 1
            if retry_count > 3:
                print("\n[CRITICAL STOP] Hit 429 limit 3 times in a row. DAILY QUOTA EXCEEDED (500 req/day).")
                sys.exit(0)
            print(f" -> [WAITING] Polling limit hit. Sleeping 60s (Attempt {retry_count}/3)...")
            time.sleep(60)
            continue
            
        if report_res.status_code == 200:
            report = report_res.json()
            if report["data"]["attributes"]["status"] == "completed":
                stats = report["data"]["attributes"]["stats"]
                try: 
                    file_hash = report["meta"]["file_info"]["sha256"]
                except Exception: 
                    pass
                break
        time.sleep(20) 
        
    time.sleep(20) 
    detected_ttps = {} 
    
    # 3. BEHAVIOR PHASE
    retry_count = 0
    while True:
        behavior_res = requests.get(f"https://www.virustotal.com/api/v3/files/{file_hash}/behavior_mitre_trees", headers=headers)
        if behavior_res.status_code == 429:
            retry_count += 1
            if retry_count > 3:
                print("\n[CRITICAL STOP] Hit 429 limit 3 times in a row. DAILY QUOTA EXCEEDED (500 req/day).")
                sys.exit(0)
            print(f" -> [WAITING] Behavior limit hit. Sleeping 60s (Attempt {retry_count}/3)...")
            time.sleep(60)
            continue
            
        if behavior_res.status_code == 200:
            data = behavior_res.json().get("data", [])
            for sandbox in data:
                tactics = sandbox.get("attributes", {}).get("tactics", [])
                for tactic in tactics:
                    for tech in tactic.get("techniques", []):
                        tech_id = tech.get("id")
                        tech_name = tech.get("name", "Unknown Technique")
                        if tech_id: 
                            detected_ttps[tech_id] = tech_name
        break
                        
    return stats, detected_ttps

def format_ttp_details(detected_dict, ttp_recipe_string):
    """Format expected vs unexpected TTPs"""
    intended_matches = set(re.findall(r'(T\d{4})', ttp_recipe_string))
    detailed_detected = []
    detailed_unexpected = []
    
    for tech_id, tech_name in detected_dict.items():
        display_string = f"{tech_id} ({tech_name})"
        detailed_detected.append(display_string)
        base_id = tech_id.split('.')[0] 
        if base_id not in intended_matches:
            detailed_unexpected.append(display_string)
            
    return " | ".join(detailed_detected), " | ".join(detailed_unexpected), len(detailed_unexpected)

def run_evaluation():
    if not os.path.exists(INPUT_CSV):
        print(f"[ERROR] File not found: {INPUT_CSV}")
        return

    completed_samples = set()
    if os.path.exists(OUTPUT_CSV):
        with open(OUTPUT_CSV, 'r', encoding='utf-8') as f_out:
            reader_out = csv.DictReader(f_out)
            for row in reader_out:
                if 'Combo_ID' in row and 'Evasion_Strategy' in row:
                    # FIX: Match the exact string to prevent duplicate Baseline scans
                    if row['Evasion_Strategy'] == "Baseline (No Evasion)":
                        completed_samples.add(f"{row['Combo_ID']}_Baseline")
                    else:
                        completed_samples.add(f"{row['Combo_ID']}_{row['Evasion_Strategy']}")
        print(f"[INFO] Resuming {INPUT_CSV}... Completed records: {len(completed_samples)}")

    # Define the new cleaner Output Headers
    output_fieldnames = [
        "Timestamp", "Combo_ID", "TTP_Recipe", "Kill_Chain_Log", 
        "Evasion_Strategy", "Analyzed_VBA_Code", 
        "VT_Malicious", "VT_Undetected", "Detection_Rate", 
        "VT_Detected_TTPs", "Unexpected_TTPs"
    ]

    with open(INPUT_CSV, 'r', encoding='utf-8') as fin, \
         open(OUTPUT_CSV, 'a', newline='', encoding='utf-8') as fout:
        
        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=output_fieldnames)
        
        if os.stat(OUTPUT_CSV).st_size == 0:
            writer.writeheader()

        processed_bases = set()

        for row in reader:
            combo_id = row['Combo_ID']
            
            # --- BASELINE SCAN (Control Group) ---
            base_sample_id = f"{combo_id}_Baseline"
            if base_sample_id not in completed_samples and combo_id not in processed_bases:
                print(f"\n--- [CHUNK: {INPUT_CSV}] Processing: {base_sample_id} ---")
                base_file_path = os.path.join(SAMPLES_DIR, f"{base_sample_id}.docm")
                
                if inject_vba(row['Base_VBA_Code'], base_file_path):
                    stats, detected_ttps_dict = vt_scan_and_report(base_file_path)
                    
                    if stats:
                        mal = int(stats.get('malicious', 0))
                        und = int(stats.get('undetected', 0))
                        rate = round((mal / (mal + und)) * 100, 2) if (mal + und) > 0 else 0
                        str_detected, str_unexpected, unexp_count = format_ttp_details(detected_ttps_dict, row.get('TTP_Recipe', ''))
                        
                        # Constructing the clean output row
                        base_out_row = {
                            "Timestamp": row.get("Timestamp", ""),
                            "Combo_ID": combo_id,
                            "TTP_Recipe": row.get("TTP_Recipe", ""),
                            "Kill_Chain_Log": row.get("Kill_Chain_Log", ""),
                            "Evasion_Strategy": "Baseline (No Evasion)",
                            "Analyzed_VBA_Code": row['Base_VBA_Code'], 
                            "VT_Malicious": mal,
                            "VT_Undetected": und,
                            "Detection_Rate": rate,
                            "VT_Detected_TTPs": str_detected,
                            "Unexpected_TTPs": str_unexpected
                        }
                        
                        writer.writerow(base_out_row)
                        fout.flush()
                        print(f"Result: {rate}% | Unexpected TTPs: {unexp_count}")
                
                processed_bases.add(combo_id)
                time.sleep(20) 
            else:
                processed_bases.add(combo_id)

            # --- MORPHED SCAN (Evasion Group) ---
            sample_id = f"{combo_id}_{row['Evasion_Strategy']}"
            if sample_id in completed_samples: continue

            print(f"\n--- [CHUNK: {INPUT_CSV}] Processing: {sample_id} ---")
            file_path = os.path.join(SAMPLES_DIR, f"{sample_id}.docm")
            
            if inject_vba(row['Morphed_VBA_Code'], file_path):
                stats, detected_ttps_dict = vt_scan_and_report(file_path)
                
                if stats:
                    mal = int(stats.get('malicious', 0))
                    und = int(stats.get('undetected', 0))
                    rate = round((mal / (mal + und)) * 100, 2) if (mal + und) > 0 else 0
                    str_detected, str_unexpected, unexp_count = format_ttp_details(detected_ttps_dict, row.get('TTP_Recipe', ''))
                    
                    # Constructing the clean output row
                    morphed_out_row = {
                        "Timestamp": row.get("Timestamp", ""),
                        "Combo_ID": combo_id,
                        "TTP_Recipe": row.get("TTP_Recipe", ""),
                        "Kill_Chain_Log": row.get("Kill_Chain_Log", ""),
                        "Evasion_Strategy": row['Evasion_Strategy'],
                        "Analyzed_VBA_Code": row['Morphed_VBA_Code'], 
                        "VT_Malicious": mal,
                        "VT_Undetected": und,
                        "Detection_Rate": rate,
                        "VT_Detected_TTPs": str_detected,
                        "Unexpected_TTPs": str_unexpected
                    }
                    
                    writer.writerow(morphed_out_row)
                    fout.flush()
                    print(f"Result: {rate}% | Unexpected TTPs: {unexp_count}")
            
            time.sleep(20) 

if __name__ == "__main__":
    print(f"Initializing Parallel Evaluation Pipeline for: {INPUT_CSV}")
    run_evaluation()
