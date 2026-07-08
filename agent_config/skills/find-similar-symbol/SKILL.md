---
name: find-similar-symbol
description: "Find code chunks similar to a named symbol — locate parallel implementations."
---

Given a known symbol name, returns other codebase chunks that are semantically similar to its implementation.

## Tool Interface
```
/bin/narsil_client.py find-similar-symbol <symbol_name: str> \
    [--max-results <n: int = 5>]
```

## Usage
Use when refactoring a symbol to check if parallel implementations exist that must be updated in tandem.
