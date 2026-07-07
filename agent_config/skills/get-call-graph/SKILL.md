---
name: get-call-graph
description: "Generate a multi-level call graph rooted at a function."
---

Generates the full call graph for a function up to `depth` levels, showing the complete execution tree of callees.

## Tool Interface
```
/bin/narsil_client.py call-graph <function_name: str> \
    [--depth <n: int = 2>] \
    [--exclude-tests]
```

## Usage
Use to capture the full pipeline view of a complex function before refactoring. Prefer `find-callers`/`find-callees` for targeted upstream/downstream hops.
