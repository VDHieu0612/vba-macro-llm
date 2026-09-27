# 🦠 Macro Malware: LLM-Driven Generation & Evasion Analysis

> An academic research project automating VBA macro malware generation using a multi-stage LLM Agent pipeline with MITRE ATT&CK-aligned TTPs and obfuscation strategies — for defensive security research purposes only.

> ⚠️ **Ethical Disclaimer:** This research is conducted solely for academic and defensive security purposes under NT230 coursework at UIT. All generated samples are analyzed in isolated environments. No malware is deployed against real systems.

---

## 📌 Project Overview

This project investigates the **automated generation of evasive VBA macro malware** using Large Language Models (LLMs) with Chain-of-Thought prompting, structured around the MITRE ATT&CK framework.

**Course:** NT230.Q22.ANTT — Malware Analysis & Security, UIT (VNU-HCM)  
**Duration:** January 2026 – May 2026  
**Type:** Group Research Project  
**Model Used:** Qwen-32B (local inference)  
**Total Samples Generated:** ~298 variants

### My Individual Contributions
- Designed the **two-phase pipeline architecture** (Base Generation + Obfuscation)
- Implemented the **PLANNER → CODER → CHECKER** agentic node system with retry logic
- Developed all **3 obfuscation strategies** (Random Renaming, String Concatenation, ASCII Encoding)
- Conducted **MITRE ATT&CK TTP mapping** and TTP combo selection logic
- Performed **detection analysis** against Windows Defender (AMSI layer)

> Full group technical report (NT230.Q22.ANTT) available upon request.

---

## 🏗️ Pipeline Architecture

### Two-Phase Generation System

```
Phase 1: Base Malware Generation (Agentic Pipeline)
─────────────────────────────────────────────────────

  TTP Recipe (1 Exec + 1 Disco + 1 C2)
           │
    ┌──────▼──────┐
    │  PLANNER    │  (temp=0.7) → Generates Cyber Kill Chain plan
    │   Node      │
    └──────┬──────┘
           │ kill_chain plan
    ┌──────▼──────┐
    │   CODER     │  (temp=0.3) → Generates raw VBA macro code
    │   Node      │
    └──────┬──────┘
           │ base_vba_code
    ┌──────▼──────┐
    │  CHECKER    │  Hard-rule: MagicLine + StringError check
    │   Node      │  LLM QA: syntax validation
    └──────┬──────┘
           │ PASS / FAIL → retry max 3x
           ▼
    Save to CSV (Combo_ID, TTP_Series, Kill_Chain, Base_VBA_Code)


Phase 2: Obfuscation Pipeline (×3 Strategies)
─────────────────────────────────────────────────────

  100 validated base samples
           │
     ┌─────┼─────┐
     ▼     ▼     ▼
  [S1]  [S2]   [S3]
  Random String ASCII
  Rename Concat Encode
     │     │     │
     ▼     ▼     ▼
  100   100    98*  morphed variants
         │
         ▼
  LLMalMorph_Obfuscated_Dataset.csv
  (Combo_ID, Evasion_Strategy, Morphed_Code)

  * 2 failed due to Chr() sequence serialization bug in .docm format
```

---

## 🎯 MITRE ATT&CK TTP Selection

Each base sample is generated from **1 TTP combo = 1 Execution + 1 Discovery + 1 C2**

### Execution Techniques
| TTP | Description |
|-----|-------------|
| T1059.001 | PowerShell — bypass policy, hidden window |
| T1059.003 | CMD execution — simple, widely used |
| T1047 | WMI — spawn process without explicit shell |
| T1059.005 | VBScript intermediary — avoid direct macro calls |

### Discovery Techniques
| TTP | Description |
|-----|-------------|
| T1082 | System Information Discovery — OS, architecture |
| T1033 | Current User Discovery — personalize payload paths |
| T1016 | Network Configuration — IP, subnet, gateway profiling |
| T1057 | Process Discovery — anti-analysis sandbox detection |
| T1083 | File & Directory Discovery — locate sensitive documents |

### C2 / Exfiltration Techniques
| TTP | Description |
|-----|-------------|
| T1105 | Ingress Tool Transfer — drop payload disguised as update.exe |
| T1071.001 | Web Protocol C2 — HTTP-based command channel |
| T1132.001 | Data Encoding — obfuscate exfiltrated data |

---

## 🔄 Obfuscation Strategies

| Strategy | Technique | Variants |
|----------|-----------|----------|
| **Random Renaming** | Variable/function names → random alphanumeric (e.g., `shell` → `xY12b`) | 100 |
| **String Concatenation** | Split string literals into chunks joined with `&` (`'WSc' & 'ript' & '.Shell'`) | 100 |
| **ASCII Encoding** | Replace strings with `Chr()` sequences (`Chr(87) & Chr(83) & Chr(99)...`) | 98* |

---

## 📊 Dataset Statistics

| Metric | Value |
|--------|-------|
| Base samples generated | 100 |
| Obfuscation strategies | 3 |
| Total variants | ~298 |
| TTP combinations tested | 20 (4 Exec × 5 Disco × 1 C2 sampled) |
| Validation pass rate | 100% (base) / 98% (ASCII obfuscation) |

---

## 🔬 Key Findings

1. **LLM Structural Quality:** >95% of generated macros were syntactically valid and behaviorally coherent
2. **Real-world Context Gap:** LLMs hallucinate environment-specific values (victim IP, file paths) without grounding → payloads are functionally correct but not operationally targeted
3. **Evasion Capability:** Obfuscated variants evade static signature detection; however, **AMSI (Anti-Malware Scan Interface)** — which scans in-memory at VBA runtime — remains the primary detection layer bypassed by none of the three strategies
4. **Model Safety Constraints:** RLHF guardrails and training data limitations reduce generation of highly specific weaponized content

---

## 🛡️ Defensive Implications

- **Detection Gap:** Slow-polymorphic VBA macros with Chr() encoding are difficult for static AV scanners
- **AMSI Monitoring:** Behavioral monitoring at the VBA runtime layer is the most effective detection point
- **User Awareness:** Social engineering delivery (email phishing + "Enable Content" prompt) remains the primary attack vector — user education is critical
- **IOCs Generated:** This dataset can be used to train/test VBA-aware sandbox detection systems

---

## 📁 Repository Contents

```
├── README.md
├── report/
│   └── project_230_final_report.pdf    # Full technical report
├── pipeline/
│   ├── phase1_generation/              # PLANNER + CODER + CHECKER nodes
│   └── phase2_obfuscation/             # 3 obfuscation strategy scripts
├── dataset/
│   ├── base_samples.csv                # 100 validated base macros
│   └── LLMalMorph_Obfuscated.csv       # ~298 obfuscated variants
└── analysis/
    └── detection_results.md            # AV/AMSI detection findings
```

---

## 👤 Author

**Võ Duy Hiếu** — Information Security, UIT (VNU-HCM)  
[![Kaggle](https://img.shields.io/badge/Kaggle-IDS_Research-20BEFF)](https://www.kaggle.com/code/vohieu0612/ids-using-rf-conv1d-bi-lstm-attention)

---

*This project is part of academic coursework (NT230.Q22.ANTT) and adheres to responsible disclosure principles.*

