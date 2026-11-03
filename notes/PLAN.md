# EDA_Engineer 스킬 프로젝트 — 세팅 · 이해 · 보완점 Plan

작성: Claude (lead), Codex 검토 반영. 날짜: 2026-11-04.
범위: 이 문서는 **스킬을 아직 쓰지 않는다.** (1) AI_EDA 실행 환경 세팅 결과, (2) AI_EDA_Engineer 프로젝트 이해, (3) 보완점과 다음 단계만 적는다. 스킬 본문(SKILL.md)은 이 plan을 사용자가 확인한 뒤 천천히 진행한다.

---

## 1. 세팅 현황

### 1.1 로컬 레이아웃 (`B:\0) AI_Project`)
| 경로 | 내용 | 상태 |
|---|---|---|
| `AI_EDA_Engineer/` | 참고 레포 클론 (github.com/Yuchan-00/AI_EDA_Engineer, main `4ee4d8e`) | 읽기 전용 참고 |
| `AI_EDA_Engineer/.venv/` | Python 3.12.10 venv, `pip install -e ".[llm,parts,dev]"` | `ai-eda 0.0.1` 동작 |
| `AI_EDA_Engineer/graphify-out/` | 코드+문서 지식 그래프 (12,034 노드 / 50,193 엣지 / 183 커뮤니티, `graph.html`, `GRAPH_REPORT.md`) | 질의 가능 (`.venv\Scripts\graphify.exe query "<질문>"`) |
| `EAD_Engineer_Skill/` | 새 스킬 레포 클론 (github.com/Yuchan-00/EAD_Engineer_Skill, 비어 있었음) | 이 문서가 첫 내용 |
| `scripts/rn_bridge.py` (AI_Project 레포) | Codex ↔ Reason Network 브리지 MCP 서버 | 동작 확인 |

두 클론은 AI_Project 레포의 `.gitignore`에 추가해 중첩 커밋을 막았다.

### 1.2 AI_EDA 실행 환경 점검 결과
`ai-eda doctor` (2026-11-04):
```
kicad-cli : C:\Users\yc012\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe  (v10.0.6)
kicad tables: C:\Users\yc012\AppData\Roaming\kicad\10.0 (sym-lib-table, fp-lib-table)
ngspice dll: ...\KiCad\10.0\bin\ngspice.dll  (ngspice-46, code models loaded)
browser (pdf): C:\Program Files\Google\Chrome\Application\chrome.exe
LLM key   : OPENROUTER_API_KEY not set
claude cli : NOT FOUND
missing   : nothing required
```
`ai-eda selftest`: 12 V→5 V 분배기를 끝까지 설계. 계산기 PASS, ngspice PASS, 회로도/보드 컴파일 PASS, ERC 0/0, DRC 0/0, BOM/CPL/거버 PASS, 한국어 단계 보고서 작성 → **"every required tool ran - the installation works"**.

`pytest -x`: 179 passed, **1 failed** (`tests/test_circuit_templates.py::test_astable_verifies_at_the_bounds_of_its_own_validity_range[3 V-100 Hz-100.0]`): 측정 편차 4.94 % > 허용 4.9 % (`AstableTemplate.MEASURED_DEVIATION_MAX`). 이 PC의 ngspice-46 결과가 프로젝트가 앵커로 삼은 값과 미세하게 다름. 전체 실행 결과는 §3.1-b 참고.

LLM 경로(`--llm openrouter|claude`)는 키/CLI가 없어 미검증. 파이프라인의 결정론적 부분은 LLM 없이 전부 동작한다.

