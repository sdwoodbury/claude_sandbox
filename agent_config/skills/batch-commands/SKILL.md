---
name: batch-commands
description: "Execute multiple calls to /bin/narsil_client.py sequentially in a single terminal execution loop."
---

Combines multiple repository exploration and search tasks into a single run to drastically reduce agent tool-call latency and roundtrips.

## Tool Interface
```bash
cat << 'EOF' | /bin/narsil_client.py batch-commands
<command_1> [--args...]
<command_2> [--args...]
EOF
```

## Usage Guidelines
* **Omit the Binary Prefix:** Inside the `cat` block, do not include the `/bin/narsil_client.py` prefix. Write only the subcommand name (e.g., `view-symbols`, `find-references`, `get-chunks-by-lines`) and its flags.
* **Argument Quoting:** Use standard double quotes (`"string thing"`) for arguments that contain spaces or special characters.
* **Comments & Whitespace:** You can add blank lines or use lines starting with `#` to logically organize your batch block; they will be ignored by the parser.

## Example
```bash
cat << 'EOF' | /bin/narsil_client.py batch-commands
view-symbols --name "Schedule" --file "search.rs"
find-references --name "HAWK_MIN_DIST_ROTATIONS"
get-chunks-by-lines --file "intra_batch.rs" --line 42
EOF
```
