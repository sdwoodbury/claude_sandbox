---
name: narsil-file-inspection
description: "Standard Operating Procedure for localized token-efficient file scanning, AST chunk reading, and exact symbol extraction."
---

# File Inspection & Symbol Extraction SOP

Use this procedure whenever you need to open a file, read source logic, or inspect the exact definition of a known symbol (struct, enum, function, trait, etc.).

## Two-Phase Local Inspection Workflow

### Phase A: Structural Layout Mapping
Never pull an entire raw file body into context. Always map boundaries first:

1. Call **`scan-file-skeletons`** on the target file path.
   Returns a lightweight AST outline (symbol names + line ranges) without pulling body text.
2. Review the skeleton. Note the line numbers of targets you need.

### Phase B: Precision AST Extraction
Choose one path based on what you know:

| Situation | Tool | Why |
|---|---|---|
| You know the exact symbol name | **`view-symbols`** | Fetches the complete block with no line hunting |
| You have a line number from a prior tool | **`get-chunks-by-lines`** | Returns the full enclosing AST chunk for that line |
| You only have a partial name / fuzzy concept | **`find-symbols-by-pattern`** → then `view-symbols` | Resolves the exact identifier first |

### Ambiguous Name Resolution
If the exact identifier is unknown:
1. Call **`find-symbols-by-pattern`** with `--pattern "*Partial*"` and the appropriate `--type` filter (`"struct"`, `"function"`, `"all"`, etc.).
2. Once the exact name is returned, call **`view-symbols`** — never guess coordinates.

