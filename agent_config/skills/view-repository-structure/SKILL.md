---
name: view-repository-structure
description: "Return a directory tree of the workspace to orient before searching."
---

Returns a visual directory tree of the workspace up to `max_depth` levels. Use to understand project architecture and module boundaries before searching.

## Tool Interface
```
/bin/narsil_client.py view-repository-structure [--max-depth <n: int = 3>]
```

## Usage
Run with `max_depth=2` or `3` first to get a clean overview without dumping leaf files. Increase depth only to inspect a specific subtree. Always run this when onboarding onto an unfamiliar crate or repository.
