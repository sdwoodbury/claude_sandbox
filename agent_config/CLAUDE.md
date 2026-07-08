
**ALWAYS** exclude `/vendor`, `/target`, and `/build` from searches.

**NEVER** run `cargo` commands (`check`, `test`, etc) unless specifically told to.

**ALWAYS** search for Rust dependencies (which were not found in the current cargo workspace / project) in /root/.cargo/. That is where your cargo cache is. 

# Guiding Principles
Think Before Coding    → stops wrong assumptions and missed tradeoffs
Simplicity First       → stops over-engineering and bloated abstractions
Surgical Changes       → stops touching code nobody asked to touch
Goal-Driven Execution  → tests first, verified success criteria

# RULES
**NEVER** spawn a sub-agent to call a tool that is directly available to the main agent. patch_file, Read, Edit, Write, Glob — call these directly. Sub-agents are onlY for multi-step research tasks.
- **NEVER** use the Edit tool. Use patch_file exclusively.
- **File Edits:** You have access to the `patch-file` skill. **NEVER** output raw code blocks to the user when modifying files. You MUST use the `/bin/patch_file.py` tool to apply all code changes directly to the filesystem. **NEVER** write a script to edit the files. **ALWAYS** use `/bin/patch_file.py` to edit a file.


# The patch-file skill is shown below

---
name: patch-file
description: "Apply surgical SEARCH/REPLACE block patches to a file. This is the ONLY approved method for editing source code."
---

Applies precise text replacements to a target file using a strict block format. Ensures edits are safe by verifying the search string is 100% unique within the target file before modifying it.

## Tool Interface
```bash
cat << 'EOF' | /bin/patch_file.py <file_path: str> -a <allowed_dir: str>
<<<<<<< SEARCH
<first_exact_text_to_find>
=======
<first_exact_text_to_replace_it_with>
>>>>>>> REPLACE
<<<<<<< SEARCH
<second_exact_text_to_find>
=======
<second_exact_text_to_replace_it_with>
>>>>>>> REPLACE
EOF

