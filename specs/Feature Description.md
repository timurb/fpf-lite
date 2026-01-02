# Feature Description - FPF Specification Tooling

## Summary
This repository provides small, local tool to manage the large FPF
specification file so it can fit within LLM context limits. The toolset
focuses on reducing size through semantic compression and splitting the spec
into logical modules that can be loaded on demand.

## Primary Features
- Provide a CLI interface for easy interaction and automation.
- Download the canonical `FPF-Spec.md` from the upstream GitHub source into
  `FPF/FPF-Spec.md`.
- Generate a compressed version that removes non-normative sections while
  preserving rules and checklists.
- Produce an aggressive compressed variant that keeps only normative content
  for strict validation or code-generation workflows.
- Split the spec into major parts (on disk) for further assembly into compressed variant.
- Provide a way to validate the integrity of the split parts against the original spec.
- Assemble spec with reduced number of parts according to user-defined list of parts.

## User Problems Addressed
- The full spec is too large for typical LLM context windows, causing
  resource errors and degraded attention.
- Teams need a smaller, reliable "runtime pack" of rules for interactive use.
- Users need the ability to load only the relevant parts for a given task
  without losing consistency or meaning.

## Inputs and Outputs
- Input: `FPF/FPF-Spec.md` initially downloaded from https://raw.githubusercontent.com/ailev/FPF/refs/heads/main/FPF-Spec.md.
- Outputs:
  - `FPF-Spec-Lite.md` and `FPF-Spec-Aggressive.md` (aggressively stripped variant)
  - Outputs for modular splits to be defined later.

## Success Criteria
- A user can obtain original FPF spec with a single command.
- A user can obtain a smaller spec file or specific module with a single
  command.
- The compressed and split outputs retain normative rules and remain usable
  for LLM prompting.
- Split outputs match the original spec when recombined in the splitter's
  integrity check.
