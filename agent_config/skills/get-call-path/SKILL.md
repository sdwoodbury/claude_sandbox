---
name: get-call-path
description: "Find the execution path between two distinct functions."
---

Returns the shortest call chain linking `from_function` to `to_function` across the codebase.

## Tool Interface
```
/bin/narsil_client.py get-call-path <from_fn: str> <to_fn: str>
```

## Usage
Use when you need to trace execution flow from a known entrypoint to a target function — e.g. "how does `main` eventually reach `flush_buffer`?" Returns the shortest call chain linking the two. Also useful for verifying that two separate modules are connected and understanding the middleware between them. Both functions must be indexed symbols.
