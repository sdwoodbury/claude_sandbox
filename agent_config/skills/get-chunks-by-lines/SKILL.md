---
name: get-chunks-by-lines
description: "Retrieve the full AST chunk(s) that contain given line numbers from a file."
---

For each `--line` arg, returns the complete AST chunk (function body, struct block, impl block, etc.) that contains that line. Safe — never reads partial syntactic units.

## Tool Interface
```
/bin/narsil_client.py get-chunks-by-lines \
    --file  <file_path: str> \
    --line <line1: int> [--line <line2: int> ...]
```

## Usage
Feed line numbers from `scan-file-skeletons` or `find-references` output here. Never guess line numbers — always derive them from a prior tool call.
