# PF-2 Spec - Download Canonical FPF Spec

## Summary
Download the canonical `FPF-Spec.md` from the upstream GitHub source into the
local `FPF/` directory.

## Inputs
- `https://raw.githubusercontent.com/ailev/FPF/refs/heads/main/FPF-Spec.md`

## Outputs
- `FPF/FPF-Spec.md`

## Behavior
- Provide a CLI command that downloads the spec to `FPF/FPF-Spec.md`.
- Create the `FPF/` directory if it does not exist.
- Fail with a non-zero exit code and a clear error message on download errors.

## Invocation
- `./fpf.py download`
- `./fpf.py download --url <spec-url> --output <path>`

## Constraints
- Use Python standard library networking for the main script.
- Do not modify any files outside `FPF/FPF-Spec.md`.

## Success Criteria
- Running the command places the file at `FPF/FPF-Spec.md`.
- The script reports the destination path on success.