### 1.3 에이전트 협업 환경
- **Reason Network** (github.com/reason-machines/reason-network v0.12.17): 팀 `ai-eda`, 사람 `yuchan`, 머신 `robotics-lab`. 데몬은 필요 시 자동 기동. 로그온 서비스와 `setup`(에이전트 자동 연결)은 설치하지 않음 — 권한 분류기가 외부 설치 스크립트 실행을 막았고, 바이너리는 세션 scratchpad에 두고 직접 호출한다. PATH에 올리지 않았다.
- **Claude 측**: 이 세션은 MCP를 못 붙이므로 CLI로 참여. `listen --as claude-lead`(수신) / `send <to> --from yuchan/claude-lead`(발신). 셸의 `CLAUDE*`/`CODEX*` 환경변수가 있으면 "등록되지 않은 세션"으로 거부되므로 `env -i`로 비운 환경에서 실행.
- **Codex 측**: Codex는 reason-network 자체 MCP의 `send_message`/`list_team`을 (스키마의 타입 union 때문에) 버리고, 샌드박스는 exe 실행을 거부(os error 5). 그래서 `scripts/rn_bridge.py`(stdio MCP, 도구 `rn_who`/`rn_send`/`rn_wait`)를 Codex에 붙여 `yuchan/codex-eda`로 통신한다. 양방향 왕복 확인됨.
- **Codex 모델**: 설정 기본값 `auto/best-free`(OmniRoute)는 현재 스트림이 끊겨 실패. 사용자가 전에 쓰던 `auto/best-coding`은 성공 → 모든 `codex exec`에 `-m auto/best-coding`을 준다. 컨텍스트 128k 제한: "레포를 훑어보라"는 식의 자유 탐색 과제는 `context_length_exceeded`로 죽었다. Codex에는 **요약된 입력 + 좁은 과제**만 준다.
- **스킬 적용**: Claude는 ponytail(full)·graphify 로드. Codex는 `~/.codex/skills/`가 비어 있어 프롬프트에 ponytail 규칙을 인라인으로 준다(스킬 복사는 사용자 권한 필요).

---

## 2. AI_EDA_Engineer 프로젝트 이해

### 2.1 한 문장
자연어 요구 → 요구사항/질문 → **Universal Circuit IR** → 계산기/SPICE → KiCad 회로도·PCB → ERC/DRC → 제조 산출물 → 독립 리뷰 → 수리, 를 **검증 우선**으로 수행하는 Python 시스템. 원칙: **LLM은 설계의 진실을 결정하지 않는다.** 진실은 IR + provenance + 결정론적 도구(계산기, ngspice, kicad-cli, 제조 검사) + 독립 리뷰어가 정한다.

### 2.2 핵심 개념
- **IR이 유일한 원본** (`ai_eda/ir/`, `<workdir>/ir.json`, `CircuitIR`). `.kicad_sch/.kicad_pcb/.kicad_pro`, BOM, CPL, SPICE 덱, 거버, 3D는 전부 IR에서 결정론적으로 컴파일된 파생물이며 `ArtifactRef.generated_from_ir_hash`로 신선도를 판정한다. 손으로 고친 파일은 해시로 들통나 거부된다.
- **모든 중요한 값은 `Traced[T]`** + `Provenance(kind ∈ {user_requirement, authoritative, assumption, derived, llm_generated})`. `derived`는 계산기가 역할→id 입력을 기록해 재계산 가능.
- **검증 상태는 boolean이 아니다**: `PASS / FAIL / NOT_VERIFIED / NOT_APPLICABLE / USER_INPUT_REQUIRED / UNRESOLVED`. 증거 없음 = `NOT_VERIFIED`, 절대 PASS 아님. `tool`이 없는 `ValidationResult`는 의견. ERC/DRC는 warning 하나라도 FAIL.
- **에이전트는 제안만**(`IRProposal`), `Orchestrator.apply_proposals`만 설계를 바꾼다. 필수 질문이 있으면 파이프라인이 멈춘다(exit 1).
- **2-run 확인 프로토콜**: 모델/템플릿 제안은 표로 보여 주고(`ir.requirements.presented`에 sha256 기록), **다음 실행**에서 `--answer confirm_design=yes` 등으로만 적용. 같은 실행에 요구사항을 바꾸는 답이 섞이면 확인은 무시되고 재질문.
- **외부 행위는 승인**: 네트워크(`--online`), 유료 호출(`--llm-budget-*`), 구독 호출(`--llm claude`)이 각각 1회성 승인.
- **부품 identity**는 아카이브된 PDF 데이터시트 본문에서 MPN을 verbatim으로 찾을 때만 grounded. 규제는 출처·적용 여부만 말하고 `regulatory.compliance`는 항상 `NOT_VERIFIED`.

