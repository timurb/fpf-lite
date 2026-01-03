# PF-9 Spec - Manifest Scaffolds for Common Intents (Pending)

## Status
- Pending

## Summary
Provide ready-to-use manifest scaffolds that assemble targeted FPF subsets for
common intents such as SoTA harvesting, architecture design, and tradeoff
evaluation.

## Inputs
- Scaffold name to apply. The same format as manifest but `output` dir is **relative to parts** but not manifest itself.

## Outputs
- Assembled manifest is created in standard output folder assembled manifests unless redefined by user.

## Behavior
- Regular behavior of PF-6 with manifest used from scaffolds folder (configurable).

## Invocation
- `./fpf.py assemble --template <template-name>`

## Constraints
- Do not modify existing part files.
- Do not overwrite existing scaffolds.
- Use UTF-8 encoding for output files.

## Success Criteria
- Scaffold files exist and are valid PF-6 manifests.
- Each scaffold assembles successfully via `./fpf.py assemble --template <template>`.
