---
name: analyze-dependencies
description: "Analyze imports and dependents for a specific file — who it imports and who imports it."
---

Returns the import graph for a given file path: what it imports (`imports`), what imports it (`imported_by`), or both.

## Tool Interface
```
/bin/narsil_client.py deps <path: str> \
    [--direction <imports|imported_by|both = "both">]
```

## Usage
Run with `--direction "both"` before proposing any refactor to establish the full blast radius of consumers and dependencies.
