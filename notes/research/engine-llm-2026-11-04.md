# 참고 레포 ai_eda/llm 제공자 층 조사 (2026-11-04, 소스 읽기; PLAN §9.4의 근거)

**Portable skill packaging: research summary (2026-11-04)**

**1. The standard.** Agent Skills spec (https://agentskills.io/specification): a directory named after the skill containing `SKILL.md` (YAML frontmatter + Markdown) plus optional `scripts/`, `references/`, `assets/`. Required: `name` (1-64 chars, `a-z0-9-`, no leading/trailing/double hyphen, must equal directory name) and `description` (1-1024 chars). Optional: `license`, `compatibility` (<=500 chars), `metadata` (string map), `allowed-tools` (explicitly "Experimental"). Progressive disclosure: name+description (~100 tokens) at startup, body (<5000 tokens, <500 lines recommended) on activation, resources on demand; reference files one level deep via relative paths. Skills over MCP (https://modelcontextprotocol.io/extensions/skills/overview) reuses the same format; the MCP ext-skills repo lists host support still mostly "in progress" (https://github.com/modelcontextprotocol/ext-skills/blob/main/docs/implementations.md).

**Claude-Code-only fields** (https://code.claude.com/docs/en/skills): `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `disallowed-tools`, `model`, `effort`, `context`/`agent`/`background`, `hooks`, `paths`, `shell`, plus body features `$ARGUMENTS`/`$0`/`$name`, `!`command`` injection, `${CLAUDE_SKILL_DIR}` etc. The same page states that outside Claude Code only `name, description, license, compatibility, metadata, allowed-tools` are allowed and claude.ai/Skills API uploads hard-fail on any other key. Cursor independently supports `disable-model-invocation` and `paths` (https://cursor.com/docs/skills). Codex puts policy/UI metadata in a separate `agents/openai.yaml` instead of frontmatter (https://learn.chatgpt.com/docs/build-skills).

**2-3. Host matrix** (paths are from each vendor's docs unless marked)

| Host | SKILL.md | MCP | Project path / global path | Notes |
|---|---|---|---|---|
| Claude Code | yes (superset) | yes: `.mcp.json`, `~/.claude.json`, `claude mcp add` (https://code.claude.com/docs/en/mcp) | `.claude/skills/` / `~/.claude/skills/` | Does NOT read `.agents/skills` (UNVERIFIED; claude-code issue #6235 cited by https://claudeskills.info/blog/claude-skills-cross-platform-guide). Skills-over-MCP support not in docs. |
| OpenAI Codex | yes (`name`,`description` only) | yes: `~/.codex/config.toml` `[mcp_servers.*]`, `.codex/config.toml`, `codex mcp add` (https://learn.chatgpt.com/docs/extend/mcp?surface=cli) | `.agents/skills/` (walks up to repo root) / `~/.agents/skills/`; admin `/etc/codex/skills` (https://learn.chatgpt.com/docs/build-skills) | Invoke `$skill` or `/skills`; `allow_implicit_invocation` lives in `agents/openai.yaml`. |
| GitHub Copilot CLI | yes | yes: `~/.copilot/mcp-config.json`, `.mcp.json`, `.github/mcp.json` (https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers) | `.github/skills/`, `.claude/skills/`, `.agents/skills/` / `~/.copilot/skills/`, `~/.agents/skills/` (https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-skills) | Reads `allowed-tools`; warns against pre-approving shell. `/skill-name` invocation. |
| Gemini CLI | yes | yes: `settings.json` `mcpServers`, `gemini mcp add` (https://geminicli.com/docs/tools/mcp-server/) | `.gemini/skills/` or `.agents/skills/` / `~/.gemini/skills/` or `~/.agents/skills/` (https://geminicli.com/docs/cli/skills/) | Activation needs user consent prompt; `activate_skill` tool. Docs say free tier moved to Antigravity CLI 2026-06-18. |
| Antigravity | yes | yes: `~/.gemini/config/mcp_config.json`, `.agents/mcp_config.json` (https://antigravity.google/docs/mcp) | `.agents/skills/` / `~/.gemini/config/skills/` (https://antigravity.google/docs/skills) | `name` optional (defaults to folder); uses `examples/`,`resources/` naming. |
| Cursor | yes (+`paths`,`disable-model-invocation`,`icon`,`color`) | yes: `.cursor/mcp.json`, `~/.cursor/mcp.json` (https://cursor.com/docs/context/mcp) | `.cursor/skills/`, `.agents/skills/`, `.claude/skills/`, `.codex/skills/` / `~/.cursor/skills/` etc. (https://cursor.com/docs/skills) | Nested dirs auto-scoped. |
| OpenCode | yes (spec fields only; others ignored) | yes: `opencode.json` `mcp` key (https://opencode.ai/docs/mcp-servers/) | `.opencode/skills/`, `.claude/skills/`, `.agents/skills/` / `~/.config/opencode/skills/`, `~/.claude/skills/`, `~/.agents/skills/` (https://opencode.ai/docs/skills/) | Loaded via `skill` tool; `permission.skill` allow/deny/ask. Skills-over-MCP "in progress". |
| Amp | yes | yes; skill may ship its own `mcp.json` or `mcpServers` frontmatter (https://ampcode.com/manual/agent-skills.md) | `.agents/skills/`, `.claude/skills/` / `~/.config/agents/skills/`, `~/.agents/skills/`, `~/.claude/skills/` | First `name` match wins. |
| Cline | yes (`name`,`description`) | yes: `cline_mcp_settings.json` (https://docs.cline.bot/mcp/mcp-overview) | `.cline/skills/`, `.clinerules/skills/`, `.claude/skills/` / `~/.cline/skills/` (https://docs.cline.bot/customization/skills) | Global overrides project (reverse of most). `.agents/skills` claimed only by third-party CLI (https://github.com/vercel-labs/skills/blob/main/docs/agents.md), UNVERIFIED. |
| Roo Code | yes (spec format + mode dirs) | yes: `mcp_settings.json`, `.roo/mcp.json` (https://roocodeinc.github.io/Roo-Code/features/mcp/using-mcp-in-roo) | `.roo/skills/`, `.agents/skills/` / `~/.roo/skills/`, `~/.agents/skills/` (https://roocodeinc.github.io/Roo-Code/features/skills) | `skills-<mode>/` variants. |
| Windsurf (now Devin Local / Devin Desktop) | yes | yes: `.devin/mcp_config.json`, `~/.config/devin/mcp_config.json` (https://docs.devin.ai/desktop/cascade/mcp) | `.devin/skills/`, `.agents/skills/`, legacy `.windsurf/skills/` / `~/.config/devin/skills/`, `~/.agents/skills/` (https://docs.devin.ai/desktop/cascade/skills) | Cascade retired 2026-07 per secondary sources (UNVERIFIED). |
| Kiro | yes (spec fields) | yes: workspace/user MCP JSON via command palette (https://kiro.dev/docs/mcp/) | `.kiro/skills/` / `~/.kiro/skills/` (https://kiro.dev/docs/skills/) | Custom agents must list `skill://.kiro/skills/*/SKILL.md` in `resources`. |

**MCP as LCD.** Every host above runs MCP servers, but the Agensi-style model (tools `search_skills`/`get_skill` returning SKILL.md text, https://www.agensi.io/learn/how-to-build-mcp-server-for-skills) only injects text as a tool result; it bypasses each host's skill loader, consent prompt, `allowed-tools`, and bundled-file access. Supporting files must be served by extra tools or scripts cannot run. The official Skills-over-MCP extension fixes that but no host in the table lists "v1" support yet (OpenCode, VS Code, Goose in progress; https://modelcontextprotocol.io/extensions/client-matrix). Verdict: MCP delivery works everywhere as plain instruction text; use it as fallback, not primary.

**4. What breaks portability** (sources: the Claude Code and host docs above)
- Non-spec frontmatter keys: Claude Code ignores unknowns; OpenCode/Kiro/Roo ignore; claude.ai/Skills API rejects.
- `$ARGUMENTS`, `$0`, `!`cmd``, `${CLAUDE_SKILL_DIR}`: only Claude Code substitutes; elsewhere they appear literally.
- `hooks`, `context: fork`, `model`, `effort`, `disallowed-tools`: Claude Code only.
- Tool names `Read`/`Grep`/`Edit`/`Bash`: Codex, Gemini, OpenCode, Cursor use different tool names; `allowed-tools: Bash(git:*)` syntax is Claude-shaped and experimental.
- Slash-command assumptions: Codex uses `$name`, Gemini uses `activate_skill` + consent, Kiro custom agents need explicit resources.
- Windows paths, `python3` vs `py`, assuming bash: Claude Code has `shell: powershell`; others don't.
- Assuming one model/context size, or `system-reminder`/CLAUDE.md presence.
- Precedence differences (Cline global beats project; Amp first-name-wins) make same-named skills behave differently.

**5. Portable subset checklist**
1. Frontmatter only `name`, `description`, optional `license`, `compatibility`, `metadata` (https://code.claude.com/docs/en/skills "outside Claude Code").
2. `name` == directory name, lowercase-hyphen, <=64 chars (https://agentskills.io/specification).
3. Put trigger phrases in `description` (<=1024 chars); no `when_to_use`.
4. Keep `SKILL.md` <500 lines/<5k tokens; details in `references/`, with explicit "read X when Y" cues (https://agentskills.io/skill-creation/best-practices).
5. No `$ARGUMENTS`/`$N`/`!`cmd``; say "the user's request" and ask the agent to read inputs from the prompt.
6. No `hooks`, `context`, `model`, `effort`, `paths`, `disable-model-invocation` in the portable copy; if needed, ship a Claude-only overlay in `.claude/skills/` and a plain copy in `.agents/skills/`.
7. Describe actions, not tools: "search the codebase for X", not "use Grep".
8. Omit `allowed-tools`; Copilot warns on shell pre-approval and the field is experimental.
9. Scripts in `scripts/` self-contained, invoked with relative paths (`scripts/x.py`), stdlib-only or with documented deps; provide `.py` over `.sh` for Windows.
10. Use forward slashes; never hardcode `~/.claude` or absolute paths.
11. Don't assume host context files (CLAUDE.md, AGENTS.md, system-reminders) exist; restate critical constraints inside SKILL.md.
12. Put critical rules at the top (Claude Code may keep only the start after compaction).
13. Install into `.agents/skills/` first (read natively by Codex, Copilot, Gemini, Antigravity, Cursor, OpenCode, Amp, Roo, Devin) and symlink/copy to `.claude/skills/`, `.cline/skills/`, `.kiro/skills/`.
14. Validate with `skills-ref validate` (https://github.com/agentskills/agentskills/tree/main/skills-ref) and `claude plugin validate`.

**Cheap smoke test per host:** install to that host's project path, start a fresh session, (a) ask "what skills are available?" and assert the name+description appear; (b) send one prompt containing a description keyword and assert the body was loaded (host shows activation/consent, or the agent cites a phrase only present in the body); (c) ask it to run `scripts/<smoke>.py` and assert expected stdout; (d) grep the transcript for literal `$ARGUMENTS`, `${CLAUDE_`, or "Read tool" to catch leaks. Optional eval tooling: https://agentskills.io/skill-creation/evaluating-skills.