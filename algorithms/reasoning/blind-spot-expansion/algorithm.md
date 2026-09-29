---
id: ALG-RES-001
name: Blind-Spot Expansion
version: 0.1.0
status: draft
asset_type: algorithm
domain:
  - reasoning
  - research
  - risk_analysis
purpose: Expand the issue space before conclusion or compression to reduce premature closure.
non_goals:
  - maximize the number of issues indefinitely
  - convert all discovered scenarios into external questions
inputs:
  - observed facts
  - current problem framing
  - intended decision
outputs:
  - expanded issue map
  - critical unknowns
  - alternative explanations
  - candidate blind spots
evidence_states:
  - OBSERVED
  - VERIFIED
  - INFERRED
  - HYPOTHESIS
  - SCENARIO
  - UNKNOWN
requires:
  - POL-EVID-001
  - POL-MOD-001
stop_conditions:
  - additional exploration no longer changes a material decision
  - newly discovered issues are lower-value than the cost of investigating them
  - required uncertainty has been explicitly surfaced
supersedes: null
---

# Blind-Spot Expansion

## Procedure

1. Freeze observed facts before extending interpretation.
2. Model the current structure: actors, systems, data, authority, time, and flows.
3. Generate first-order implications.
4. Run a dedicated blind-spot scan across at least:
   - actors
   - data
   - time
   - threats
   - privileges
   - downstream effects
5. Reverse the perspective:
   - What would make the current explanation wrong?
   - Which actor sees a different problem?
   - What historical state is hidden by the current state?
   - What recovery/fallback path bypasses the main control?
6. Label every result by evidence state.
7. Separate internal analysis from externally actionable questions.
8. Apply stop conditions before compression.

## Failure modes

- Premature closure after a plausible first explanation.
- Treating current-state data as the entire historical exposure.
- Treating the observed attack vector as the only threat worth controlling.
- Asking every internally useful question externally.
- Compressing conditional scenarios into instructions.
