# FPF Specification Tooling

This repository provides small, local tooling to manage the **First Principles Framework (FPF)** specification (`FPF-Spec.md`) so it fits within LLM context limits.

The full specification is approximately **1,000,000 tokens**. This size challenges even large-context LLMs (Gemini 1.5 Pro, GPT-4 Turbo), causing `resource_exhausted` errors, increased costs, and "Lost in the Middle" attention degradation.

The toolset supports two workflows:
- semantic compression (lite and aggressive)
- modular splitting and assembly

## Features (PF-1 to PF-6)
- **PF-1** CLI interface for interaction and automation.
- **PF-2** Download the canonical `FPF-Spec.md` into `FPF/FPF-Spec.md`.
- **PF-3** Produce a lite compressed variant that removes non-normative sections.
- **PF-4** Produce an aggressive compressed variant for strict validation/codegen.
- **PF-5** Split the spec into per-part files with a YAML manifest.
- **PF-6** Assemble a spec from a manifest-defined part list, with stats output.

## Requirements
- Python 3.10+

## CLI Usage

### Download the spec (PF-2)
```bash
./fpf.py download
./fpf.py download --url <spec-url> --output <path>
```

### Compress the spec (PF-3 / PF-4)
```bash
./fpf.py strip
./fpf.py strip-lite --input FPF/FPF-Spec.md --output FPF/FPF-Spec-Lite.md
./fpf.py strip-aggressive --input FPF/FPF-Spec.md --output FPF/FPF-Spec-Aggressive.md
```

Default outputs:
- `FPF/FPF-Spec-Lite.md`
- `FPF/FPF-Spec-Aggressive.md`

### Split into parts (PF-5)
```bash
./fpf.py split
./fpf.py split --input FPF/FPF-Spec.md --output-dir FPF/parts
```

Default outputs:
- `FPF/parts/FPF-Part-Preface.md`
- `FPF/parts/FPF-Part-A.md`, `FPF/parts/FPF-Part-B.md`, ...
- `FPF/parts/FPF-Parts-Manifest.yaml`

### Assemble from parts (PF-6)
```bash
./fpf.py assemble --manifest <manifest-path>
```

Manifest format (YAML, minimal subset):
```yaml
output: FPF/FPF-Spec-Custom.md
parts:
  - FPF-Part-Preface.md
  - FPF-Part-A.md
baseline_manifest: FPF/parts/FPF-Parts-Manifest.yaml
```

Paths can be absolute or relative to the manifest file directory.