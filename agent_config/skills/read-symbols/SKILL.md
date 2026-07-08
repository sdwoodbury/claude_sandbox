---
name: read-symbols
description: "Fetch the complete source code of one or more symbols by name — no line numbers needed."
---

Returns the complete, exact source code of one or more named symbols (function, struct, enum, trait, const, etc.) looked up by names across the repository.

## Tool Interface
```
/bin/narsil_client.py symbol <symbol_name: str> [<symbol_name: str> ...] \
    [--context-lines <n: int = 0>]
```

## Usage
Pass one or more symbol names as positional arguments. Results are concatenated with a `# Symbol  <name>` header between each. If you know the symbol name(s), call this directly — do not hunt via `scan-file-skeletons` first. Use `find-symbols-by-pattern` only when the exact name is unknown.
