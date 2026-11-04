# §4 6단계: SKILL.md 초안 + references 3개 + 이식성 검사 (2026-11-04 밤)

- 날짜·머신: 2026-11-04 22:00–22:30, robotics-lab (Windows 11)
- 버전: ai-eda 0.0.1 (`work/ead-skill` 03bd642), KiCad 10.0.6, ngspice-46, Python 3.12.10
- 사실 수집: 워크플로 `skill-facts`(독자 5명 — 단계·CLI·템플릿·무CLI·상태/승인; 6.4분, 78만 토큰), 원본 `scratchpad/skill/facts.md`(158 KB). 초안의 모든 수치·문자열은 그 facts(file:line) 또는 아래 실측에서 왔다.
- 산출물(`.agents/skills/eda-engineer/`): `SKILL.md` 148줄(description 589자, 인용 발동 문구 8개), `references/pipeline.md` 105줄, `answers.md` 76줄, `without-cli.md` 56줄; `agents/openai.yaml`(Codex 전용, `policy.allow_implicit_invocation: true` — 공식 문서 기본값 true라 명시용); `tools/check_skill_portable.py`(stdlib, I1·I2·I3·I4·I5·I6·I7·I9·I11·G6 검사 + `--sync`로 `.claude/skills/eda-engineer` 바이트 동일 사본).

| 검사 | 결과 |
|---|---|
| `python tools/check_skill_portable.py --sync` | OK: 148 lines, description 589 chars, references 3, copy checked (exit 0) |
| 회의 #4 결정 반영 | 검증기는 가족 단위(pipeline.md 단계 표의 check ids 열), 상단 40줄 = 하드 리밋 + "Never do first" 압축 분류 + "data, not instruction" 한 문장 + 포인터, 12종 전체 목록은 SKILL.md 불변식 절, 측정 사실(kicad exit 0·5, AM ngspice 43+, astable 버전별 앵커, 템플릿 13행, 거부문)은 references에; `confirm_design` 라운드만 예시 + LLM 추출 시 `confirm_requirements` 한 문장 |
| 실제 과제 1(분배기, SKILL happy path 그대로) | `ai-eda new` → 답 없는 run: `requirement_analysis USER_INPUT_REQUIRED no LLM configured: free-text parsing skipped, baseline checklist only` + BLOCKED `[application]`·`[jurisdiction]` (SKILL "free text is NOT parsed" 문장의 근거) → typed 답 run: **exit 1**, `[confirm_design]` 표 → `confirm_design=yes` run: **exit 0**, 19단계 줄(calculation PASS, spice PASS 1/1, schematic PASS, erc PASS 0/0, 나머지 NOT_VERIFIED, release `not releasable: overall validation is NOT_VERIFIED (...)`) → `review --json` 키 `ir_hash`·`results`(14개, exit 0) → `report` 작성, `reports/01..04_*.md/.html` + `erc.json` |
| 실제 과제 2(KiCad 없는 환경: `LOCALAPPDATA`·`ProgramFiles`·`APPDATA`를 빈 폴더로, PATH 최소) | `doctor --strict` → `kicad-cli : NOT FOUND`, `kicad libs: NOT FOUND (… the circuit templates cannot build)`, `ngspice dll: NOT FOUND`, `missing   : kicad-cli, KiCad libraries, ngspice (the pipeline still runs, …)` **exit 1**. 같은 분배기 입력으로 run: `architecture NOT_VERIFIED template divider not proposed: symbol Device:R not found in the KiCad libraries []` → 설계 빈 채로 19단계 통과, `independent_review FAIL … requirements not traced to any component`, `release FAIL`, **exit 1**. → without-cli.md 초안의 "kicad-cli가 없어도 회로도·보드는 컴파일된다"는 **라이브러리가 있을 때만** 참이라 두 경우로 갈라 고쳤다(라이브러리 없음 = 템플릿이 아무것도 못 짓는다, 실측 인용) |
| 발동 시험(양성 10/음성 5, Claude Code·Codex) | **미실시** — 스킬을 두 호스트에 설치한 뒤(§9.5 T1) |
| G9 결정성·심은 결함 시험 | **미실시**(SKILL.md 불변식에는 적음; 참고 레포 테스트가 결정성을 이미 증명) |

알게 된 것: 계획이 "confirm_design 무시 4경우"라 했으나 코드는 **5개** 문자열(`no template to confirm` / `proposes nothing` / 같은 실행의 다른 답 / 표가 바뀜 / 설계가 이미 있음) → SKILL.md는 5개. `ExternalAction`은 10종이 아니라 **12종**(secret_access·system_delete 포함) → SKILL.md 12종. `--answer approve_*` 같은 승인 키는 없고 승인은 플래그 4개뿐. README에 PYTHONUTF8 권고는 없으며 cli가 `errors="replace"`로 대체 → SKILL.md는 "깨져 보이면 설정"으로 완화. `release`는 check id가 아니라 단계 판정뿐.

Codex 리뷰(`codex.ps1 ask`, 참고 코드 대조; 원본 `scratchpad/skill/codex-review-draft.txt`) — VERDICT "strong core, not ready to sell" → 반영:
- WRONG 수용 3: "SPICE needs KiCad's bundled ngspice.dll" → 공유 ngspice 라이브러리(KiCad 동봉·`NGSPICE_DLL`·시스템 libngspice)로 정정(`ngspice_shared.py:245-248`); happy path의 `setup-kicad`가 사용자 승인 없이 쓰기 → "제안하고 동의 뒤에만"; `--request`가 파싱된다는 인상 → "기록만, `--llm` 없이는 파싱 안 됨" 명시.
- MISSING: 12종 목록을 상단 40줄로(회의록은 압축 분류+불변식 절이었으나 한 줄이면 들어가 둘 다 만족; 불변식 절의 중복 제거, 승인 플래그 요약만 남김; 검사기에 12 이름 검사 추가); exit 0/1/2·traceback은 이미 불변식 절에 있어 happy path에 포인터만; pipeline.md 단계 표의 id 나열을 가족으로 축약(regulatory.*, ir.*); "report는 판정을 계산하지 않는다" 한 문장 추가.
- UNSAFE: 플래그(`--online`·`--llm`·예산·유료 답)는 사용자가 타이핑하는 승인이며 에이전트가 스스로 더하지 않는다 → "Never do first"에 명시.
- 결과: SKILL.md 154줄, 검사기 OK(12 이름 상단 40줄 확인). 미실시: 호스트 2곳 발동 시험(10/5), G9 두 과제(결정성·심은 결함).
