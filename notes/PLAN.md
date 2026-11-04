# EDA_Engineer 스킬 프로젝트 — 세팅 · 이해 · 보완점 Plan

작성: Claude (lead), Codex 검토 반영. 날짜: 2026-11-04.
범위: 이 문서는 **스킬을 아직 쓰지 않는다.** (1) AI_EDA 실행 환경 세팅 결과, (2) AI_EDA_Engineer 프로젝트 이해, (3) 보완점과 다음 단계, (4) 확장 방향(범용 회로 설계·프로그래머블 소자 시뮬레이션, §7)만 적는다. 스킬 본문(SKILL.md)은 이 plan을 사용자가 확인한 뒤 천천히 진행한다.

---

## 1. 세팅 현황

### 1.1 로컬 레이아웃 (`B:\0) AI_Project`)
| 경로 | 내용 | 상태 |
|---|---|---|
| `AI_EDA_Engineer/` | 참고 레포 클론 (github.com/Yuchan-00/AI_EDA_Engineer, main `4ee4d8e`) | 직접 커밋 금지; 수정은 브랜치+PR(§4 1단계 ①) |
| `AI_EDA_Engineer/.venv/` | Python 3.12.10 venv, `pip install -e ".[llm,parts,dev]"` | `ai-eda 0.0.1` 동작 |
| `AI_EDA_Engineer/graphify-out/` | 코드+문서 지식 그래프 (12,034 노드 / 50,193 엣지 / 183 커뮤니티, `graph.html`, `GRAPH_REPORT.md`) | 질의 가능: `AI_EDA_Engineer/` 안에서 `"B:\0) AI_Project\.venv\Scripts\graphify.exe" query "<질문>"` (graphify는 AI_Project의 venv에 설치됨; AI_EDA_Engineer의 venv에는 없음) |
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

`pytest -x`: 179 passed, **1 failed** (`tests/test_circuit_templates.py::test_astable_verifies_at_the_bounds_of_its_own_validity_range[3 V-100 Hz-100.0]`): 측정 편차 4.94 % > 허용 4.9 % (`AstableTemplate.MEASURED_DEVIATION_MAX`). 이 PC의 ngspice-46 결과가 프로젝트가 앵커로 삼은 값과 미세하게 다름. 전체 실행(`-x` 없이): 13 failed / 2870 passed / 55 skipped, 15 분 — 한 테스트(A7)는 Windows에서 영원히 멈추므로 deselect 필요. 상세는 §3.1-b.

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
- `PROJECT_RULES_MEASURED_VERSIONS`, `EXPORT_3D_MEASURED_VERSIONS` 비어 있음 → `mfg.capability` 기하 행 전부 NOT_VERIFIED. 3D export 플래그 canary는 이 PC에서 통과했으나 **미기록**(§3.1-b).
- 배치된 보드의 실제 DRC는 설치 CI에서는 selftest 분배기 보드만 측정. ATmega128·라디오 보드의 ERC/DRC canary는 이 PC(KiCad 10.0.6)에서 통과(§3.1-b); 측정 버전 상수가 비어 있어 **기록만 남음**(§3.2 B1).
- Windows: `.ai-eda.lock`의 `msvcrt.locking`, claude.exe stdin 경로, cp949 로케일 설치 미측정.
- `domain.high_speed.si`, `domain.power.pi`는 항상 NOT_VERIFIED인 스텁.
- `regulatory_conflict`, `unverified_component_data`, `circuit_structure_change` 수리 범주는 선언만 있고 어디서도 emit되지 않는다.

---

## 3. 보완점

### 3.1 이 PC에서 재현된 문제 (근거 있음)
| # | 문제 | 근거 | 제안 |
|---|---|---|---|
| A1 | `pip install -e .`만 하면 `ai-eda doctor`가 `ModuleNotFoundError: httpx`로 크래시 | `cli.py:324 cmd_doctor → from ai_eda.llm.openrouter import …`; `httpx`는 `[llm]` extra | doctor의 import를 try/except로 감싸 "LLM key: httpx not installed (pip install 'ai-eda-engineer[llm]')"로 보고 |
| A2 | ~~selftest/run이 콘솔에 한국어 파일명을 깨뜨려 출력~~ → **제품 결함 아님** (2차 검토에서 철회) | `cli.py` `_tolerant_output()`이 비-UTF-8 파이프에 이미 `errors="replace"`를 건다. 내가 본 `01_�̷�_������.md`는 cp949로 바르게 쓴 바이트를 UTF-8 터미널이 그린 것 | 참고 레포 수정 없음. 스킬은 `PYTHONUTF8=1`로 실행하고, 파일명은 stdout이 아니라 `pipeline.json`/`ai-eda report`에서 읽는다 |
| A3 | `test_astable_verifies_at_the_bounds…[3 V-100 Hz]` 실패: 편차 4.94 % > `MEASURED_DEVIATION_MAX` 0.049 | 이 PC ngspice-46 (KiCad 10.0.6 동봉) | 먼저 원인 확인(§3.5 A3): `pytest "tests/test_circuit_templates.py::test_astable_verifies_at_the_bounds_of_its_own_validity_range[3 V-100 Hz-100.0]"`로 측정값을 찍고, 참고 레포가 앵커를 잡은 커밋의 ngspice 버전과 비교. 드리프트로 확인되면 버전별 앵커(이미 RF 테스트가 쓰는 방식)로 확장; 상한을 측정값으로 재기록하는 것은 하지 않는다(§3.5 "테스트 연극" 금지) |
| A4 | 문서 3개가 에이전트 도구(Read)로 읽히지 않는 초장문 줄 | README/CLAUDE.md/ARCHITECTURE.md 최대 17 KB/줄 | 줄바꿈(80~120자) 또는 섹션 분할. 스킬은 이 문서를 그대로 쓰지 않고 **증류본**을 가져야 한다 |
| A5 | `ai-eda run`/`review`가 손상된 ir.json(모르는 키, 다른 schema_version)에 **traceback + exit 1** | `cli.py:839`(run)·`cli.py:1047`(review)의 `ir = _load(args.ir)`가 try 밖이고 `main()`에 핸들러가 없다. `report`·`serve`·`stage-reports`(공용 로더 `_report_inputs`, `cli.py:1073-1088`)·`relocate`(`:1173`)만 exit 2(`gui`는 IR 파일을 받지 않아 대상 아님). 2차 검토에서 이 PC로 재측정(3차 검토 2026-11-04에 run·report 재확인): `ai-eda new a5 --dir <tmp>` → `<tmp>/ir.json` 최상위에 `"bogus_key": 1` 추가 → `ai-eda run <tmp>/ir.json` / `ai-eda report <tmp>/ir.json` → run/review 모두 `IRSchemaError: … unknown key(s) the IR models would drop: bogus_key` traceback, **exit 1**; report는 한 줄 + exit 2 | run/review도 `IRSchemaError → stderr 한 줄 + exit 2`로 통일(이미 `report`가 쓰는 except 절 그대로). 스킬의 exit code 표에는 수정 전 버전을 위해 "traceback+exit 1 = ir.json 로드 실패, 설계 FAIL 아님"을 남긴다 |
| A6 | ~~`confirm_design=yes`가 조용히 무시되는 경우가 4가지~~ → **조용하지 않다** (2차 검토에서 정정) | `agents/circuit.py` 4경우 모두 stage 메시지에 `confirm_design ignored: <사유>`를 넣는다(144·149·167·174·208행; 4경우에 문자열 5개 — "템플릿 없음" 경우가 `no template to confirm`/`template <t> proposes nothing` 두 문자열). 메시지는 `run` 출력의 stage 줄(`cli.py:913`)과 `pipeline.json`의 `state.outcomes[].message`에 같은 문자열로 남는다. 테스트: 같은 실행의 답(`test_circuit_templates.py:315`, `:980`, `test_leave_out.py:188`), 설계 내용 존재(`:414`), 템플릿 없음(`:427`), 표 해시 불일치(`:1004`) 있음. **`template <t> proposes nothing`(149행)만 테스트 없음** | 코드 수정 없음. 남은 것: (1) `proposes nothing` 사유 테스트 1개, (2) 스킬 `answers.md`가 4개 사유 문자열을 verbatim으로 싣고 "stage 줄에 `confirm_design ignored:`가 보이면 적용 안 된 것"이라고 가르친다 |
| A7 | **Windows에서 `ai-eda serve`가 이미 사용 중인 포트에 두 번째로 바인딩된다** → 전체 pytest가 `tests/test_report.py::test_serve_loopback_read_only_and_live`에서 영원히 멈춤(첫 실행 7시간 후 강제 종료; 재실행은 faulthandler 15분 타임아웃으로 확인) | `report/server.py:104` `ThreadingHTTPServer`는 stdlib `HTTPServer.allow_reuse_address = 1`(SO_REUSEADDR)을 물려받는데, Windows의 SO_REUSEADDR는 LISTEN 중인 포트에도 bind를 허용한다. 이 PC에서 재현: 같은 127.0.0.1 포트에 `HTTPServer` 두 번째 생성 성공. 테스트는 `serve(ir_path, port) == 2`(OSError)를 기대하지만(`test_report.py:657-659`) 두 번째 `serve()`가 `serve_forever`에 들어가 돌아오지 않는다. 제품 영향: 사용자가 같은 포트로 `serve`를 두 번 띄우면 오류 없이 두 서버가 공존(요청이 어느 쪽에 가는지 불명) | GUI 서버는 이미 고쳐져 있다(`gui/server.py:696-700` `_LoopbackServer.allow_reuse_address = os.name != "nt"`, 독스트링이 정확히 이 문제를 설명). `report/server.py:104`만 같은 서브클래스를 쓰도록 바꾸면 끝(두 줄). 테스트는 Windows에서도 OSError 경로를 타게 된다 |

