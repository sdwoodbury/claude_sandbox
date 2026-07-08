---
name: catalog-usages
description: "Find cross-file symbol usages, optionally including import sites."
---

Locates all cross-file usages of a symbol, including import statements unless suppressed.

## Tool Interface
```
/bin/narsil_client.py catalog-usages <symbol_name: str> \
    [--no-imports] \
    [--exclude-tests]
```

## Difference from find-references
`catalog-usages` includes import sites by default; `find-references` focuses on call/usage sites. Use `catalog-usages` for migration impact analysis, `find-references` for call-site audits.
