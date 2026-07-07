---
name: find-similar-code
description: "Find existing codebase logic similar to a raw code snippet — duplication guard."
---

Given a raw code snippet, returns existing codebase chunks that are semantically similar. Use to check for pre-existing abstractions before writing new ones.

## Tool Interface
```
/bin/narsil_client.py similar-code <code_snippet: str> \
    [--max-results <n: int = 5>] \
    [--exclude-tests]
```

## Usage
Call this before implementing any new helper, utility, or transformation function to avoid duplicating existing logic.