**§3.1-b 전체 pytest 결과 (2026-11-04, 이 PC = 첫 Windows 측정)**: `pytest -v -o faulthandler_timeout=900 --deselect tests/test_report.py::test_serve_loopback_read_only_and_live` → **13 failed, 2870 passed, 55 skipped, 1 deselected, 14 분 57 초** (exit 1). deselect 없이 돌리면 A7에서 영원히 멈춘다(첫 실행은 7 시간 뒤 강제 종료). 가장 느린 테스트: `test_kr447_tx_exciter.py::test_the_pipeline_on_the_bench_header_board` 81 s. 로그는 크기 때문에 레포에 넣지 않음(AM 프로브 덱은 `notes/measurements/2026-11-04/`).

| 묶음 | 실패 테스트 | 첫 오류 | 분류 |
|---|---|---|---|
| A3 | `test_circuit_templates.py::test_astable_verifies_at_the_bounds…[3 V-100 Hz]`, `[3 V-200 Hz]` | 편차 4.94 % > 0.049 | ngspice-46 드리프트 (A3; 추정 — 원인 확인 전, §3.5 A3) |
| A8 Windows | `test_claude_cli_client.py::test_an_interrupt_during_the_call_kills_and_reaps_the_child` | `OSError: [WinError 87] 매개 변수가 틀립니다` (자식 종료 경로) | Windows 전용, README가 "미측정"이라 한 claude.exe 경로 |
| A8 Windows | `test_claude_cli_client.py::test_an_argument_the_os_cannot_encode_is_an_llm_error_not_a_value_error` | 오류 종류 `'http' != 'transport'` | Windows 전용 (인코딩 불가 인수의 분류) |
| A8 Windows | `test_gui_server.py::test_post_needs_the_pages_own_origin_and_a_json_body`, `…::test_the_run_endpoints_need_the_pages_own_origin_and_a_json_body` | `ConnectionAbortedError: [WinError 10053]` | Windows 전용: 서버가 본문을 읽지 않고 거부하면 클라이언트 쓰기가 중단됨(POSIX에서는 상태 코드가 보임) |
| A8 Windows | `test_report.py::test_report_of_offline_divider_run`, `…::test_questions_have_answer_commands_and_model_labels`, `test_leave_out.py::test_a_refusal_is_answered_by_leave_out…` | 보고서의 답 명령이 `ai-eda run '…\ir.json'`로 따옴표 붙음(기대: 따옴표 없음) | Windows 전용: `report/data.py:390,395` `shlex.quote(str(ir_path))`가 역슬래시 경로를 POSIX 규칙으로 인용. 제품 영향: 보고서가 보여 주는 명령이 cmd.exe에서 그대로 안 돈다 |
| A8 Windows | `test_md_review_findings_regressions.py::test_7_remove_matches_by_design_content` | `assert rebuilt != divider_ir.net("GND")  # model equality sees the wall clock` 실패: 두 `Net`의 `created_at`이 같음 | Windows 전용(추정): 픽스처와 테스트가 같은 시계 눈금 안에 만들어짐. 테스트 가정(벽시계가 항상 다르다)의 문제 |
| A8 Windows | `test_report_pdf.py::test_a_snap_browser_is_not_started_on_a_file_it_cannot_read` | `pdf.is_snap(WindowsPath(…/chromium-browser))`가 True | Windows 전용: snap 판정이 경로 이름만 본다 |
| A9 ngspice-46 | `test_rf_spice.py::test_am_depth_of_ngspice_s_am_source`, `…::test_a_biased_am_depth_never_passes_a_depth_outside_the_band` | `no carrier: the amplitude (0 .. 0) is within the engine's resolution`; `KeyError: 'measured'` | ngspice 변경: NEWS에 ngspice-43 "Update the AM voltage/current sources: enable amplitude modulation, carrier suppression", ngspice-46 "FM and FC exchange place in the parameter sequence of SFFM". 이 PC 측정: 래퍼로 `AM(1 0 1k 20k 0)` → 0…1 V(음의 반주기 없음), `AM(1 0 1k 20k)` → ±970 V. 컴파일러는 `AM(VA VO MF FC TD)`/`SFFM(VO VA FC MDI FS)` 옛 순서로 쓴다(순서의 출처는 `ir/simulation.py:174-181` `STIMULUS_PARAMS`, 소비는 `compilers/spice.py:423` `_stimulus_spec`; `:73-75`는 독스트링). 측정 덱: `notes/measurements/2026-11-04/am.cir`, `am2.cir`. 새 파라미터 의미는 UNVERIFIED — 담당 Claude: ngspice-46 매뉴얼 §4.1.6(ngspice.sourceforge.io/docs)을 읽고 AM/SFFM 인자 순서 표를 이 행에 추가 |

같은 실행에서 **통과한 것 중 plan에 중요한 것**: `test_kicad_cli.py::test_sibling_project_rules_are_applied_by_drc_canary` PASSED (14 s), `test_kicad_3d_export.py::test_3d_exports_write_step_glb_and_png_canary` + `…flags_are_listed_by_help_canary[×3]` PASSED, `test_silkscreen.py::test_silk_drc_canary…` PASSED, 실제 브라우저(Chrome) 렌더/PDF 테스트 전부 PASSED → **B1의 canary는 이 PC(KiCad 10.0.6)에서 이미 통과했다. 남은 일은 측정 버전 상수에 `10.0.6`을 기록하는 것뿐**(§3.2 B1). 55 skipped는 대부분 "도구 없음" 분기(LLM 키, claude.exe 등).

