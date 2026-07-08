---
name: find-callees
description: "Find all functions called BY the specified function, with optional transitive traversal."
---

Returns the set of functions that `function_name` calls directly (or transitively). Use to trace downstream execution paths.

## Tool Interface
```
/bin/narsil_client.py find-callees <function_name: str> \
    [--max-depth <n: int = 1>] \
    [--transitive] \
    [--exclude-tests]
```

## Usage
Use at `max_depth=1` to see immediate dependencies. Use `--transitive` to map the full downstream blast radius before a refactor.
