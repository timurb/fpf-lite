# fpf-cli: FPF Specification Tooling

This repository provides small, local tooling to manage the **First Principles Framework (FPF)** specification (`FPF-Spec.md`) so it fits within LLM context limits.

The full specification is approximately **1,000,000 tokens**. This size challenges even large-context LLMs (Gemini 1.5 Pro, GPT-4 Turbo), causing `resource_exhausted` errors, increased costs, and "Lost in the Middle" attention degradation.

The toolset supports:
- semantic compression (lite and aggressive)
- modular splitting and assembly
- predefined profile manifests for common intents (experimental)

## Features (PF-1 to PF-9)
- **PF-1** CLI interface for interaction and automation.
- **PF-2** Download the canonical `FPF-Spec.md` into `FPF/FPF-Spec.md`.
- **PF-3** Produce a lite compressed variant that removes non-normative sections.
- **PF-4** Produce an aggressive compressed variant for strict validation/codegen.
- **PF-5** Split the spec into per-part files with a YAML manifest.
- **PF-6** Assemble a spec from a manifest-defined part list, with stats output.
- **PF-7** Normalize typographics in the spec (pending).
- **PF-8** Verify the spec for typographic violations (pending).
- **PF-9** Assemble from predefined profile manifests (profiles live in `profiles/`).

## Requirements
- Python 3.10+

## CLI Usage

### Download the spec (PF-2)
```bash
./fpf-cli download
./fpf-cli download --url <spec-url> --work-dir <dir>
```

### Compress the spec (PF-3 / PF-4)
```bash
./fpf-cli strip
./fpf-cli strip-lite --work-dir <dir>
./fpf-cli strip-aggressive --work-dir <dir>
```

Default outputs:
- `<work-dir>/FPF-Spec-Lite.md`
- `<work-dir>/FPF-Spec-Aggressive.md`

### Split into parts (PF-5)
```bash
./fpf-cli split
./fpf-cli split --work-dir <dir>
```

Default outputs:
- `<work-dir>/FPF-Part-Preface.md`
- `<work-dir>/FPF-Part-A.md`, `<work-dir>/FPF-Part-B.md`, ...
- `<work-dir>/FPF-Parts-Manifest.yaml`

### Assemble from parts (PF-6)
```bash
./fpf-cli assemble --manifest <manifest> --work-dir <dir>
```

Manifest format (YAML, minimal subset):
```yaml
output_file: FPF-Spec-Custom.md
parts:
  - FPF-Part-Preface.md
  - FPF-Part-A.md
baseline_file: FPF-Spec.md
```

Rules:
- `output_file`, `parts`, and `baseline_file` must be filenames (no path separators).
- Manifest can be a filename (resolved in `<work-dir>`) or a path to a YAML file.

### Assemble from profiles (PF-9)
```bash
./fpf-cli assemble --profile <name|filename|path> --work-dir <dir>
./fpf-cli assemble --profile <name|filename|path> --profiles-dir <dir> --work-dir <dir>
```

Profile resolution order:
1. If `--profile` is a path, use it as-is.
2. If `--profile` is a filename, resolve it in `--profiles-dir`.
3. If `--profile` is a name (no extension), append `.yaml` and resolve in `--profiles-dir`.

The `profiles/` directory may contain non-profile markdown files that document
the reasoning behind a profile. Only `.yaml` files are treated as profile manifests.


## License and authors
* License:: MIT
* Author:: Timur Batyrshin <erthad@gmail.com>

[FPF](https://github.com/ailev/FPF) is authored by Anatoly Levenchuk and I hold no claims or responsibility for it or for derivatives produced by this tool.
