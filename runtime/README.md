# Derived Runtime

The SQLite database is a generated artifact.

## Authority rule

If SQLite and canonical Markdown/YAML disagree, canonical source wins.

## Intended build

1. Validate canonical metadata.
2. Parse registry.
3. Parse algorithm/policy front matter.
4. Resolve dependencies and reject cycles.
5. Store normalized metadata in SQLite.
6. Populate FTS5 from canonical text.
7. Record canonical hashes and build metadata.
8. Run test vectors.

## Retrieval strategy

Prefer:
1. exact ID lookup
2. structured domain/trigger filters
3. FTS discovery
4. semantic/vector retrieval only as an optional discovery layer

Do not treat retrieval score as authority or correctness.

## Future extensions

- vector index as a derived sidecar
- dependency graph cache
- runtime linting
- fresh-session reconstruction tests
- conflict/supersession resolution
