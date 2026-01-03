# PF-2 Spec - Download Canonical FPF Spec

## Status
- Implemented

## Summary
Download the canonical `FPF-Spec.md` from the upstream GitHub source into the
local work directory (default `FPF/`).

## Inputs
- `https://raw.githubusercontent.com/ailev/FPF/refs/heads/main/FPF-Spec.md`

## Outputs
- `<work-dir>/FPF-Spec.md`

## Behavior
- Provide a CLI command that downloads the spec to `<work-dir>/FPF-Spec.md`.
- Create the `<work-dir>` directory if it does not exist.
- Fail with a non-zero exit code and a clear error message on download errors.

## Invocation
- `./fpf-cli download`
- `./fpf-cli download --url <spec-url> --work-dir <dir>`

## Constraints
- Use Python standard library networking for the main script.
- Do not modify any files outside `<work-dir>/FPF-Spec.md`.

## Success Criteria
- Running the command places the file at `<work-dir>/FPF-Spec.md`.
- The script reports the destination path on success.
