"""
Obfuscation Strategy 2: String Concatenation
NT230.Q22.ANTT | Võ Duy Hiếu

Splits string literals into chunks joined with VBA & operator.
Example: "WScript.Shell" -> "WSc" & "ript" & ".Shell"
"""

import re
import random


def split_string_random(s: str, min_chunk: int = 2, max_chunk: int = 4) -> str:
    """Splits a string into random-length chunks joined by &"""
    if len(s) <= min_chunk:
        return f'"{s}"'
    
    chunks = []
    i = 0
    while i < len(s):
        chunk_size = random.randint(min_chunk, min(max_chunk, len(s) - i))
        chunks.append(f'"{s[i:i+chunk_size]}"')
        i += chunk_size
    
    return " & ".join(chunks)


def obfuscate_strings(vba_code: str) -> str:
    """
    Finds all string literals in VBA code and applies concatenation obfuscation.
    
    Args:
        vba_code: Raw VBA macro source code
    
    Returns:
        str: Obfuscated VBA code with split string literals
    """
    # Match string literals (simple quoted strings)
    pattern = r'"([^"]{4,})"'
    
    def replace_match(m):
        original = m.group(1)
        # Skip strings that are already short or are format strings
        if len(original) < 4 or '%' in original:
            return m.group(0)
        return split_string_random(original)
    
    obfuscated = re.sub(pattern, replace_match, vba_code)
    return obfuscated


if __name__ == "__main__":
    sample = '''Shell "WScript.Shell"'''
    print("Original:", sample)
    print("Obfuscated:", obfuscate_strings(sample))
