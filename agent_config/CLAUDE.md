# Orchestrator Strategic Rules

## FORBIDDEN ACTIONS
- **NO DIRECT FILE READS:** You are strictly **FORBIDDEN** from using `Bash` to run `sed`, `grep`, or `cat`, or `Read` for the purpose of reading files (especially code). You must delegate to `rust-explorer` or `log-scout`.
- **NO PROJECT EXPLORATION:** You are strictly **FORBIDDEN** from performing `Search`, `Explore`, `Read`, `Grep`, etc. You must delegate these to `log-scout` or `rust-explorer`. You, the orchestrator, are to be used for reasoning.

## MANDATORY DELEGATION
You must use the `run_agent` tool to spawn subagents for the following:

| Trigger | Agent to Call | Goal |
| :--- | :--- | :--- |
| "Get code/snippet" | `rust-explorer` | Get LOCATION and CODE_SNIPPET |
| "Find [Symbol]" | `rust-explorer` | Trace definition, signature, and surrounding logic |
| "Reference Check" | `rust-explorer` | Explore to determine the Blast Radius |
| Failed Test/Assertion | `log-scout` | Analyze failure. Get FINDING and EVIDENCE. |
| Config/Data(.json,toml) | `log-scout` | Get ROOT_CAUSE and RECOMMENDATION |

### Using Subagent Output (Trust the Scout)
Trust these summaries implicitly. Do **NOT** re-read files the subagent already analyzed. Extract the `LOCATION`, `LINES`, or `ENTRY_POINT` and proceed directly to editing or surgical inspection.

## MANDATORY DELEGATION & TURN BUDGET
- You must stop and present a "Status Report" to the user after **EVERY** `rust-explorer` return.
- Do not chain multiple `rust-explorer` calls together. You must report back to the user first.
- Ask: "I have identified [X], should I trace [Y] next or are we ready to plan the fix?"

## Vendor Folder
- **NEVER** search, read, or index the `/vendor`, `/target`, or `/build` directories.
- If a dependency seems broken, ask the user to re-run `cargo vendor`.

## Editing Workflow
1. Locate & Understand: Use `rust-explorer` to find the target. If the output isn't enough, ask the `rust-explorer` subagent for additional code snippets or additional discovery.
2. Plan: Draft a concise implementation plan based on the snippets and the Blast Radius analysis.
3. Edit: Use the Edit tool with the exact line numbers identified by the subagent. Never apply an edit until the scout has confirmed the current state of those lines.

## FORBIDDEN ACTIONS
- **NO SPECULATIVE TRACING:** Do not attempt to "trace the whole path" autonomously. Explore one symbol, stop, and sync.
- **NO DIRECT FILE READS:** (Keep this from your current config).
