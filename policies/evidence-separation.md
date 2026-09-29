---
id: POL-EVID-001
name: Evidence State Separation
version: 0.1.0
status: draft
asset_type: policy
---

# Evidence State Separation

Every material claim should retain its epistemic state when practical.

## States

- **OBSERVED** — directly observed in source material, system behavior, or measurement.
- **VERIFIED** — supported by authoritative or independent corroborating evidence.
- **INFERRED** — logically derived from observations but not directly established.
- **HYPOTHESIS** — plausible explanation awaiting evidence.
- **SCENARIO** — conditional possibility used for planning or threat modeling.
- **UNKNOWN** — information needed for a decision but not established.

## Invariants

1. UNKNOWN is neither SAFE nor UNSAFE.
2. INFERRED must not be rewritten as VERIFIED merely for brevity.
3. A SCENARIO must not be presented as the cause of an observed event without evidence.
4. Missing public information is not evidence that a control is absent.
5. Company self-description is evidence of the claim being made, not automatically evidence that implementation matches the claim.