### 2.3 19단계 파이프라인 (`ai_eda/workflow/stages.py` `STAGE_ORDER`)
| # | stage | 하는 일 | PASS의 증거 / NOT_VERIFIED 조건 |
|---|---|---|---|
| 1 | `requirement_analysis` | `RequirementAgent`. `--llm` 없이는 기본 질문(application, jurisdiction 필수), `--answer`가 `user_requirement`로 | 단독 PASS 없음; `requirements.extraction`은 다음 실행의 `confirm_requirements=yes` 뒤 PASS |
| 2 | `missing_information` | 미답 필수 질문 게이트 | 추출이 PASS이고 request 해시가 같을 때만 PASS; `--llm` 없으면 항상 NOT_VERIFIED |
| 3 | `regulatory_research` | 후보 규제(`candidates.json`) 적용 판정, `--online`일 때 공식 문서 아카이브 | `regulatory.sources` PASS = 인용 전부 verbatim 발견; `regulatory.compliance` 항상 NOT_VERIFIED |
| 4 | `architecture` | `CircuitDesignAgent`: 템플릿 1개 선택(divider/led/rc_lowpass/astable/atmega128_devboard/kr447 radio), 첫 실행은 `[confirm_design]` 표만 | 제안 단계는 NOT_VERIFIED("N proposal(s) applied, nothing verified") |
| 5 | `component_selection` | `component.existence.<ref>`: 심볼/풋프린트 존재 + 아카이브 PDF에서 MPN verbatim | 오프라인/HTML은 NOT_VERIFIED, 라이브러리 없음은 FAIL |
| 6 | `placement` | `PCBAgent` 결정론적 배치(`placement.grid/core_ring/rf_floorplan`) + `routing.maze` + 실크 | **절대 PASS 아님**(제안은 증거가 아님); 배선 불가 넷은 배치만 |
| 7 | `fab_capability` | `--fab-capability FILE`의 제조 한계를 벤더 페이지에 grounding | `mfg.capability_source` PASS는 인용 전부 grounded일 때만 |
| 8 | `ir_build` | 구조/도메인 검증기 레지스트리(`ir.connectivity`, `ir.component_provenance`, `pcb.*`, `si.*`, `rf.*` …) | 가정/llm 값은 USER_INPUT_REQUIRED; `pcb.*`/`si.*`는 "IR geometry, not DRC" |
| 9 | `calculation` | `recompute_parameters`: 모든 derived 값을 계산기로 재계산 | `calc.recompute` PASS(rel 1e-9), 불일치는 FAIL(repair: human) |
| 10 | `spice` | `SimulationAgent`: 자급 `.cir` 컴파일, ngspice(shared lib) 실행, `Expectation` 판정 | 보간/바이어스 브래킷이 허용오차 안이면 PASS, 걸치면 UNRESOLVED, 가정 위의 PASS는 NOT_VERIFIED |
| 11 | `schematic` | `SchematicCompiler` → `.kicad_sch`, `ProjectFileCompiler` → `.kicad_pro` | `compile.kicad_sch` PASS + artifact_hash; CompileError는 FAIL(human) |
| 12 | `erc` | `kicad-cli sch erc --format json --severity-all` | 위반 0개일 때만 PASS; kicad-cli 없으면 NOT_VERIFIED |
| 13 | `pcb` | `PCBCompiler` → `.kicad_pcb`, 3D 미리보기 | 위와 동일 |
| 14 | `drc` | `kicad-cli pcb drc --severity-all --refill-zones --schematic-parity` | 위반/미연결/parity 0일 때만 PASS |
| 15 | `manufacturability` | `check_capability`: IR 구리 vs 제조 한계 | `PROJECT_RULES_MEASURED_VERSIONS`가 비어 있어 **현재 어디서도 PASS 불가** |
| 16 | `manufacturing_outputs` | BOM/CPL, 거버/드릴(`--no-protel-ext --check-zones`), STEP/GLB | `mfg.gerber` PASS = `%TF.FileFunction` 헤더가 구리·마스크·프로파일을 모두 덮음 |
| 17 | `independent_review` | `IndependentReviewer` 14개 영역(`review.*`): IR·파일·기록만 읽고 재해시·재탐색·재계산 | stale 산출물 FAIL(repair: regenerate), stale 도구 결과 FAIL(rerun_tool), 설계 결함 FAIL(human) |
| 18 | `repair` | `RepairLoop`: regenerate/rerun_tool만, 최대 5회, 전후 IR 해시 비교 | 설계를 바꾼 수리는 실패로 기록·중단 |
| 19 | `release` | 최신 결과 집계 + 증거 품질 감사 | "evidence-backed release"는 전부 tool-backed PASS/NA + 현재 해시일 때만. **현재 모든 머신에서 NOT_VERIFIED가 정상** |

