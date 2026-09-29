# AKR Architecture Synthesis v0.2 — Draft

Status: architecture proposal  
Authority: non-canonical draft  
Source basis: AKR v0.1 implementation + observed use cases and failure modes  
Design rule: current repository taxonomy is evidence, not an architectural premise.

## 1. Purpose

AKR exists to externalize reusable reasoning assets so that an AI can recover, select, compose, execute, and validate them across sessions and model providers without depending on chat history or model memory.

The target is not merely an algorithm repository.

The target capability is:

> **Persistent, reconstructable, composable, testable reasoning infrastructure for AI systems.**

## 2. Top-level objectives

AKR should enable an AI system to:

1. recover the intended meaning of a reasoning asset in a fresh session;
2. determine when the asset applies;
3. compose multiple assets without semantic collision;
4. preserve epistemic state, modality, scope, actor, and conditions;
5. stop retrieval and reasoning when additional detail no longer changes the decision;
6. distinguish canonical knowledge from derived indexes and runtime representations;
7. validate that an execution remains faithful to the stored reasoning contract;
8. evolve assets without silently changing the meaning of stable identifiers.

## 3. Non-goals

AKR is not, by default:

- a general document archive;
- a vector database whose retrieval score defines truth;
- a replacement for model weights;
- a general-purpose workflow engine;
- an architecture authority for unrelated AI systems;
- a place where every useful observation must become a reusable asset;
- a guarantee that a stored procedure is correct merely because it is registered.

## 4. Architectural requirements

### R1 — Model independence
Canonical meaning must not depend on a particular LLM, chat product, or memory system.

### R2 — Representation independence
Canonical meaning must survive changes in storage and retrieval implementation.

### R3 — Reconstructability
A fresh AI session must be able to recover purpose, applicability, procedure, constraints, and stop conditions from repository content alone.

### R4 — Composability
Assets must expose enough structure to determine dependencies, conflicts, ordering constraints, and applicability.

### R5 — Semantic preservation
Compression and transformation must preserve:
- evidence state;
- modality;
- actor;
- condition;
- scope;
- temporal qualifier;
- exception;
- authority level.

### R6 — Bounded context
The runtime must retrieve the smallest sufficient set of reasoning assets.

### R7 — Evaluability
Reasoning assets must be testable against representative and adversarial cases.

### R8 — Provenance and evolution
Semantic changes must be versioned and traceable.

### R9 — Authority separation
Canonical source, derived runtime indexes, model-generated summaries, and external architecture authorities must remain distinguishable.

### R10 — Failure-aware execution
The system must be able to represent uncertainty, conflict, unresolved dependencies, and invalid runtime state.

## 5. Failure modes observed or anticipated

The architecture must explicitly resist:

1. **Premature taxonomy lock-in**  
   Early labels such as algorithm/policy/heuristic become permanent architecture without justification.

2. **Prompt-shaped ontology**  
   User wording or conversational structure becomes the data model merely because it appeared first.

3. **Premature closure**  
   A plausible first explanation ends exploration before blind spots are searched.

4. **Modality collapse**  
   OPTION becomes REQUEST or COMMAND; SCENARIO becomes FACT.

5. **Epistemic collapse**  
   INFERRED or UNKNOWN becomes VERIFIED.

6. **Microscope drift**  
   Increasing technical detail continues after it stops changing the decision.

7. **Context flooding**  
   Too many assets are loaded because retrieval optimizes recall rather than sufficiency.

8. **Dependency explosion**  
   Reusable assets recursively pull in large reasoning graphs without bounded resolution.

9. **Authority bleed**  
   Derived SQLite/index/model summary silently overrides canonical source.

10. **Stale runtime**  
    Derived indexes lag canonical source but are still used as current.

11. **Self-modification without governance**  
    AI-generated revisions silently rewrite reasoning contracts.

12. **Actor collapse**  
    Information value is treated as universal despite different incentives, authority, and decisions.

