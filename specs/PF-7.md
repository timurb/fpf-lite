# PF-7 Spec - Normalize Typographics

## Status
- Pending

## Summary
Normalize typographic characters and Part headers in the spec to a standard
ASCII form.

## Inputs
- `FPF/FPF-Spec.md` (default; configurable via `--input`)

## Outputs
- `FPF/FPF-Spec-Normalized.md` (default; configurable via `--output`)
- If `--in-place` is set, overwrite the input file.

## Behavior
- Read input line-by-line.
- Replace typographic characters:
  - U+2011, U+2013, U+2014 -> `-`
  - U+00A0 -> ` `
  - U+2018, U+2019 -> `'`
  - U+201C, U+201D -> `"`
- Normalize Part headers:
  - Identify lines whose normalized text matches
    `^#+\s*\**Part\s+([A-Z])` (case-insensitive).
  - Preserve the header level (number of leading `#`).
  - Rewrite as `<hashes> Part <LETTER><suffix>` where:
    - `<LETTER>` is the uppercase part letter.
    - `<suffix>` is any remaining text after the letter, trimmed and prefixed
      with a single space if present.
  - Remove any `*` emphasis around `Part` or the letter.
- Write output with UTF-8 encoding.
- If both `--output` and `--in-place` are provided just produce a warning on ambivalent usage of params and work as usual.

## Invocation
- `./fpf.py normalize-typographics`
- `./fpf.py normalize-typographics --input <path> --output <path>`
- `./fpf.py normalize-typographics --input <path> --in-place`

## Constraints
- Do not load entire input into memory.
- Do not modify files outside the output target.
- Keep all typography-related helper functions and constants in a reusable
  module and use it across features (PF-3/4/5/7/8).

## Success Criteria
- Output exists and differs from input only by the defined typographic and
  header normalizations.
