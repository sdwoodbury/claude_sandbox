---
name: workspace-search
description: "Fuzzy-search for symbols by name across the entire workspace."
---

Performs a fuzzy name search across all workspace symbols, returning matches with their type and location.

## Tool Interface
```
/bin/narsil_client.py workspace-search <fuzzy_name: str> \
    [--kind  <function|class|struct|interface|enum|variable|all = "all">] \
    [--limit <n: int = 10>]
```

## Usage
Use when you have a rough idea of a symbol name but don't know the exact casing, module, or file. Follow up with `read-symbols` once the exact name is identified.