| # | 문제 | 근거 | 제안 |
|---|---|---|---|
| A8 | Windows에서 실패하는 테스트 9개(위 표) — 제품 결함은 그중 보고서 답 명령 인용(`report/data.py:390,395`; cmd.exe에서 안 도는 명령을 보여 줌)과 두 서버의 본문 미수신 거부(클라이언트에 10053) | 첫 Windows 전체 실행 | 각 테스트를 "Windows에서 기대값 분기"로 고치지 말고 제품 쪽을 먼저 본다: 답 명령은 Windows면 따옴표 없이(또는 PowerShell 규칙), 서버는 거부 전에 본문을 읽고 버린다. 나머지(claude.exe 종료 경로, snap 판정, 벽시계 동일성)는 Windows 분기 |
| A9 | ngspice-43/46의 AM·SFFM 소스 파라미터 변경으로 AM 테스트 2개 실패 | NEWS + 이 PC 측정(위 표) | A3과 함께 "ngspice 버전 앵커" 작업으로 묶는다: 매뉴얼로 새 파라미터 의미 확인 → 컴파일러가 엔진 버전에 따라 순서를 쓰거나, 46 이상만 지원한다고 선언. 참고 레포의 앵커는 ngspice-42(소스·문서에 177회 언급, 46은 36회) → 42→46 사이의 변경이 원인 범위 |

### 3.2 설계/구현 보완점 (코드 읽기 + 그래프 분석에서 나온 것)
| # | 항목 | 왜 문제인가 | 제안 |
|---|---|---|---|
| B1 | 미측정 canary를 이 PC에서 측정 → **측정 완료, 기록만 남음** | KiCad 10.0.6 + ngspice-46이 있는 첫 실제 머신. §3.1-b 전체 실행에서 `…sibling_project_rules_are_applied_by_drc_canary`, `…3d_exports_write_step_glb_and_png_canary`, 3D `--help` 플래그 canary ×3, silk DRC canary가 모두 PASSED | `PROJECT_RULES_MEASURED_VERSIONS`/`EXPORT_3D_MEASURED_VERSIONS`에 `"10.0.6"` 기록(+ 기록 근거로 이 실행 로그 요약을 PR 본문에) → `mfg.capability`가 처음으로 PASS 가능. ATmega128/라디오 보드 ERC·DRC도 같은 실행의 `test_kr447_*`·`test_atmega128_template` 통과로 측정됨 |
| B2 | 규제 범위 질문이 non-blocking | 후보가 UNDECIDED인 채 RELEASE 도달 가능(`regulatory.applicability` NOT_VERIFIED) | RELEASE 메시지에 미결 키를 명시(이미 일부) + 스킬이 반드시 되묻도록 |
| B3 | 수리 범주 3종이 emit되지 않음 | `NON_REPAIRABLE` 선언과 실제 불일치 | emit 지점을 만들거나 목록에서 제거(문서 정합) |
| B4 | 컴파일 거부 시 이전 산출물 pop | `Orchestrator._compile`이 FAIL/NOT_VERIFIED면 그 kind를 `ir.artifacts`에서 제거 → 하류가 "no PCB artifact" | 의도된 동작이지만 메시지에 "previous artifact removed" 명시 |
| B5 | `doctor` exit 0 (`--strict` 없이) | 스크립트가 exit code만 보면 "ai-eda가 import된다"만 안다 | 설치 스크립트/스킬은 항상 `--strict` |
| B6 | 기본 배선이 all-or-nothing | 넷 하나 못 그리면 구리 0 → DRC unconnected_items | 스킬이 `pcb.routing=partial`을 안내; 기본값 재검토는 사용자 결정 |
| B7 | README 현재 상태 표 날짜(2026-09-27) vs 변경 이력(2026-10-14) | 최신 권위는 변경 이력 | 상태 표 날짜 갱신 |
| B8 | 단계 이름 대소문자 혼용(README 대문자, 코드 `StrEnum` 소문자) | 스킬이 run 출력을 파싱할 때 혼란 | 문서를 소문자 id로 통일 |
| B9 | `worst_status`에서 USER_INPUT_REQUIRED < FAIL이지만 오케스트레이터는 질문에서 멈춤 | FAIL 단계가 동시에 blocking 단계가 될 수 있음 | 출력에 "blocked by question" 라벨 분리 |
| B10 | 리뷰에 USER_INPUT_REQUIRED만 있으면 `failures`가 비어 수리 루프가 "no failures"로 종료 | 설계는 막혀 있는데 수리 루프는 성공처럼 보임 | 리뷰 요약에 blocked 카운트 추가 |

2차 검토에서 소스로 재확인한 근거: B1 `tools/kicad/cli.py:139,143`(빈 `frozenset()`), `tools/manufacturing/capability.py:197-198`("not measured" 반환) · B2 `agents/regulatory.py:188`(`required=False`) · B3 `repair/strategies.py:20-23` 외 emit 지점 없음 · B4 `workflow/orchestrator.py:458,462`(pop; 메시지는 `<kind> compile refused: …`뿐) · B5 `cli.py:408` · B7 README 35행 `## 현재 상태 (2026‑09‑27)` · B8 README에 `DRC` 70회, `SPICE` 46회, `RELEASE` 35회, `IR_BUILD` 12회 등 대문자 vs 소문자 id 2회 · B9 `ir/validation.py` `_SEVERITY` 순서 · B10 `repair/loop.py:101-104`(`report.failures`만 순회) · 락 범위 `cli.py:846,1053,1120,1179`(run/review/stage-reports/relocate).

