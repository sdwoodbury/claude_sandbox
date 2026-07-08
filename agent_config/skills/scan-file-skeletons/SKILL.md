---
name: scan-file-skeletons
description: "Map one or more files' AST structure before any targeted reads. Use this FIRST when opening new files."
---

Returns a lightweight outline of one or more files broken down by AST logic (structs, fns, impls, modules, etc.) without pulling full bodies into context.

## Tool Interface
```
/bin/narsil_client.py scan-file-skeletons --file <file_path: str> [--file <file_path: str> ...]
```

The `--file` flag is repeatable — pass it multiple times to skeleton several files in a single call.

## Usage
Always call this before `get-chunks-by-lines` or `view-symbols` on unfamiliar files. Use the returned skeleton line numbers as inputs to subsequent targeted reads. When opening several related files at once, pass them all in one call to reduce round-trips.
