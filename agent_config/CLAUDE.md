available skills: search-rust, ra-tool, search-log

**ALWAYS** exclude `/vendor`, `/target`, and `/build` from searches.

**NEVER** run `cargo` commands (`check`, `test`, etc) unless specifically told to. And ask for permission before every run.

# Guiding Principles
Think Before Coding    → stops wrong assumptions and missed tradeoffs
Simplicity First       → stops over-engineering and bloated abstractions
Surgical Changes       → stops touching code nobody asked to touch
Goal-Driven Execution  → tests first, verified success criteria

# Code Generation Constraints
- **File Edits:** You have access to the `patch_file` tool. **NEVER** output raw code blocks to the user when modifying files. You MUST use the `patch_file` tool to apply all code changes directly to the filesystem.

