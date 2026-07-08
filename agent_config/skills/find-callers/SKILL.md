---
name: find-callers
description: "Find all functions that call the specified function, with optional transitive traversal."
---

Finds the set of functions that directly (or transitively) call `function_name`. Use to trace upstream execution paths.

## Tool Interface
```
/bin/narsil_client.py find-callers <function_name: str> \
    [--max-depth <n: int = 1>] \
    [--transitive] \
    [--exclude-tests]
```

## Usage
Use with `max_depth=1` first for direct callers. Increase depth or use `--transitive` only when tracing a panic or cascading failure upstream.
