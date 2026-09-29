# AKR AI Consumption Contract

This file defines how an AI agent should use this repository.

## Authority

1. Canonical authority is the repository's Markdown/YAML/JSON source.
2. Files under `runtime/` that are generated databases or indexes are derived artifacts.
3. If a derived artifact conflicts with canonical source, canonical source wins.
4. Chat history, model memory, and generated summaries are not authority for AKR content.

## Retrieval sequence

For an ordinary task:

1. Read `registry/registry.yaml`.
2. Select the smallest set of candidate algorithms by trigger and domain.
3. Read the selected algorithm file(s).
4. Resolve `requires` recursively.
5. Read required policies.
6. Read test vectors only when validating interpretation or behavior.
7. Do not load the whole repository unless performing a repository-wide audit.

## Execution rules

- Preserve evidence states.
- Preserve modality.
- Keep UNKNOWN distinct from SAFE and UNSAFE.
- Run blind-spot expansion before final compression when premature closure is material.
- Apply actor-specific information value before sending external questions or requests.
- Stop when further detail no longer changes a material decision.

## Mutation rules

When adding or changing an asset:

1. Give it a stable ID.
2. Update the registry.
3. Increment the asset version when semantics change.
4. Add or update tests for changed behavior.
5. Preserve supersession/history rather than silently repurposing an ID.
6. Rebuild and validate the derived runtime.

## Fresh-session reconstruction test

A fresh AI session should be able to:
- identify the asset's purpose,
- distinguish goals from non-goals,
- recover its decision procedure,
- preserve epistemic and modal state,
- identify its stop conditions,
- execute representative tests,

using only canonical repository content.
