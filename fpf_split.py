#!/usr/bin/env python3

import re
import os
import sys

def normalize_text(text):
    """
    Normalizes text to handle non-standard hyphens used in FPF.
    """
    text = text.replace('\u2011', '-') # Non-breaking hyphen
    text = text.replace('\u2013', '-') # En dash
    text = text.replace('\u2014', '-') # Em dash
    text = text.replace('\u00A0', ' ') # Non-breaking space
    return text

def get_header_part_letter(line):
    """
    Detects if a line is a 'Part X' header and returns the letter (A, B, C...).
    Returns None if it's not a Part header.
    """
    clean_line = normalize_text(line).strip()
    
    # Regex to find "# Part X" or "## Part X" (case insensitive)
    # We look for the pattern: Start of line -> hashes -> whitespace -> "Part" -> whitespace -> Single Letter
    match = re.search(r'^#+\s*Part\s+([A-Z])', clean_line, re.IGNORECASE)
    
    if match:
        return match.group(1).upper()
    return None

def verify_integrity(input_file, parts_content, part_order):
    """
    Self-Test Function:
    Reconstructs the file from the parsed memory chunks in the order they were found
    and compares it byte-for-byte with the original input.
    """
    print("-" * 30)
    print("Running Self-Test (Integrity Check)...")
    
    # 1. Reconstruct in memory
    reconstructed_data = []
    for part_id in part_order:
        if part_id in parts_content:
            reconstructed_data.extend(parts_content[part_id])
    
    # 2. Read original file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            original_data = f.readlines()
    except Exception as e:
        print(f"  [ERROR] Could not read original file for verification: {e}")
        return False

    # 3. Compare statistics
    count_orig = len(original_data)
    count_recon = len(reconstructed_data)
    
    if count_orig != count_recon:
        print(f"  [FAIL] Line count mismatch! Original: {count_orig}, Reconstructed: {count_recon}")
        return False

    # 4. Deep comparison
    mismatch_found = False
    for i, (l1, l2) in enumerate(zip(original_data, reconstructed_data)):
        if l1 != l2:
            print(f"  [FAIL] Mismatch at line {i+1}:")
            print(f"    Orig: {repr(l1)}")
            print(f"    Copy: {repr(l2)}")
            mismatch_found = True
            break
    
    if not mismatch_found:
        print(f"  [PASS] Perfect match ({count_orig} lines). Parsing is lossless.")
        
        # Optional: Dump the verified copy to proof
        proof_filename = "compressed/FPF-Spec-Verified-Copy.md"
        with open(proof_filename, 'w', encoding='utf-8') as f:
            f.writelines(reconstructed_data)
        print(f"  [INFO] Verified copy saved to: {proof_filename}")
        return True
    else:
        return False

def write_module(filename, parts_content, parts_list):
    """
    Writes a list of Part contents into a single module file.
    """
    if not parts_list:
        return

    # Filter out parts that weren't found in this file
    valid_parts = [p for p in parts_list if p in parts_content]
    
    if not valid_parts:
        return

    print(f"  Building {filename} from: {', '.join(valid_parts)}")
    
    with open(filename, 'w', encoding='utf-8') as f:
        for i, part_id in enumerate(valid_parts):
            # Write the content
            f.writelines(parts_content[part_id])
            
            # Add a separator between parts for clarity (except for the last one)
            # This separator is NOT in the original file, it is added for the Modules only.
            if i < len(valid_parts) - 1:
                f.write("\n\n<!-- MODULE SEPARATOR: End of Part " + part_id + " -->\n\n")
    
    if os.path.exists(filename):
        size_kb = os.path.getsize(filename) / 1024
        print(f"    -> Created {filename} ({round(size_kb, 1)} KB)")

def split_and_assemble_fpf(input_file):
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found.")
        return

    # 1. READ & PARSE
    parts_content = {}
    part_order = [] # To track original sequence for integrity check
    
    current_part = 'PREFACE' 
    parts_content[current_part] = []
    part_order.append(current_part)

    print(f"Reading {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            # Check for new Part header
            new_part_letter = get_header_part_letter(line)
            
            if new_part_letter:
                current_part = new_part_letter
                if current_part not in parts_content:
                    parts_content[current_part] = []
                    part_order.append(current_part) # Record the order
                    print(f"  -> Found start of Part {current_part}")
            
            # Append line to the currently active part bucket
            parts_content[current_part].append(line)

    # 2. RUN SELF-TEST
    # We verify that we haven't lost any lines during parsing
    if not verify_integrity(input_file, parts_content, part_order):
        print("Error: Integrity check failed. Aborting module generation to prevent data loss.")
        sys.exit(1)

    # 3. DEFINE ASSEMBLY RULES ("Split by Layers")
    print("-" * 30)
    print("Assembling Modules...")

    # Kernel: Preface + A (Ontology) + E (Constitution)
    kernel_parts = ['PREFACE', 'A', 'E']
    
    # Logic: B (Reasoning) + F (Unification)
    logic_parts = ['B', 'F']
    
    # Domain: C (Architheories) + D (Ethics) + G (SoTA) + Appendices (H-Z)
    # We dynamically grab all other found parts that are not Kernel or Logic
    all_found_keys = set(parts_content.keys())
    used_keys = set(kernel_parts + logic_parts)
    domain_parts = sorted(list(all_found_keys - used_keys))

    # 4. WRITE MODULES
    write_module('compressed/FPF-Module-Kernel.md', parts_content, kernel_parts)
    write_module('compressed/FPF-Module-Logic.md', parts_content, logic_parts)
    write_module('compressed/FPF-Module-Domain.md', parts_content, domain_parts)

    print("-" * 30)
    print("Done.")

if __name__ == "__main__":
    INPUT_FILE = "FPF-Spec.md"
    split_and_assemble_fpf(INPUT_FILE)