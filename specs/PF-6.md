# PF-6 Spec - Assemble Spec From Parts (Manifest-Driven)

## Status
- Implemented

## Summary
Assemble a spec file from a user-provided YAML manifest that lists the output
filename and the ordered part files to include.

## Inputs
- YAML manifest file (see Manifest Format)
- Part files referenced in the manifest

## Outputs
- Assembled spec file at the manifest `output` path.
- Compression-style stats printed to stdout (same format as strip commands).

## Manifest Format
Top-level YAML mapping with:
- `output`: `<path>`
- `parts`: `<list of part filenames>`
- `baseline_manifest`: `<path>` (required for stats; YAML manifest listing the full parts set). Defaults to default FPF-Spec.md location.

Paths may be absolute or relative to the manifest file directory.

## Behavior
- Parse the manifest as YAML.
- Validate required keys: `output`, `parts`, `baseline_manifest`.
- Load `baseline_manifest` and read its `parts` list. If the manifest is not found or not readable produce warning message but keep working.
- Treat `parts` as an ordered list; assemble output by concatenating listed
  part files in order.
- Fail if any part listed in `parts` is missing or unreadable.
- Fail if `parts` contains an entry not present in the baseline `parts` list.
- Write the assembled output exactly as the parts appear, without added
  separators or whitespace changes.
- Produce stats using the same format as strip commands:
  - `Stats for <output>`
  - `Removal statistics:` listing each baseline part not included (count 1 per part).
  - `Lines: <baseline> -> <output> (Reduction: X%)`

## Invocation
- `./fpf.py assemble --manifest <manifest-path>`

## Constraints
- Do not modify part files.
- Do not load entire part files into memory; stream line-by-line.
- Write output with UTF-8 encoding.
- Accept only a minimal YAML subset: top-level mapping with `output` (string),
  `parts` (list of strings), and `baseline_manifest` (string).

## Success Criteria
- The assembled file equals the concatenation of the listed parts, in order.
- Stats are printed and computed against the baseline manifest's full parts set.
- If all parts are included the produced file should exactly match the original file (a test with FPF-Spec.md downloaded from internet)
