# Agent Prompting Rules (global for this repo)

## Scope discipline
- No implementation code until prompts/spec are merged to main.
- Optimize for free tier usage: short tool calls, avoid repeated loops, prefer reading files over regenerating.

## Safety
- Agent may run safe commands (ls, cat, rg, git status, tests, formatters).
- If any command requires sudo, the agent must ask first and explain why.

## Dependency discipline
- Prefer stdlib-first and minimal dependencies.
- Any third-party dependency must include:
  - Clear value statement
  - Alternative considered
  - Why minimal/necessary

## Quality discipline
- Tests are first-class.
- Pre-commit gating required.
- CI required.

## Process
- Work on feature branches only.
- Use gh for PR lifecycle when possible.
- Commits must include model disclosure in the subject line: [model: ...]

---

## Prompt Canonicalization and Cursor Sync Rule

### Canonical Rule
- `prompts/` is the **only** canonical source of agent prompts.
- `.cursor/prompts/` contains non-canonical wrapper stubs only.

### Mandatory Sync Requirement
If you modify, add, rename, or delete **any file under `prompts/`**, you MUST:

1) Create/update/delete the corresponding wrapper file under `.cursor/prompts/`
2) Do so in the **same commit**
3) Ensure the wrapper clearly points to the canonical file path

Failure to do this is considered a **process violation**, even if the prompt content itself is correct.

### No Exceptions
- Do not place authoritative instructions in `.cursor/prompts/`
- Do not update `prompts/` without updating `.cursor/prompts/`
- Do not assume a future script will “fix it later”

Agents are expected to enforce this rule proactively and call it out explicitly if violated.
