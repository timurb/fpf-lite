# PF-4 Spec - Semantic Compression (Aggressive)

## Status
- Implemented

## Summary
Produce an aggressive compressed version of the FPF specification that keeps
only normative content needed for strict validation or code generation.

## Inputs
- `<work-dir>/FPF-Spec.md`

## Outputs
- `<work-dir>/FPF-Spec-Aggressive.md`

## Behavior
- Apply all PF-3 behavior.
- Additionally remove sections whose headings include any of:
  - `Problem frame`
  - `Problem`
  - `Forces`
  - `Rationale`
  - `Anti-patterns`
- Keyword checks are case-insensitive and apply to normalized header text.
- Preserve all other sections and their subsections.
- Write output with UTF-8 encoding.
- Print compression stats to stdout, including per-keyword removal counts and
  line reduction.

## Invocation
- `./fpf.py strip-aggressive`
- `./fpf.py strip-aggressive --work-dir <dir>`

## Constraints
- Operate line-by-line without loading the full file into memory beyond the
  existing read in `fpf_compressor.py`.
- Do not modify the source file.
- Input and output filenames are resolved within `<work-dir>`.

## Success Criteria
- The output file exists at `<work-dir>/FPF-Spec-Aggressive.md`.
- Removed sections include all PF-3 keywords plus the aggressive list.
- All remaining content is preserved in original order.
- Stats are printed to stdout for the run.
