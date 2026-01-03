# PF-8 Spec - Verify Typographics

## Status
- Pending

## Summary
Verify that the spec contains only standard ASCII typography and normalized Part
headers. Report all violations and fail if any are found.

## Inputs
- `<work-dir>/FPF-Spec.md` (default; configurable via `--input`)

## Outputs
- None. Reports violations to stdout/stderr.

## Behavior
- Read input line-by-line.
- Flag any occurrence of:
  - U+2011, U+2013, U+2014
  - U+00A0
  - U+2018, U+2019, U+201C, U+201D
- Flag Part header lines that are not already in the normalized form defined in
  PF-7.
- Report all violations (do not fail fast). Each report includes line number
  and a short reason.
- Exit with non-zero status if any violations are found.

## Invocation
- `./fpf-cli check-typographics`
- `./fpf-cli check-typographics --work-dir <dir>`
- `./fpf-cli check-typographics --input <filename> --work-dir <dir>`

## Constraints
- Do not load entire input into memory.
- Keep all typography-related helper functions and constants in a reusable
  module and use it across features (PF-3/4/5/7/8).
- `--input` MUST be a filename resolved within `<work-dir>`.

## Success Criteria
- Exit code 0 when no violations are found.
- Exit code non-zero and all violations reported when violations exist.
