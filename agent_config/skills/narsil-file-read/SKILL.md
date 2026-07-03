---
name: narsil_file_read
description: "SOP for file reading. Directs the agent to use native MCP tools."
---

# Critical Tool Usage Rules

You are strictly prohibited from using standard bash tools (`cat`, `grep`, `rg`, `sed`, `head`, `tail`) to read files or search code. They break context windows and fail on this infrastructure.

Instead, you must use the provided native MCP tools according to this precise workflow:

1. **File Exploration:** Always call `scan_file_skeleton` first when opening a file. This returns a token-efficient map of symbols and boundaries without flooding your context window with raw implementation code.
2. **Targeted Read:** After finding the symbol you need in the skeleton, use `read_symbol` to fetch its exact, full implementation source code.
3. **Range/Error Context:** If you need to view a raw line range (e.g., from a stack trace), use `read_excerpt`. This automatically expands your range to return logically complete code blocks rather than blind line cuts.
