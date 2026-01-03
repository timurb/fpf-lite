# Feature Description - FPF Specification Tooling

## Status
- Implemented

## Summary
This repository provides small, local tooling to manage the large FPF
specification file so it can fit within LLM context limits. The toolset
focuses on reducing size through semantic compression and splitting the spec
into logical modules that can be loaded on demand.

## Primary Features
- PF-1 Provide a CLI interface for easy interaction and automation.
- PF-2 ([specs/PF-2.md](PF-2.md)) Download the canonical `FPF-Spec.md` from the
  upstream GitHub source into `FPF/FPF-Spec.md`.
- PF-3 ([specs/PF-3.md](PF-3.md)) Generate a compressed version that removes
  non-normative sections while preserving rules and checklists, and display
  compression stats.
- PF-4 ([specs/PF-4.md](PF-4.md)) Produce an aggressive compressed variant that
  keeps only normative content for strict validation or code-generation
  workflows, and display compression stats.
- PF-5 ([specs/PF-5.md](PF-5.md)) Split the FPF spec into major parts (on disk)
  for further assembly into a compressed variant.
- PF-6 ([specs/PF-6.md](PF-6.md)) Assemble a spec with a reduced number of
  parts according to a user-defined list of parts.
- PF-7 ([specs/PF-7.md](PF-7.md)) Normalize typographics in the spec into a
  standard ASCII form. (Pending)
- PF-8 ([specs/PF-8.md](PF-8.md)) Verify the spec for typographic violations and
  fail if any are found. (Pending)
- PF-9 Create manifest templates for common intents (SoTA harvesting,
  architecture design, tradeoff evaluation). (Pending)

## User Problems Addressed
- UP-1 The full spec is too large for typical LLM context windows, causing
  resource errors and degraded attention.
- UP-2 Teams need a smaller, reliable "runtime pack" of rules for interactive
  use.
- UP-3 Users need the ability to load only the relevant parts for a given task
  without losing consistency or meaning.

## Inputs and Outputs
- IO-1 Input: `FPF/FPF-Spec.md` initially downloaded from
  `https://raw.githubusercontent.com/ailev/FPF/refs/heads/main/FPF-Spec.md`.
- IO-2 Outputs:
  - IO-2.1 `FPF/FPF-Spec-Lite.md` and
    `FPF/FPF-Spec-Aggressive.md` (aggressively stripped variants)
  - IO-2.2 Outputs for modular splits to be defined later.

## Success Criteria
- SC-1 A user can obtain the original FPF spec with a single command.
- SC-2 A user can obtain a smaller spec file or specific module with a single
  command.
- SC-3 The compressed and split outputs retain normative rules and remain usable
  for LLM prompting.
- SC-4 Split outputs match the original spec when recombined in the splitter's
  integrity check.

## TODOs
- [ ] Produce warnings on format drift in upstream
- Fix format in upstream for returning of fixes:
  - [ ] Part headers
  - [ ] Hyphens and typographics
