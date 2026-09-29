---
id: POL-MOD-001
name: Modality Preservation
version: 0.1.0
status: draft
asset_type: policy
---

# Modality Preservation

Compression, summarization, and delegation must preserve the force of a statement.

## Modal categories

- FACT
- INFERENCE
- HYPOTHESIS
- SCENARIO
- OPEN QUESTION
- OPTION
- RECOMMENDATION
- REQUEST
- REQUIREMENT
- COMMAND

## Rule

Do not transform a weaker modality into a stronger modality without explicit authorization or a separately justified decision.

Example:

> If identity documents were leaked, credit-bureau protective measures could be considered.

must not become:

> Register protective measures with every credit bureau.

The first is a conditional scenario plus option. The second is an unconditional instruction.

## Compression check

Before emitting a compressed form, ask:
1. Did a condition disappear?
2. Did an option become a request or command?
3. Did uncertainty disappear?
4. Did the responsible actor change?
5. Did the time horizon or scope broaden?
