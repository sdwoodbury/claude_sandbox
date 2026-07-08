---
name: get-exports
description: "List all exported symbols from a specific file or module."
---

Returns the public API surface of a file or module: all exported functions, types, constants, and traits.

## Tool Interface
```
/bin/narsil_client.py get-exports <path: str>
```

## Usage
Run this before proposing changes to a module's public interface to understand what external consumers depend on.
