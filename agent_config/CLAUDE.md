
**ALWAYS** exclude `/vendor`, `/target`, and `/build` from searches.

**NEVER** run `cargo` commands (`check`, `test`, etc) unless specifically told to.

**ALWAYS** search for Rust dependencies (which were not found in the current cargo workspace / project) in /root/.cargo/. That is where your cargo cache is. 

# Guiding Principles
Think Before Coding    → stops wrong assumptions and missed tradeoffs
Simplicity First       → stops over-engineering and bloated abstractions
Surgical Changes       → stops touching code nobody asked to touch
Goal-Driven Execution  → tests first, verified success criteria

# Code Generation Constraints
- **File Edits:** You have access to the `patch_file` tool. **NEVER** output raw code blocks to the user when modifying files. You MUST use the `patch_file` tool to apply all code changes directly to the filesystem. **NEVER** spawn a subagent to use `patch_file`. Do it yourself. **ALWAYS** use `patch_file` to edit a file.

# RULES
**NEVER** spawn a sub-agent to call a tool that is directly available to the main agent. patch_file, Read, Edit, Write, Glob — call these directly. Sub-agents are onlY for multi-step research tasks.
- **NEVER** use the Edit tool. Use patch_file exclusively.
