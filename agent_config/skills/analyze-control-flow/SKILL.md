---
name: analyze-control-flow
description: "Map basic blocks, conditional branches, and loops inside a function."
---

Produces a structural control-flow graph for a function: basic blocks, conditional branches (if/match arms), and loop cycles. Use to isolate dead branches or unhandled match variants.

## Tool Interface
```
/bin/narsil_client.py control-flow <path: str> <function_name: str>
```

## Usage
Use when a bug is localized to a single dense conditional or match block. Do not guess branch evaluations — read the graph output directly.
