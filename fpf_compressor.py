#!/usr/bin/env python3

import re
import os
import sys
from pathlib import Path

def normalize_text(text):
    """
    Replaces all types of dashes, hyphens, and non-breaking spaces with standard ASCII characters.
    This is critical for FPF, where '‑' (U+2011) is often used instead of '-'.
    """
    text = text.replace('\u2011', '-') # Non-breaking hyphen
    text = text.replace('\u2013', '-') # En dash
    text = text.replace('\u2014', '-') # Em dash
    text = text.replace('\u00A0', ' ') # Non-breaking space
    return text

def compress_fpf(input_path, output_path, aggressive=False):
    # Keywords to remove.
    # We use standard hyphens here because the text is normalized before checking.
    REMOVE_KEYWORDS = [
        "SoTA-Echoing", 
        "SOTA-Echoing",
        "SoTA Echoing",      # Вариант с пробелом
        "SOTA Echoing",
        "State-of-the-Art alignment" # Для A.14:14 и подобных
        ]
    
    if aggressive:
        REMOVE_KEYWORDS.extend([
            "Problem frame", 
            "Problem", 
            "Forces", 
            "Rationale",
            "Anti-patterns" # Optional: add if extreme saving is needed
        ])

    # Markdown header pattern (1 to 6 hashes)
    header_pattern = re.compile(r'^(#+)\s+(.*)')
    
    # Pattern for the start of the "payload" content (skip Preface/TOC)
    # Looks for the start of "Part A" or "A.0"
    start_marker_pattern = re.compile(r'^#+\s+(Part A|A\.0)', re.IGNORECASE)

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File {input_path} not found.")
        return

    output_lines = []
    
    # State flags
    is_content_started = False
    skipping_section = False
    skip_level = 0
    
    removed_counters = {k: 0 for k in REMOVE_KEYWORDS}
    
    print(f"Processing {len(lines)} lines...")

    for line in lines:
        # 1. Preface removal logic (skip everything before Part A)
        if not is_content_started:
            if start_marker_pattern.match(line):
                is_content_started = True
                output_lines.append(line)
                print("--> Found content start (Part A/A.0). Preface removed.")
                continue
            else:
                continue # Skip Preface lines

        # 2. Header checking
        match = header_pattern.match(line)
        if match:
            level = len(match.group(1)) # Header level (# count)
            raw_title = match.group(2).strip()
            
            # Normalize title for robust checking (remove special chars)
            clean_title = normalize_text(raw_title)

            # If we are currently skipping a section...
            if skipping_section:
                # If we meet a header of the same level or higher (fewer #) -> stop skipping
                if level <= skip_level:
                    skipping_section = False
                else:
                    # This is a subsection -> continue skipping
                    continue

            # Check if we need to start skipping this new section
            found_keyword = None
            for keyword in REMOVE_KEYWORDS:
                # Check: search for keyword in the normalized title (case-insensitive)
                if keyword.lower() in clean_title.lower():
                    found_keyword = keyword
                    break
            
            if found_keyword and not skipping_section:
                skipping_section = True
                skip_level = level
                removed_counters[found_keyword] += 1
                # Uncomment the line below for debugging:
                # print(f"  [Removed] {raw_title}")
                continue

        # 3. Write line (if not in skip mode)
        if not skipping_section:
            output_lines.append(line)

    # Save results
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)

    print("-" * 30)
    print(f"Removal statistics:")
    for k, v in removed_counters.items():
        if v > 0:
            print(f"  - {k}: {v} sections")
    
    original_size = len(lines)
    new_size = len(output_lines)
    reduction = round((1 - new_size/original_size)*100, 1)
    
    print("-" * 30)
    print(f"Done. Result: {output_path}")
    print(f"Lines: {original_size} -> {new_size} (Reduction: {reduction}%)")

if __name__ == "__main__":
    INPUT_FILE = "FPF-Spec.md"

    Path("compressed").mkdir(parents=True, exist_ok=True)
    compress_fpf(INPUT_FILE, "compressed/FPF-Spec-Lite.md", False)
    compress_fpf(INPUT_FILE, "compressed/FPF-Spec-Aggressive.md", True)