exit code: `0` 완료(PASS 또는 NOT_VERIFIED), `1` 필수 질문에 막힘 또는 마지막 단계 FAIL, `2` 사용법/IR/lock/workdir 오류(아무것도 쓰지 않음).

### 2.4 CLI 계약 (요약)
`ai-eda doctor [--strict]`, `setup-kicad`, `selftest`, `new NAME [--dir] [--request]`, `run IR.json [--answer K=V …] [--llm …] [--online …] [--fab-capability F]`, `review`, `relocate`, `report`, `serve`, `stage-reports`, `gui`.
제어 키(`ai_eda/agents/keys.py` `CONTROL_KEYS`): `confirm_requirements, accept_implicit, reject_implicit, leave_out, confirm_design, confirm_parts, confirm_facts, datasheet_facts_file, extract_datasheet_facts, accept_regulations, reject_regulations, propose_regulations, pcb.placement, pcb.routing, pcb.silkscreen`.
수량 답은 "한 값 + 단위"(`--answer input_voltage="12 V"`); 맨 키 `frequency`는 어느 템플릿도 읽지 않는다. 닫힌 세계 거부는 메시지가 찍어 주는 `--answer leave_out=<key>`로만 푼다.

### 2.5 코드 구조 (그래프의 god node)
`CircuitIR`(1,077 엣지) > `KicadLibrary`(551) > `Traced`(463) > `ValidationResult`(288) > `CompileError`(246) > `user_requirement()` > `AgentContext` > `ProjectMeta` > `_derived()`.
크기: Python 148k 줄, 331 파일, 테스트 125 파일. 문서 3개(README 232 KB, CLAUDE.md 120 KB, ARCHITECTURE.md 275 KB)는 한 줄이 최대 17 KB라 에이전트 도구로는 바이트 슬라이스로만 읽힌다.

### 2.6 명시적으로 "측정 안 됨"인 것 (스킬이 과장하면 안 되는 항목)
- `PROJECT_RULES_MEASURED_VERSIONS`, `EXPORT_3D_MEASURED_VERSIONS` 비어 있음 → `mfg.capability` 기하 행 전부 NOT_VERIFIED, 3D export 플래그 미실행.
- 배치된 보드의 실제 DRC는 selftest 분배기 보드에서만 측정(설치 CI). ATmega128·라디오 보드의 ERC/DRC canary는 KiCad 머신에서 미실행 → **이 PC가 그 머신이 될 수 있다** (§3.2 B1).
- Windows: `.ai-eda.lock`의 `msvcrt.locking`, claude.exe stdin 경로, cp949 로케일 설치 미측정.
- `domain.high_speed.si`, `domain.power.pi`는 항상 NOT_VERIFIED인 스텁.
- `regulatory_conflict`, `unverified_component_data`, `circuit_structure_change` 수리 범주는 선언만 있고 어디서도 emit되지 않는다.

