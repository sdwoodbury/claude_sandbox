---
name: narsil_symbol_lookup
description: "Standard Operating Procedure for symbol lookup."
---

# Critical Tool Restrictions

You are strictly prohibited from using standard bash tools (`cat`, `grep`, `rg`) or traditional line-number language server lookups (`ra_tool.py`) to navigate code. They are highly inefficient and flood your context window.

You MUST use the native Narsil MCP tools according to this precise workflow:

## 1. Finding & Inspecting Symbols (The Precision Strike)
* **Do not search for coordinates:** Never try to find a symbol's line number just to read it.
* **Direct Lookup:** Use the `read_symbol` MCP tool directly with the symbol name. Narsil is AST-aware and will immediately return the entire, complete source code block for that symbol in a single call.
* **Fuzzy Patterns:** If you only know a partial name, use `find_symbols_by_pattern` or `workspace_search` to locate the exact symbol identifier first, then call `read_symbol`.

## 2. File Reading & Exploration
* **Initial Map:** Never `cat` a whole file. Always call `scan_file_skeleton` first. This returns a lightweight outline of the file's structures and signatures while hiding the heavy implementation bodies to preserve your context window.
* **Targeted Extraction:** Once you identify the target block in the skeleton, use `read_symbol` or `read_excerpt` to pull the exact implementation code you need.
