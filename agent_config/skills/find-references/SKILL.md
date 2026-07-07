---
name: find-references
description: "Find all references to a named symbol across the codebase."
---

Locates every site in the repository where `symbol_name` is referenced (call sites, type annotations, macro invocations, etc.).

## Tool Interface
```
/bin/narsil_client.py refs <symbol_name: str> \
    [--include-definition | --no-include-definition] \
    [--exclude-tests | --include-tests]
```

## Usage
Use returned line numbers as inputs to `read-excerpts` for full context around each reference site.

If you need the body of each reference site — not just its location — use **`search-chunks`** instead. It returns the same file/line info plus the full enclosing code block for each match.
