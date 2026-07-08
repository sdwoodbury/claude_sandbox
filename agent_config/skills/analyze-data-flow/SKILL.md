---
name: analyze-data-flow
description: "Trace variable definitions, mutations, and consumption sites within a function."
---

Returns intra-function data-flow information: where each variable is defined, mutated, and consumed. Use to eliminate state-override bugs and ownership ambiguities.

## Tool Interface
```
/bin/narsil_client.py analyze-data-flow <path: str> <function_name: str>
```

## Usage
Use when tracking a value mutation chain or ownership transfer through a non-trivial function. Pair with `analyze-control-flow` for full intra-function diagnostics.