### 3.3 스킬(EDA_Engineer) 설계에서 결정할 것 — 나의 권고
| 질문 | 권고 |
|---|---|
| 파일 구조 | **SKILL.md + references 3개(그중 no-CLI 페이지는 한 화면)**: `references/pipeline.md`(19단계 표: 무엇이 돌고, PASS 조건, NOT_VERIFIED vs FAIL, 수리 범주; RF/SI는 한 문단), `references/answers.md`(제어 키 `CONTROL_KEYS` + 기본 키 4개 + 템플릿 입력 키와 범위 + 규제 범위 키 + `pcb.*` 조향 + 승인 플래그; 나머지는 `ai-eda run --help`로), `references/without-cli.md`(감지 → 설치 제안 → 거절 시 kicad-cli ERC/DRC 두 명령, ngspice 호출, 증거 장부 행 형식) |
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
| A5 | `run`·`review`가 `IRSchemaError`를 exit 2 + 한 줄 메시지로 매핑(report/serve/stage-reports/relocate는 이미 그렇다; `gui`는 IR 파일을 받지 않음) + run/review 각 1개 테스트 |
| A6 | (2차 검토로 축소) 사유 문자열·stdout·pipeline.json은 이미 충족. 남은 PASS 조건: `proposes nothing` 사유 테스트 1개 추가, 그리고 사유 문자열 5개(4경우; `ignored: answer(s) […] were given in this run`, `ignored: the table below (…) is not the one you confirmed`, `ignored: design content already present`, `ignored: no template to confirm` / `ignored: template <t> proposes nothing`)을 `answers.md`에 verbatim 수록. 이 문자열은 스킬이 참조하는 **고정 API**이므로 참고 레포에서 바꾸면 스킬도 바꾼다 |
| B4 | pop은 의도된 설계로 유지(오래된 산출물이 현재인 척하는 쪽이 더 나쁨). 단, 단계 메시지에 `previous <kind> artifact removed (compile refused: <reason>)`를 **stdout 최상위**와 pipeline.json 양쪽에 남긴다. 복원 메커니즘은 만들지 않는다 |
| B2+B9+B10 | 한 번의 "단계 의미론" 변경으로 함께 고친다: 미결 규제 후보가 있으면 RELEASE가 그 키를 명시하고, 질문에 막힌 단계와 FAIL 단계를 구분해 표시하며, USER_INPUT_REQUIRED만 있는 리뷰는 "blocked"로 요약된다. 메시지 문구만 고쳐 통과하지 못하도록 픽스처 2개: UNDECIDED 규제 후보를 가진 채 RELEASE에 도달하는 실행, USER_INPUT_REQUIRED만 있는 리뷰 |
| B1 | (canary는 §3.1-b에서 통과) 기록 근거로 canary 테스트 node id 6개(§3.1-b 목록)와 그 PASSED 줄을 `notes/measurements/2026-11-04/`에 커밋하고 PR 본문에 복사(세션 scratchpad 로그는 사라진다); 그 뒤 `PROJECT_RULES_MEASURED_VERSIONS` / `EXPORT_3D_MEASURED_VERSIONS`에 10.0.6 기록 후 `tests/test_fab_capability.py`의 monkeypatch 없이 `mfg.capability`가 PASS; 스킬의 pipeline.md는 그 측정 기준으로 동결 |
| A7 | `report/server.py`가 `gui/server.py:696-700`의 `_LoopbackServer`를 쓰고, Windows에서 `test_serve_loopback_read_only_and_live`가 멈추지 않고 통과 |
| A8/A9 | A8: 보고서 답 명령이 Windows에서 따옴표 없이 나오고 두 서버 테스트가 10053 없이 통과; 나머지는 Windows 분기로 통과. A9: 원인(ngspice-46 AM 소스) 확인 뒤 A3과 같은 버전 앵커 방식 |

## 4. 다음 단계 (천천히)
1. **이 plan 검토** — 사용자 확인. 답이 필요한 결정(2단계 이후는 ①의 답 없이 시작하지 않는다):
   ① 참고 레포 수정 방식 — (a) 업스트림 PR(Yuchan-00/AI_EDA_Engineer; 비용: 항목마다 테스트+리뷰, 머지 대기) / (b) 수정 없이 스킬에 우회만 기록(비용: 스킬이 §3의 주의사항을 영구히 안고 감). 2–4단계와 §7은 (a)를 전제한다.
   ② 확장 순서 — D1(범용 입구, 가장 큰 변경)을 먼저 / E1→E3(펌웨어 요청에 직접 해당, 오늘 도구로 PASS 가능)을 먼저. 현재 §7.4는 D 먼저.
   ③ B6 기본 배선 all-or-nothing 유지 여부(비용: 바꾸면 기본값 테스트와 DRC 기대값 수정).
   ④ C1 reason-network 공식 설치(비용: 외부 설치 스크립트 실행, PATH·서비스 등록) / ⑤ C2 `config.toml` model 변경(비용: 한 줄; 안 하면 호출마다 `-m`) / ⑥ C3 Codex 스킬 복사(비용: 파일 복사 권한) / ⑦ C4 `codex.ps1` meet 모드(비용: 스크립트 수정).
   ⑧ D7 넷리스트→D1 변환기(비용: 파서 + 왕복 테스트; D1 형식 확정 뒤).
   ⑨ §7.4 (c)(d) 외부 설치: standalone ngspice-47, C 컴파일러·Verilator(비용: 설치 + 라이선스 경계 판단, §7.4 위험 표).
   ⑩ §3.3 권고 확인: `check_evidence.py`·`references/ir.md` 만들지 않음, SKILL.md 250줄 이하.
2. **A5 수정 + A6 잔여 테스트 1개** (Codex 1순위였던 "A5+A6"의 축소판): run/review의 `IRSchemaError → exit 2` 매핑(시작 전 확인: README의 exit code 설명과 `tests/test_cli_llm.py`의 `assert code == 1`이 손상 IR이 아니라 질문 차단을 뜻하는지), `proposes nothing` 테스트(트리거: `plan.buildable`이 False인 plan — `agents/circuit.py:147-149` — 을 `design_from_requirements` monkeypatch로 만들고 `confirm_design=yes`를 준다). A6의 제품 코드 수정은 없음(테스트 1개만 추가); 사유 문자열 5개의 `answers.md` 수록은 6단계에서. 검증은 15분 전체 실행이 아니라 `pytest tests/test_ir.py tests/test_workdir_relocate.py tests/test_circuit_templates.py tests/test_leave_out.py`로.
3. **B4 메시지 + B2/B9/B10 단계 의미론** (Codex 2순위).
4. **B1 기록 + A7 두 줄 수정** (Codex 3순위; canary는 §3.1-b에서 이미 통과): 측정 버전 상수에 10.0.6 기록, `report/server.py`에 `_LoopbackServer` 적용 → 참고 레포에 PR. 스킬 문서는 측정된 버전만 말한다.
   4b. **A1 · A3 · A8 · A9**(스킬을 막지 않는 항목, §5 MISSING): A1 smoke test(§3.5); A3+A9는 원인 확인(§3.1 A3 명령, A9 매뉴얼 확인) 뒤 ngspice 버전 앵커로 함께; A8은 제품 쪽 2건(보고서 답 명령 인용, 본문 미수신 거부)을 먼저, 나머지는 Windows 분기. 5단계 이후와 병행해도 된다.
5. **스킬 설계 회의 #3** (Codex와 reason-network; #2는 §7 검토로 이미 열렸다, §5): §3.3 확정. B1 기록(4단계) 뒤에 연다(문서가 "바라는 버전"이 아니라 측정값을 말하도록).
6. **SKILL.md 초안** → 실제 과제 2개로 시험(분배기 재설계, 의도적으로 kicad-cli 없는 환경) → Codex review → 수정. PASS 조건: 두 과제 모두 스킬이 보고한 단계 상태가 `pipeline.json`의 `state.outcomes[]`와 일치하고, 스킬이 pipeline.json에 없는 PASS를 한 번도 주장하지 않으며, kicad-cli 없는 과제에서 ERC/DRC를 NOT_VERIFIED로 보고한다.
7. **푸시**: EAD_Engineer_Skill에 커밋. AI_Project 레포에는 `scripts/rn_bridge.py`와 `.gitignore`만.
8.–11. **확장(§7.4)**: §7.4의 순서(D1→D4→D3→D6; E1→E3→E2(+E4); 측정 뒤 E5/E6)를 따른다. 1–7이 끝난 뒤에만.

