---
name: find-symbols-by-pattern
description: "Find structs, classes, functions, traits, etc. by fuzzy name pattern and/or type filter."
---

Searches all indexed symbols by fuzzy name pattern and optional type filter. Returns matching symbol names, types, and file locations.

## Tool Interface
```
/bin/narsil_client.py find-symbols \
    [--pattern <pattern: str = "*">] \
    [--type    <struct|class|enum|interface|function|method|trait|type|all = "all">] \
    [--file-pattern <glob: str>] \
    [--exclude-tests | --include-tests]
```

## Usage
Use when you know a partial name or concept but not the exact identifier. Output includes the definition file, line number, **and the definition text itself** — so it can answer "where is X defined and what does it look like" in a single call. Once the exact name is resolved, call `read-symbols` to fetch the complete body if needed.
