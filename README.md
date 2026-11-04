# EDA_Engineer_Skill

`eda-engineer` agent skill (first draft): a verification-first electronics design engineer, built from the AI_EDA_Engineer reference system. Target hosts: any agent that loads Agent Skills (`SKILL.md`) or an MCP skill connector; sold through agensi.io.

**License: proprietary, view-only.** See [LICENSE](LICENSE). Reading this repository grants no right to use its content with any AI agent or tool; a license comes only with a purchase on an authorized marketplace or a written agreement. Third-party references are listed in [NOTICE](NOTICE).

- `.agents/skills/eda-engineer/` — the skill: `SKILL.md` and `references/` (`pipeline.md`, `answers.md`, `without-cli.md`), plus Codex-only metadata in `agents/openai.yaml`.
- `.claude/skills/eda-engineer/` — byte-identical copy for Claude Code.
- `tools/check_skill_portable.py` — portability checks for the skill (`--sync` refreshes the `.claude` copy first).
- `notes/PLAN.md` — setup status, understanding of AI_EDA_Engineer, improvement points, extension plan, next steps (Korean).
- `notes/meetings/` — Claude ↔ Codex design meetings held over Reason Network.
- `notes/measurements/` — evidence behind every "measured" claim in the plan.
- `notes/research/` — background research for the plan.
- `notes/review-2026-11-04.md` — improvement review of the plan.

The skill is a first draft: it has been tried on two real tasks and passed a trigger test on Codex; see the plan for what is still open.

Copyright (c) 2026 Yuchan. All rights reserved.
