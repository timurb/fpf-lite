# PF-9 Spec - Manifest Scaffolds for Common Intents (Pending)

## Status
- Pending

## Summary
Provide ready-to-use manifest scaffolds that assemble targeted FPF subsets for
common intents such as SoTA harvesting, architecture design, and tradeoff
evaluation.

## Inputs
- Scaffold name to apply.
- Assemble CLI parameter: `--work-dir`.

## Outputs
- Assembled spec file at `<work-dir>/<output_file>` where `output_file` is taken
  from the scaffold.

## Behavior
- Regular behavior of PF-6 with scaffold resolved from the work directory.
- Paths inside the scaffold are resolved relative to `--work-dir`.
- `output_file` inside the scaffold is resolved relative to `--work-dir`.

## Invocation
- `./fpf.py assemble --scaffold <template-name> --work-dir <dir>`

## Constraints
- Do not modify existing part files.
- Use UTF-8 encoding for output files.

## Success Criteria
- Scaffold files exist and are valid PF-6 manifests.
- Each scaffold assembles successfully via `./fpf.py assemble --scaffold <template-name>`.
