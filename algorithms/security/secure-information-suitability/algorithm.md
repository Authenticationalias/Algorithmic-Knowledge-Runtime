---
id: ALG-SEC-001
name: Secure Information Handling Suitability
version: 0.2.0
status: draft
asset_type: algorithm
domain:
  - security
  - privacy
  - risk_decision
purpose: Determine whether a service is suitable for entrusting a particular class of information for a particular use case.
non_goals:
  - declare a service globally safe or unsafe
  - infer incident causality from technology age alone
  - replace professional penetration testing or forensic investigation
inputs:
  - service
  - data_type
  - purpose
  - user_controls
outputs:
  - suitability_by_data_class
  - provider_only_risks
  - user_controllable_risks
  - critical_unknowns
  - recommended_action
evidence_states:
  - OBSERVED
  - VERIFIED
  - INFERRED
  - HYPOTHESIS
  - SCENARIO
  - UNKNOWN
requires:
  - ALG-RES-001
  - ALG-GOV-001
  - POL-EVID-001
  - POL-MOD-001
stop_conditions:
  - a decision can be made with current evidence
  - remaining unknowns cannot reasonably change the decision
  - marginal value of further investigation is below its cost
supersedes: null
---

# Secure Information Handling Suitability

## Decision object

Do not ask whether a site is simply "secure."

Evaluate:

```text
(Service, DataType, Purpose, UserControls)
```

The same provider can be suitable for a low-sensitivity email alias and unsuitable for persistent biometric or identity-document storage.

## Phase 1 — Data sensitivity

Evaluate:
- identification power
- revocability / changeability
- correlation power
- authority-enabling power
- persistence of harm

Increase scrutiny when data is difficult to revoke and useful for identity proofing or cross-dataset linkage.

## Phase 2 — Necessity and minimization

Before asking whether storage is secure, ask:
1. Is collection necessary?
2. Can weaker data satisfy the purpose?
3. Can verification occur without retaining the raw source?
4. Can retention duration be shortened?

Prefer strong verification with minimal raw-data retention.

## Phase 3 — Trust boundaries

Map all actors that can reach the data, including providers, merchants, processors, identity services, cloud services, and recovery channels.

Apply ALG-GOV-001 to distinguish their incentives and information needs.

## Phase 4 — Observable security surface

Inspect proportionally to data sensitivity:
- HTTPS / TLS
- HSTS / CSP / other browser security controls
- cookies and session attributes
- third-party scripts
- framework / technology fingerprints
- authentication and MFA
- recovery and account-change flows

## Phase 5 — Technology lifecycle

For any detected technology:

```text
Fingerprint
→ Lifecycle Status
→ Maintenance Model
→ Security-Boundary Relevance
```

EOL alone is a risk signal, not proof of exploitability or incident causality.

Ask whether maintenance is provided by upstream support, a vendor-maintained fork, or compensating controls.

## Phase 6 — Authentication graph

Evaluate the whole graph, not only login:

```text
Login
∩ MFA
∩ Recovery
∩ Email/Phone Change
∩ Support Override
∩ Session Management
```

A strong primary authenticator can be undermined by a weak recovery path.

## Phase 7 — Data lifecycle

Map:

```text
Collect → Store → Copy → Update → Archive → Delete
```

Check current and historical values, account closure, backups, raw identity images, and retention policy where decision-relevant.

## Phase 8 — Incident maturity

If incidents exist, evaluate:
- detection
- containment
- first notice
- scope correction
- affected-user notification
- credential/session invalidation
- follow-up reporting
- remediation
- distinction between confirmed, investigating, unknown, and non-public states

## Phase 9 — Blind-spot expansion

Invoke ALG-RES-001 before finalizing.

## Phase 10 — User-compensable vs provider-only risk

Examples of user-compensable risk:
- password reuse
- email correlation
- optional MFA not enabled

Examples of provider-only risk:
- raw identity-document retention
- internal access controls
- server compromise
- backup retention
- provider-side deletion behavior

Do not subtract provider-only risk merely because the user has strong endpoint security.

## Phase 11 — Hard gates

For high-sensitivity data, do not allow strong average scores to cancel a critical failure.

Potential hard-gate concerns include:
- weak recovery that bypasses strong authentication
- indefinite raw identity-data retention with no clear necessity
- unsupported critical technology with an unclear maintenance model
- unresolved critical unknowns when practical alternatives exist

## Phase 12 — Value of further investigation

Before deeper technical inspection, ask whether the answer could change the user's decision.

Prefer high-value questions such as:
- retention of identity images
- recovery bypasses
- current validity of leaked credentials

over low-value microscope detail that does not change action.

## Output

Avoid one-dimensional "security scores."

Prefer:
- normal use
- use with controls
- minimize disclosure
- avoid high-sensitivity use
- migrate / choose an alternative

Always state:
- observed protections
- provider-only risks
- user-controllable risks
- critical unknowns
- evidence state for material conclusions
