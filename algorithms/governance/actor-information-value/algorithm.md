---
id: ALG-GOV-001
name: Actor-Specific Information Value
version: 0.1.0
status: draft
asset_type: algorithm
domain:
  - governance
  - decision_theory
  - communication
purpose: Evaluate information value relative to each actor's incentives, authority, decisions, and costs.
non_goals:
  - assume all actors value the same information
  - equate technical detail with user value
inputs:
  - actors
  - candidate information items
  - decisions
  - incentives
  - authority
  - acquisition cost
outputs:
  - actor-specific information value
  - information-holder map
  - external-query shortlist
  - internal-only issue list
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
  - actionable information for the target actor is identified
  - remaining detail does not change a material decision
  - query cost exceeds expected uncertainty reduction
supersedes: null
---

# Actor-Specific Information Value

## Core model

Information value is actor-relative.

Conceptually:

```text
Value(actor, information)
≈ Decision Impact
× Actionability
× Risk Reduction
× Authority to Act
- Acquisition / Processing Cost
```

This is a reasoning model, not a calibrated numerical formula.

## Procedure

1. Enumerate actors.
2. For each actor, identify:
   - objective / incentive
   - authority
   - risk exposure
   - decisions they can change
   - costs and constraints
3. For each candidate information item, ask:
   - Who needs it?
   - Who possesses it?
   - What decision changes if it is known?
   - Can the target actor act on it?
   - Can the information be abstracted into an actionable assurance?
4. Classify each item:
   - EXTERNAL_HIGH_VALUE
   - INTERNAL_ANALYSIS_ONLY
   - LOW_VALUE / DROP
5. Prefer decision-relevant abstractions over microscope-level implementation detail when communicating externally.
6. Preserve unresolved incentive conflicts explicitly.

## Example transformation

Instead of asking a user-facing service:

> Which exact password hashing primitive, salt layout, and database table were used?

prefer, when that is the decision need:

> Are the leaked credentials still usable, and is any action currently required from affected users?

The internal technical question remains available for engineering or forensic actors.