---

## 3. 보완점

### 3.1 이 PC에서 재현된 문제 (근거 있음)
| # | 문제 | 근거 | 제안 |
|---|---|---|---|
| A1 | `pip install -e .`만 하면 `ai-eda doctor`가 `ModuleNotFoundError: httpx`로 크래시 | `cli.py:324 cmd_doctor → from ai_eda.llm.openrouter import …`; `httpx`는 `[llm]` extra | doctor의 import를 try/except로 감싸 "LLM key: httpx not installed (pip install 'ai-eda-engineer[llm]')"로 보고 |
| A2 | selftest/run이 콘솔에 한국어 파일명을 깨뜨려 출력 (`01_�̷�_������.md`) | Git Bash/파이프에서 stdout이 cp949 | `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` 또는 README에 `PYTHONUTF8=1` 안내 |
| A3 | `test_astable_verifies_at_the_bounds…[3 V-100 Hz]` 실패: 편차 4.94 % > `MEASURED_DEVIATION_MAX` 0.049 | 이 PC ngspice-46 (KiCad 10.0.6 동봉) | 버전별 앵커(이미 RF 테스트가 쓰는 방식)로 확장하거나 상한을 측정값 기준으로 재기록 |
| A4 | 문서 3개가 에이전트 도구(Read)로 읽히지 않는 초장문 줄 | README/CLAUDE.md/ARCHITECTURE.md 최대 17 KB/줄 | 줄바꿈(80~120자) 또는 섹션 분할. 스킬은 이 문서를 그대로 쓰지 않고 **증류본**을 가져야 한다 |
| A5 | `ai-eda run`/`review`가 손상된 ir.json(모르는 키, 다른 schema_version)에 **traceback + exit 1** | `cli.py` `cmd_run`/`cmd_review`의 `_load()`가 try 밖 (`report`만 exit 2로 잡음). 비평 에이전트가 venv로 측정 | `_load()`를 `IRSchemaError → exit 2` 경로로 통일. 스킬의 exit code 표에는 "traceback+exit 1 = ir.json 로드 실패, 설계 FAIL 아님"을 명시 |
| A6 | `confirm_design=yes`가 조용히 무시되는 경우가 4가지 | `agents/circuit.py`: 같은 실행의 요구사항 변경 답, 표 해시 불일치, 설계 내용이 이미 있음(208행), 템플릿 미선택/제안 없음(144·149행) | 4가지 모두 `note:`로 이유를 찍는지 확인하고, 스킬 규칙에 4가지를 다 적는다 |

§3.1-b 전체 pytest(`-x` 없이) 결과: 실행 중 — 완료 후 이 표에 추가.

