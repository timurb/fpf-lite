# PF-6 Spec - Assemble Spec From Parts (Manifest-Driven)

## Status
- Implemented / Здесь какая-то бага, скорее всего в самой постановке задачи

## Summary
Assemble a spec file from a user-provided YAML manifest that lists the output
filename and the ordered part files to include.

## Inputs
- YAML manifest file name (see Manifest Format), located in `<work-dir>` OR a path to the YAML file.
- If a manifest path is specified, set `<work-dir>` to the manifest directory and emit a warning message.
- If a manifest path is specified and `--work-dir` is also provided, use the CLI `--work-dir` value and emit another warning message.
- Part files referenced in the manifest (in `<work-dir>`).
- (Optional) Original file to calculate statistics (`baseline_file`, in `<work-dir>`).

## Outputs
- Assembled spec file at `<work-dir>/<output_file>`.
- Compression-style stats printed to stdout (same format as strip commands) if
  `baseline_file` is present and readable; otherwise a warning is printed and
  stats are skipped.

## Manifest Format
Top-level YAML mapping with:
- `output_file`: `<filename>`
- `parts`: `<list of part filenames>`
- `baseline_file`: `<filename>` (optional; used for stats if present)

## Behavior
- Parse the manifest as YAML.
- Determine `<work-dir>` based on `--manifest`:
  - If `--manifest` is a path and `--work-dir` is not set, use the manifest directory and emit a warning.
  - If `--manifest` is a path and `--work-dir` is set, use `--work-dir` and emit another warning.
- Validate required keys: `output_file`, `parts`.
- Treat `parts` as an ordered list; assemble output by concatenating listed
  part files in order.
- Fail if any part listed in `parts` is missing or unreadable.
- Write the assembled output exactly as the parts appear, without added
  separators or whitespace changes.
- If `baseline_file` is present, load it to gather statistics. If the file is
  not found or not readable, print a warning and keep working.
- Produce stats using the same format as strip commands:
  - `Stats for <output>`
  - `Removal statistics:` (empty unless populated by future rules)
  - `Lines: <baseline> -> <output> (Reduction: X%)`
- Resolve the manifest file as:
  - the provided path if `--manifest` includes a path, or
  - `<work-dir>/<manifest-name>` if `--manifest` is a filename.
- Resolve `parts` and `baseline_file` entries relative to `<work-dir>`.
- Resolve `output_file` relative to `<work-dir>`.
- Reject absolute paths inside the manifest.

## Invocation
- `./fpf.py assemble --manifest <manifest-name> --work-dir <dir>`

## Constraints
- Do not modify part files.
- Do not load entire part files into memory; stream line-by-line.
- Write output with UTF-8 encoding.
- Accept only a minimal YAML subset: top-level mapping with `output_file` (string),
  `parts` (list of strings), and `baseline_file` (string, optional).
  - `output_file` MUST be a filename (no path separators).
  - `parts` and `baseline_file` entries MUST be filenames (no path separators).
- `--manifest` MAY be a filename (resolved within `<work-dir>`) or a path to a YAML file.

## Success Criteria
- The assembled file equals the concatenation of the listed parts, in order.
- If `baseline_file` is present and readable, stats are printed and computed
  against its line count.
- If all parts are included the produced file should exactly match the original file (a test with FPF-Spec.md downloaded from internet)