## 6. Capability model

The architecture is defined first by capabilities, not folders.

### C1 — Capture
Preserve candidate reasoning knowledge from conversations, research, and operations without forcing final taxonomy.

Output: candidate asset / observation.

### C2 — Normalize
Separate:
- observation;
- invariant;
- procedure;
- heuristic;
- constraint;
- example;
- test;
- provenance;
- unresolved question.

Output: normalized semantic units.

### C3 — Model
Represent applicability, dependencies, conflicts, inputs, outputs, evidence states, modality, stop conditions, and version lineage.

Output: machine-readable reasoning graph.

### C4 — Resolve
Given a task, identify the minimal applicable reasoning set and resolve dependencies and conflicts.

Output: execution plan.

### C5 — Compose
Order and compress selected assets into a context package while preserving semantics.

Output: bounded execution context.

### C6 — Execute
Apply the selected reasoning process to the current task.

Output: result + execution trace sufficient for validation.

### C7 — Validate
Check:
- semantic fidelity;
- evidence-state preservation;
- modality preservation;
- stop-condition compliance;
- expected behavior on tests.

Output: pass/fail/warnings.

### C8 — Govern
Manage lifecycle:
- draft;
- experimental;
- validated;
- deprecated;
- superseded;
- conflict;
- provenance;
- migration.

Output: controlled evolution.

## 7. Proposed logical planes

These planes are conceptual responsibilities. They do not yet imply folders, services, or databases.

### A. Canonical Reasoning Plane
Stores the authoritative semantic definition of reusable reasoning assets.

### B. Semantic Graph Plane
Represents dependencies, conflicts, applicability, lineage, and composition constraints.

May be compiled from canonical text.

### C. Retrieval and Resolution Plane
Maps a task to candidate assets, resolves dependencies, and stops before context flooding.

### D. Context Composition Plane
Transforms resolved assets into a model-consumable context package with explicit compression constraints.

### E. Execution and Validation Plane
Runs reasoning and checks conformance against asset contracts and tests.

### F. Governance Plane
Controls change, status, provenance, supersession, and fresh-session reconstructability.

## 8. Provisional relationship to v0.1

Current v0.1 elements map into the capability model as follows:

| v0.1 construct | v0.2 interpretation |
|---|---|
| algorithms/ | candidate canonical reasoning assets |
| policies/ | candidate invariant constraints |
| heuristics/ | candidate defeasible reasoning assets |
| registry/ | early metadata catalog; may evolve into semantic graph source |
| context/ | early Retrieval + Context Composition rules |
| runtime/schema.sql | derived runtime representation |
| tests/ | early Validation Plane |
| AGENTS.md | consumption/governance bootstrap contract |

No row above is considered architecturally final.

## 9. Key open architectural questions

1. What is the smallest canonical semantic unit: whole algorithm, rule, operator, constraint, or graph node?
2. Should "policy", "heuristic", and "algorithm" remain first-class types or become metadata over a more general reasoning asset?
3. Should ordering constraints be explicit graph edges rather than embedded prose?
4. How should conflicting assets be represented and resolved?
5. Should examples and tests be embedded with assets or maintained as separate linked entities?
6. How much execution trace is necessary to validate fidelity without storing private chain-of-thought?
7. Should SQLite remain the primary derived runtime, or become one of several compiled targets?
8. When should semantic/vector retrieval be permitted to select assets versus only discover candidates?
9. What constitutes enough evidence to promote an asset from experimental to validated?
10. How should AASA reference AKR without importing its authority model?

## 10. Immediate design principle

Do not migrate v0.1 taxonomy mechanically.

The next step is:

```text
Observed use cases
    ↓
Failure modes
    ↓
System requirements
    ↓
Capability model
    ↓
Logical planes
    ↓
Canonical semantic model
    ↓
Storage/runtime mapping
```

Only after the canonical semantic model is selected should the repository layout be redesigned.
