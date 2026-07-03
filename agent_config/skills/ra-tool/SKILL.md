---
name: ra-tool
description: "Use when: querying rust-analyzer for symbol definitions, references, type info, and workspace symbols with precise semantic understanding."
---

## Usage

```bash
/bin/ra_tool.py [FLAGS] <COMMAND> [ARGS]
```
### Strict Path Parity Note
Ensure that the file paths passed to the tool are absolute paths that match the host's filesystem.

## Global Flags

| Flag | Description |
|------|-------------|
| `-q, --quiet` | Suppress all informational output (stderr) |
| `-v, --verbose` | Enable detailed diagnostic output (stderr) |
| `--format json\|markdown` | Output format (default: json) |

## Commands

### Position-based commands (require file + line + column)

All position arguments use **1-based indexing**.

#### `definition` - Go to definition
```bash
/bin/ra_tool.py definition <file> <line> <column>
```
Returns the location(s) where the symbol at the cursor is defined.

#### `references` - Find all references
```bash
/bin/ra_tool.py references <file> <line> <column>
```
Returns all locations that reference the symbol at the cursor (includes declaration).

#### `typeDefinition` - Go to type definition
```bash
/bin/ra_tool.py typeDefinition <file> <line> <column>
```
Returns the location where the type of the symbol is defined.

#### `hover` - Get hover information
```bash
/bin/ra_tool.py hover <file> <line> <column>
```
Returns documentation, type signature, and other hover info for the symbol.

#### `implementations` - Find implementations
```bash
/bin/ra_tool.py implementations <file> <line> <column>
```
For traits: returns all impl blocks. For types: returns trait implementations.

### File-based commands

#### `documentSymbols` - List symbols in a file
```bash
/bin/ra_tool.py documentSymbols <file>
```
Returns all symbols (functions, structs, impls, etc.) defined in the file with their locations.

### Query-based commands

#### `workspaceSymbols` - Search all symbols
```bash
/bin/ra_tool.py workspaceSymbols <symbol_name>
```
Fuzzy-searches the entire workspace for symbols matching the query string.

## Output Format

### JSON (default)

Success:
```json
{
  "status": "success",
  "result": [...]
}
```

Error:
```json
{
  "status": "error",
  "message": "...",
  "details": {...}
}
```

### Location results (definition, references, typeDefinition, implementations)
```json
{
  "status": "success",
  "result": [
    {"uri": "file:///path/to/file.rs", "line": 42, "column": 5},
    ...
  ]
}
```

### Hover results
```json
{
  "status": "success",
  "result": {
    "kind": "markdown",
    "value": "```rust\nfn example() -> i32\n```\n\nDocumentation here..."
  }
}
```

### Symbol results (documentSymbols, workspaceSymbols)
```json
{
  "status": "success",
  "result": [
    {
      "name": "MyStruct",
      "kind": "Struct",
      "location": {"uri": "file:///...", "line": 10, "column": 1},
      "containerName": "my_module"
    },
    ...
  ]
}
```

## Symbol Kinds

File, Module, Namespace, Package, Class, Method, Property, Field, Constructor, Enum, Interface, Function, Variable, Constant, String, Number, Boolean, Array, Object, Key, Null, EnumMember, Struct, Event, Operator, TypeParameter

## Examples

```bash
# Find where a function is defined (use -q for clean output)
/bin/ra_tool.py -q definition src/main.rs 15 10

# Get all references to a struct
/bin/ra_tool.py -q references src/lib.rs 42 5

# Get hover info with markdown output
/bin/ra_tool.py -q --format markdown hover src/lib.rs 100 20

# List all symbols in a file
/bin/ra_tool.py -q documentSymbols src/parser.rs

# Search for symbols named "Config"
/bin/ra_tool.py -q workspaceSymbols Config

# Find all implementations of a trait
/bin/ra_tool.py -q implementations src/traits.rs 8 10
```

## Tips

- Use `-q` flag for clean, parseable output (suppresses stderr diagnostics)
- Use `--format markdown` for human-readable output
- The tool auto-initializes the LSP connection and waits for rust-analyzer to be ready
- First invocation may be slower as rust-analyzer indexes the workspace
- File paths can be relative or absolute