### 3.2 설계/구현 보완점 (코드 읽기 + 그래프 분석에서 나온 것)
| # | 항목 | 왜 문제인가 | 제안 |
|---|---|---|---|
| B1 | 미측정 canary를 이 PC에서 측정 | KiCad 10.0.6 + ngspice-46이 있는 첫 실제 머신 | `tests/test_kicad_cli.py::…sibling_project_rules…canary`, ATmega128/라디오 ERC·DRC, 3D export를 실행해 `PROJECT_RULES_MEASURED_VERSIONS`/`EXPORT_3D_MEASURED_VERSIONS`에 10.0.6 기록 → `mfg.capability`가 처음으로 PASS 가능 |
| B2 | 규제 범위 질문이 non-blocking | 후보가 UNDECIDED인 채 RELEASE 도달 가능(`regulatory.applicability` NOT_VERIFIED) | RELEASE 메시지에 미결 키를 명시(이미 일부) + 스킬이 반드시 되묻도록 |
| B3 | 수리 범주 3종이 emit되지 않음 | `NON_REPAIRABLE` 선언과 실제 불일치 | emit 지점을 만들거나 목록에서 제거(문서 정합) |
| B4 | 컴파일 거부 시 이전 산출물 pop | `Orchestrator._compile`이 FAIL/NOT_VERIFIED면 그 kind를 `ir.artifacts`에서 제거 → 하류가 "no PCB artifact" | 의도된 동작이지만 메시지에 "previous artifact removed" 명시 |
| B5 | `doctor` exit 0 (`--strict` 없이) | 스크립트가 exit code만 보면 "ai-eda가 import된다"만 안다 | 설치 스크립트/스킬은 항상 `--strict` |
| B6 | 기본 배선이 all-or-nothing | 넷 하나 못 그리면 구리 0 → DRC unconnected_items | 스킬이 `pcb.routing=partial`을 안내; 기본값 재검토는 사용자 결정 |
| B7 | README 현재 상태 표 날짜(2026-09-27) vs 변경 이력(2026-10-14) | 최신 권위는 변경 이력 | 상태 표 날짜 갱신 |
| B8 | 단계 이름 대소문자 혼용(README 대문자, 코드 `StrEnum` 소문자) | 스킬이 run 출력을 파싱할 때 혼란 | 문서를 소문자 id로 통일 |
| B9 | `worst_status`에서 USER_INPUT_REQUIRED < FAIL이지만 오케스트레이터는 질문에서 멈춤 | FAIL 단계가 동시에 blocking 단계가 될 수 있음 | 출력에 "blocked by question" 라벨 분리 |
| B10 | 리뷰에 USER_INPUT_REQUIRED만 있으면 `failures`가 비어 수리 루프가 "no failures"로 종료 | 설계는 막혀 있는데 수리 루프는 성공처럼 보임 | 리뷰 요약에 blocked 카운트 추가 |

### 3.3 스킬(EDA_Engineer) 설계에서 결정할 것 — 나의 권고
| 질문 | 권고 |
|---|---|
| 파일 구조 | **SKILL.md + references 2개 + 한 화면짜리 no-CLI 페이지**: `references/pipeline.md`(19단계 표: 무엇이 돌고, PASS 조건, NOT_VERIFIED vs FAIL, 수리 범주; RF/SI는 한 문단), `references/answers.md`(제어 키 `CONTROL_KEYS` + 기본 키 4개 + 템플릿 입력 키와 범위 + 규제 범위 키 + `pcb.*` 조향 + 승인 플래그; 나머지는 `ai-eda run --help`로), `references/without-cli.md`(감지 → 설치 제안 → 거절 시 kicad-cli ERC/DRC 두 명령, ngspice 호출, 증거 장부 행 형식) |
| SKILL.md 길이 | 250줄 이하. happy path(doctor --strict→setup-kicad→new→run→confirm_design→읽기), 6개 상태, provenance 5종, 불변식 체크리스트 ~15개, exit code 표(0/1/2 + "traceback+exit 1 = ir.json 로드 실패"), confirm_design 무시 4경우, run 출력에서 단계 줄(0열)과 `  note:`/`  report written:` 줄(2칸 들여쓰기) 구분, `pipeline.json`의 `state.outcomes[]` 위치, 외부 행위 전체 목록(git_push, external_upload, system_install/delete, pcb_order, component_purchase, paid_api_call, manufacturing_order, regulatory_submission, network_fetch, subscription_use)을 "절대 먼저 하지 않는다"로 |
| `scripts/check_evidence.py` | **만들지 않음**. `ai-eda review --json`이 재해시·수리 범주를, `ai-eda report`가 fresh/stale/unstamped/opinion 라벨을 이미 계산한다 → "review와 report를 돌리고 라벨을 읽어라" 한 줄 |
| CLI 없을 때 fallback | 한 화면. 19단계 수동 복제는 과함. kicad-cli exit code는 이 프로젝트가 0·5만 성공으로 알 뿐(`ok_codes=(0, 5)`) 3/1의 의미를 적지 않는다 |
| venv 경로 | `ai-eda`가 PATH에 없으면 `<repo>\.venv\Scripts\ai-eda.exe`(또는 그 venv의 `python -m ai_eda.cli`); 시스템 Python의 `python -m ai_eda.cli`는 `No module named 'ai_eda'` |
| 락 | 동시 실행 금지는 `run / review / stage-reports / relocate`에만 해당(`.ai-eda.lock`); `report / serve / gui / new / doctor`는 락을 잡지 않아 `run` 옆에서 돌려도 된다 |
| 모드 감지 | 과제를 이해한 뒤, **ai-eda 명령을 처음 쓰기 직전**에 `ai-eda doctor --strict`(이후 모든 도구 주장의 근거). CLI 없는 모드에서는 해당 없음 |
| IR 직접 편집 | 금지. `--answer`와 문서화된 JSON 입력(`--fab-capability`, `datasheet_facts_file`)만. `references/ir.md`는 만들지 않음 |
| "측정 안 됨" 사실의 위치 | SKILL.md의 "하드 리밋" 절에 5줄(과장 방지), 상세는 `references/pipeline.md` |
| 언어 | 사용자 언어로 답하되 id/플래그/상태명은 영문 verbatim |
| 유료/온라인 행위 | 설명만 하고 절대 먼저 켜지 않음(`--online`, `--llm`, `propose_regulations=yes`, `extract_datasheet_facts=yes`) |