## 5. Codex 검토 의견 (회의 #1, 2026-11-04, reason-network)
전문: `notes/meetings/2026-11-04-meeting-1.md`. 요지:
- **WRONG으로 지적, 수용**: R4 "모든 과제의 첫 명령 = doctor"는 과함 → "과제를 이해한 뒤, ai-eda 명령을 처음 쓰기 직전에 `doctor --strict`"로 수정. A3는 원인 미확인 상태의 추정 → 완료 조건에 "원인 먼저" 명시. A2는 콘솔 인코딩 문제라 제품 결함이 아님 → 스킬은 찍힌 파일명에 의존하지 않고 exit code와 JSON만 읽는다(수용; 참고 레포 수정 없음 — §3.1 A2).
- **MISSING, 수용**: 항목별 완료 조건(§3.5 신설), A1 회귀 테스트, "스킬을 막는 항목"의 우선순위 매핑(A5·A6·B1이 먼저 정리돼야 스킬을 진실되게 쓸 수 있다).
- **OVERBUILT, 수용**: answers.md는 한 화면·"나머지는 `ai-eda run --help`"; without-cli.md는 증거 장부 원칙 + 가장 흔한 fallback 하나만, 더 깊으면 설치를 권한다; pipeline.md 표의 셀은 한 줄. R2(check_evidence.py 없음)·R3(ir.md 없음) 전적으로 동의.
- **TOP-3**: ① A5+A6 ② B4 메시지 + B2/B9/B10 ③ B1 canary 후 pipeline.md 동결 — §4 순서에 반영.
- **후속 질의 결과**: B4 롤백 요구 철회(pop 유지 + stdout/pipeline.json 메시지). A6 완료 조건은 Claude 초안에 "4가지 사유 문자열을 고정 API로" 추가.
- **회의 #2 (§7 검토, 1라운드, 전문 `notes/meetings/2026-11-04-meeting-2.md`)**: WRONG 3건 수용("입구만 닫혀 있다"→검사·리뷰·보고서의 템플릿 결합으로 정정; d_cosim은 파싱까지만 측정; "불가"→"시도한 두 형태로는 불가"). MISSING: 아날로그 IC 벤더 모델 입구(D6 신설), 넷리스트→IR 변환(D7, 사용자 결정), 시간축 결합 위험(위험 표에 추가); "E1부터 엔진 사망 위험"은 E1–E3가 코시뮬 카드를 만들지 않으므로 거부(§7.4에 명시). OVERBUILT 수용: E4를 E2가 쓰는 탐지로 축소, 7.5를 두 줄로. ORDER: E1→E3→E2→E4로 변경, D 순서 유지. TOP-3: D1, E3(`A` 소자), E2(simavr VCD).
- **회의 뒤 2차 검토(Claude 단독, 소스 재확인)**: A6은 회의 때 양쪽 다 "조용히 무시"로 믿었으나 코드·테스트가 이미 이유를 찍고 있었다 → §3.1·§3.5·§4에서 축소. A2는 Codex 지적대로 제품 결함이 아님을 소스(`_tolerant_output`)로 확인해 철회. A5는 이 PC에서 재측정해 유지. 회의 전 사실 확인이 부족했던 것이 교훈: **다음 회의부터 "문제" 항목은 재현 명령과 결과를 붙여서만 올린다.**

## 6. 미검증 / 건너뛴 것
- `--llm openrouter|claude` 경로는 키/CLI가 없어 실행하지 못했다.
- 그래프 건강 경고: dangling-endpoint 엣지 2,063개(문서 노드가 추측한 코드 id), 중복 엣지 ~3.8k — 질의에는 지장 없으나 `graphify update` 전에 참고.
- pytest 전체 결과는 §3.1-b에 반영됨. 미확인으로 남은 것: A9의 새 AM/SFFM 파라미터 의미(매뉴얼), 참고 레포가 측정한 ngspice 버전, `test_7_remove…`의 Windows 의존(추정).
- §7의 UNVERIFIED: `d_cosim`의 실제 DLL 실행(ngspice-46), `d_process` 실행, STM32 아날로그 브리지 부재(찾지 못했을 뿐).

---

## 7. 확장 방향: 범용 회로 설계와 프로그래머블 소자 시뮬레이션

사용자 요청(2026-11-04): "모든 회로 설계에 활용이 가능하고, 가능하면 FPGA·STM32·ATmega 같은 프로그래머블 소자에 코드를 넣어 그 회로의 시뮬레이션까지." 이 절은 그 요청을 이 시스템의 원칙(IR 단일 원본, provenance, 증거 없음 = NOT_VERIFIED, LLM은 제안만, 측정 안 된 것은 동작한다고 말하지 않음, ponytail)으로 번역한다. 근거: 코드 조사 2건(범용성·시뮬레이션 스택, 소스 직접 읽기), 웹 조사 2건(MCU·FPGA 도구), 비평 2건, 그리고 Claude가 이 PC에서 직접 실행한 측정(2026-11-04, 아래 "측정됨"). 출처 없는 사실은 UNVERIFIED로 표시한다.

