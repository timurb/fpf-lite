# PF-5 Spec - Split Spec Into Parts (On Disk)

## Summary
Split the canonical FPF spec into per-part files on disk so the parts can be
reassembled or selectively assembled later.

## Inputs
- `FPF/FPF-Spec.md`

## Outputs
- `FPF/parts/` (default; configurable via `--output-dir`)
  - `FPF-Part-Preface.md`
  - `FPF-Part-A.md`, `FPF-Part-B.md`, ... (one file per Part header found)
  - `FPF-Parts-Manifest.txt` (one filename per line, in original order)

## Behavior
- Read the input line-by-line.
- Treat all content before the first Part header as the Preface.
- Detect Part headers using a case-insensitive match for `^#+\s*Part\s+([A-Z])`.
- Also treat bold Part markers as Part headers using a case-insensitive match for
  `^\s*\*\*Part\s+([A-Z])\b`.
- Normalize header text before matching by replacing:
  - non-breaking hyphen (U+2011) with `-`
  - en dash/em dash with `-`
  - non-breaking space (U+00A0) with a regular space
- Start a new output file when a new Part header is encountered.
- Write each part file exactly as it appears in the input, without extra
  separators or modified whitespace.
- Write `FPF-Parts-Manifest.txt` listing the part filenames in the order
  encountered, starting with `FPF-Part-Preface.md`.
- Fail with a non-zero exit code and a clear error message if the input does not
  exist or any output cannot be written.

## Invocation
- `./fpf.py split`
- `./fpf.py split --input <spec-path> --output-dir <dir>`

## Constraints
- Reuse normalization function across all features
- Do not modify the source file.
- Do not load the entire input into memory.
- Write output files with UTF-8 encoding.

## Success Criteria
- The output directory contains one file per part plus the manifest.
- Concatenating the parts in manifest order reproduces the original input
  byte-for-byte.