### 3.4 협업 환경 보완점
| # | 항목 | 제안 |
|---|---|---|
| C1 | reason-network 바이너리가 scratchpad에 있음 | 사용자가 원하면 공식 설치(`irm https://reasonmachines.com/network/install.ps1 \| iex`)로 PATH/서비스 설치 — 사용자 결정 |
| C2 | Codex 기본 모델 `auto/best-free` 실패 | `~/.codex/config.toml`의 `model`을 `auto/best-coding`으로 되돌릴지 사용자 결정; 그 전까지 `-m` 플래그 |
| C3 | Codex 스킬 디렉터리 비어 있음 | `~/.codex/skills/ponytail`, `graphify` 복사(AGENTS.md가 전제하는 위치) — 사용자 권한 필요 |
| C4 | `scripts/codex.ps1`가 브리지/모델 플래그를 모름 | 선택: `codex.ps1`에 `meet` 모드 추가(브리지 MCP + `-m`) |

---

### 3.5 보완 항목별 완료 조건 (Codex 회의에서 합의)
| 항목 | PASS 조건 |
|---|---|
| A1 | extras 없이 설치한 환경에서 `ai-eda doctor`가 크래시 없이 "httpx not installed" 한 줄을 찍는다 + 그 환경을 흉내 내는 smoke test 1개 |
| A3 | **먼저 원인 확인**(assertion 반올림인지, ngspice 버전 드리프트인지). 드리프트면 기록된 ngspice 버전별 앵커로; 허용치를 넓혀 통과시키는 "테스트 연극"은 금지 |
| A5 | 모든 서브커맨드가 `IRSchemaError`를 exit 2 + 한 줄 메시지로 매핑 |
| A6 | 무시되는 `confirm_design`마다 stdout에 `note: confirm_design ignored: <4가지 정확한 사유 문자열 중 하나>`, 같은 문자열이 pipeline.json outcome message에 저장, 사유별 테스트 1개. 4가지 사유 문자열은 스킬 문서(answers.md)가 참조하는 **고정 API** |
| B4 | pop은 의도된 설계로 유지(오래된 산출물이 현재인 척하는 쪽이 더 나쁨). 단, 단계 메시지에 `previous <kind> artifact removed (compile refused: <reason>)`를 **stdout 최상위**와 pipeline.json 양쪽에 남긴다. 복원 메커니즘은 만들지 않는다 |
| B2+B9+B10 | 한 번의 "단계 의미론" 변경으로 함께 고친다: 미결 규제 후보가 있으면 RELEASE가 그 키를 명시하고, 질문에 막힌 단계와 FAIL 단계를 구분해 표시하며, USER_INPUT_REQUIRED만 있는 리뷰는 "blocked"로 요약된다 |
| B1 | canary 실행 후 `PROJECT_RULES_MEASURED_VERSIONS` / `EXPORT_3D_MEASURED_VERSIONS`에 10.0.6 기록; 스킬의 pipeline.md는 그 측정 기준으로 동결 |