### 7.1 현재 한계 (사실)
- 회로 입구는 템플릿뿐(§2.3 행 4·§2.4; `ai_eda/design/__init__.py:1`, `design/templates.py:1524`, `design/rf/registry.py:32-38`; 거부문 `agents/circuit.py:141`; 거부문이 권하는 "직접 쓰라" `design/base.py:604`인데 CLI에 IR 편집 명령 없음 `cli.py:1268-1330`). 손으로 만든 IR은 SPICE까지 돈다(`tests/fixtures_rc.py:1-15`) — **IR→SPICE→KiCad 엔진은 범용이지만, 검사·리뷰·보고서·스택업은 템플릿에 결합돼 있다**(다음 항목; Codex 회의 #2 지적으로 "입구만 닫혀 있다"에서 정정). D3·D4가 그 결합을 푸는 항목이다.
- 비템플릿 설계가 들어오면 깨지거나 NOT_VERIFIED가 되는 곳: `design.inputs_vs_requirements`는 결과 자체가 없음(`design/checks.py:10-28`); 바인딩 없는 부품 하나면 `CompileError`(FAIL), 전부 없으면 `NothingToCompileError`(NOT_VERIFIED)(`compilers/spice.py:809-843`, `workflow/orchestrator.py:447-460`); 보고서 `NO_TEMPLATE`(`report/stages.py:139,280,373,699`); 스택업은 템플릿 선택 안의 `add_board`만(`templates.py:1670-1673`); 리뷰어는 `serves_requirements`가 비면 FAIL(`review/reviewer.py:400`).
- SPICE가 MCU/FPGA에 대해 오늘 할 수 있는 것: 엔진은 KiCad 동봉 `ngspice.dll`(ngspice-46, `tools/spice/ngspice_shared.py:17-19`). IR 소자는 R C L V I D Q M X T뿐, XSPICE `A`는 `SpiceDevice`에 없음(`ir/simulation.py:29-41`); 자극은 DC/PULSE/SINE/PWL(인라인 점만)/AM/SFFM(`ir/simulation.py:165-181`, `compilers/spice.py:400-422`); 판정은 `v()/i()` 아날로그 축약 11종(`ir/simulation.py:251-297`). `digital.cm`은 로드되고(`ngspice_shared.py:105`) 쓰임은 `gainblk` 자가시험 1건(`:787-811`). `.model` 카드는 subckt 밖에서도 통과하므로(`compilers/spice.py:366`) `.model d_*`는 이미 허용, 빠진 것은 `A` 소자뿐. `validate_deck`은 따옴표 문자를 금지한다(`ngspice_shared.py:393`).
- ATmega128 템플릿의 U1은 `exclude=True` + "nothing simulates or claims that the MCU runs"(`design/atmega128.py:266-269, 512`); KR447은 441 부품/211 넷에 IC 모델 0, 펌웨어 없음(`tests/test_kr447_transceiver.py:269,422`, `design/rf/t_transceiver.py:475`). 유일한 "IC 거동"은 SI 드라이버의 PULSE-R-T-C 모델(`tools/si/driver.py:1-33`). `Stage`는 아날로그 SPICE 하나(`workflow/stages.py:4-23`), `domain.digital.*` 검증기 없음.
- **측정됨(이 PC, KiCad 10.0.6 / ngspice-46, 2026-11-04; 덱·펌웨어·프로브 스크립트는 `notes/measurements/2026-11-04/`):**
  - KiCad `lib/ngspice/digital.cm`에 있는 모델(바이트 스캔): `d_and d_buffer d_cosim d_dff d_dlatch d_fdiv d_genlut d_in d_inout d_inverter d_jkff d_lut d_nand d_nor d_open_c d_open_e d_or d_osc d_out d_process d_pulldown d_pullup d_pwm d_ram d_source d_srff d_srlatch d_state d_tff d_tristate d_xnor d_xor`; `xtraevt.cm`에 `d_to_real`. `vlnggen*`/`ivlng*`/`ghnggen*` 헬퍼는 KiCad 디렉터리에 없음.
  - 혼성 덱(PULSE → `adc_bridge` → `d_inverter` → `dac_bridge` → RC)을 **기존 `NgspiceShared.run`으로 그대로** `tran 10u 5m` 실행: 성공, plot `tran1`, 795점, `in`=0일 때 `vout`=5 V(반전 확인), `out`은 RC 추종. 비평자는 subckt 안 `A1 … d_inverter`도 같은 래퍼로 실행(자동 `dac_bridge` 삽입, 0–3.3 V). → **XSPICE 디지털 + 브리지는 래퍼 수정 없이 동작한다.**
  - `d_cosim`을 래퍼로 넣기는 **시도한 두 형태로는 불가**: `simulation="<dll>"`에 따옴표가 필요한데 `ngspice_shared.py:393`이 거부. 따옴표를 빼면 경로가 식으로 파싱돼(`Undefined parameter`) 엔진이 "cannot recover"로 죽는다(프로세스 전체).
  - `d_cosim`을 ctypes로 `ngspice.dll`에 직접(`codemodel digital.cm` 로드 뒤, 따옴표 경로): 인스턴스가 파싱되고 `d_cosim failed to load simulation binary C:/nonexistent/fake_rtl.dll` 메시지, 엔진 생존(rc 0). → **파싱·DLL 로드 시도까지만 측정됨**; 실제 코시뮬 DLL이 이 DLL(ngspice-46)에서 돌아가는지는 UNVERIFIED(E6의 ngspice-47 전제 참고). 디지털 시뮬레이터 DLL(Verilator/GHDL 빌드)은 이 PC에 없다.
  - 펌웨어 도구: `C:\Users\yc012\.platformio\packages\`에 `toolchain-atmelavr`(avr-gcc 7.3.0)와 `tool-simavr` 1.8(패키지 1.10800.0; `--list-cores`에 atmega128/1280/1281/1284p/2560/328 등; CLI에 `-i/-o` VCD 입·출력, `--gdb`; `include/simavr/avr/avr_mcu_section.h`와 `lib/libsimavr.a` 동봉) **있음(PATH에는 없음)**. Arduino15에 avr-gcc·esp32 툴체인. **NOT FOUND**: arm-none-eabi-gcc, renode, qemu-system-arm, verilator, iverilog, ghdl, gcc/g++/cl/make/cmake, yosys, nextpnr, cocotb, openvaf.
  - **펌웨어 → VCD 실측(E2의 L1a 생산자)**: `PORTB ^= 1`을 200회 토글하는 blink.c를 avr-gcc로 ATmega128용 ELF로 빌드(`AVR_MCU_VCD_FILE` + `_MMCU_` 추적 선언), `simavr -m atmega128 -f 16000000 blink.elf` 실행 → `blink.vcd`(timescale 1 ns, PORTB 8비트) 401개 에지, 에지 간격 중앙값 ≈ 501 µs(지연 루프와 일치), 총 99.7 ms. 외부 설치 없이 됨. 남은 변환은 VCD→PWL뿐.

### 7.2 목표 정의
"모든 회로 설계에 활용 가능"은 이 시스템에서 "입구를 연다"이지 "엔진을 바꾼다"가 아니다. 유지: IR 단일 원본, 모든 값의 provenance, 2-run 확인(`confirm_design` 표·sha256), 바인딩 없는 부품은 `exclude`+사유, 증거 없음 = NOT_VERIFIED. 변경: 회로가 IR에 들어오는 길을 템플릿 외에 하나 더 두고(사용자 제공 설계 파일, 뒤에 LLM 제안), 비템플릿 설계에서 `NO_TEMPLATE`·스택업 부재·입력 검사 부재가 "결과 없음"이 아니라 명시적 상태가 되게 한다. 한계는 솔직히: **SPICE 모델이 없는 부품은 영원히 exclude**이며 그 부품을 지나는 요구는 NOT_VERIFIED다.

"펌웨어를 넣은 시뮬레이션"의 현실적 3단계(단계별 도구·측정 상태를 여기 한 번만 적는다):

| 단계 | 뜻 | 이 PC 측정 결과 | 미측정 / UNVERIFIED | 시간축 정확도 |
|---|---|---|---|---|
| L0 스펙 자극 | 펌웨어 없이 스펙(PWM 주파수·듀티, GPIO 시퀀스)을 PULSE/PWL로 MCU 핀에 건다. MCU는 계속 exclude | ngspice-46 DLL, 기존 자극·판정 모두 동작 | 없음 | 자극 가정 그대로 |
| L1 추적 자극 / 거동 핀 모델 | (a) 외부 에뮬레이터의 VCD를 PWL 점으로 변환해 건다; (b) 논리를 XSPICE `d_*`/`astate`로 거동 모델링(자동 `adc/dac_bridge`) | (b) 래퍼로 `A` 소자 실행 동작(7.1). (a) simavr 1.8 + avr-gcc로 **실제 펌웨어 → VCD 실측 완료**(7.1: 401 에지, ≈501 µs) | (a) VCD→PWL 변환기 없음(만들 것); Renode/wokwi-cli NOT FOUND | simavr: AVR 사이클; Renode: MIPS 처리량 모델이라 사이클·이벤트 시각 모두 부정확(웹 MCU 표); wokwi: 명시 없음 |
| L2 코시뮬레이션 | AVR: `d_process` + simavr 래퍼(파이프). FPGA: `d_cosim` + Verilator/Icarus RTL(소프트코어+펌웨어 포함). STM32: 오픈소스 아날로그 브리지를 **찾지 못함**(Renode Verilator/DPI 경로는 있으나 SPICE 연결 사례 없음; Proteus VSM만 상용) | `d_process`/`d_cosim` 모델 존재; `d_cosim`은 ctypes 직접 호출에서 파싱·DLL 로드 시도까지(7.1); 실행은 UNVERIFIED | `d_process` 실행(래퍼 프로그램 없음); simavr를 `d_process`로 감싸려면 libsimavr를 링크하는 C 프로그램이 필요한데 C 컴파일러 NOT FOUND; Verilator DLL 빌드는 standalone ngspice-47 필요(46은 bug 843로 `vlnggen` 불가) + Verilator/MinGW NOT FOUND; 래퍼의 따옴표 금지 규칙 예외 설계 | 디지털 이벤트 수준; 아날로그 패드 거동 아님 |

모든 단계에서 "펌웨어가 동작한다"가 아니라 "이 자극/모델 아래 이 넷의 이 파형이 기대와 맞았다"만 말한다. 논리 레벨은 자동 브리지 기본값(3.3 V)이지 AVR 5 V·STM32 3.3 V가 아니므로, L1(b) 이상은 `dac_bridge`/`adc_bridge` 레벨과 `r_out`을 명시해야 전압이 맞는다(측정에서 도출: 명시 브리지 0–5 V, 자동 브리지 0–3.3 V).

### 7.3 보완 항목
**D: 범용성(입구 열기)**

| # | 항목 | 왜 | 제안(가장 작은 변경) | 측정 가능한 PASS 조건 |
|---|---|---|---|---|
| D1 | `--design FILE.json` 입력 경로 | 입구가 템플릿뿐; 거부문이 권하는 "직접 쓰기"가 CLI에 없음(`base.py:604`, `cli.py:1268-1330`) | `components/nets/topology/simulation` 블록을 기존 pydantic 모델로 검증해 `CircuitDesignAgent` 제안으로 넣고, 빈 IR일 때만·기존 `confirm_design` 표/해시 게이트(`circuit.py:156-182`) 그대로 통과; 부품 provenance는 `user_requirement`(파일 해시) | `tests/fixtures_rc.py` RC를 `--design`으로 넣어 1차 `[confirm_design]` 표, 2차 `spice.*` PASS가 템플릿 RC와 같은 값; 모든 부품에 provenance; 비어 있지 않은 IR이면 새 문자열 `ignored: --design needs an empty IR`(A6의 4개 문자열과 별개) |
| D2 | 설계가 자기 입력 키·단위를 선언 | `_NEEDABLE_KEYS`/`UNIT_OF` 고정(`base.py:116`, `inputs.py:96-105`) | D1 파일에 `inputs: {key: {unit, range}}` 허용, 그 키만 세션 `UNIT_OF`에 합침; 맨 키 거부 유지 | 선언 키가 `user_requirement`로 들어가고, 선언 없는 키는 현재와 같은 거부문 |
| D3 | 비템플릿 설계의 하류 상태 명시 | `checks.py:10-28`는 `None`, 스택업은 `add_board`만, 보고서 `NO_TEMPLATE` | 검사는 템플릿 객체 대신 IR provenance로; 스택업은 D1 파일 `pcb.stackup` 또는 기본값+메시지; 보고서 라벨 "사용자 제공 설계(해시)" | `design.inputs_vs_requirements`가 PASS/NOT_VERIFIED 중 하나로 존재, DRC가 스택업 부재로 FAIL 않음, 보고서에 `NO_TEMPLATE` 없음 |
| D4 | `serves_requirements` 필수화 | 비면 리뷰어 FAIL(`reviewer.py:400`) | D1 검증에서 요구 id 없는 부품은 한 줄 메시지 + exit 2(A5 매핑) | 누락 파일은 `run` 전 거부, 채운 파일은 `review.*`에 trace FAIL 없음 |
| D5 | LLM `CIRCUIT_DESIGN` 제안 | 라벨뿐(`llm/router.py:86`), 프롬프트 없음 | LLM이 D1 파일 형식을 내놓게 해 D1 경로로(`llm_generated` → 표 확인 필수); 이 PC는 LLM 키 없음(§1.2) → 키 생긴 뒤 | `--llm` 없이는 메시지 불변 |
| D6 | 아날로그 IC 벤더 모델(op-amp·레귤레이터·비교기)의 입구 (Codex 회의 #2 MISSING 4) | "모든 회로"는 펌웨어보다 먼저 IC 모델에서 막힌다. IR은 이미 `SpiceBinding.model_card`(verbatim `.model`/`.subckt`, authoritative/user provenance 필수, `ir/simulation.py:100-104`)를 지원하지만 벤더 `.lib`를 가져오는 절차·검사가 없다 | 새 필드 없음: D1 파일의 부품에 `model_card` + 출처(URL/파일 해시)를 허용하고, D1 검증이 그 텍스트를 `validate_deck` 규칙(따옴표·금지 카드·`.include` 없음)으로 미리 검사; 출처 없는 카드는 `assumption`으로 강등 → 그 부품의 결과 NOT_VERIFIED | 벤더 op-amp subckt 하나를 D1 파일로 넣어 `spice.*` PASS에 `model_card` 해시·출처가 찍힘; 출처를 빼면 같은 실행이 NOT_VERIFIED |
| D7 | KiCad 회로도/넷리스트 → D1 파일 변환 (Codex 회의 #2 MISSING 5) | 아무도 임의 회로의 IR을 손으로 쓰지 않는다; 변환기가 없으면 D1은 실사용자가 거의 없다 | **사용자 결정 사항**: 이 시스템은 IR이 원본이고 KiCad 파일은 파생물인데, 변환기는 흐름을 거꾸로 돌린다. 만든다면 "읽기 전용 입력, provenance `user_requirement`+파일 해시, 한 번 들어온 뒤로는 IR만 원본"으로 한정. D1 형식 확정 뒤 결정 | (결정 뒤) 템플릿이 만든 `.kicad_sch`를 변환해 D1으로 넣으면 원래 IR과 부품·넷이 동일 |

**E: 프로그래머블 소자**(단계·도구는 7.2 표)

| # | 항목 | 왜 | 제안(가장 작은 변경) | 측정 가능한 PASS 조건 |
|---|---|---|---|---|
| E1 | MCU 핀 스펙 자극(L0) | ATmega 보드는 LED·리셋·AVCC만 측정(`atmega128.py:575-605`); PWM 출력 회로 검증 불가 | 템플릿/D1 파일에서 "U1 핀 X = PULSE(요구 키 `pwm_frequency`,`pwm_duty`)" 선언; 두 키는 고정 `UNIT_OF`에 추가(D2 불필요); U1은 exclude 유지, `exclude_reason`은 `stimulus from spec, not firmware`; `Stimulus` provenance를 보고서에 인쇄 | 기대값 `nominal`이 요구(예: LED 평균 전류 스펙)에서 유도돼 `RMS` PASS — 자극 파라미터에서 유도하면 거부; `exclude_reason` 위 문자열; 보고서가 "펌웨어"를 쓰지 않음 |
| E2 | 추적 파일 자극(`Stimulus.trace`, L1a) | PWL은 인라인 점만(`compilers/spice.py:400-422`); 이 PC에 VCD 생산자(simavr `-o`)가 이미 있음 | `ArtifactKind.EXTERNAL_MODEL`(`tool`/`version`/`sha256`; 여기선 VCD) + VCD→PWL 변환기; `tool`/`version` 비면 `assumption` provenance → NOT_VERIFIED(`tools/spice/stage.py:761-763`) | VCD 픽스처가 PWL 점으로 변환돼 에지 시각 일치; `spice.*` details에 trace sha256·생산 도구 버전이 찍히고, 해시가 다른 추적은 결과가 달라짐; 버전 없는 추적은 NOT_VERIFIED. 첫 실측 중 "ELF → simavr → VCD"는 7.1에서 완료; 남은 것은 VCD→PWL 변환과 `spice.*` details의 provenance |
| E3 | XSPICE 거동 핀 모델(L1b) | `SpiceDevice`에 `A` 없음(`ir/simulation.py:32-41`); `.model d_*` 카드는 이미 통과; 래퍼로 실행 동작 측정됨 | `SpiceDevice.A` + 검증기 `domain.digital.behavioural`(모델 provenance `authoritative`/`user`; `dac_bridge`/`adc_bridge` 레벨과 `r_out`을 SI 드라이버 사실에서 명시); `_uses_code_models`(`tools/spice/stage.py:554-561`) 스탬프 재사용 | `d_inverter` 하나를 IR로 컴파일·실행해 `VALUE` PASS가 선언 레벨(5 V 또는 3.3 V)에서; 레벨 미선언이면 NOT_VERIFIED |
| E4 | doctor에 추적 생산자 점검(E2가 쓰는 것만) | E2 결과의 provenance에 도구 버전이 필요; 측정 없이 "바람"이 되는 것을 막음 | (Codex 회의 #2로 축소) `doctor`에 `trace: simavr <ver/NOT FOUND>, avr-gcc <ver/NOT FOUND>` 줄(PlatformIO 패키지 경로도 탐색). verilator/standalone ngspice 탐지와 `COSIM_MEASURED_VERSIONS` 대조는 **E5/E6이 열릴 때** 추가 | 이 PC 현재값: simavr 1.8, avr-gcc 7.3.0; E2는 doctor가 찍은 버전과 trace의 `tool`/`version`이 맞을 때만 PASS |
| E5 | AVR 펌웨어 코시뮬(`d_process` + simavr, L2) | 유일한 오픈소스 AVR 경로 | **보류 — E4 측정 뒤 설계.** 전제: libsimavr를 `d_process` 프로토콜로 감싸는 C 프로그램(C 컴파일러 설치 = 사용자 승인) + `validate_deck` 따옴표 규칙에 문자열 파라미터 예외 설계(따옴표 없는 카드는 엔진을 죽임, 측정) + 공유 DLL 대신 standalone 서브프로세스 여부 결정 | 설계 시 포함할 것: 주기가 다른 2차 HEX가 FAIL/다른 값(음성 대조), 버전은 E4 대조 |
| E6 | FPGA RTL 코시뮬(`d_cosim` + Verilator, L2) | HDL 코시뮬은 ngspice 공식 경로; 모델은 이 PC에서 DLL 로드까지 동작(7.1) | **보류 — E4 측정 뒤 설계.** 전제: standalone ngspice-47(46은 bug 843) + Verilator 툴체인(사용자 승인) + E5와 같은 따옴표 예외; STM32는 대상 아님(L1로 끝) | 설계 시 포함할 것: ngspice 555 예제 `FREQUENCY` PASS + DLL 해시·버전 provenance |

"소자를 provenance 있는 부품으로"는 IR이 이미 지원한다(`Component.spice: SpiceBinding | None`, `exclude`+사유, `ir/components.py:19-90`) — E3/E5/E6은 새 바인딩 종류이지 새 부품 개념이 아니다. 참고 레포 재작성은 없지만 변경 목록은 정직하게: `--design` CLI 경로·pydantic 검증(D1), `UNIT_OF` 키 2개(E1)·선언 키 합치기(D2), `checks.py`/`add_board`/보고서 라벨(D3), exit-2 검증(D4), `ArtifactKind` 1개, `SpiceDevice` 1개, `Stimulus` 필드 1개, 검증기 id 1개, doctor 줄 + 버전 대조. E5/E6이 열리면 standalone 러너(같은 `SpiceResult` 계약)가 추가될 수 있으며 그것이 가장 큰 항목이다.

### 7.4 순서와 위험
§4의 1-7(plan 확인 → A5/A6 → B4·B2/B9/B10 → B1 기록+A7 → 회의 #3 → SKILL.md 초안 → 푸시) 뒤에 붙인다. 스킬 초안은 §7 없이도 진실되게 쓸 수 있다(7.5 첫 줄만 먼저 반영).
8. **D1 → D4 → D3 → D6.** D2는 첫 비템플릿 회로가 실제로 새 키를 필요로 할 때. D5는 LLM 키가 생긴 뒤. D7은 D1 형식 확정 뒤 사용자 결정.
9. **E1 → E3**(둘 다 오늘 도구로 PASS 가능: `A` 소자 실행 측정됨) **→ E2(+E4)**(Codex 회의 #2: simavr가 이미 있으므로 E2의 첫 실측은 외부 설치 없이 가능하고, E4는 E2가 필요로 하는 탐지만. E2의 PASS가 doctor 버전 대조를 전제하므로 E4의 doctor 줄은 E2의 일부로 같이 만든다). D 순서 D1→D4→D3는 D4(파일 검증 exit 2)가 D3의 상태값에 의존하지 않으므로 유지.
10. **이 PC에서 남은 측정**(E5/E6의 진입 조건): (a) ~~simavr VCD 생산~~ 완료(7.1); (b) `d_process` 한 줄 덱 실행(래퍼 프로그램이 있어야 하므로 E5 설계와 함께); (c) standalone ngspice-47 — 현재 NOT FOUND(7.1), 설치할지는 사용자 결정(§4 1단계 ⑨); (d) C 컴파일러·Verilator — 현재 NOT FOUND(7.1), 설치할지는 사용자 결정. **(c)(d)는 외부 설치라 사용자 승인 사항**(§3.3 `system_install`). 완료된 측정(7.1)은 반복하지 않는다.
11. **측정 결과에 따라 E5 / E6.** 없다고 나온 도구에 의존하는 항목은 "보류(이유: 측정 결과)"로 바꾸고 지우지 않는다.

| 위험 | 내용 | 규칙 |
|---|---|---|
| 충실도 착시 | "PASS = 펌웨어 동작"으로 읽힘. L0는 펌웨어 없음, L1은 다른 시간축(Renode는 사이클 비정확), L2도 이벤트 수준 | 새 메시지 문법 없음: E1의 `exclude_reason` 문자열과 `Stimulus`/trace provenance(도구·버전·해시)를 보고서가 그대로 인쇄; 둘 다 없는 MCU 핀 결과는 NOT_VERIFIED |
| 엔진 사망 | 잘못된 코시뮬 카드(따옴표 없는 문자열 파라미터)가 프로세스의 공유 DLL을 죽임(측정) | 컴파일러가 `d_process`/`d_cosim` 카드를 만들 때 문자열 파라미터는 따옴표 포함으로만 생성하고, 래퍼의 금지 규칙은 그 카드에 한해 예외; 예외 설계 전에는 공유 DLL 경로에 두 카드를 넣지 않는다 |
| 범위 팽창 | "모든 회로"가 디지털 버스·멀티시트·STM32 코시뮬까지 번짐 | 각 항목은 PASS 조건 하나로 끝; 요청되지 않은 기능은 "미검증/건너뜀"에 적고 만들지 않는다 |
| 라이선스 | simavr GPL-3, Verilator/Icarus GPL | 래퍼는 별도 프로세스·별도 디렉터리로 두되, 경계가 충분한지와 배포 판단은 사용자 |
| 시간축 결합(Codex 지적, 설계는 나중) | L2의 이벤트 구동 디지털 스텝과 SPICE `tran` 타임스텝의 결합(`d_process`/`d_cosim`의 이벤트 시각 ↔ `tran 10u`)이 미설계 | E5/E6 설계 시 첫 항목으로; 그 전에는 L2 결과를 말하지 않는다 |

E1–E3는 `d_process`/`d_cosim` 카드를 전혀 만들지 않으므로(측정된 `A`+브리지 카드만) 엔진 사망 위험은 E5/E6부터다(Codex 회의 #2 지적 6에 대한 답).

### 7.5 스킬에 미치는 영향
- 지금(스킬 초안)은 현재 사실 한 줄만: SKILL.md "하드 리밋"에 "MCU/FPGA/IC는 SPICE 모델이 없으면 `exclude`이며, 그 부품을 지나는 요구는 NOT_VERIFIED다. 펌웨어는 실행되지 않는다. 템플릿 외 회로는 `no template matches…` 거부가 정상이다."
- 그 외의 스킬 문서 갱신은 해당 항목이 PASS 조건을 통과한 뒤에만(구현 전 문서화 없음; Codex 회의 #2로 목록 삭제). "동작한다"는 동사는 tool-backed PASS가 있는 넷·기대값에만 쓴다.
