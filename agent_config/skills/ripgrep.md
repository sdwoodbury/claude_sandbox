# ripgrep (rg) - Fast Code Search

Use `rg` (ripgrep) via Bash instead of the built-in Grep or Search tools.

## Why Use rg

- Faster than built-in tools on large codebases
- Respects `.gitignore` by default
- Better regex support and output formatting

## Usage

```bash
rg [OPTIONS] PATTERN [PATH...]
```

## Common Patterns

### Basic search
```bash
rg "pattern" src/
```

### Case-insensitive
```bash
rg -i "pattern"
```

### Show context lines
```bash
rg -C 3 "pattern"      # 3 lines before and after
rg -B 2 -A 2 "pattern" # 2 before, 2 after
```

### Filter by file type
```bash
rg -t rust "pattern"   # Rust files only
rg -t py "pattern"     # Python files only
rg -g "*.rs" "pattern" # Glob pattern
```

### List matching files only
```bash
rg -l "pattern"
```

### Show line numbers (default on)
```bash
rg -n "pattern"
```

### Fixed string (no regex)
```bash
rg -F "literal[string]"
```

### Multiline matching
```bash
rg -U "start.*\n.*end"
```

### Exclude directories
```bash
rg --glob '!vendor/' "pattern"
rg --glob '!target/' "pattern"
```

## Output Format

Default output includes file path, line number, and matching line:
```
src/main.rs:42:    let config = Config::new();
```

## Tips

- Always exclude `/vendor` and `/target` directories
- Use `-q` (quiet) to check if a pattern exists (exit code only)
- Use `--json` for machine-parseable output
- Combine with `head -n 50` to limit results