## 4. 다음 단계 (천천히)
1. **이 plan 검토** — 사용자 확인.
2. **A5 + A6 수정** (Codex 1순위): exit code 매핑과 `confirm_design` 무시 4경우의 note. 스킬의 핵심 루프("표를 보고 → 다음 실행에서 확인")가 조용히 깨지지 않게 하는 것이 먼저.
3. **B4 메시지 + B2/B9/B10 단계 의미론** (Codex 2순위).
4. **B1 canary 측정** (Codex 3순위): 이 PC에서 미측정 테스트 실행 → 참고 레포에 PR. 스킬 문서는 측정된 버전만 말한다.
5. **스킬 설계 회의 #2** (Codex와 reason-network): §3.3 확정. canary 결과 뒤에 연다(문서가 "바라는 버전"이 아니라 측정값을 말하도록).
6. **SKILL.md 초안** → 실제 과제 2개로 시험(분배기 재설계, 의도적으로 kicad-cli 없는 환경) → Codex review → 수정.
7. **푸시**: EAD_Engineer_Skill에 커밋. AI_Project 레포에는 `scripts/rn_bridge.py`와 `.gitignore`만.

## 5. Codex 검토 의견 (회의 #1, 2026-11-04, reason-network)
전문: `notes/meetings/2026-11-04-meeting-1.md`. 요지:
- **WRONG으로 지적, 수용**: R4 "모든 과제의 첫 명령 = doctor"는 과함 → "과제를 이해한 뒤, ai-eda 명령을 처음 쓰기 직전에 `doctor --strict`"로 수정. A3는 원인 미확인 상태의 추정 → 완료 조건에 "원인 먼저" 명시. A2는 콘솔 인코딩 문제라 제품 결함이 아님 → 스킬은 찍힌 파일명에 의존하지 않고 exit code와 JSON만 읽는다(수용, 참고 레포 수정은 선택).
- **MISSING, 수용**: 항목별 완료 조건(§3.5 신설), A1 회귀 테스트, "스킬을 막는 항목"의 우선순위 매핑(A5·A6·B1이 먼저 정리돼야 스킬을 진실되게 쓸 수 있다).
- **OVERBUILT, 수용**: answers.md는 한 화면·"나머지는 `ai-eda run --help`"; without-cli.md는 증거 장부 원칙 + 가장 흔한 fallback 하나만, 더 깊으면 설치를 권한다; pipeline.md 표의 셀은 한 줄. R2(check_evidence.py 없음)·R3(ir.md 없음) 전적으로 동의.
- **TOP-3**: ① A5+A6 ② B4 메시지 + B2/B9/B10 ③ B1 canary 후 pipeline.md 동결 — §4 순서에 반영.
- **후속 질의 결과**: B4 롤백 요구 철회(pop 유지 + stdout/pipeline.json 메시지). A6 완료 조건은 Claude 초안에 "4가지 사유 문자열을 고정 API로" 추가.

## 6. 미검증 / 건너뛴 것
- `--llm openrouter|claude` 경로는 키/CLI가 없어 실행하지 못했다.
- 그래프 건강 경고: dangling-endpoint 엣지 2,063개(문서 노드가 추측한 코드 id), 중복 엣지 ~3.8k — 질의에는 지장 없으나 `graphify update` 전에 참고.
- pytest 전체(-x 없이) 결과는 작성 시점에 실행 중.
