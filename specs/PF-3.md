# PF-3 Spec - Semantic Compression (Lite)

## Status
- Implemented

## Summary
Produce a compressed version of the FPF specification by removing
non-normative sections while preserving rules and checklists.

## Inputs
- `FPF/FPF-Spec.md`

## Outputs
- `FPF/FPF-Spec-Lite.md` (default; configurable via `--output`).

## Behavior
- Remove the Preface and any content before the first `Part A` or `A.0` header.
- Remove sections whose headings include any of:
  - `SoTA-Echoing`
  - `SOTA-Echoing`
  - `SoTA Echoing`
  - `SOTA Echoing`
  - `State-of-the-Art alignment`
- Preserve all other sections and their subsections.
- Normalize header text when checking removal keywords by replacing:
  - non-breaking hyphen (U+2011) with `-`
  - en dash/em dash with `-`
  - non-breaking space (U+00A0) with a regular space
- Write output with UTF-8 encoding.
- Print compression stats to stdout, including per-keyword removal counts and
  line reduction.

## Invocation
- `./fpf.py strip-lite`

## Constraints
- Operate line-by-line without loading the full file into memory.
- Do not modify the source file.

## Success Criteria
- The output file exists at `FPF/FPF-Spec-Lite.md` by default, or the
  user-specified `--output` path.
- Removed sections match only the keyword list above.
- All remaining content is preserved in original order.
- Stats are printed to stdout for the run.
