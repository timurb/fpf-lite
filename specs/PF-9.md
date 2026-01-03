# PF-9 Spec - Manifest Profiles for Common Intents (Pending)

## Status
- Pending

## Summary
Provide ready-to-use manifest profiles that assemble targeted FPF subsets for
common intents such as SoTA harvesting, architecture design, and tradeoff
evaluation.

## Inputs
- Profile manifest name (filename without extension, `.yaml` implied), filename, or path to apply (resolution order: path, filename, name).
- Assemble CLI parameter: `--work-dir`.
- Profiles directory (default: `profiles/`), configurable via `--profiles-dir`.

## Outputs
- Assembled spec file at `<work-dir>/<output_file>` where `output_file` is taken
  from the profile manifest.

## Behavior
- Regular behavior of PF-6 with profile manifest resolved from the profiles directory instead of work-dir.
- Resolve `--profile` in this order:
  - If `--profile` is a path, use it as-is.
  - If `--profile` is a filename, resolve it within `--profiles-dir`.
  - If `--profile` is a name (filename without extension), append `.yaml` and resolve within `--profiles-dir`.
- File names inside the profile manifest are resolved relative to `--work-dir`.
- `output_file` inside the profile is resolved relative to `--work-dir`.

## Invocation
- `./fpf-cli assemble --profile <profile> --work-dir <dir> --profiles-dir <dir>`

## Constraints
- Do not modify existing part files.
- Use UTF-8 encoding for output files.
- Profiles directory is independent of `--work-dir`.

## Success Criteria
- Profile files exist and are valid PF-6 manifests.
- Each profile assembles successfully via `./fpf-cli assemble --profile <profile-name>`.
