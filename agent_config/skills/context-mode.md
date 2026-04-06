# Skill: context-mode (ctx_*)
**Goal:** Sandbox high-volume data and return only summaries to the agent context.

| Tool | Primary Use Case |
| :--- | :--- |
| `ctx_execute` | Runs code in sandbox; stdout stays OUT of context. |
| `ctx_execute_file` | Access `FILE_CONTENT` variable; parse/filter without reading. |
| `ctx_batch_execute` | Chain multiple commands + semantic searches in one call. |
| `ctx_index/search` | Create/Query local semantic indexes for docs/READMEs. |

## Usage Patterns

### Surgical File Filtering (ctx_execute_file)
```javascript
// intent: Extract error counts from large logs
const logs = FILE_CONTENT.split('\n');
const errors = logs.filter(l => l.includes('ERROR'));
console.log(`Found ${errors.length} errors. First 3:`, errors.slice(0, 3));
```

### Sandbox Execution (ctx_execute)
```javascript
// intent: Run tests without flooding terminal
const { execSync } = require('child_process');
try {
    const out = execSync('cargo test 2>&1', { encoding: 'utf8' });
    console.log("Tests passed successfully.");
} catch (e) {
    console.log("Tests failed. Top 5 lines of stderr:");
    console.log(e.stdout.split('\n').slice(0, 5).join('\n'));
}
```

### Batch Discovery (ctx_batch_execute)
Used to combine multiple shell commands and semantic searches into a single turn.
```json
{
  "commands": [
    {"label": "Recent Commits", "command": "git log -n 5"},
    {"label": "Build Status", "command": "cargo check --message-format=short"}
  ],
  "queries": ["recent changes to mpc logic", "compiler warnings"]
}
```
