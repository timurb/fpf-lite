# FPF Specification Tooling

This repository contains utilities for managing the **First Principles Framework (FPF)** specification (`FPF-Spec.md`).

The full specification is approximately **1,000,000 tokens**. This size challenges even large-context LLMs (Gemini 1.5 Pro, GPT-4 Turbo), causing `resource_exhausted` errors, increased costs, and "Lost in the Middle" attention degradation.

These tools provide two strategies to solve this: **Semantic Compression** and **Modular Splitting**.

---

## 🛠 Tools

### 1. Semantic Compressor (`fpf_compress.py`)

**Strategy:** Increases *instruction density* by stripping non-normative text.

*   **Input:** `FPF-Spec.md`
*   **Output:** `FPF-Spec-Compressed.md`
*   **What it does:** Removes introductory essays (Preface), historical context (SoTA-Echoing), and table of contents.
*   **Modes:**
    *   `AGGRESSIVE_MODE = False` (Default): Removes Preface/SoTA. Reduces size by ~25%. Good for general context.
    *   `AGGRESSIVE_MODE = True`: Removes `Problem`, `Forces`, and `Rationale` sections. Leaves only `Solution` and `Conformance Checklists`. Reduces size by ~50%. Best for strict code generation or validation tasks.

### 2. Modular Splitter (`fpf_split.py`)

**Strategy:** Logic-aware splitting based on the FPF "Hourglass Architecture". It allows you to load only the specific layers relevant to your task.

*   **Input:** `FPF-Spec.md`
*   **Output:** Three logical modules.
*   **Integrity:** Includes a self-test that reconstructs the file in memory and verifies it byte-for-byte against the source before writing modules.

| Module File | Content | Context | Use Case |
| :--- | :--- | :--- | :--- |
| **`FPF-Module-Kernel.md`** | **Preface, Part A, Part E** | **Mandatory** | The Core. Defines Ontology, Roles, and Lexicon (`E.10`). Always include this to set the model's "operating system" and speaking style. |
| **`FPF-Module-Logic.md`** | **Part B, Part F** | **Optional** | The Engine. Defines Reasoning cycles, Trust calculus (`B.3`), and Unification/Bridging (`F.9`). Load for complex reasoning tasks. |
| **`FPF-Module-Domain.md`** | **Part C, D, G, Appendices** | **On Demand** | The Library. Specific Architheories (Creativity, Ethics, SoTA). Load only when specific domain definitions are needed. |

---

## 🚀 Usage

### Requirements
*   Python 3.x

### Execution
1.  Clone the repository
2.  Run the command:

```bash
python fpf-lite/fpf_compressor.py
```

3.  The script will create 2 files: `FPF-Spec-Lite.md` (Removes only Preface and SoTA) and `FPF-Spec-Aggressive.md` (Also removes Problem, Forces, Rationale. Leaves only dry rules).

4. Alternative: Generate the modular splits
```bash
python fpf_split.py
```

---

## 🧠 Prompt Engineering Strategy

How to construct your System Prompt based on your goal:

### Scenario A: "Act as an FPF Expert" (General Chat)
*   **Goal:** General Q&A, style mimicking.
*   **Files:** `FPF-Spec-Compressed.md`
*   **Why:** The compressed file fits in context and retains enough "flavor" for chat.

### Scenario B: "Validate this Architecture" (Reasoning)
*   **Goal:** Deep reasoning, checking against rules, finding contradictions.
*   **Files:** `FPF-Module-Kernel.md` + `FPF-Module-Logic.md`
*   **Why:** You need the full Rationale and Forces (which compression might strip) to understand *why* a rule exists, but you don't need the specific definitions of "Creativity" or "Ethics" (Domain module).

### Scenario C: "Design a Metric" (Domain Specific)
*   **Goal:** Creating specific artifacts using Part C/G patterns.
*   **Files:** `FPF-Module-Kernel.md` + `FPF-Module-Domain.md`
*   **Why:** You need the Lexicon (Kernel) and the specific Metric templates (Domain).

---

## ⚠️ Notes on `SoTA-Echoing` Removal
The `fpf_compress.py` script uses a smart filter to remove "State of the Art" historical comparisons (which are noise for the LLM) while preserving normative requirements regarding SoTA (e.g., in `G.2` or `E.15`). It handles non-breaking hyphens (`\u2011`) used in the spec text.

## TODOs

 - [ ] Combine the modular split and compressed version into a single workflow.
 - [ ] Implement splitting into parts in text files and then recombining them (this was original intent but LLM did that in memory)