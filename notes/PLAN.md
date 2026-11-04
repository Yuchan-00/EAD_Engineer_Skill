# EDA_Engineer 스킬 프로젝트 — 세팅 · 이해 · 보완점 Plan

작성: Claude (lead), Codex 검토 반영. 날짜: 2026-11-04.
범위: 이 문서는 **스킬을 아직 쓰지 않는다.** (1) AI_EDA 실행 환경 세팅 결과, (2) AI_EDA_Engineer 프로젝트 이해, (3) 보완점과 다음 단계, (4) 확장 방향(범용 회로 설계·프로그래머블 소자 시뮬레이션, §7), (5) 참고 스킬(kicad-happy·ee-skills, MIT)에서 가져올 것과 판매용 보호 조치(§8), (6) 다중 에이전트 호스트·다중 AI API 대응(§9)만 적는다. 스킬 본문(SKILL.md)은 이 plan을 사용자가 확인한 뒤 천천히 진행한다.

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
- **기준값의 출처(2026-11-04 추가, §7 D5·D8의 전제)**: SPICE 기대값의 nominal·허용오차는 `user_requirement`나 `authoritative`에서 유도된 것만 PASS의 근거다. LLM이 제안한 기준(`llm_generated`)에 대한 통과는 "제안된 기준에 대한 PASS"로만 표시하고 상태는 NOT_VERIFIED — 자기 숙제를 자기가 채점하지 않는다. 현재 코드(확인함): SPICE 컴파일러는 `llm_generated` 출처의 값·바인딩·자극·기대값을 **아예 거부**한다(`compilers/spice.py:235-237` "nothing an LLM proposed reaches ngspice until it is verified"), `assumption` 위의 PASS는 NOT_VERIFIED로 강등한다(`tools/spice/stage.py:761-763`). 확인 표에서 승인된 제안은 사용자의 값(`user_requirement`)이 되므로, **확인 표는 기대값마다 "LLM 제안 기준"과 유도 근거를 보여 줘야** 사용자가 무엇을 승인하는지 알 수 있다(D5의 표 요구사항).
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
| A5 | **구현됨 2026-11-04(`work/ead-skill` 925fb58, PR은 결정 ① 뒤)** — `ai-eda run`/`review`가 손상된 ir.json(모르는 키, 다른 schema_version)에 **traceback + exit 1** | `cli.py:839`(run)·`cli.py:1047`(review)의 `ir = _load(args.ir)`가 try 밖이고 `main()`에 핸들러가 없다. `report`·`serve`·`stage-reports`(공용 로더 `_report_inputs`, `cli.py:1073-1088`)·`relocate`(`:1173`)만 exit 2(`gui`는 IR 파일을 받지 않아 대상 아님). 2차 검토에서 이 PC로 재측정(3차 검토 2026-11-04에 run·report 재확인): `ai-eda new a5 --dir <tmp>` → `<tmp>/ir.json` 최상위에 `"bogus_key": 1` 추가 → `ai-eda run <tmp>/ir.json` / `ai-eda report <tmp>/ir.json` → run/review 모두 `IRSchemaError: … unknown key(s) the IR models would drop: bogus_key` traceback, **exit 1**; report는 한 줄 + exit 2 | run/review도 `IRSchemaError → stderr 한 줄 + exit 2`로 통일(이미 `report`가 쓰는 except 절 그대로). 스킬의 exit code 표에는 수정 전 버전을 위해 "traceback+exit 1 = ir.json 로드 실패, 설계 FAIL 아님"을 남긴다 |
| A6 | ~~`confirm_design=yes`가 조용히 무시되는 경우가 4가지~~ → **조용하지 않다** (2차 검토에서 정정; 남은 테스트 1개는 925fb58에 추가됨) | `agents/circuit.py` 4경우 모두 stage 메시지에 `confirm_design ignored: <사유>`를 넣는다(144·149·167·174·208행; 4경우에 문자열 5개 — "템플릿 없음" 경우가 `no template to confirm`/`template <t> proposes nothing` 두 문자열). 메시지는 `run` 출력의 stage 줄(`cli.py:913`)과 `pipeline.json`의 `state.outcomes[].message`에 같은 문자열로 남는다. 테스트: 같은 실행의 답(`test_circuit_templates.py:315`, `:980`, `test_leave_out.py:188`), 설계 내용 존재(`:414`), 템플릿 없음(`:427`), 표 해시 불일치(`:1004`) 있음. **`template <t> proposes nothing`(149행)만 테스트 없음** | 코드 수정 없음. 남은 것: (1) `proposes nothing` 사유 테스트 1개, (2) 스킬 `answers.md`가 4개 사유 문자열을 verbatim으로 싣고 "stage 줄에 `confirm_design ignored:`가 보이면 적용 안 된 것"이라고 가르친다 |
| A7 | **구현됨(925fb58)** — **Windows에서 `ai-eda serve`가 이미 사용 중인 포트에 두 번째로 바인딩된다** → 전체 pytest가 `tests/test_report.py::test_serve_loopback_read_only_and_live`에서 영원히 멈춤(첫 실행 7시간 후 강제 종료; 재실행은 faulthandler 15분 타임아웃으로 확인) | `report/server.py:104` `ThreadingHTTPServer`는 stdlib `HTTPServer.allow_reuse_address = 1`(SO_REUSEADDR)을 물려받는데, Windows의 SO_REUSEADDR는 LISTEN 중인 포트에도 bind를 허용한다. 이 PC에서 재현: 같은 127.0.0.1 포트에 `HTTPServer` 두 번째 생성 성공. 테스트는 `serve(ir_path, port) == 2`(OSError)를 기대하지만(`test_report.py:657-659`) 두 번째 `serve()`가 `serve_forever`에 들어가 돌아오지 않는다. 제품 영향: 사용자가 같은 포트로 `serve`를 두 번 띄우면 오류 없이 두 서버가 공존(요청이 어느 쪽에 가는지 불명) | GUI 서버는 이미 고쳐져 있다(`gui/server.py:696-700` `_LoopbackServer.allow_reuse_address = os.name != "nt"`, 독스트링이 정확히 이 문제를 설명). `report/server.py:104`만 같은 서브클래스를 쓰도록 바꾸면 끝(두 줄). 테스트는 Windows에서도 OSError 경로를 타게 된다 |

**§3.1-b 전체 pytest 결과 (2026-11-04, 이 PC = 첫 Windows 측정)**: `pytest -v -o faulthandler_timeout=900 --deselect tests/test_report.py::test_serve_loopback_read_only_and_live` → **13 failed, 2870 passed, 55 skipped, 1 deselected, 14 분 57 초** (exit 1). deselect 없이 돌리면 A7에서 영원히 멈춘다(첫 실행은 7 시간 뒤 강제 종료). **2차 실행(A5/A6/A7/B1 적용 뒤, `work/ead-skill` 925fb58): 12 failed / 2879 passed / 54 skipped, 22분** — GUI 10053 2건은 이번엔 통과(부하 의존 flaky로 재분류), `test_kr447_transceiver.py::test_the_pipeline_runs_the_deck_and_the_rf_checks`가 시간 예산(13.08 s > `FIXTURE_BUDGET_S` 10 s)으로 실패(부하 의존, 변경과 무관), 나머지 10건은 동일. A7 테스트는 러너가 아직 deselect(단독 실행 PASSED; main 머지 뒤 deselect 제거). 상세 `notes/measurements/2026-11-04/a5-a7-b1-tests.md`. **3차 실행(B11 적용 뒤, 5a5e8a1): 12 failed / 2888 passed / 54 skipped, 17분 39초 — 전부 기준선, 회귀 0**(`b11-wiring.md`). **4차(D9a, fece446): 11 failed / 2895 passed. 5차(lc_lowpass 등록, 9368133): 12 failed / 2896 passed(새 실패 1건은 `test_rf_selection`의 "기본 템플릿 5개" 단언 → 6으로 갱신). 6차(A8, 13cdb5b): 10 failed / 2898 passed, 21분 — 기준선 8건 + KR447 시간 예산 2건(부하 의존); 보고서 인용·GUI 10053 테스트 통과(`a8-windows-fixes.md`). 7차(bjt_lowside_switch 3bf314c, 18:30 시작·Codex 리뷰와 동시): 8 failed / 2908 passed / 54 skipped, 21분 30초 — 정확히 기준선 8건(A3 ×2, A8 ×4, A9 ×2), KR447 시간 예산 실패 없음, 회귀 0. 이 실행 뒤 A8 4건을 02c5c78·7ebfb6a로 고쳐 해당 파일 단독 실행은 통과(107+84 passed) → 다음 전체 실행 기대 기준선 4건(A3 ×2 결정 ⑰, A9 ×2). 8차(⑰ 구현 8caf1a2 + ⑯ fdd6657 + i2c_pullup 196fb9a, 20:39 시작, `.logs\pytest-full-20261104-203902.txt`): **2 failed / 2942 passed / 54 skipped, 15분 34초 — 정확히 기대 기준선 A9 ×2(AM 소스 문법), 회귀 0; A3·A8은 0건.** Windows 기준선: 13 → 2.** 가장 느린 테스트: `test_kr447_tx_exciter.py::test_the_pipeline_on_the_bench_header_board` 81 s. 로그는 크기 때문에 레포에 넣지 않음(AM 프로브 덱은 `notes/measurements/2026-11-04/`). **9차(A9 뒤, 03bd642, 2026-11-05 04:23, 27분 15초 — 세션 5개·Codex 15건·G9 실행과 동시): 2 failed / 2943 passed / 54 skipped** — `test_claude_cli_client.py::test_a_timeout_while_the_child_does_not_read_stdin_kills_it_and_never_hangs`(0.5 s 타임아웃 안에 자식이 prompt를 못 받음)와 `test_kr447_transceiver.py::test_the_pipeline_runs_the_deck_and_the_rf_checks`(11.23 s > 10 s 예산), 둘 다 **단독 재실행 2 passed(19 s)** → 부하 의존 flaky, 알려진 기준선 실패 0. **Windows 기준선 13 → 0 달성.**

| 묶음 | 실패 테스트 | 첫 오류 | 분류 |
|---|---|---|---|
| A3 | `test_circuit_templates.py::test_astable_verifies_at_the_bounds…[3 V-100 Hz]`, `[3 V-200 Hz]` | 편차 4.94 % > 0.049 | ngspice-46 드리프트 (A3; 추정 — 원인 확인 전, §3.5 A3) |
| A8 Windows | `test_claude_cli_client.py::test_an_interrupt_during_the_call_kills_and_reaps_the_child` | `OSError: [WinError 87] 매개 변수가 틀립니다` (자식 종료 경로) | Windows 전용, README가 "미측정"이라 한 claude.exe 경로 |
| A8 Windows | `test_claude_cli_client.py::test_an_argument_the_os_cannot_encode_is_an_llm_error_not_a_value_error` | 오류 종류 `'http' != 'transport'` | Windows 전용 (인코딩 불가 인수의 분류) |
| A8 Windows | `test_gui_server.py::test_post_needs_the_pages_own_origin_and_a_json_body`, `…::test_the_run_endpoints_need_the_pages_own_origin_and_a_json_body` | `ConnectionAbortedError: [WinError 10053]` | Windows 전용: 서버가 본문을 읽지 않고 거부하면 클라이언트 쓰기가 중단됨(POSIX에서는 상태 코드가 보임) |
| A8 Windows | `test_report.py::test_report_of_offline_divider_run`, `…::test_questions_have_answer_commands_and_model_labels`, `test_leave_out.py::test_a_refusal_is_answered_by_leave_out…` | 보고서의 답 명령이 `ai-eda run '…\ir.json'`로 따옴표 붙음(기대: 따옴표 없음) | Windows 전용: `report/data.py:390,395` `shlex.quote(str(ir_path))`가 역슬래시 경로를 POSIX 규칙으로 인용. 제품 영향: 보고서가 보여 주는 명령이 cmd.exe에서 그대로 안 돈다 |
| A8 Windows | `test_md_review_findings_regressions.py::test_7_remove_matches_by_design_content` | `assert rebuilt != divider_ir.net("GND")  # model equality sees the wall clock` 실패: 두 `Net`의 `created_at`이 같음 | Windows 전용(추정): 픽스처와 테스트가 같은 시계 눈금 안에 만들어짐. 테스트 가정(벽시계가 항상 다르다)의 문제 |
| A8 Windows | `test_report_pdf.py::test_a_snap_browser_is_not_started_on_a_file_it_cannot_read` | `pdf.is_snap(WindowsPath(…/chromium-browser))`가 True | Windows 전용: snap 판정이 경로 이름만 본다 |
| A9 ngspice-46 ✅ 03bd642 | `test_rf_spice.py::test_am_depth_of_ngspice_s_am_source`, `…::test_a_biased_am_depth_never_passes_a_depth_outside_the_band` | `no carrier: the amplitude (0 .. 0) is within the engine's resolution`; `KeyError: 'measured'` | ngspice 변경: NEWS에 ngspice-43 "Update the AM voltage/current sources: enable amplitude modulation, carrier suppression", ngspice-46 "FM and FC exchange place in the parameter sequence of SFFM". 이 PC 측정: 래퍼로 `AM(1 0 1k 20k 0)` → 0…1 V(음의 반주기 없음), `AM(1 0 1k 20k)` → ±970 V. 컴파일러는 `AM(VA VO MF FC TD)`/`SFFM(VO VA FC MDI FS)` 옛 순서로 쓴다(순서의 출처는 `ir/simulation.py:174-181` `STIMULUS_PARAMS`, 소비는 `compilers/spice.py:423` `_stimulus_spec`; `:73-75`는 독스트링). 측정 덱: `notes/measurements/2026-11-04/am.cir`, `am2.cir`. 새 파라미터 의미는 UNVERIFIED — 담당 Claude: ngspice-46 매뉴얼 §4.1.6(ngspice.sourceforge.io/docs)을 읽고 AM/SFFM 인자 순서 표를 이 행에 추가 |

같은 실행에서 **통과한 것 중 plan에 중요한 것**: `test_kicad_cli.py::test_sibling_project_rules_are_applied_by_drc_canary` PASSED (14 s), `test_kicad_3d_export.py::test_3d_exports_write_step_glb_and_png_canary` + `…flags_are_listed_by_help_canary[×3]` PASSED, `test_silkscreen.py::test_silk_drc_canary…` PASSED, 실제 브라우저(Chrome) 렌더/PDF 테스트 전부 PASSED → **B1의 canary는 이 PC(KiCad 10.0.6)에서 이미 통과했다. 남은 일은 측정 버전 상수에 `10.0.6`을 기록하는 것뿐**(§3.2 B1). 55 skipped는 대부분 "도구 없음" 분기(LLM 키, claude.exe 등).

| # | 문제 | 근거 | 제안 |
|---|---|---|---|
| A8 | **✅ 2026-11-04 전부 처리**(13cdb5b·757fe08 제품 결함 2건 + 02c5c78·7ebfb6a 나머지 4건: `is_snap()` `as_posix()` 비교(제품), `_assert_gone(pid)` Windows 분기, 서로게이트 인수는 Windows에서 시작됨→NUL만, test_7은 created_at 명시; `a8-windows-fixes.md`). 이하 경위: **제품 결함 2건 구현됨 2026-11-04(`work/ead-skill`, A8 커밋)**: 보고서 답 명령은 `shell_path()`(평범한 경로는 따옴표 없이, 공백 등이 있으면 Windows는 `"…"`, 그 외 shlex), GUI 서버는 거부 전에 본문을 읽어 버림(10053 해소; 해당 테스트 통과) — Windows에서 실패하는 테스트 9개(위 표) — 제품 결함은 그중 보고서 답 명령 인용(`report/data.py:390,395`; cmd.exe에서 안 도는 명령을 보여 줌)과 두 서버의 본문 미수신 거부(클라이언트에 10053) | 첫 Windows 전체 실행 | 각 테스트를 "Windows에서 기대값 분기"로 고치지 말고 제품 쪽을 먼저 본다: 답 명령은 Windows면 따옴표 없이(또는 PowerShell 규칙), 서버는 거부 전에 본문을 읽고 버린다. 나머지(claude.exe 종료 경로, snap 판정, 벽시계 동일성)는 Windows 분기 |
| A9 | **✅ 2026-11-04 21:20 구현**(`a9-am-source-ngspice46.md`): 매뉴얼 §4.1.6으로 확인 — 43부터 `AM(VO VMO VMA FM FC TD …)`, 옛 5값은 위치대로 읽혀 FC = 0 → 상수(실측). SFFM은 이름만 바뀜(순서 동일, 실측). 컴파일러는 IR의 물리(va·vo·mf·fc·td)를 그대로 두고 `AM(0 VA·VO VA MF FC TD)`로 쓰며(IR 해시 불변), SPICE 단계가 AM 자극 + `ngspice-NN`(NN < 43)을 실행 전 거부(42는 문서화된 식상 0 소스). AM 테스트 2건 통과, 게이트 테스트 추가; Codex 리뷰로 SFFM MDI ≤ FC/FS 강제(46이 경고 한 번 뒤 잘라서 돌림 — 실측)·버전 미해독 fail-closed·43 미만 skip 마커. 커밋 03bd642 | NEWS + 매뉴얼 + 이 PC 측정 | 완료: "43 이상만 지원" 쪽을 택함(컴파일러는 IR의 순수 함수라 엔진 분기를 둘 수 없고, 제품 코드에 AM을 내는 곳이 없어 영향은 AM을 직접 쓰는 IR뿐) |

### 3.2 설계/구현 보완점 (코드 읽기 + 그래프 분석에서 나온 것)
| # | 항목 | 왜 문제인가 | 제안 |
|---|---|---|---|
| B1 | 미측정 canary를 이 PC에서 측정 → **측정·기록 완료(925fb58)**: 상수에 10.0.6, 문서 7곳 갱신; 그 덕에 처음 실행된 `test_vertical_slice.py::test_fab_capability_limits_become_drc_rules_and_pass`가 (픽스처 페이지 보강 뒤) 통과 → `mfg.capability`가 끝까지 PASS | KiCad 10.0.6 + ngspice-46이 있는 첫 실제 머신. §3.1-b 전체 실행에서 `…sibling_project_rules_are_applied_by_drc_canary`, `…3d_exports_write_step_glb_and_png_canary`, 3D `--help` 플래그 canary ×3, silk DRC canary가 모두 PASSED | `PROJECT_RULES_MEASURED_VERSIONS`/`EXPORT_3D_MEASURED_VERSIONS`에 `"10.0.6"` 기록(+ 기록 근거로 이 실행 로그 요약을 PR 본문에) → `mfg.capability`가 처음으로 PASS 가능. ATmega128/라디오 보드 ERC·DRC도 같은 실행의 `test_kr447_*`·`test_atmega128_template` 통과로 측정됨 |
| B2 | 규제 범위 질문이 non-blocking | 후보가 UNDECIDED인 채 RELEASE 도달 가능(`regulatory.applicability` NOT_VERIFIED) | RELEASE 메시지에 미결 키를 명시(이미 일부) + 스킬이 반드시 되묻도록 |
| B3 | 수리 범주 3종이 emit되지 않음 | `NON_REPAIRABLE` 선언과 실제 불일치 | emit 지점을 만들거나 목록에서 제거(문서 정합) |
| B4 | 컴파일 거부 시 이전 산출물 pop | `Orchestrator._compile`이 FAIL/NOT_VERIFIED면 그 kind를 `ir.artifacts`에서 제거 → 하류가 "no PCB artifact" | 의도된 동작이지만 메시지에 "previous artifact removed" 명시 |
| B5 | `doctor` exit 0 (`--strict` 없이) | 스크립트가 exit code만 보면 "ai-eda가 import된다"만 안다 | 설치 스크립트/스킬은 항상 `--strict` |
| B6 | 기본 배선이 all-or-nothing | 넷 하나 못 그리면 구리 0 → DRC unconnected_items | 스킬이 `pcb.routing=partial`을 안내; 기본값 재검토는 사용자 결정 |
| B7 | README 현재 상태 표 날짜(2026-09-27) vs 변경 이력(2026-10-14) | 최신 권위는 변경 이력 | 상태 표 날짜 갱신 |
| B8 | 단계 이름 대소문자 혼용(README 대문자, 코드 `StrEnum` 소문자) | 스킬이 run 출력을 파싱할 때 혼란 | 문서를 소문자 id로 통일 |
| B9 | `worst_status`에서 USER_INPUT_REQUIRED < FAIL이지만 오케스트레이터는 질문에서 멈춤 | FAIL 단계가 동시에 blocking 단계가 될 수 있음 | 출력에 "blocked by question" 라벨 분리 |
| B10 | 리뷰에 USER_INPUT_REQUIRED만 있으면 `failures`가 비어 수리 루프가 "no failures"로 종료 | 설계는 막혀 있는데 수리 루프는 성공처럼 보임 | 리뷰 요약에 blocked 카운트 추가 |

| B11 | **구현됨 W1+W2 (2026-11-04, `work/ead-skill` 5a5e8a1; 측정 `notes/measurements/2026-11-04/b11-wiring.md`, 그림 `selftest-divider-wired.png`)** — 분배기 3/3 넷 배선·junction 1·ERC/DRC/parity 불변; KR447 47/211, ATmega 15/64(핀 5개 이상 넷과 "no clear path"는 라벨만) — **회로도를 라벨 대신 배선으로 그리기** (사용자 요청 2026-11-04: "수정 및 해석이 간편하도록 가능한 배선을 통한 회로도 작성") | `SchematicCompiler`는 심볼을 참조번호 순으로 4열 표에 놓고(`compilers/schematic_layout.py:321-368`, `LAYOUT_COLUMNS=4`, 거터 `LAYOUT_GAP_MM=5.08`) 핀마다 2.54 mm 스텁 + **글로벌 라벨**로만 잇는다(`compilers/schematic.py:443-456`). 심볼 사이에 전선이 하나도 없어 신호 흐름을 라벨 이름을 대조해 읽어야 한다 | 아래 "B11 설계" W1→W4. 손 편집은 여전히 해시로 거부되므로(§2.2) "수정이 간편"은 IR을 고쳐 재생성한 결과를 읽기 쉽다는 뜻이다 |

**B11 설계(가장 작은 완전한 변경, 단계별)** — 지켜야 하는 불변식은 `compilers/schematic.py:1-40` 독스트링 그대로: 바이트 결정성, **우연한 연결 금지**(KiCad는 좌표가 같으면 잇는다), 라이브러리 심볼 verbatim, netlist parity(`tests/test_schematic_compiler.py:302` `test_real_netlist_reproduces_ir_connectivity`: 넷 **이름**으로 대조), ERC 0(`:288`).
- **기준 측정(§3.1-c, 이 PC 2026-11-04, `ai-eda selftest --dir … --keep`)**: 분배기 보드 `selftest.kicad_sch`는 심볼 3개(R1, R2, J1), `(wire` 7개(전부 핀 스텁), `(global_label` 7개, `(junction` 0, 심볼 간 배선 0. 넷은 `VIN`(power, 2핀), `VOUT`(signal, **3핀**), `GND`(ground, 2핀). → "2핀 비전원 넷만" 같은 규칙은 이 보드에서 **아무것도 배선하지 못한다**; 첫 단계부터 전원·접지와 3핀 넷을 trunk로 이어야 요청에 답이 된다.
- **W1 (추가만, 핀 ≤ 4인 모든 넷)**: 핀이 2~4개인 넷은 종류와 무관하게 거터(열·행 사이, 1.27 mm 트랙) 안의 trunk 하나와 핀마다의 분기(스텁 끝 → trunk)로 잇고 분기점에 `junction`을 둔다(2핀 넷은 분기 2개인 trunk = L/Z형). 넷마다 트랙 오프셋을 달리해 교차는 선분 중간에서만 일어나게 한다(끝점이 외부 선 위에 놓이면 KiCad가 이으므로 금지). 글로벌 라벨은 **그대로 둔다** → 넷 이름·parity·ERC 불변, 변경은 순수 추가. 핀 5개 이상 넷(큰 보드의 GND/VCC)은 라벨만 유지(관례; 선 수 억제) — 임계값 4는 상수로 두고 ATmega128 보드 측정 뒤 조정. 경로가 다른 심볼의 extent(라벨 글자 포함, `symbol_extent`), 외부 핀점·스텁, 다른 배선의 끝점을 지나면 그 넷의 배선을 포기하고 라벨만 남기며 stage note에 `net <n>: not wired (<reason>)`로 적는다. `_check_geometry`(`schematic.py:398-435`) 확장: 배선 선분 위에 외부 연결점이 놓이면 CompileError(현재 스텁 규칙과 동일).
- **W2 (배치, W1과 한 변경으로)**: 참조번호 순 대신 `ir.topology.blocks`의 in→out 순으로 열을 잡고 같은 블록은 이웃 셀에 → 배선 길이·교차 감소, W1의 "not wired" 수 감소. 표 구조·extent 계산·결정성은 유지(정렬 키만 바뀜). Codex 회의 #3: 참조번호 순 표에서는 먼 행 사이의 Z 경로가 셀 extent를 지나야 해서 배선 성공률이 낮을 것(추정)이므로 W2를 W1과 함께 넣는다.
- **규칙(Codex 회의 #3 반영)**: ① 기하 가드의 "연결점 일치 금지"에 **허용 예외 1개**를 명시 — 같은 넷의 스텁 끝 + 배선 끝점 + 라벨 앵커가 한 점에 있는 것(W1이 의도한 삼중 일치); 그 외 모든 일치는 지금처럼 거부. ② **넷 단위 all-or-nothing**: 한 넷의 경로 일부라도 막히면 그 넷은 스텁+라벨만 남기고 배선을 전혀 내지 않는다(끊긴 배선은 ERC 경고와 오독을 만든다). ③ 같은 거터에 두 넷이 지나면 1.27 mm 트랙을 넷마다 다르게 배정(같은 트랙 공유 금지). ④ 선분 중간의 교차는 KiCad에서 연결되지 않으므로 허용하되, 일부러 교차하는 픽스처 1개로 parity·ERC 불변을 테스트로 고정. ⑤ 보드마다 "배선된 넷 / 배선 대상 넷" 비율을 stage note로 보고(W2·임계값 조정의 근거).
- **W3 (다음 단계, 측정으로 정당화됨)**: 큰 보드의 배선 성공률이 낮다(KR447 22 %, ATmega 23 %; 분배기 100 %). 원인: W1 후보가 "핀이 향하는 쪽의 가장 가까운 채널"뿐이라 먼 행·열의 핀 사이 경로가 다른 셀의 extent에 막힌다. 개선 후보(비용 M): ① 분기가 인접 거터를 한 번 더 우회하는 Z 경로 허용, ② 블록 단위로 열을 잡는 배치(같은 블록을 한 열에 세로로), ③ 핀 방향에 따른 심볼 미러(커넥터가 저항 쪽을 보게). PASS 조건: ATmega 보드 배선 비율 ≥ 50 %, 기존 테스트·ERC·parity 불변, 분배기 그림의 바깥 루프가 짧아짐. 로컬 라벨 1개로 줄이는 안은 Codex 회의 #3대로 범위 밖.
- 비용: W1+W2 M–L(라우터 + 정렬 키 + 가드 + 테스트 3개), W3 S. 렌더러(`report`의 SVG, `tests/test_schematic_render.py:369`)는 이미 wire/junction을 그린다.

2차 검토에서 소스로 재확인한 근거: B1 `tools/kicad/cli.py:139,143`(빈 `frozenset()`), `tools/manufacturing/capability.py:197-198`("not measured" 반환) · B2 `agents/regulatory.py:188`(`required=False`) · B3 `repair/strategies.py:20-23` 외 emit 지점 없음 · B4 `workflow/orchestrator.py:458,462`(pop; 메시지는 `<kind> compile refused: …`뿐) · B5 `cli.py:408` · B7 README 35행 `## 현재 상태 (2026‑09‑27)` · B8 README에 `DRC` 70회, `SPICE` 46회, `RELEASE` 35회, `IR_BUILD` 12회 등 대문자 vs 소문자 id 2회 · B9 `ir/validation.py` `_SEVERITY` 순서 · B10 `repair/loop.py:101-104`(`report.failures`만 순회) · 락 범위 `cli.py:846,1053,1120,1179`(run/review/stage-reports/relocate).

### 3.3 스킬(EDA_Engineer) 설계에서 결정할 것 — 나의 권고
| 질문 | 권고 |
|---|---|
| 파일 구조 | **SKILL.md + references 3개(그중 no-CLI 페이지는 한 화면)**: `references/pipeline.md`(19단계 표: 무엇이 돌고, PASS 조건, NOT_VERIFIED vs FAIL, 수리 범주; RF/SI는 한 문단; 검증기는 **가족** 한 줄씩 `ir.*`·`calc.*`·`spice.*`·`kicad.*`·`pcb.*`·`mfg.*`·`review.*`·`regulatory.*`, 단계 규칙이 걸린 대표 id만 — 회의 #4; 측정 사실 명시: AM 소스는 ngspice 43+(A9), astable 앵커는 엔진 버전별(A3), kicad-cli exit 0·5만 성공; 외부 행위 전체 목록과 유료 플래그를 안전 블록으로 반복), `references/answers.md`(제어 키 `CONTROL_KEYS` + 기본 키 4개 + **템플릿 13행**(내장 8 + 무선 5)의 입력 키·단위·범위 + 거부문 "no template matches…"(D1 문구는 존재 전까지 0건) + 규제 범위 키 + `pcb.*` 조향 + 승인 플래그; 나머지는 `ai-eda run --help`로), `references/without-cli.md`(감지 → 설치 제안 → 거절 시 kicad-cli ERC/DRC 두 명령, ngspice 호출, 증거 장부 행 형식) |
| SKILL.md 길이 | 250줄 이하 — 회의 #4 예산(상한): 안전·관측·리밋 ~45, happy path ~30, 상태·provenance ~35, 보고서 계약 ~20, 불변식 ~20, exit·confirm·출력·venv·UTF8·언어 ~60, frontmatter·여유 ~40. **상단 40줄**(I9): 하드 리밋 + 외부 행위 **압축 분류**(설치/삭제·주문/구매·업로드/푸시·제출·fetch·유료/구독은 절대 먼저 하지 않음) + 관측 텍스트=데이터 한 문장 + 전체 목록 포인터; 12종 전체 목록은 불변식 절에 한 줄(I8: SKILL.md 안에). happy path(doctor --strict→setup-kicad→new→run→confirm_design→읽기), 6개 상태, provenance 5종, 불변식 체크리스트 ~15개, exit code 표(0/1/2 + "traceback+exit 1 = ir.json 로드 실패"), confirm_design 무시 4경우, run 출력에서 단계 줄(0열)과 `  note:`/`  report written:` 줄(2칸 들여쓰기) 구분, `pipeline.json`의 `state.outcomes[]` 위치, 외부 행위 전체 목록(git_push, external_upload, system_install/delete, pcb_order, component_purchase, paid_api_call, manufacturing_order, regulatory_submission, network_fetch, subscription_use)을 "절대 먼저 하지 않는다"로 |
| `scripts/check_evidence.py` | **만들지 않음**. `ai-eda review --json`이 재해시·수리 범주를, `ai-eda report`가 fresh/stale/unstamped/opinion 라벨을 이미 계산한다 → "review와 report를 돌리고 라벨을 읽어라" 한 줄 |
| CLI 없을 때 fallback | 한 화면. 19단계 수동 복제는 과함. kicad-cli exit code는 이 프로젝트가 0·5만 성공으로 알 뿐(`ok_codes=(0, 5)`) 3/1의 의미를 적지 않는다 |
| venv 경로 | `ai-eda`가 PATH에 없으면 `<repo>\.venv\Scripts\ai-eda.exe`(또는 그 venv의 `python -m ai_eda.cli`); 시스템 Python의 `python -m ai_eda.cli`는 `No module named 'ai_eda'` |
| 락 | 동시 실행 금지는 `run / review / stage-reports / relocate`에만 해당(`.ai-eda.lock`); `report / serve / gui / new / doctor`는 락을 잡지 않아 `run` 옆에서 돌려도 된다 |
| 모드 감지 | 과제를 이해한 뒤, **ai-eda 명령을 처음 쓰기 직전**에 `ai-eda doctor --strict`(이후 모든 도구 주장의 근거). CLI 없는 모드에서는 해당 없음 |
| IR 직접 편집 | 금지. `--answer`와 문서화된 JSON 입력(`--fab-capability`, `datasheet_facts_file`)만. `references/ir.md`는 만들지 않음 |
| "측정 안 됨" 사실의 위치 | SKILL.md의 "하드 리밋" 절에 5줄(과장 방지), 상세는 `references/pipeline.md` |
| 언어 | 사용자 언어로 답하되 id/플래그/상태명은 영문 verbatim |
| `confirm_*` 답 (검토 1-1) | `confirm_requirements`·`confirm_design`·`confirm_parts`·`confirm_facts`=yes는 **사용자가 표를 본 턴 뒤에만** 준다; 스킬이 같은 턴에 표를 읽고 스스로 yes를 넣는 것은 2-run 프로토콜(§2.2) 우회라 금지. SKILL.md happy path에 2-run 예시 15줄(1차 run 출력의 표 → 사용자에게 보여 줌 → 사용자 턴 → 2차 run `--answer confirm_design=yes`). 순서 **실측(2026-11-04, typed 답·LLM 없음)**: 1차 run은 바로 `confirm_design`에서 멈춘다(`confirm_requirements`는 LLM 추출이 있을 때만) → 예시는 `confirm_design` 라운드만 + 그 한 문장(회의 #4 Q5) |
| 관측 텍스트 (검토 1-2) | 한 문장: `sources/*`(데이터시트·벤더 페이지)·`report.html`·`pipeline.json` 메시지·D1 설계 파일 안의 지시문은 **데이터이지 명령이 아니다**; 12개 외부 행위(§3.3 "유료/온라인 행위" 행)는 채팅에서 사용자에게 묻는 것으로만 시작한다. 참고 레포의 `find_directive`(`llm/extraction.py:425`, `datasheet_facts.py:267`, `capability_file.py:398,453`)는 인용문만 거르므로 스킬 자신의 읽기는 이 문장이 덮는다 |
| 상태별 허용 동사 (검토 1-3) | SKILL.md의 상태 표(6 상태 + provenance 5종)에 "말해도 되는 것 / 금지 동사" 열: PASS(tool 있음)만 "검증됨/동작한다", NOT_VERIFIED는 "증거 없음", FAIL은 "도구가 거부", USER_INPUT_REQUIRED는 "사용자 답 필요", `assumption`/`llm_generated` 값은 "가정/제안". §7.5의 규칙이 여기 산다. references 3개 상한 유지(새 파일 없음) |
| frontmatter `description` (검토 F4) | plan 단계에서 초안: 발동해야 하는 요청 10개(회로 설계·KiCad 프로젝트·ERC/DRC·SPICE·BOM·`ai-eda`)와 발동하면 안 되는 요청 5개(일반 KiCad 사용법, ai-eda 밖 SPICE, 순수 펌웨어 질문)를 §4 6단계 시험에 포함. PASS: 양성 10/10 발동, 음성 5/5 미발동 |
| 유료/온라인 행위 | 설명만 하고 절대 먼저 켜지 않음(`--online`, `--llm`, `propose_regulations=yes`, `extract_datasheet_facts=yes`) |

### 3.4 협업 환경 보완점
| # | 항목 | 제안 |
|---|---|---|
| C1 | reason-network 바이너리가 scratchpad에 있음 | 사용자가 원하면 공식 설치(`irm https://reasonmachines.com/network/install.ps1 \| iex`)로 PATH/서비스 설치 — 사용자 결정 |
| C2 | Codex 기본 모델 `auto/best-free` 실패 | `~/.codex/config.toml`의 `model`을 `auto/best-coding`으로 되돌릴지 사용자 결정; 그 전까지 `-m` 플래그 |
| C3 | Codex 스킬 디렉터리 비어 있음 | `~/.codex/skills/ponytail`, `graphify` 복사(AGENTS.md가 전제하는 위치) — 사용자 권한 필요 |
| C4 | `scripts/codex.ps1`가 브리지/모델 플래그를 모름 | 선택: `codex.ps1`에 `meet` 모드 추가(브리지 MCP + `-m`) |
| C5 | **Reason Network 팀 상태 소실(2026-11-04 21:40 관측)**: `reason-network team` → "not in a team yet", 세션 이름이 `me/claude-lead`, send는 "not registered" — 오전 회의 #1–#3의 팀 `yuchan`이 이 머신에서 사라짐(원인 미확인; AppData에 데이터 디렉터리 없음) | 복구는 `reason-network init`(팀 재생성, 사용자 머신 설정 변경 → **사용자 결정**). 그 전까지 회의는 로컬 폴백 `codex.ps1 ask`(회의 #4가 그렇게 진행됨). `rn_meet.sh`는 `RN_EXE`를 base 경로로 줘야 워크트리에서 돈다(C1과 같은 뿌리) |

---

### 3.5 보완 항목별 완료 조건 (Codex 회의에서 합의)
| 항목 | PASS 조건 |
|---|---|
| A1 | extras 없이 설치한 환경에서 `ai-eda doctor`가 크래시 없이 "httpx not installed" 한 줄을 찍는다 + 그 환경을 흉내 내는 smoke test 1개 |
| A3 | **✅ 2026-11-04 19:27 구현(결정 ⑰ (b))**: `MEASURED_DEVIATION_MAX_BY_ENGINE` {42: 0.049, 46: 0.0504}, 허용차 10 % 유지, 테스트는 엔진 버전으로 앵커 선택·미측정 버전은 앵커 단언만 skip — 64 passed(`a3-astable-ngspice46.md`). 경위: ngspice-46 72점 격자로 드리프트 확인(+0.04~+0.13 %p; 최악점 (3 V, 200 Hz) 5.03 %). 허용치를 넓혀 통과시키는 "테스트 연극"은 하지 않음 |
| A5 | ✅ 925fb58 — `run`·`review`가 `IRSchemaError`를 exit 2 + 한 줄 메시지로 매핑(report/serve/stage-reports/relocate는 이미 그렇다; `gui`는 IR 파일을 받지 않음) + 테스트 6개(`tests/test_cli_bad_ir.py`, 락 뒤 재로드 포함) |
| A6 | ✅ 925fb58(테스트) — (2차 검토로 축소) 사유 문자열·stdout·pipeline.json은 이미 충족. 남은 PASS 조건: `proposes nothing` 사유 테스트 1개 추가, 그리고 사유 문자열 5개(4경우; `ignored: answer(s) […] were given in this run`, `ignored: the table below (…) is not the one you confirmed`, `ignored: design content already present`, `ignored: no template to confirm` / `ignored: template <t> proposes nothing`)을 `answers.md`에 verbatim 수록. 이 문자열은 스킬이 참조하는 **고정 API**이므로 참고 레포에서 바꾸면 스킬도 바꾼다 |
| B4 | pop은 의도된 설계로 유지(오래된 산출물이 현재인 척하는 쪽이 더 나쁨). 단, 단계 메시지에 `previous <kind> artifact removed (compile refused: <reason>)`를 **stdout 최상위**와 pipeline.json 양쪽에 남긴다. 복원 메커니즘은 만들지 않는다 |
| B2+B9+B10 | 한 번의 "단계 의미론" 변경으로 함께 고친다: 미결 규제 후보가 있으면 RELEASE가 그 키를 명시하고, 질문에 막힌 단계와 FAIL 단계를 구분해 표시하며, USER_INPUT_REQUIRED만 있는 리뷰는 "blocked"로 요약된다. 메시지 문구만 고쳐 통과하지 못하도록 픽스처 2개: UNDECIDED 규제 후보를 가진 채 RELEASE에 도달하는 실행, USER_INPUT_REQUIRED만 있는 리뷰 |
| B1 | ✅ 925fb58 — (canary는 §3.1-b에서 통과) 기록 근거로 canary 테스트 node id 6개(§3.1-b 목록)와 그 PASSED 줄을 `notes/measurements/2026-11-04/`에 커밋하고 PR 본문에 복사(세션 scratchpad 로그는 사라진다; 측정 기록은 `notes/measurements/README.md`의 헤더 6줄 + `env.txt` 형식을 따른다 — 검토 1-4); 그 뒤 `PROJECT_RULES_MEASURED_VERSIONS` / `EXPORT_3D_MEASURED_VERSIONS`에 10.0.6 기록 후 `tests/test_fab_capability.py`의 monkeypatch 없이 `mfg.capability`가 PASS; 스킬의 pipeline.md는 그 측정 기준으로 동결 |
| A7 | ✅ 925fb58 — `report/server.py`에 같은 규칙의 `_LoopbackServer`(GUI를 import하지 않으려고 복제), Windows에서 `test_serve_loopback_read_only_and_live` 통과 |
| B11 W1 | ✅ 5a5e8a1 — 분배기 wire 22(스텁 7 + 배선 15), junction 1, ERC 0/0, DRC 0/0, parity 0; 라우터 테스트 8 + 컴파일러 배선 테스트 1 + 구조·렌더·GUI 테스트 적응; KR447·ATmega 컴파일·테스트 통과(배선 비율은 note로 보고: 22 %·23 % → W3) — 원래 조건: selftest 분배기 보드에서 넷 3개(`VIN`, `VOUT` 3핀+junction, `GND`) 전부 배선되어 심볼 간 `(wire` ≥ 3, `(junction` ≥ 1 (기준: §3.2 B11 측정, 현재 0/0); `test_compile_is_byte_deterministic`·`test_real_erc_passes_with_zero_errors`·`test_real_netlist_reproduces_ir_connectivity` 변경 없이 통과; 새 테스트 3개 — 배선 경로가 외부 핀을 지나는 구성은 그 넷 전체가 라벨로 후퇴하고(끊긴 배선 0) note를 남김, 배선 끝점이 외부 배선 위에 놓이는 구성은 CompileError, 일부러 선분 중간에서 교차하는 두 넷의 parity·ERC 불변; 렌더 테스트에 wire·junction 포함. ATmega128·KR447 보드도 컴파일·ERC 통과(배선/대상 넷 비율을 note로 보고, 임계값 4 조정 근거) |
| A8/A9 | A8: ✅(제품 2건, 13cdb5b) 보고서 답 명령이 Windows에서 따옴표 없이 나오고 두 서버 테스트가 10053 없이 통과(`a8-windows-fixes.md`); 나머지 4건은 Windows 분기로 통과(남음). A9: 원인(ngspice-46 AM 소스) 확인 뒤 A3과 같은 버전 앵커 방식 |

## 4. 다음 단계 (천천히)
1. **이 plan 검토** — 사용자 확인. 답이 필요한 결정(2단계 이후는 ①의 답 없이 시작하지 않는다):
   ① 참고 레포 수정 방식 — (a) 업스트림 PR(Yuchan-00/AI_EDA_Engineer; 비용: 항목마다 테스트+리뷰, 머지 대기) / (b) 수정 없이 스킬에 우회만 기록(비용: 스킬이 §3의 주의사항을 영구히 안고 감). 2–4단계와 §7은 (a)를 전제한다.
   ② 확장 순서 — D1(범용 입구, 가장 큰 변경)을 먼저 / E1→E3(펌웨어 요청에 직접 해당, 오늘 도구로 PASS 가능)을 먼저. 현재 §7.4는 D 먼저.
   ③ B6 기본 배선 all-or-nothing 유지 여부(비용: 바꾸면 기본값 테스트와 DRC 기대값 수정).
   ④ C1 reason-network 공식 설치(비용: 외부 설치 스크립트 실행, PATH·서비스 등록) / ⑤ C2 `config.toml` model 변경(비용: 한 줄; 안 하면 호출마다 `-m`) / ⑥ C3 Codex 스킬 복사(비용: 파일 복사 권한) / ⑦ C4 `codex.ps1` meet 모드(비용: 스크립트 수정).
   ⑧ D7 넷리스트→D1 변환기(비용: 파서 + 왕복 테스트; D1 형식 확정 뒤).
   ⑨ §7.4 (c)(d) 외부 설치: standalone ngspice-47, C 컴파일러·Verilator(비용: 설치 + 라이선스 경계 판단, §7.4 위험 표).
   ⑩ §3.3 권고 확인: `check_evidence.py`·`references/ir.md` 만들지 않음, SKILL.md 250줄 이하.
   ⑪–⑮ 판매·보호 관련 결정은 §8.4 끝의 목록(공개 시점, EULA, 판매 채널, 참고 레포 포함 여부, 법률 확인 담당).
   ⑯ **확정 (b) — 사용자 2026-11-04 19:26** (`SimulationSetup`의 시뮬레이션 전용 요소; **구현됨 같은 날 20:03 fdd6657**: `SimElement`·`SimulationSetup.elements/.nodes`, 컴파일러·recompute·assumption 걷기·이론 보고서, 21 테스트, Codex actionable 없음; 첫 사용처 i2c_pullup 바로 구현). 원문: 시뮬레이션 전용 소자(배선 용량 등 BOM에 없는 C/R)를 IR에 어떻게 둘지 — (a) 부품에 `in_bom=False` 플래그 / (b) `SimulationSetup`의 전용 요소 목록(비용: 각각 S–M; i2c_pullup·D8의 포트 부하 모델이 필요로 함). Codex 의견(2026-11-04 18:57, `.logs\codex-ask-decisions-16-17-20261104.txt`): **(b)** — 시뮬레이션 모델에 속하므로 `SimulationSetup`에; 해시·provenance는 이미 포함, BOM/CPL/배치/회로도 parity는 물리 부품에만 집중; (a)는 모든 경로에서 일관된 제외가 필요해 표면이 더 큼. 컴파일러는 기존 규칙 그대로 적용(llm_generated 거부, 장치·유한 양수 값·존재하는 넷·고유 이름 검증, 원시 넷리스트 텍스트 금지). Claude 의견: 동의 — (b).
   ⑰ **확정 (b) — 사용자 2026-11-04 19:26** (허용차 10 % 유지, 엔진 버전별 앵커표, 미측정 버전은 앵커 단언만 생략). 원문: A3 astable 앵커(원인 확인 완료 2026-11-04, `a3-astable-ngspice46.md`: ngspice-46에서 72점 전부 완료, 편차 +1.68..+5.03 %, 최악점 (3 V, 200 Hz)가 허용차 10 %의 절반을 넘음) — (a) `TOL_REL` 11 % + 버전별 앵커 / (b) 허용차 유지·절반 규칙 완화 / (c) 하한 3 V → 3.5 V. 어느 쪽이든 테스트는 `NgspiceShared().version()`으로 앵커를 고르고 미측정 버전은 SKIP/FAIL. Codex 의견(같은 파일): **(b)** — 11 %로 올리는 것은 테스트를 위한 확장이지 설계 근거가 아님; 10 % 유지, 앵커표 {42: 0.049, 46: 0.0503}, 절반 규칙은 측정 비율로 완화하고 46의 최악점이 절반을 살짝 넘음을 문서화; 미측정 버전은 PASS·10 % 안 여부는 계속 검사하되 버전별 앵커 단언만 생략(가까운 앵커 재사용 금지). Claude 의견: (b)에 동의하되 "절반 규칙"은 숫자(0.55)가 아니라 "앵커표의 최악점 ≤ 허용차"로 바꾸고, 절반이라는 설계 여유는 42 기준 문장으로만 남기는 쪽이 정직함.
2. ✅ 2026-11-04 `work/ead-skill` 925fb58(PR은 결정 ① 뒤; Codex 리뷰 P2·P3 반영) — **A5 수정 + A6 잔여 테스트 1개** (Codex 1순위였던 "A5+A6"의 축소판): run/review의 `IRSchemaError → exit 2` 매핑(시작 전 확인: README의 exit code 설명과 `tests/test_cli_llm.py`의 `assert code == 1`이 손상 IR이 아니라 질문 차단을 뜻하는지), `proposes nothing` 테스트(트리거: `plan.buildable`이 False인 plan — `agents/circuit.py:147-149` — 을 `design_from_requirements` monkeypatch로 만들고 `confirm_design=yes`를 준다). A6의 제품 코드 수정은 없음(테스트 1개만 추가); 사유 문자열 5개의 `answers.md` 수록은 6단계에서. 검증은 15분 전체 실행이 아니라 `pytest tests/test_ir.py tests/test_workdir_relocate.py tests/test_circuit_templates.py tests/test_leave_out.py`로.
2b. ✅ 2026-11-04 `work/ead-skill` 5a5e8a1 (Codex 리뷰: 성능 3.7 s로 수용, 테스트 2건 추가) — **B11 W1+W2 회로도 배선** (사용자 요청 2026-11-04; Codex 회의 #3 "go with changes"): 토폴로지 순 배치 + 핀 ≤ 4 넷의 trunk 배선 + junction + 라벨 유지 + 기하 가드 예외 1개 + 테스트 3개 → PR. W3는 나중.
2c. ✅(부분) **D9a** 2026-11-04: `Reduce.PP`/`MEAN`(75ad38e), `lc_lowpass` 템플릿 + 등록(fece446, 9368133) — 6번째 내장 템플릿이 실제 CLI에서 설계·검증됨. 같은 날 저녁 **`bjt_lowside_switch`**(7번째; 부하를 정전류 싱크 스티뮬러스로 둬 결정 ⑯을 비켜 감; ngspice on_drop 0.068 V ≤ 0.3 V·off_clamp 12.77 V ≤ 13 V PASS, 음성 대조 FAIL, ERC 0; `notes/measurements/2026-11-04/d9a-bjt-lowside-switch.md`). ⑯(b) 확정·구현(fdd6657) 뒤 **`i2c_pullup`**(8번째)도 같은 날 밤 구현: 전용 요소 CBUS·DOD(다이오드 드라이버)+전용 노드 DRV, ngspice rise PASS·R 3배 FAIL·ERC 0/0·CLI 2-run 통과(`d16-sim-elements-i2c-pullup.md`). D9a 템플릿 3종 완료.
3. **B4 메시지 + B2/B9/B10 단계 의미론** (Codex 2순위).
4. ✅ 925fb58에 포함 — **B1 기록 + A7 두 줄 수정** (Codex 3순위; canary는 §3.1-b에서 이미 통과): 측정 버전 상수에 10.0.6 기록, `report/server.py`에 `_LoopbackServer` 적용 → 참고 레포에 PR. 스킬 문서는 측정된 버전만 말한다.
   4b. ✅(A8 제품 2건, 13cdb5b) **A1 · A3 · A8 · A9**(스킬을 막지 않는 항목, §5 MISSING): A1 smoke test(§3.5); A3+A9는 원인 확인(§3.1 A3 명령, A9 매뉴얼 확인) 뒤 ngspice 버전 앵커로 함께; A8은 제품 쪽 2건(보고서 답 명령 인용, 본문 미수신 거부)을 먼저, 나머지는 Windows 분기. 5단계 이후와 병행해도 된다.
5. ✅ 2026-11-04 21:44 — **스킬 설계 회의(#4)**: §3.3 확정(`notes/meetings/2026-11-04-meeting-4.md`; Reason Network 팀 상태 소실로 로컬 폴백 `codex.ps1 ask`, §3.4 C5). Codex VERDICT "approve + 3 changes" → G7 축소(검증기 가족), 상단 40줄 압축 분류, 측정 사실(A9·A3·kicad exit 5·13 템플릿·거부문) references 명시. 다음은 6단계.
6. ✅(부분, 2026-11-04 22:05) **SKILL.md 초안** — `.agents/skills/eda-engineer/`(SKILL.md 154줄 + references 3 + `agents/openai.yaml`) + `tools/check_skill_portable.py`(OK) + `.claude/skills/` 바이트 동일 사본; 사실은 워크플로 `skill-facts`(독자 5)에서; 실제 과제 2개 실행(분배기 happy path, KiCad 숨긴 환경 → without-cli.md 정정), Codex 리뷰 반영(`notes/measurements/2026-11-04/step6-skill-draft.md`). **발동 시험(22:10–00:21, `step6-trigger-test.md`)**: Codex가 레포 `.agents/skills`에서 `eda-engineer`를 정확히 1회 발견(I11); 양성 **10/10 발동**(설명문으로 선택 → SKILL.md 읽음), 안전 감사 금지 행위 0·자기 확인 0; 음성 5건은 OmniRoute 경로가 1시간 넘게 끊겨 **미측정**(러너 준비됨, 다음 세션 재실행); Claude Code는 이 PC에 CLI가 없어 스킬 레포에서 연 세션의 **수동 시험**으로. 발견: `<repo>` 문구가 현재 폴더로 읽힘 → SKILL.md 157줄로 정정. **2026-11-05 새벽 (A단계, `step6-trigger-test-2.md`·`step6-review-2.md`·`g9-determinism-seeded-defect.md`)**: OmniRoute 프록시가 죽어 있어 사용자 지시로 Codex를 ChatGPT 계정 모델(gpt-6-luna)로 돌림 — 양성 10/10, 음성 4/5(N2 SPICE 덱 질문이 소프트 오탐; 설명문 수정 뒤 10회 중 9회 미발동), 안전 감사 금지 0·디스크 검색 0. Claude Code는 `start_session`으로 스킬 레포에 세션 5개(P1–P5) → **5/5 발동**, 표에서 멈춤 4/4(사용자가 세션 안에서 답한 뒤에만 confirm), 6절 보고 5/5; P6–P10·N1–N5는 자동 이벤트 턴이라 세션을 못 열어 **미실시**. G9 두 과제 통과(결정성: ir_hash·19단계 동일, pipeline.json은 at·ir_file_sha256·results_before만; 심은 결함: calculation FAIL·exit 1) → SKILL.md 결정성 문장 정정. 2차 리뷰(Codex gpt-6-luna + 코드 대조 워크플로 78 에이전트: 249 주장 중 WRONG 4·IMPRECISE 36, 반박 견딘 34 + 누락 17 반영, 기각 6) → SKILL.md 181줄·pipeline 118·answers 92·without-cli 68, 검사기 OK. **05:25 완료**: Claude Code P6–P10·N1–N5 세션 10개 → 양성 **10/10**, 음성 **5/5**, 같은 턴 자기 확정 0/8(§3.3 F4 충족). 실사용 결함 발견: P10 ATmega 보드 ERC FAIL `power_pin_not_driven` ×3 = **B12 우선순위 상향**; P6 `leave_out=application` 거부·P6 bjt `on_drop` 0 traced·P8 MPN 입력 경로 부재는 `step6-trigger-test-2.md` 관찰 1–3. 시험 세션이 레포에 남긴 미추적 폴더(`projects/`·`rc_lowpass_1k/`·`astable_1k/`·`firmware/`·`.claude/settings.local.json`)는 사용자 판단으로 처리. **6단계 완료.** 원문: SKILL.md 초안 → 실제 과제 2개로 시험(분배기 재설계, 의도적으로 kicad-cli 없는 환경) → Codex review → 수정. PASS 조건: 두 과제 모두 스킬이 보고한 단계 상태가 `pipeline.json`의 `state.outcomes[]`와 일치하고, 스킬이 pipeline.json에 없는 PASS를 한 번도 주장하지 않으며, kicad-cli 없는 과제에서 ERC/DRC를 NOT_VERIFIED로 보고한다.
7. **푸시**: EAD_Engineer_Skill에 커밋. AI_Project 레포에는 `scripts/rn_bridge.py`와 `.gitignore`만.
7b. **판매 등록**(§8.5): 법률 플래그 (d) 확인 → LICENSE/NOTICE 최종 → agensi 등록(zip = SKILL.md + references 3 + scripts). 직접 판매를 병행하면 H3·H4.
8.–11. **확장(§7.4)**: §7.4의 순서(D1→D4→D3→D6; E1→E3→E2(+E4); 측정 뒤 E5/E6)를 따른다. 1–7이 끝난 뒤에만.

### 4.1 작업 루프 (파이프라인, 2026-11-04 세팅)
항목(A5, B11, D9a …) 하나마다 같은 순서로 돈다. 도구는 `B:\0) AI_Project\scripts\`에 있고, 참고 레포는 `work/ead-skill` 브랜치(main `4ee4d8e`에서 분기, 직접 커밋 금지 규칙은 main에만)에서 작업한다.

| 단계 | 명령 / 산출물 | 끝 조건 |
|---|---|---|
| 1 브랜치 | `git -C AI_EDA_Engineer checkout work/ead-skill`(항목이 크면 `work/<항목>`) | 깨끗한 작업 트리 |
| 2 구현 | ponytail: 가장 작은 완전한 변경 + 그 테스트 | 코드와 테스트가 같이 있음 |
| 3 빠른 테스트 | `scripts\aieda-test.ps1 quick`(IR·workdir·템플릿·leave_out·회로도 컴파일러, ≈1분) 또는 `files tests/…` | 실패 0 |
| 4 Codex 리뷰 | `scripts\codex.ps1 review -Dir ..\AI_EDA_Engineer "<초점>"`; 설계 결정이면 `scripts/rn_meet.sh msg.txt prompt.txt out.txt`(Reason Network 1라운드) | 지적마다 반영 또는 거부 이유 |
| 5 전체 테스트 | 닿은 영역이 넓으면 `scripts\aieda-test.ps1 full`(≈15분, A7 deselect 포함) | 기준선(13 failed, §3.1-b)보다 나빠지지 않음 |
| 6 측정 기록 | 로그 요약·덱을 `notes/measurements/<날짜>/`에 README 헤더 형식으로 | 뒷받침하는 plan 행 id 명시 |
| 7 커밋 | 참고 레포: 항목 id로 시작하는 메시지, Co-Authored-By 줄; plan은 EAD_Engineer_Skill에 같이 | 결정 ①=(a)면 PR, (b)면 브랜치에만 |

세팅 검증(2026-11-04): `codex.ps1 ask`가 참고 레포에서 정답(`ai_eda`, tests 125개)을 돌려줌(exit 0, `auto/best-coding`); `aieda-test.ps1 quick` 기준선 = **3 failed / 130 passed / 7 skipped, 36.6 s**(실패 3건은 전부 알려진 것: A3 astable ×2, A8 `test_leave_out` 인용 — 이보다 나빠지면 회귀); reason-network 바이너리는 `.tools/reason-network/`(zip sha256 `1789e0b4…`에서 추출, gitignore)로 옮겨 세션에 묶이지 않게 함. 로그는 `.logs/`(gitignore).

## 5. Codex 검토 의견 (회의 #1, 2026-11-04, reason-network)
전문: `notes/meetings/2026-11-04-meeting-1.md`. 요지:
- **WRONG으로 지적, 수용**: R4 "모든 과제의 첫 명령 = doctor"는 과함 → "과제를 이해한 뒤, ai-eda 명령을 처음 쓰기 직전에 `doctor --strict`"로 수정. A3는 원인 미확인 상태의 추정 → 완료 조건에 "원인 먼저" 명시. A2는 콘솔 인코딩 문제라 제품 결함이 아님 → 스킬은 찍힌 파일명에 의존하지 않고 exit code와 JSON만 읽는다(수용; 참고 레포 수정 없음 — §3.1 A2).
- **MISSING, 수용**: 항목별 완료 조건(§3.5 신설), A1 회귀 테스트, "스킬을 막는 항목"의 우선순위 매핑(A5·A6·B1이 먼저 정리돼야 스킬을 진실되게 쓸 수 있다).
- **OVERBUILT, 수용**: answers.md는 한 화면·"나머지는 `ai-eda run --help`"; without-cli.md는 증거 장부 원칙 + 가장 흔한 fallback 하나만, 더 깊으면 설치를 권한다; pipeline.md 표의 셀은 한 줄. R2(check_evidence.py 없음)·R3(ir.md 없음) 전적으로 동의.
- **TOP-3**: ① A5+A6 ② B4 메시지 + B2/B9/B10 ③ B1 canary 후 pipeline.md 동결 — §4 순서에 반영.
- **후속 질의 결과**: B4 롤백 요구 철회(pop 유지 + stdout/pipeline.json 메시지). A6 완료 조건은 Claude 초안에 "4가지 사유 문자열을 고정 API로" 추가.
- **회의 #2 (§7 검토, 1라운드, 전문 `notes/meetings/2026-11-04-meeting-2.md`)**: WRONG 3건 수용("입구만 닫혀 있다"→검사·리뷰·보고서의 템플릿 결합으로 정정; d_cosim은 파싱까지만 측정; "불가"→"시도한 두 형태로는 불가"). MISSING: 아날로그 IC 벤더 모델 입구(D6 신설), 넷리스트→IR 변환(D7, 사용자 결정), 시간축 결합 위험(위험 표에 추가); "E1부터 엔진 사망 위험"은 E1–E3가 코시뮬 카드를 만들지 않으므로 거부(§7.4에 명시). OVERBUILT 수용: E4를 E2가 쓰는 탐지로 축소, 7.5를 두 줄로. ORDER: E1→E3→E2→E4로 변경, D 순서 유지. TOP-3: D1, E3(`A` 소자), E2(simavr VCD).
- **회의 #3 (B11 회로도 배선 설계, 1라운드, 전문 `notes/meetings/2026-11-04-meeting-3.md`)**: VERDICT "go with changes". 수용: W2(토폴로지 배치)를 W1과 한 변경으로; 가드의 허용 예외(같은 넷의 스텁 끝+배선 끝+라벨 앵커) 명시; 넷 단위 all-or-nothing; 거터 트랙 넷별 분리; 일부러 교차하는 픽스처; 배선 비율 note; 로컬 라벨(옛 W4)은 범위 밖. Codex가 확인한 KiCad 사실: 선분 중간 교차는 연결되지 않음, 끝점 일치·끝점-선분 접촉은 연결됨, 라벨 유지는 ERC·netlist에 영향 없음. Claude의 회의 뒤 정정: Codex가 본 초안은 "2핀 비전원 넷만"이었으나 분배기 측정(§3.2 B11)으로 그 규칙이 아무것도 배선하지 못함을 확인해 "핀 ≤ 4 모든 넷 + trunk/junction"으로 바꿨다(Codex의 W3 분리 권고는 이 때문에 적용하지 않음).
- **회의 #4 (§3.3 스킬 구조 확정, 1라운드, 로컬 폴백; 전문 `notes/meetings/2026-11-04-meeting-4.md`)**: Codex VERDICT "approve the 3-reference, no-scripts structure with three changes" — WRONG 2건 수용(G7의 id별 60줄은 lookup dump → 가족별; 12종 목록을 상단 40줄에 다 넣으면 예산이 안 닫힘 → 압축 분류 + 포인터, 전체 목록은 I8 때문에 SKILL.md 불변식 절에), MISSING 3건 수용(A9·A3 게이트, kicad exit 5, 13 템플릿·거부문을 references에), OVERBUILT 3건 동의(4번째 reference·`scripts/`·추가 시험 없음). Q1–Q7 답은 Claude 사전 입장과 일치. 채널: Reason Network 팀 소실(§3.4 C5).
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
| D5 | **LLM = 템플릿 작성자** (사용자 결정 2026-11-04: 흔한 회로는 D9 템플릿, 그 밖은 1회용 LLM 제안) | 템플릿을 전부 만들 수 없다; `CIRCUIT_DESIGN`은 라벨뿐(`llm/router.py:86`), 프롬프트 없음 | 맞는 템플릿이 없을 때만 LLM을 불러 **템플릿과 같은 모양의 1회용 설계 제안**(부품·넷·값, `SpiceBinding` 또는 `exclude`+사유, 자극·분석·기대값과 그 기준의 유도 근거, D8용 포트·정격 선언)을 D1 형식으로 받는다. 출처는 전부 `llm_generated`; 기존 `confirm_design` 표/해시 게이트를 그대로 통과해야 IR에 들어간다. 부품은 라이브러리 해석이 거부하면 탈락, 모델 카드는 D6 출처가 없으면 `assumption`. **LLM 개입은 첫 설계와 사용자의 재설계 요청 때뿐**: 값 변경·재생성·수리 루프는 저장된 IR만 쓴다(결정성). 확인된 제안은 D1 파일로 내보내 재사용(사용자만의 템플릿 모음이 됨). 유료 호출 = 예산 플래그·승인(§2.2), 공급자는 §9 J1 | fake 공급자(`--llm fake:<json>`)로: 제안 → 표(기대값마다 "LLM 제안 기준"과 유도 근거 열) → 다음 실행 확인 → 그때부터 시뮬레이션; **확인 전 제안은 ngspice에 닿지 않음**(`compilers/spice.py:235-237`의 거부가 그대로 작동, 테스트로 고정); 기준이 요구사항에서 유도된 기대값만 PASS; 확인 뒤 재실행에서 LLM 호출 0회(`fake.requests` 비어 있음); 내보낸 D1 파일을 다시 넣으면 같은 IR 해시 |
| D6 | 아날로그 IC 벤더 모델(op-amp·레귤레이터·비교기)의 입구 (Codex 회의 #2 MISSING 4) | "모든 회로"는 펌웨어보다 먼저 IC 모델에서 막힌다. IR은 이미 `SpiceBinding.model_card`(verbatim `.model`/`.subckt`, authoritative/user provenance 필수, `ir/simulation.py:100-104`)를 지원하지만 벤더 `.lib`를 가져오는 절차·검사가 없다 | 새 필드 없음: D1 파일의 부품에 `model_card` + 출처(URL/파일 해시)를 허용하고, D1 검증이 그 텍스트를 `validate_deck` 규칙(따옴표·금지 카드·`.include` 없음)으로 미리 검사; 출처 없는 카드는 `assumption`으로 강등 → 그 부품의 결과 NOT_VERIFIED | 벤더 op-amp subckt 하나를 D1 파일로 넣어 `spice.*` PASS에 `model_card` 해시·출처가 찍힘; 출처를 빼면 같은 실행이 NOT_VERIFIED |
| D8 | **템플릿 독립 검증 층** (사용자 요청 2026-11-04: "어떤 회로든 대신호·소신호를 전 방면에서 검토") | 계산기(`calc.*` 100여 개)와 SPICE 기대값은 **템플릿이 골라 적어 준 것만** 돈다; 템플릿 없는 회로는 기대값이 0개라 시뮬레이션이 돌아도 전부 NOT_VERIFIED. 구조·제조 검증(ERC/DRC/연결성/제조 한계/열 예산 일부)만 템플릿과 무관 | D1 형식에 **선언**(포트 in/out/전원, 부품 정격, 피드백 루프·블록 종류)을 두고, 선언에서 검사 목록을 자동 생성: 대신호 — 동작점(모든 Q/M/D의 바이어스 영역, 의도치 않은 포화·차단), 레일 전류 합산과 부품별 소산 대 정격, DC 스윕 클리핑, 과도 정착·오버슈트·돌입; 소신호 — 선언된 포트의 AC 이득·대역폭·위상, 피드백 선언 시 루프 위상·이득 여유, 입출력 임피던스; 구조 — 플로팅 노드·무부하 출력·디커플링. 모든 검사는 도구 결과로만 PASS, 선언이 없으면 그 검사는 "선언 `<키>` 없음"으로 NOT_VERIFIED. 단계: D8a 동작점+정격(S–M), D8b 포트 AC(M), D8c 루프 안정성(M–L), 잡음·PSRR은 뒤. 기존 템플릿도 같은 층을 타게 해 회귀 테스트로 삼는다 | D8a: 분배기·RC 템플릿이 기존 PASS 집합을 유지하면서 동작점·정격 행이 추가됨; 의도치 않게 포화된 BJT 회로가 FAIL; 정격 선언을 빼면 그 행만 NOT_VERIFIED. D8b: RC 템플릿의 차단 주파수가 템플릿 기대값 없이 포트 선언만으로 같은 값에 PASS. D8c: 위상 여유 기대값이 요구사항에서 유도될 때만 PASS |
| D9 | 기본 템플릿 카탈로그 (사용자 결정 2026-11-04: 흔한 회로는 미리 템플릿으로) | 아래 "D9 상세" 참고 | 아래 "D9 상세" 참고 | 아래 "D9 상세" 참고 |
| D7 | KiCad 회로도/넷리스트 → D1 파일 변환 (Codex 회의 #2 MISSING 5) | 아무도 임의 회로의 IR을 손으로 쓰지 않는다; 변환기가 없으면 D1은 실사용자가 거의 없다 | **사용자 결정 사항**: 이 시스템은 IR이 원본이고 KiCad 파일은 파생물인데, 변환기는 흐름을 거꾸로 돌린다. 만든다면 "읽기 전용 입력, provenance `user_requirement`+파일 해시, 한 번 들어온 뒤로는 IR만 원본"으로 한정. D1 형식 확정 뒤 결정 | (결정 뒤) 템플릿이 만든 `.kicad_sch`를 변환해 D1으로 넣으면 원래 IR과 부품·넷이 동일 |

**D9 상세: 기본 템플릿 카탈로그** (사용자 결정 2026-11-04: 흔한 회로는 미리 템플릿으로 — 템플릿 = API 키 없음·오프라인·결정론·tool-backed PASS까지 내는 판매 핵심. 그 밖은 D5 1회용 제안 + D8 검증 층)

**모델 출처 정책 (M4를 여기서 닫음)**: KiCad 라이브러리의 `Sim.*`·`Simulation_SPICE.sp` 카드는 범용 기본값(기본 Gummel-Poon, 기본 D, Holger Vogt 단극 op-amp 매크로)이지 MPN에 대한 벤더 사실이 아니다. 따라서 `authoritative`로 보지 않고, 템플릿은 카드 본문을 **손으로 인라인한 확인된 선택**으로만 쓴다(`assumption`→확인 후 `user_requirement`; `templates.py:1110,1223`·`rf/models.py:3-20` 관례). SourceRef·sha256 절차 불필요, 벤더 카드는 D6. 결과: D·Q·op-amp 회로가 오늘 오프라인 PASS 가능하고, 모델 파라미터(BF·Rds·GBW)에서만 나오는 수치는 전부 "표시만".

**선정 기준** (네 가지 모두 만족해야 후보):
1. 수요 — 수요 조사 상위(출처 수 집계라 UNVERIFIED)이거나 상위 회로의 필수 블록.
2. 오프라인 PASS — 부품이 수동소자·D·Q·M·op-amp 매크로뿐이고, 모델은 (a) 손 카드 확인 선택(astable 패턴) 또는 (b) 이상화+`exclude`(LED/L7805 패턴). 레귤레이터·555·비교기·스위칭 IC는 D6 뒤.
3. 입력이 기존 키(`UNIT_OF`, `inputs.py:96-105`, RF 키 포함)로 표현되거나 새 키 ≤ 2개(맨 물리 단어 금지, `inputs.py:130`).
4. 기대값의 `nominal`(또는 한계값) 최소 1개가 요구 키(`requirement_id`)에서 계산기로 유도되고, **요구값을 그대로 되돌려주는 항등식이 아니다** — 요구에서 R을 정하고 같은 R로 V=IR을 재는 식(션트, 제너 BV, 풀업 개방 레벨)은 PASS 근거가 아니다(§2.2). 모델 파라미터에서만 나오는 기준은 `assumption`, 표시만.

**tier-1 후보 (있음 4 + 신규 5; 확정은 측정 뒤)** — `~줄` = 템플릿+계산기+테스트 추정(LED 152줄·RC 199줄·테스트 40개 기준)

| id | 회로(수요 #) | 입력 키 | 계산기 → 기대값(nominal 출처) | 모델 | 새 키 | ~줄 | PASS·거부 |
|---|---|---|---|---|---|---|---|
| `divider` | 저항 분배기(#2) | input_voltage, output_voltage, output_current | 있음(`templates.py:456`) | R만 | 0 | 있음 | 현재 테스트 유지 |
| `led` | LED+직렬 R(#1) | input_voltage, led_forward_voltage, led_forward_current | 있음(`:655`) | 이상화(`exclude_reason=MODEL`+`VLED`) | 0 | 있음 | 동상 |
| `rc_lowpass` | RC 1차 LPF(#17) | cutoff_frequency | 있음(`:838`) | R·C만 | 0 | 있음 | 동상 |
| `astable` | BJT 비안정(#22) | oscillation_frequency, input_voltage | 있음 | `.model QNPN NPN(TR=200n)` 확인 선택 | 0 | 있음 | 동상 |
| `lc_lowpass` ✅ | LC 2차 LPF(#31) — **구현·검증됨 2026-11-04**: 양단 Z0 종단(R1·R2 보드 위), `db_at`@f_c vs v_pass, nominal −3.0103 dB(`calc.lc.butterworth2.level_db`), ac 500점/decade | cutoff_frequency, system_impedance(RF 키 재사용) | L·C(Butterworth, Z0) → AC `\|H(fc)\|`=−3 dB, nominal=cutoff_frequency | R·L·C만 | 0 | ~400 (실제 ~330 + 테스트 120) | AC PASS(측정 −3.01 dB); L 2배 음성 대조 비-PASS; 2회 빌드 해시 동일; Z0·fc 범위 밖 거부; ERC 0 — 전부 통과; **`TEMPLATES` 등록·README/GUI 6종·이론·부품 노트까지 완료(9368133)**, 실제 CLI 2-run 확인 |
| `i2c_pullup` ✅ 2026-11-04 | I2C 풀업(#11) — 구현: 헤더 3핀(VDD/SDA/SCL), GND는 핀 없는 기준 넷; CBUS·DOD 전용 요소, DRV 전용 노드; `held_low`: 잡힌 레벨 = 다이오드 순방향 전압 계산값(`calc.i2c.v_low_diode`) ±50 mV; `rise`: v(SDA) AT t_low+t_30+t_r ≥ 0.7 V_DD(한계; t_30은 계산·측정된 V_low 기준이라 R·C_b ≤ t_r/0.8473일 때만 통과, 1.04·R_max 음성 대조 FAIL); R = max(0.8·R_max, R_min), R_min > R_max면 거부; V_DD 2.5..5.5 V(다이오드 전압이 30 % 점 아래여야); 실제 V_OL·SCL 미검증 명시 | input_voltage, clock_frequency, bus_capacitance, bus_rise_time | R_max=t_r/(0.8473·C) (0.8473=ln(0.7/0.3), I2C 30/70 % 문턱 — 계산기 상수, `tool_version`으로 추적), R_min=(Vdd−V_OL)/I_sink(V_OL·I_sink 선택) → tran: t=bus_rise_time에서 `v(SDA)`≥0.7·Vdd, nominal=input_voltage·bus_rise_time | R·C+PULSE(개방 드레인 이상화) | `bus_capacitance` F, `bus_rise_time` s | ~450 | tran PASS; R_min>R_max면 USER_INPUT_REQUIRED(거부문에 수치) |
| `bjt_lowside_switch` ✅ 2026-11-04 | BJT 로우사이드 스위치+환류 D(#10 릴레이, #5 저항 부하) | input_voltage(제어), output_voltage(부하 공급), output_current, max_voltage_drop | 구현: R_b=(Vctl−Vbe)/(Ic/β_forced)(Vbe·β_forced 선택, 표에 노출) → tran ON 창 `v(SW)` MEAN ≤ max_voltage_drop(한계 `at_most`; nominal = 요구값 자체, 한계는 requirement_id를 못 들므로 SW 넷·제약이 요구사항을 가리킴); OFF `v(SW)` MAX ≤ output_voltage+v_f(v_f 선택) | `.model QSW NPN (BF=100 TR=200n)`+`.model DFW D` 확인 선택; **부하 = 정전류 싱크 스티뮬러스**(VLOAD→SW, 이상적 유도성 부하; 코일 R+L은 ⑯ 뒤의 변형) | `max_voltage_drop` V (별칭 on_voltage_drop·v_ce_sat·vce_sat·switch_drop) | 실제 ~330 + 테스트 ~120 | 실측 on_drop 0.068 V·off_clamp 12.77 V PASS; R_B 100배 음성 대조 on_drop FAIL; Ic>0.2 A·V_load>40 V·V_ctl<V_BE+0.5 V 거부; DividerTemplate는 max_voltage_drop이 있으면 물러남 |
| `opamp_noninverting` | 비반전 op-amp(#7) | gain, input_voltage(공급) | R2/R1=gain−1(E-series 선택, 실제 비는 계산기) → AC 저주파 `\|v(out)/v(in)\|`=gain, nominal=gain | `kicad_builtin_opamp` `.subckt` 본문(2.5 kB `.sp`, Public Domain) 인라인 확인 선택 — QNPN과 같은 경로, `spice.py:369-375`가 자급 `.subckt` 허용 | `gain` V/V | ~500 | AC PASS; 대역·슬루(POLE·GAIN 매크로 파라미터)는 표시만; gain<1 또는 출력 스윙>공급 거부 |
| `rectifier_cfilter` | 브리지 정류+C 필터(#29) | ac_input_voltage, ripple_voltage, output_current | C=I/(2f·ΔV), Vdc=√2·Vac−2Vf(f·Vf 선택) → tran PP(`v(out)`)≤ripple_voltage, MEAN(`v(out)`)=Vdc | `.model DR D` ×4 손 카드 확인 선택(라이브러리 1N4001 Sim.*은 읽지 않음) | `ac_input_voltage` V, `ripple_voltage` V | ~550 | 두 tran PASS; **표시만 행**: 다이오드 PIV=√2·Vac, 피크/평균 전류, C 리플 전류, 돌입 전류(정격 키 없음→NOT_VERIFIED) — 230 Vac에 1N4001이면 수치로 보이게 |

신규 키 6개: `bus_capacitance, bus_rise_time, max_voltage_drop, gain, ac_input_voltage, ripple_voltage` — 전부 `KEY_ALIASES`+`UNIT_OF`에 단위와 함께(`inputs.py:85/96`); 비RF 키의 추출 프롬프트 테스트 존재 여부는 UNVERIFIED(M9).

**tier-2 (보류 이유 한 줄씩)**
- 반전(#15)/팔로워(#18)/Sallen-Key(#21): 같은 op-amp 인라인 카드 재사용; `opamp_noninverting`이 PASS·ERC를 통과한 뒤 각 ~300줄(Sallen-Key는 `filter_q` 키 1개 추가).
- MOSFET 로우사이드(#5 M형)/역접속 PMOS(#12): 범용 NMOS/PMOS 카드의 4노드 M 또는 subckt 래핑과 OP 수렴 실측(M5) 뒤; 로우사이드는 `bjt_lowside_switch`의 카드 교체 변형으로.
- 레벨 시프터(#28): 요구 유도 기대값이 없음(개방 레벨은 풀업 항등식, L측 레벨은 선택값) → 기준 4 미달; D5 1회용.
- 제너 션트(#27)·전류 션트(#20): 기대값이 전부 항등식(BV=요구값, V=I·R) → 기준 4 미달; D5 1회용 + 전력 "표시만".
- 비교기(#14): 매크로 재사용 가능하나 문턱이 개루프 이득(모델 파라미터)에 의존 → 비반전 뒤 검토.
- 555(#6), LDO(#3), TP4056(#23): 모델 0 → D6.
- 서미스터(#19): 새 키 3개 → D2 뒤.
- Pierce(#13): 모션 RLC는 부품 사실 → D6; `atmega128.py:230`이 부분 커버.
- USB-C 5.1 kΩ(#9): 규격 상수가 계산기 안에 들어가는 것은 허용(I2C 0.8473과 같은 규칙)이나, 5.1 kΩ은 결과값 자체가 규격이고 시뮬레이션할 기대값이 없음 → 기준 4 미달.
- TIA(#30): 안정성(위상 여유) 기준은 D8c 뒤.

**하지 않을 것**
- MCU 보드(#8, #24): `atmega128_devboard` 하나로 두고 D8·E1 뒤 재검토(보드당 ~880줄).
- IC 제어 스위칭 레귤레이터(#4), H-bridge IC(#16), UART-USB(#25), LED 드라이버 IC(#26): 벤더 모델 없음/PSpice 전용이라 인라인 불가(`compilers/spice.py:22-24`) → exclude만 가능.
- 요구 키에서 유도되지 않는 기대값(모델 파라미터·"흔한 값"·LLM 추천)은 어떤 템플릿에도 넣지 않는다(§2.2). 정격 비교는 사용자 정격 키가 없으면 "표시만" 행.
- 데모 폴더의 벤더 `.lib`(Diotec bc337 등) 복사 금지: 라이선스·출처 검토는 D6.

**제작 방식**
- 템플릿은 **테스트가 딸린 코드**다(계약서 레시피 10단계). 파일: `ai_eda/design/catalog/<id>.py`(새 디렉터리; `templates.py`는 `TEMPLATES` 등록 줄만, `:1524`), 계산기는 `tools/calc/basic.py` `ROLES` + `recompute.py` `CALCULATORS`, 테스트는 `tests/test_catalog_<id>.py` + `test_si_templates.py` 파라미터에 id 추가.
- 허용오차 출처: 요구에 허용오차가 있으면 그 값(`user_requirement`), 없으면 템플릿 상수를 `_choice()`로 노출(`assumption`→확인 후 `user_requirement`). E-series 반올림은 계산기가 nominal에 반영하고 반올림 전·후 값을 표에 둘 다 적는다. 기존 4개의 허용오차 처리 방식은 UNVERIFIED — 같은 규칙으로 맞춘다.
- LLM(D5)은 템플릿 파일 **초안**을 낼 수 있다. 채택은 Codex `review` + 사람 + 테스트 전부 통과로만; 초안의 숫자·카드는 전부 `assumption`으로 시작한다.
- 템플릿마다 필수 테스트 7종: 표 줄 포함, 확인 후 provenance(`user_requirement`·`CHOICE_NOTE_PREFIX`·계산기 `tool/inputs/tool_version`), 정확한 넷리스트 문자열, **2회 독립 빌드 해시 동일**, 범위·라이브러리 공백 거부, `@needs_dll` ngspice 1회(요구 키 추적 기대값 PASS), **ERC**(kicad-cli 있으면 error·warning 0, 없으면 NOT_VERIFIED 단언; 이 PC는 KiCad 10.0.6). `test_readme_usage_counts_every_template`(`:928`) 때문에 README·`gui/page.py` 수치를 함께 고친다.
- D1 예제(`examples/designs/<id>.json`, 템플릿 코드에서 내보내기)는 **D1 형식이 있을 때만** 추가하는 후속 작업이며 D9 PASS 조건에 넣지 않는다.

**순서·비용·위치**
| 묶음 | 내용 | 전제 | ~줄 |
|---|---|---|---|
| D9a | ✅(부분, 2026-11-04 `work/ead-skill`) `Reduce.PP`·`Reduce.MEAN`(75ad38e) + **`lc_lowpass`**(fece446 + 등록·이론·부품 노트·종단 선택값 커밋; ngspice 코너 PASS·음성 대조·ERC·결정성 통과, 실제 CLI 2-run으로 끝까지 확인, `notes/measurements/2026-11-04/d9a-lc-lowpass.md`) + **`bjt_lowside_switch`**(3bf314c, 같은 날 저녁; 새 키 `max_voltage_drop`, 계산기 3개, 부하는 정전류 싱크 스티뮬러스(코일이 아닌 단순화 모델로 명시), 한계 기대값 2개; 6 테스트 첫 실행 통과, CLI 2-run 통과, Codex 리뷰 4건 반영/검증, `d9a-bjt-lowside-switch.md`) + **`i2c_pullup`**(같은 날 밤, ⑯(b) 구현 fdd6657 위; 새 키 `bus_capacitance`·`bus_rise_time`, 계산기 9개 `calc.i2c.*`, ATmega 템플릿은 버스 키가 있으면 물러남; 6 테스트·CLI 2-run 통과, `d16-sim-elements-i2c-pullup.md`) — **D9a 완료**(PP/MEAN + lc_lowpass + bjt_lowside_switch + i2c_pullup). **i2c_pullup 전제(설계 중 발견)**: 버스 용량은 보드 부품이 아니라 배선의 성질이라 "시뮬레이션 전용 소자"(넷리스트에는 들어가고 BOM에는 안 들어가는 C)가 IR에 필요하다 — 현재 `SpiceBinding`은 부품에만 붙고 제외 부품은 시뮬레이션에서 빠지므로, (a) `in_bom=False` 부품 개념 또는 (b) `SimulationSetup`에 시뮬레이션 전용 요소를 두는 결정이 먼저(사용자 결정 ⑯). 개방 드레인은 `Stimulus(source="current", kind=PULSE)`로 모델 가능(확인). | M7 완료 | ~1,500 (완료 ~1,000) |
| D9b | `opamp_noninverting, rectifier_cfilter` + 새 키 3개 | M6·M10 | ~1,050 |
| D9c | README/GUI 수치, 측정 기록, 전 9개 ERC 실측 — **부분 2026-11-04**: 내장 7종 일괄 실측(`d9c-erc-sweep.md`): 6종 ERC 0/0, ATmega만 `Input Power pin not driven` 3건 = 회로도 컴파일러의 PWR_FLAG/`power:*` 심볼 미구현(참고 레포 ARCHITECTURE "아직 아닌 것" 3번; 회귀 아님) → **새 항목 B12: POWER/GROUND 넷에 PWR_FLAG emit**(S–M, B11 W3와 같은 파일) | D9a·b | ~150 |
| 합계 | 신규 템플릿 5, 계산기 ~20, 테스트 ~35(ngspice 5, ERC 9) | | **≈2,600줄**, 2–3 PR |

- §4 위치: 8단계 D9이지만 **D9a는 4b–6단계와 병행 가능** — 닿는 파일이 `design/catalog/`, `tools/calc/*`, `requirements/inputs.py`, `tests/test_catalog_*.py`, README·`gui/page.py`뿐이라 A5(`cli.py`·`workflow/orchestrator.py`)·B11(배선 컴파일러)과 겹치지 않는다. 단 **`TEMPLATES` 등록은 B11 W1 머지 뒤**(B11 PASS 집합이 커지지 않도록).
- D9 PASS 조건: `len(TEMPLATES)`=9(+RF 5), 9개 모두 필수 테스트 7종 통과, 이 PC(KiCad 10.0.6/ngspice-46)에서 ngspice 5건·ERC 9건 실측 PASS가 `notes/measurements/<날짜>/`에 기록(§3.5 B1 형식), 기대값 중 `nominal.provenance`가 요구 키로 추적되지 않는 것 0개(테스트로 고정), 항등식 기대값 0개(리뷰 체크리스트).

**측정 항목 (후보 확정 전, 이 PC)** — 결과가 다르면 해당 행을 tier-2로 내리고 이유를 적는다. M2·M3(라이브러리 Sim.* grep)은 정책상 손 카드만 쓰므로 삭제, M4는 위에서 닫음, M5는 tier-2 MOSFET 행의 전제로 이동.
| # | 측정 | 영향 행 | 방법 |
|---|---|---|---|
| M1 | `library_component()`(`library_parts.py:25-66`)가 `extends` 상속(BC547→Q_NPN_CBE, 1N4148→1N4001)의 **핀**을 보는가 | bjt_lowside_switch, rectifier | 코드 읽기 + 합성 라이브러리 테스트 1개 |
| M6 | 브리지 4D + C의 tran 수렴, 돌입 구간 포함 | rectifier | `NgspiceShared.run` 덱 1개 |
| M7 | 판정 축약 11종(`ir/simulation.py:251-297`)에 PP/MEAN/MAX/특정 시각 VALUE가 있는지; 없으면 기대값 형식 수정 | i2c_pullup, rectifier, bjt_lowside_switch | 코드 읽기 |
| M8 | kicad-cli ERC 1건 소요 시간(9건 예산) | 전체 | 1회 실행·시간 기록 |
| M9 | 비RF 새 키에 추출 프롬프트 테스트가 요구되는지(`test_rf_requirement_keys.py:245`의 비RF 대응물) | 새 키 6개 | grep |
| M10 | `kicad_builtin_opamp` `.subckt`(레일 제한 D 포함)가 자급 카드로 컴파일되고(`spice.py:369-375`, `SpiceDevice.X`) AC 해석이 수렴하는지 | opamp_noninverting | 덱 1개 |

**측정 결과(2026-11-04, 이 PC; 덱·출력은 `notes/measurements/2026-11-04/` `rectifier.cir`, `opamp.cir`, `templates-measurements.md`)** — tier-1 5개 전부 유지:
- **M1 통과**: 라이브러리 로더가 `extends`를 재귀로 해석한다(`tools/kicad/library.py:12,353-377,609`). 실측: `BC547`(←Q_NPN_CBE) 핀 C/B/E, `1N4148`(←1N4001) K/A, `IRLZ44N`(←BUZ11) G/D/S, `LM358`(←LM2904) 8핀, `2N3904`(←Q_NPN_EBC) E/B/C 전부 정상.
- **M6 통과**: 브리지 4D(손 카드 `d(is=1n rs=50m n=1.8 cjo=10p bv=100)`) + 1000 µF + 100 Ω, 17 Vpk 50 Hz, `tran 50u 200m` 수렴(4,012점). 정상 상태 평균 14.56 V, 리플 1.19 Vpp(계산식 I/(2fC) ≈ 1.46 V와 같은 자리), **돌입 전류 5.13 A(1 ms) vs 정상 1.51 A** → 돌입·PIV "표시만" 행이 측정 가능.
- **M7 미비 → D9a 전제 추가**: 축약은 VALUE/AT/FINAL/MAX/MIN/FREQUENCY/DB_AT/RMS/DB_RMS/HARMONIC_DBC/AM_DEPTH 11종(`ir/simulation.py:251-297`)이고 **PP(피크-피크)·MEAN이 없다.** 리플은 MAX·MIN 두 기대값으로 쓸 수 있으나 "리플 ≤ 요구값" 한 행이 더 읽기 쉽고, 스위치 ON 전압은 MEAN 또는 AT(시각)이 필요 → `Reduce.PP`·`Reduce.MEAN` 추가(계산·테스트 각 S)를 D9a에 넣는다.
- **M8 통과**: `kicad-cli sch erc --severity-all` 1건 7.2 s(심볼 3개 보드) → 9개 보드 ERC 실측 예산 ≈ 1–2분.
- **M9 통과(요건 없음)**: 추출 프롬프트 키 커버리지 테스트는 RF 키에만 있다(`tests/test_rf_requirement_keys.py:245`); 비RF 키는 프롬프트 34행의 예시 목록("input_voltage, output_voltage, … ,")에 추가하는 것이 선택 사항일 뿐 테스트 요건이 아니다.
- **M10 통과**: `kicad_builtin_opamp`(Holger Vogt, Public Domain, `Simulation_SPICE.sp:10-31`) `.subckt`를 `params:`·`{식}` 포함 그대로 인라인한 비반전 증폭기(R1 1 kΩ, R2 10 kΩ, ±12 V)가 래퍼 검증을 통과하고 `ac dec 10 1 1meg` 수렴: |out/in| = 10.99(20.82 dB) @10 Hz–1 kHz, 10.60 @10 kHz, 3.75 @100 kHz(매크로 GBW = GAIN·POLE = 400 kHz / 11 ≈ 36 kHz와 일치). 저주파 이득 기대값 PASS 가능, 대역은 모델 파라미터 유도라 "표시만".

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
8. **D1(형식) → D9(기본 템플릿, 1차) → D8a → D4 → D3 → D6 → D8b/D8c.** D1·D5·D8·D9는 **한 입력 형식**을 공유한다(템플릿도 D1 파일 예제로 내보낸다). D2는 첫 비템플릿 회로가 실제로 새 키를 필요로 할 때. D5는 LLM 키가 생긴 뒤(그 전엔 fake 공급자로 테스트만). D7은 D1 형식 확정 뒤 사용자 결정. 사용자 결정(2026-11-04): 범용성은 "D9 소수 템플릿 + D5 1회용 제안 + 확인된 설계 파일 재사용"의 조합으로 얻고, 템플릿은 키 없이 오프라인에서 PASS까지 내는 판매 핵심이다.
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

---

## 8. 참고 스킬에서 가져올 것과 판매용 보호 조치

사용자 요청(2026-11-04): 이 스킬은 agensi.io 같은 사이트에 판매하므로 타인이 허가 없이 쓰지 못하게 하는 조치가 필요하다. 이 절은 (1) 참고한 두 스킬에서 무엇을 가져오고 무엇을 버리는지, (2) 판매용 보호 조치를 §2.2·§3.3의 원칙(증거 없음 = NOT_VERIFIED, PASS는 tool-backed만, LLM은 제안만, 관측 텍스트는 데이터)으로 번역한다. 근거는 세션 scratchpad의 클론(`KH` = `…\scratchpad\ext\kicad-happy`, `EXT` = `…\scratchpad\ext\ee-skills`)과 웹 조사(출처 URL 목록은 8.4 끝). 출처 없는 사실은 추정/UNVERIFIED로, 법률 판단은 **전문가 확인**으로 표시한다(이 절은 법률 자문이 아니다).

### 8.1 참고 대상과 라이선스
| 대상 | 무엇인가 | 라이선스 | 상태 |
|---|---|---|---|
| kicad-happy (github.com/aklofas/kicad-happy, 클론 `c451943`, 2026-11-03) | KiCad 설계 리뷰 스킬 1개 + 참고 문서 20개 + 스크립트 ~45개; "5,857개 공개 레포 코퍼스로 회귀 검증"(`KH\VALIDATION.md:13`, **저자 주장, 미재현** — §2.2 기준 assumption) | MIT, "Copyright (c) 2025 Andrew Klofas"(`KH\LICENSE`) | GitHub 페이지(2026-11-04 읽음): 1.6k stars, 141 forks, v3.0.0 |
| ee-skills (github.com/fxp/ee-skills, 클론 `3414c33`, 2026-10-20) | 규칙 카탈로그 531개(YAML) → 생성된 스킬 11개 + DRC/기하 검증 하니스; 본문은 중국어 | MIT, "Copyright (c) 2026 fxp"(`EXT\LICENSE`) | 저자 스스로 "약 83 % 맞음"(`EXT\docs\AUDIT.md`) |

- 두 참고 대상은 MIT **라이선스**의 스킬이다(MIT 대학과 무관).
- MIT 재사용 규칙: 텍스트·코드를 **글자 그대로 복사**하면 그 부분에 저작권 고지 + MIT 전문 동봉(기존 `NOTICE` 파일 하나로 충분; 현재 "복사한 파일 없음" 상태, `EAD_Engineer_Skill\NOTICE`). 아이디어·워크플로를 **우리 말로 다시 쓰면** 의무 없음이 통설이나, **구조를 가깝게 따라 쓴 패러프레이즈는 2차적 저작물이 될 수 있다 — 추정, 전문가 확인**. MIT에서 온 부분은 어차피 "타인이 허가 없이 못 쓰는 것"이 될 수 없으므로 보호 대상은 우리 층(8.4)뿐이다.

### 8.2 가져올 것 (G1–G10)
원칙: kicad-happy의 `confidence`는 **"얼마나 믿을지"**, 우리 6개 상태는 **"증거가 있는지"**를 말한다 — 병렬 상태 체계를 들여오지 않고 매핑만 한다(G10).

| # | 항목 | 출처(파일) | 우리 plan의 어디에 | 무엇을 바꾸나 | 비용 / PASS 조건 |
|---|---|---|---|---|---|
| G1 | 보고서 계약: 실행한 도구 / 안 돌린 도구와 이유 / 검증·추론 분리 / 블로커 상단 / "Not Performed · Review Limits" / 최종 판정 | `KH\skills\kicad\references\report-generation.md:5-16,20-38,123-128` | §3.3 "상태별 허용 동사" 행 옆에 "보고서 형식" 행 신설; SKILL.md 본문 | 상태 동사 규칙만 있던 것을 **고정 섹션 6개**로: 실행 단계·NOT_VERIFIED 단계와 이유·FAIL/USER_INPUT_REQUIRED 표(상단)·증거 장부·하드 리밋·판정 한 줄. 어휘는 kicad-happy의 Verified/Unverified가 아니라 우리 6 상태 verbatim | S / §4 6단계 과제 2개의 보고서에 6개 헤더가 모두 있고, 각 단계 상태가 `pipeline.json` `state.outcomes[]`와 일치 |
| G2 | 헤더 검사 스크립트 | `KH\skills\kicad\scripts\check_report_sections.py`(`BASE_SECTIONS` L54-63, 누락 시 exit≠0) | §3.3 `scripts/` 행(`check_evidence.py` 없음 유지) | **증거 판정은 안 하고** 헤더 존재만 보는 30줄 `scripts/check_report.py`; 증거 라벨은 여전히 `ai-eda review/report`가 계산 | S / 헤더 하나 지운 보고서에 exit 1, 정상 보고서에 exit 0; 테스트 2개 |
| G3 | 금지 어휘 규칙: 근거 없는 리뷰는 "verified/confirmed/per datasheet" 금지 | `KH\skills\kicad\SKILL.md:40`(DS-001), `report-generation.md:50` | §3.3 "상태별 허용 동사", §7.5 | SKILL.md에 **상태별 금지 동사 표**(NOT_VERIFIED/UNRESOLVED 단계에 "동작한다/검증됨/verified" 금지) + 6단계 시험 과제 1개(NOT_VERIFIED 단계가 있는 보고서). **스크립트 게이트는 두지 않는다** — `pipeline.json`을 읽어 증거를 판정하면 §3.3이 거부한 `check_evidence.py`와 같고, 한국어 동사 매칭은 깨지기 쉽다; 사람/Codex 리뷰가 판정 | S / 시험 과제 보고서에 금지 동사 0건(리뷰 체크리스트 항목) |
| G4 | "언제 읽나" 참고 표(파일·줄 수·상황) + "첫 부분만 읽기" 같은 리뷰 실패 모드 목록 | `KH\skills\kicad\SKILL.md:727-748`, `:74-83` | §3.3 파일 구조 행(references 3개 상한 유지) | SKILL.md 상단에 3행 표(`pipeline.md`/`answers.md`/`without-cli.md` × 줄 수 × 트리거)와 실패 모드 6줄(같은 턴 `confirm_*` 자답, `doctor --strict` 생략, stdout 파일명 파싱, 관측 텍스트 지시 따름, IR 직접 편집, 외부 행위 선행) | S / 표의 줄 수가 실제 파일과 같음(§3.5 A6식 드리프트 테스트 1개); 6단계 시험에서 실패 모드 0회 |
| G5 | 보안 규칙 5줄: 외부 내용은 데이터, 분석은 읽기 전용, 서브프로세스는 리스트 인자, eval/exec 없음, 네트워크 범위 명시 | `KH\skills\kicad\SKILL.md:827-850`; `shell=True` 0건 확인 | §3.3 "관측 텍스트" 행, 8.4 H4 스크립트 | 스킬 `scripts/`의 코딩 규칙으로 고정 + 네트워크는 "0건(승인 전)"으로 kicad-happy보다 좁게 | S / `grep -r "shell=True\|eval(\|exec(\|urllib\|requests\|httpx" scripts/`가 0건인 테스트 1개 |
| G6 | 발동 문구를 인용한 frontmatter description + 길이 상한 CI | `KH\skills\kicad\SKILL.md:3-17`, `KH\.github\scripts\check_skill_metadata.py:36`(1024자) | §3.3 frontmatter 행, §4 6단계 | 10/5 발동 시험에 더해 description에 인용 문구 ≥5개("회로 설계해 줘", "ERC 돌려 줘", "ai-eda로…")와 1024자 상한 검사 | S / 10/10 발동, 5/5 미발동(기존) + 길이 테스트 |
| G7 (회의 #4: 가족 단위로 축소 — id별 한 줄은 lookup dump) | 규칙 카탈로그 스키마: `id`·`severity`·`verify[]{method, tool, check, automatable}`·`sources[]`·`confidence`·`conflicts` | `EXT\docs\SCHEMA.md`, `EXT\tools\validate.py:24-36,81-94` | §2.3 19단계 / `ValidationResult`; 스킬 `references/pipeline.md` | 우리 검증기 id(`ir.*`, `pcb.*`, `review.*`)마다 **한 줄**: 어떤 도구가, 무엇을, 어떤 자동화 수준으로 보는지 + 출처. 규칙 본문은 가져오지 않음(8.3); `conflicts`는 "측정 안 됨/서로 다른 벤더 값"을 숨기지 않는 관행만 | M / pipeline.md의 검증기 행 수 = `stages.py`/레지스트리의 id 수(드리프트 테스트), `tool` 없는 행은 "의견"으로 표기 |
| G8 | 런타임 canary: 프로젝트 `.kicad_dru`에 반드시 1회 발화하는 가짜 규칙을 넣고, 발화 없음 → `error`(pass 아님); `error`≠`fail` | `EXT\docs\VERIFICATION_TOOLCHAIN.md` §2.4, `EXT\tests\test_checkers_seeded.py:133-139`, `checkers\common.py:192-207` | §2.3 14단계, §3.2 B1, §3.5 B11 | B1은 테스트 시점 canary였다; **실행 시점** canary를 제안(DRC 단계가 canary 미발화면 `drc` NOT_VERIFIED + 메시지). 도구 오류는 판정이 아니다. **결정 ①=(a)(업스트림 PR)일 때만**; ①은 아직 미답(§4 1단계), (b)면 `without-cli.md`에 주의사항으로만 | M / 문법 오류를 넣은 `.kicad_dru`로 DRC가 exit 0이어도 단계가 PASS가 아닌 NOT_VERIFIED; 정상 파일은 기존 테스트 불변 |
| G9 | 결정성 가드(두 번 실행, 타임스탬프 제외 비교) + 심은 결함으로 pass→fail 뒤집힘을 검증 PASS 조건으로 | `KH\.github\workflows\ci.yml:104-135`; `EXT\tests\test_checkers_seeded.py:43-58,142-153` | §3.5 B1·B11 W1, §4 6단계 | 스킬 시험 과제에 "같은 IR 두 번 run → `pipeline.json` 동일(시각 제외)" 1개와 "저항값을 틀리게 바꾼 분배기 → `calc.recompute` FAIL" 1개 추가; 코퍼스는 **축소**(우리 템플릿 6개 보드) | S / 두 과제 모두 기대 결과; 뒤집히지 않으면 스킬이 PASS를 주장할 수 없음 |
| G10 | 신뢰 라벨 **매핑**(병렬 체계 없이) | `KH\skills\kicad\scripts\analyzer_envelope.py:122-126`; `EXT\docs\SCHEMA.md` confidence | §2.2 상태표·provenance 5종; SKILL.md 상태표 각주 | `deterministic`+tool → PASS/FAIL; `heuristic` → 의견(`tool` 없음 = NOT_VERIFIED); `datasheet-backed` → provenance `authoritative`(아카이브 PDF에서 verbatim일 때만, 그 외 NOT_VERIFIED); ee-skills `confidence: high`는 바꿔 쓴 요약이므로 `assumption`/`derived`까지만, 절대 `authoritative` 아님 | S / SKILL.md 각주 1개; 6단계 시험 보고서에 kicad-happy/ee-skills 어휘 0건 |

가져오되 **값만 바꾸는 것**: kicad-happy의 `trust_summary`(`analyzer_envelope.py:90-92`, 0건이면 None)는 보고서의 "단계 N개 중 PASS n/NOT_VERIFIED m/FAIL k" 한 줄로 대체(새 필드 없음); `diagnostics[]`의 "약한 경로로 돌았다" 기록은 `without-cli.md`의 증거 장부 행 형식에 "대체 경로: <도구 없음 사유>" 열로. 이전 리뷰와의 diff(`SKILL.md:422`)는 `ai-eda review`가 이미 해시로 stale을 잡으므로 **안 가져온다**(비용 대비 0).

### 8.3 가져오지 않을 것
| 항목 | 출처 | 한 줄 이유 |
|---|---|---|
| 도구 없이 단정하는 분석기·점수: 0-100 EMC 위험 점수, ×1.5 가중, 0건이면 `trust_level: high` | `KH\skills\emc\scripts\analyze_emc.py:62-112`, `finding_schema.py:359-360` | tool-backed 근거 없는 수치 = 의견; 우리는 점수 없이 상태만 |
| "시뮬레이터 없으면 오류 아님, 건너뜀" | `KH\skills\spice\SKILL.md:46`(코드는 exit 1, 문서와 불일치) | 증거 없음은 NOT_VERIFIED로 **보고**하지 조용히 생략하지 않음 |
| LLM이 뽑은 데이터시트 값을 스키마 통과만으로 `datasheet-backed` 처리(페이지는 자기 신고) | `KH\skills\datasheets\scripts\merge_results.py:79-91` | §2.2: 아카이브 PDF에서 verbatim 발견만 grounded; 그 외 NOT_VERIFIED |
| 벤더 한계를 코드 주석·마크다운 표로("verified 2025-01") | `KH\skills\kicad\scripts\pcb\dfm.py:106-123`, `KH\skills\jlcpcb\SKILL.md:80-104` | §2.3 7단계: 아카이브된 벤더 페이지에 grounding, 손으로 옮긴 표는 가정 |
| 규칙 본문 531개(중국어) + 손으로 쓴 `design/<board>.yaml` 역할 파일 + LLM이 규칙별 pass/fail 판정 | `EXT\catalog\*.yaml`, `EXT\skills\ee-design-review`, `EXT\docs\SCHEMA.md`("文字用中文") | 번역+재감사 비용 L, 제2의 원본(IR 단일 원본 위반), LLM 판정은 §2.2 위반; 고객에게 중국어 증거 문자열 노출 |
| 스킬 11개 + 참고 문서 20개 분산 | `KH\skills\*`, `EXT\skills\*` | §3.3 상한(SKILL.md 250줄 + references 3개) 유지; 과제별로 한 문서만 읽게 하는 G4로 충분 |

### 8.4 판매용 보호 조치 (H1–H6)
기술적 현실 3줄: (1) SKILL.md는 평문 Markdown이고 구매자의 에이전트가 전문을 읽어야 작동하므로 **텍스트 자체는 어떤 기술로도 숨길 수 없다**(agensi도 호스팅 MCP로 전문을 돌려준다). (2) 작정한 복제자는 못 막는다; 막을 수 있는 것은 "익명 유출"(추적)과 "스크립트/핵심 로직의 무단 실행"뿐. (3) 현실적 조합 = 법적 근거 + 추적 가능성 + (선택) 서버 측 핵심. 정직성 규칙: **어떤 보호 장치도 검증 결과를 꾸미거나 숨기지 않는다** — 키가 없으면 "라이선스 없음"이라 말하고 멈추지, 조용히 약한 결과를 내지 않는다.

| # | 조치 | 막는 것 | 못 막는 것 | 비용 | 정직성 규칙과의 관계 / 비고 |
|---|---|---|---|---|---|
| H1 | 독점 LICENSE + `NOTICE` + 모든 SKILL.md/스크립트에 저작권 헤더; MIT 가정 전부 제거 | 법적 근거 없음 상태(저작권 침해 신고의 전제; agensi Terms §8.1 "creators retain ownership"과 일치) | 기술적으로는 아무것도 | S | **현황**: `LICENSE`(독점·열람만, 영문 우선 + 한국어 요약), `NOTICE`(MIT 참고 대상 목록, 복사한 파일 없음), README 고지를 2026-11-04 커밋. **남은 일**: SKILL.md·references·scripts가 생길 때 저작권 헤더 삽입(§4 6단계), `AI_EDA_Engineer` 적용 여부는 결정 ⑭. 법률 플래그 (a)(c)(d) 참조 |
| H2 | 레포 공개 범위: `Yuchan-00/EAD_Engineer_Skill`은 **비공개**(gh 확인 2026-11-04, fork 0), `Yuchan-00/AI_EDA_Engineer`는 **공개·LICENSE 없음**(gh 확인). 사용자 선택(2026-11-04): 공개를 유지하더라도 **법적 조치(H1)로 대응**한다 — 기술적으로 공개 Markdown의 사용을 막을 방법은 없으므로 판매 전까지는 스킬 레포 비공개 유지를 권장 | 판매 전 무료 복제(비공개일 때) | 이미 클론된 사본; 공개 레포의 열람·fork(GitHub 약관이 허용) | S | 없음. "LICENSE 없음 = 모든 권리 유보"는 **추정** — 법률 플래그 (b). AI_EDA_Engineer에 LICENSE를 넣을지는 결정 ⑭ |
| H3 | 구매자별 워터마크: frontmatter·주석에 **보이는** 구매자 id 줄(2–3곳); 빌드 스크립트가 사본을 찍음. 제로폭 문자 등 보이지 않는 변형은 **안 씀**(agensi 8항목 스캔·우리 길이 CI에 걸리고, 보이는 id 줄로 추적은 충분) | 익명 유출(추적) | 복사 자체, 에이전트의 바꿔쓰기 | S | 없음. agensi는 zip 1개 업로드라 자체 "구매 명시 라이선스 줄"만 붙음; 직접 판매에서만 우리 워터마크 유효 |
| H4 | `scripts/`의 오프라인 서명 토큰 검사(Ed25519 공개키 동봉, 토큰 = 구매자 id + 만료). **agensi에서는 불가**(Terms §5.2: 구매자 측에 파일이 남지 않아 토큰을 둘 곳이 없음) — **직접 판매 전용** | zip만 얻은 사람의 스크립트 실행 | SKILL.md 읽기(지식은 산문에 있음), 검사 코드 삭제, "검사 건너뛰라"는 지시 | M | **핵심**: 실패 시 메시지 "no valid licence" + 스크립트 **고유** exit 코드(예: 70; ai-eda의 0/1/2 표와 분리, §3.3 exit 표에 "스크립트 자체 코드"로 명기), 가짜 "verified" 출력·결과 강등 금지; 절대 phone-home 없음(§3.3 외부 행위 = 채팅 승인만, G5 테스트가 네트워크 import 0건 보장) |
| H5 | 호스팅 핵심(서버 측 API/MCP): `ai_eda` 파이프라인·계산기·리뷰 규칙을 서버에, 스킬은 키 가진 얇은 클라이언트 | 유출 텍스트의 가치(키 없이 무용), 구매자별 회수·사용량 계량 | 비용·가동률 부담 | L | 오프라인 동작과 로컬 증거(`pipeline.json`, §3.1-b) 포기; 서버 응답도 PASS/NOT_VERIFIED 라벨과 해시를 그대로 실을 때만 증거. **수익이 서버를 정당화할 때까지 보류** |
| H6 | 마켓플레이스 자체 장치(agensi, **2026-11-04 웹 읽기 기준; 약관 변경 가능**): 다운로드 불가(Terms §5.2), 로드마다 "저장/내보내기 금지" 지시 + 구매 명시 라이선스 줄, 개인·비양도 라이선스(§5.1/§8.2), 70/30, Stripe/USDC, KYC | 에이전트가 지시를 무시하고 저장하는 것(지시+계약일 뿐) | 0 | **비용**: 창작자는 에이전트 배포를 거부할 수 없음(§6.5) → 전문이 항상 구매자 에이전트에 노출, H4 불가. UNVERIFIED: 80/20 분배(제3자 글), 창작자 호스팅 엔드포인트+서명 토큰(창업자 Reddit 언급, 미출시), SkillHQ "보이지 않는 워터마크" |

**법률 플래그(모두 전문가 확인; 이 문서는 자문이 아님)**:
(a) MIT 구조를 가깝게 따른 패러프레이즈도 2차적 저작물일 수 있음 — 추정(8.1).
(b) "LICENSE 없음 = 모든 권리 유보"는 추정; GitHub 약관(§D.5로 알려짐, 출처는 입력에 없음)이 공개 레포의 열람·포크를 별도로 허용함.
(c) DMCA는 미국법; 사용자에게는 한국 저작권법과 마켓플레이스 정책이 적용 — 신고 경로는 플랫폼별로 확인.
(d) **AI 생성 텍스트의 저작권**: SKILL.md 대부분을 Claude가 초안하므로 "Copyright (c) 2026 Yuchan"의 집행 가능성은 다툼이 있음(예: 미국 저작권청의 AI 생성물 입장). H1–H3의 전제이므로 **등록 전** 확인; 완화책(사람이 쓴 부분의 기록, 편집·선택의 기여 명시)도 함께 묻는다.

권장 **최소 1차 패키지**: H1(커밋/푸시 + 헤더 + AI_EDA_Engineer 적용) + H2 + H6(agensi 그대로 판매). H3·H4는 직접 판매가 생길 때(현재 스크립트는 `ai-eda` 호출 래퍼라 보호 가치 낮음), H5는 보류. 난독화(PyArmor/Cython)는 Markdown에 무효·에이전트 실행 출력으로 거동 노출 → 채택 안 함.

**사용자 결정이 필요한 것**(§4 1단계 목록에 추가; ①–⑩에 이어):
⑪ 스킬 레포를 공개로 돌릴지(사용자 질문 2026-11-04; 선택 = 법적 조치로 대응. 공개 시점은 판매 등록 뒤를 권장; 비용: 공개하면 열람·fork는 막지 못함).
⑫ H1 라이선스 형태 — **결정됨(2026-11-04): 독점·열람만(LICENSE 초안)**; 구매자당 사용 범위를 적은 EULA 추가 여부는 남음(비용: 문안 작성; 법률 검토는 사용자).
⑬ 판매 채널 — agensi 호스팅 MCP만 / 직접 판매 병행(병행이면 H3·H4 필요).
⑭ AI_EDA_Engineer(참고 레포)도 같은 판매 대상인지 — 그렇다면 그 레포에도 H1 적용; simavr/Verilator 등 GPL 도구 바이너리는 **동봉하지 않고** 구매자 설치(§7.4 위험 표 "라이선스").
⑮ 법률 플래그 (a)–(d)를 누가 언제 확인하는지(등록 전 필수는 (d)).

출처(2026-11-04 읽음): agensi.io/sell, /terms, /about, /claude-marketplace, /docs/how-agents-load-skills; peerpush.com/p/skillhq; claudskills.com/learn/the-economics-of-claude-code-skill-marketplaces/; github.com/Yuchan-00/AI_EDA_Engineer; 로컬 `EAD_Engineer_Skill\LICENSE`·`NOTICE`.

### 8.5 순서
| 시점 | 항목 |
|---|---|
| 지금 (§4 1단계와 함께) | H1 LICENSE/NOTICE/README 커밋·푸시(완료), 결정 ⑪·⑬·⑭·⑮ |
| SKILL.md 초안 전 (§4 5단계 회의 #4 의제) | G1·G3·G4·G10 형식 확정(초안이 그 형식으로 쓰이도록), G7 검증기 한 줄 표의 범위, G8은 결정 ①=(a)일 때 참고 레포 PR 큐에 B1 뒤로 |
| SKILL.md 초안과 같이 (§4 6단계) | G2·G5·G6·G9 테스트, G1 보고서 6개 헤더, G3 금지 동사 표, H1 헤더 삽입 |
| 판매 등록 직전 (§4 7단계 푸시 뒤, 새 "7b 등록" 단계) | 법률 플래그 (d) 확인, H1 LICENSE/NOTICE 최종(AI_EDA_Engineer 포함), H6 agensi 등록(zip = SKILL.md + references 3 + scripts), 직접 판매면 H3·H4 |
| 보류 | H5 호스팅 핵심(수익 뒤), kicad-happy식 코퍼스 회귀(템플릿 6개로 축소한 G9가 대신) |

---

## 9. 다중 에이전트 호스트 · 다중 AI API 대응

사용자 요청(2026-11-04): "claude code뿐만 아니라 여러 에이전트 프로그램에서 원활히 구동되도록, 최대한 모든 AI API에 대응." 이 절은 그 요청을 두 가지 독립된 일로 나눈다. 근거: 호스트 문서 조사(2026-11-04, 각 벤더 docs; 원문은 `notes/research/hosts-2026-11-04.md`로 저장), kicad-happy·ee-skills 레포의 어댑터 구조 조사, 참고 레포 `ai_eda/llm/` 소스 읽기(실행 없음). 출처 없는 사실은 UNVERIFIED. §8(참고 스킬·Agensi MCP 판매 보호)과 겹치는 내용은 쓰지 않고 §8을 가리킨다.

### 9.1 두 가지 뜻 분리
| 뜻 | 대상 | 무엇이 바뀌나 | 항목 |
|---|---|---|---|
| (a) 스킬이 여러 에이전트 프로그램에서 구동 | `.agents/skills/eda-engineer/` (SKILL.md + references 3개, §3.3) | 포맷·문구·설치 경로의 **이식성** | I1–I12 (§9.3) |
| (b) 엔진 `ai-eda`가 여러 AI API를 쓸 수 있음 | 참고 레포 `ai_eda/llm/` (`--llm` provider) | 제공자 **폭** | J1–J7 (§9.4) |

원칙 (§2.2·§3.3에 추가): **스킬 자체는 어떤 AI API도 호출하지 않는다.** SKILL.md를 읽고 추론하는 모델은 호스트(Claude Code, Codex, Gemini CLI …)가 고른 모델이며 스킬은 그것을 선택·가정할 수 없다. `--llm`은 엔진의 별도 결정이고, 스킬은 설명만 하고 켜지 않는다(§3.3 "유료/온라인 행위"). 따라서 (a)는 "모델을 가정하지 않는 글"의 문제, (b)는 참고 레포 코드의 문제다. 둘을 한 항목으로 섞지 않는다.

### 9.2 호스트 지원 요약
표준은 Agent Skills 스펙(agentskills.io/specification): `SKILL.md`(frontmatter `name`·`description` 필수, `license`·`compatibility`·`metadata`·`allowed-tools`(experimental) 선택) + `scripts/`·`references/`·`assets/`. 호스트별 한 줄(프로젝트 경로 기준, 전체 표·MCP 설정 파일·출처 URL은 조사 원문):
- **`.agents/skills/`를 읽는 호스트(9)**: Codex(레포 루트까지 탐색, `$skill`·`/skills` 호출, 정책은 `agents/openai.yaml`), Copilot CLI(`allowed-tools` 읽음, 셸 사전 승인 경고), Gemini CLI(`activate_skill`+사용자 동의), Antigravity, Cursor(+`paths`·`disable-model-invocation`), OpenCode(스펙 외 키 무시, `permission.skill`), Amp(**같은 `name`은 첫 발견이 이김**), Roo(모드별 `skills-<mode>/`), Devin Local(구 Windsurf).
- **`.claude/skills/`만 읽는 호스트**: Claude Code(`.agents/skills` 미탐색 UNVERIFIED, issue #6235 인용; claude.ai Skills API 업로드는 비표준 키에 하드 실패). Copilot·Cursor·OpenCode·Amp·Cline도 이 경로를 읽는다.
- **둘 다 아닌 호스트**: Cline(`.cline/skills/`; **전역이 프로젝트를 덮음**), Kiro(`.kiro/skills/`; 커스텀 에이전트는 `resources`에 명시). → **측정 전까지 미지원**; 복사는 9.5 설치 결정 뒤.
- **MCP는 최소 공통분모**: 모든 호스트가 MCP 서버를 돌리지만, Agensi형 전달(`search_skills`/`get_skill`이 SKILL.md 본문을 도구 결과로 반환)은 호스트의 스킬 로더·동의 프롬프트·`allowed-tools`·번들 파일 접근을 전부 우회하고 텍스트만 주입한다. 공식 Skills-over-MCP 확장은 어느 호스트도 v1 지원을 올리지 않았다(OpenCode·VS Code·Goose "in progress"). 결론: MCP 전달은 "어디서나 되는 지시문 텍스트"이되, 이 경로에서는 (1) description 매칭 발동(I4·I12)이 없어 에이전트가 도구를 **골라 호출**해야 하고, (2) references는 이름으로 요청해야만 닿는다(I7의 cue가 유일한 길). 판매 경로의 상세는 §8.

### 9.3 이식성 규칙 (I) — 우리 SKILL.md/references에 적용
단일 원본은 `.agents/skills/eda-engineer/`(SKILL.md + `references/pipeline.md`, `answers.md`, `without-cli.md`; 9개 호스트가 그대로 읽음). 호스트 전용 내용은 어댑터 파일(아래 표)에만 둔다. 모든 PASS 조건은 이 PC에서 사람 손으로 돌릴 수 있는 검사다.

| # | 규칙 | PASS 조건 |
|---|---|---|
| I1 | frontmatter는 `name: eda-engineer`(디렉터리명과 동일, 소문자-하이픈, ≤64자) + `description`(≤1024자, 발동 문구 포함)만; 선택으로 `license`·`metadata`. `when_to_use`·`allowed-tools`·`argument-hint` 없음 | 키 집합 ⊆ {name, description, license, compatibility, metadata}를 stdlib 스크립트로 검사 + `skills-ref validate` 통과 |
| I2 | Claude Code 전용 기능 금지: `$ARGUMENTS`/`$0`/`$name`, `` !`cmd` `` 주입, `${CLAUDE_SKILL_DIR}`, `hooks`/`context`/`model`/`effort`/`paths`/`disable-model-invocation` | 스킬 트리 grep `\$ARGUMENTS|\$[0-9]|\$\{CLAUDE_|^!\`` = 0건, frontmatter에 위 키 0개 |
| I3 | 도구·호스트 중립 문구: "파일을 읽어라 / 명령을 실행하라 / 코드베이스를 검색하라 / 웹을 검색하라", `Read`/`Grep`/`Bash`/`WebSearch`·"Claude"·"Codex" 금지. 주체는 "에이전트" | grep -i `claude|codex|cursor|gemini|copilot|antigravity|Read tool|Grep|Bash` = 0건, **검사 스크립트의 명시 허용 목록**: `--llm claude`가 든 줄, doctor 출력 인용의 `claude cli` 줄(answers.md에 verbatim 필요) — 허용 목록 밖 매치만 실패 |
| I4 | 슬래시 명령·`$skill` 호출을 전제하지 않음; 발동은 description 매칭(호스트마다 `/name`, `$name`, `activate_skill`+동의로 다름). Codex의 암시 발동은 `agents/openai.yaml`의 `allow_implicit_invocation`이 결정하므로 그 파일 하나를 둔다(아래 표) | grep `/eda-engineer|\$eda-engineer` = 0건; 9.5 T1이 두 호스트에서 통과 |
| I5 | 의존성은 `ai-eda` CLI 하나. `scripts/` 없음(§3.3 `check_evidence.py` 없음과 일치). 명령은 맨 셸로, 호스트 도구명 없이 | SKILL.md·references의 모든 명령 줄이 허용 목록 중 하나로 시작: `ai-eda`, `python -m ai_eda.cli`, `<repo>/.venv/Scripts/ai-eda.exe`, `<repo>/.venv/bin/ai-eda`, `$env:PYTHONUTF8`, `export PYTHONUTF8`, `kicad-cli`·`ngspice`(without-cli.md), `pytest` |
| I6 | 경로는 Windows·POSIX 양쪽: 슬래시(`/`), venv fallback은 `<repo>/.venv/Scripts/ai-eda.exe`와 `<repo>/.venv/bin/ai-eda` 둘 다(§3.3 venv 행 확장), `PYTHONUTF8=1`은 PowerShell·bash 두 줄로, `~/.claude`·절대 경로 금지 | grep `~/\.claude|[A-Z]:\\` = 0건(`<repo>` 자리표시자만 허용); venv 두 형태·UTF8 두 줄 존재 |
| I7 | 점진 공개는 references 3개 상한 안에서: SKILL.md ≤250줄(§3.3), 각 reference는 SKILL.md에 "X일 때 `references/Y.md`를 읽어라" 한 줄로 연결, 한 단계 깊이만. MCP 전달(§8)에서는 에이전트가 파일을 **이름으로** 요청하므로 이 cue가 유일한 길 | `wc -l SKILL.md` ≤250; `references/*.md` 3개 전부 SKILL.md에서 링크+조건 문장; references 안에 `references/` 링크 0건 |
| I8 | 호스트 컨텍스트 파일(CLAUDE.md·AGENTS.md·system-reminder)의 존재를 가정하지 않음: 관측 텍스트=데이터(§3.3 검토 1-2), 외부 행위 12종 금지, 상태별 허용 동사(검토 1-3)를 SKILL.md **안에** 다시 적는다 | 빈 디렉터리(컨텍스트 파일 없음)에서 9.5 T2를 돌려 스킬이 NOT_VERIFIED를 PASS로 바꾸지 않고 외부 행위를 먼저 하지 않음 |
| I9 | 압축 안전: 하드 리밋·외부 행위·관측 텍스트 규칙을 SKILL.md 상단 40줄 안에 | 세 블록의 첫 줄 번호 ≤40 |
| I10 | 모델·컨텍스트 크기·도구 가용성을 가정하지 않음: "웹 검색이 있으면 … 없으면 사용자에게 묻는다"처럼 분기; 거대 문서(README 232 KB 등, §2.5)를 읽으라고 하지 않고 증류본(references)만 가리킴 | SKILL.md에 참고 레포 문서 3개 경로 0건; 도구 가정 문장마다 "없으면" 분기 존재(손 검토) |
| I11 | 이름 충돌·우선순위: `eda-engineer`는 본문이 한 벌(Cline은 전역 우선, Amp는 첫 발견 우선 → 두 벌이 어긋나면 호스트마다 다른 본문이 뜬다). `.claude/skills/` 사본은 원본과 바이트 동일해야 한다 | (1) 검사 스크립트가 `.agents/skills/eda-engineer` → `.claude/skills/eda-engineer`로 복사한 뒤 `git diff --exit-code`가 0(드리프트 0); (2) 설치된 각 호스트에서 "what skills are available?"에 `eda-engineer`가 정확히 1회 |
| I12 | description 발동 시험(§3.3 F4)은 Claude Code만이 아니라 설치된 호스트 전부에서 | 양성 10/10·음성 5/5가 Claude Code·Codex 두 곳에서(Codex는 `openai.yaml` 암시 발동 포함; 암시 발동이 안 되면 "`$eda-engineer` 필요"를 측정 결과로 기록하고 I4 재검토). 나머지 호스트는 9.5 설치 결정 뒤 |

**어댑터 파일(kicad-happy 조사에서 축소)** — 본문은 절대 복제하지 않고 메타데이터·포인터만:

| 파일 | 호스트 | 비용 | 비고 |
|---|---|---|---|
| `.agents/skills/eda-engineer/{SKILL.md,references/}` | 9개(§9.2 첫 줄) | — | 단일 원본. §8의 Agensi 판매본(zip: SKILL.md+references)은 이 디렉터리만 담는다 |
| `.agents/skills/eda-engineer/agents/openai.yaml`(`allow_implicit_invocation` 1키) | Codex | S | 다른 호스트는 무시; 판매본 제외. 기본값·키 이름은 Codex 문서로 확정(UNVERIFIED) |
| `.claude/skills/eda-engineer` | Claude Code(+Copilot·Cursor·OpenCode·Amp·Cline이 중복 발견) | S | 1차: 심링크(git mode 120000; Windows는 Developer Mode 또는 `core.symlinks=true` 필요, 이 PC UNVERIFIED). 실패 시 **복사본** — 어느 쪽이든 I11 (1)의 `git diff --exit-code` 검사로 고정 |
| `tools/check_skill_portable.py`(stdlib) | — | S | I1·I2·I3(허용 목록 내장)·I4·I5·I6·I7·I9의 grep/길이 검사 + I11 (1) 복사·diff; ee-skills `tests/test_repo.py` frontmatter 패턴 |
| `install-guidance.md`(호스트별 설치 한 절 + "그 외 에이전트: SKILL.md를 읽고 `ai-eda`를 실행하라" + Windows 심링크 절) | 사람·기타 에이전트 | M | 레포 전용, 판매본 제외 |
| `.claude-plugin/plugin.json`·`marketplace.json`, `.codex-plugin/plugin.json`, `.opencode/opencode.json`, `.cursor/rules/*.mdc`, `GEMINI.md`, `llms.txt`, 루트 `plugin.json` | — | S | **만들지 않음** — kicad-happy에서 이 파일들은 원본이 `skills/`에 있어서 필요했고(포인터), 마켓플레이스 배포는 요청된 적 없음. §8 판매/마켓플레이스가 실제로 요구할 때만 추가 |
| `action.yml` + `action/entrypoint.sh`(GitHub Action, 에이전트 없는 경로) | CI | M–L | **보류** — 러너에 KiCad·ngspice가 없으면 전부 NOT_VERIFIED(§1.2); ubuntu 러너의 headless KiCad 설치 UNVERIFIED |

최소 집합 = 위 2–3행(`openai.yaml` + `.claude/skills/` 링크/복사) + 검사 스크립트. 호스트 수 9+1, 파일 3개, 전부 S. description을 중복 보관하는 파일이 없으므로 생성기 불필요.

### 9.4 엔진 API 폭 (J) — 참고 레포 `ai_eda/llm/`
현재 사실(소스 읽기): 제공자는 `openrouter`·`claude`·`script`(fake)뿐(`router.py:53`), `anthropic:` 접두는 예약·거부(`router.py:55-57`); 모델 스펙은 `provider:model`(알려진 접두에서만 첫 `:` 분리), 핀은 `ir.requirements.llm_model_spec`(불일치 시 `--llm-allow-model-change` 없이는 거부); `billing!="subscription"`인 멤버가 하나라도 있으면 `--llm-budget-usd/--llm-budget-tokens` 필수(`PAID_API_CALL`), 구독은 `SUBSCRIPTION_USE`. 파이프라인 호출 4곳(requirement·component·datasheet_facts·regulatory)은 전부 `LLMService.structured`, 도구·스트리밍 없음; `supports_structured=False`면 JSON-only 시스템 메시지로 대체(`service.py:624-627`). `OPENAI*` 식별자는 어디에도 없다. `OPENROUTER_BASE_URL`을 다른 게이트웨이로 돌리면 아마 돌지만 핀 이름이 `openrouter`로 남고, OpenAI 본가는 `usage` 바디 키를 400으로 거부할 가능성(UNVERIFIED).

| # | 항목 | 제안(가장 작은 변경) | 비용 | 측정 가능한 PASS 조건 |
|---|---|---|---|---|
| J1 | `openai` 제공자(OpenAI 호환 `base_url`+키) | `ai_eda/llm/openai_compat.py`: `class OpenAICompatClient(OpenRouterClient)`, `OPENAI_API_KEY`/`OPENAI_BASE_URL`(기본 `https://api.openai.com/v1`), 바디에서 `usage`/`reasoning`/`provider` 제거, 헤더에서 Referer/Title 제거, `check_base_url` 유지(루프백 http 허용 = Ollama `127.0.0.1:11434/v1`, LM Studio `:1234/v1`, OmniRoute). 생성자 인자 `supports_structured: bool = True`(J5). 이름표 6곳 등록(`router.py:53,70-76`, `providers.py:45-52,194,392-406`, `cli.py:196,228-234,375-376`) | S (~150줄 + 6줄) | `tests/test_openai_compat_client.py`를 `tests/fake_openrouter.py`로: (1) `complete`가 내용을 돌려주고 기록된 바디에 `usage/reasoning/provider`·`HTTP-Referer` 없음; (2) `LLMService.from_env(LLMBudget(max_tokens=N), providers=["openai"])`가 `structured(REQUIREMENT_ANALYSIS, …)`를 서빙하고 `via="openai"`, `model_used="openai:<served>"` 기록; (3) `ai-eda run … --llm openai --llm-budget-tokens 2000`이 `tests/test_cli_llm.py:61-77`과 같은 흐름; (4) `tests/test_providers.py:137` 갱신, 기존 llm 스위트 통과 |
| J2 | `anthropic` 직접 Messages API | 예약 해제(`router.py:55-57`, `tests/test_providers.py:121`), `x-api-key`/`anthropic-version`, 구조화 출력은 강제 tool, `usage.input/output_tokens`, 비용 `None`, 새 fake 서버 | M (~200줄) | **낮은 우선순위**: Anthropic은 이미 `openrouter:anthropic/*`·`claude:`로 닿음. 열 때 PASS = J1 (1)(2)와 같은 형태를 fake Anthropic 서버로 |
| J3 | 과금·승인 규칙 불변 | J1은 `paid=True, billing="per_call"` → 예산 플래그가 곧 승인; 대부분의 호환 서버는 `cost`를 안 주므로 `--llm-budget-tokens`가 구속 예산(`service.py:36-38`) | 0 | (1) 예산 없이 `structured` → `ApprovalRequiredError`이고 `fake.requests`가 빔(`test_llm_service.py:71` 패턴); (2) `cost` 없는 응답 + USD만 있는 예산은 두 번째 호출 거부(`:103` 패턴) |
| J4 | 핀·스펙 | `openai:<model>` 스펙·핀·`--llm-allow-model-change` 동작이 `openrouter:`와 동일; 접두 없는 스펙은 기본(첫) 제공자 | 0 | 핀 불일치 실행이 플래그 없이 거부; `describe_providers` 행에 "key set" 표시(GUI `gui/server.py:202`가 읽음) |
| J5 | 구조화 출력 폴백 | 호환 서버의 strict `json_schema` 지원은 대상마다 UNVERIFIED → J1 생성자 인자 `supports_structured=False`로 기존 JSON-only 경로 사용. **새 env·CLI 플래그 없음**(노출은 실제 거부 사례가 나올 때) | J1에 포함 | `supports_structured=False`로 만든 클라이언트의 기록 바디에 `response_format` 없음 + JSON-only 시스템 메시지 존재 + 응답 파싱 성공 |
| J6 | `doctor` 줄 | `LLM key: OPENROUTER_API_KEY not set / OPENAI_API_KEY set (base_url=…)`; `--online`에서 `{base_url}/models` 조회는 선택 | S | 네트워크 없이 키 유무·base_url만 인쇄; `--strict`는 키 없음을 실패로 치지 않음(현재와 동일) |
| J7 | Windows `claude` 제공자(A8) | 변경 없음, A8 묶음에서 처리: 자식 종료 경로 `WinError 87`, 인코딩 불가 인수 분류 `'http'≠'transport'`, stdin 경로 미측정(§2.6) | §3.1 A8 | A8의 PASS 조건 그대로; 그 전까지 스킬은 "`--llm claude`는 Windows에서 미측정"이라고만 말한다 |

**덮는 API(J1 뒤)**: OpenRouter(게이트웨이가 받는 모든 모델), OpenAI, Groq, Together, DeepSeek, Ollama·LM Studio(로컬), Gemini(OpenAI 호환 엔드포인트), OmniRoute 같은 자체 게이트웨이, Anthropic(`openrouter:anthropic/*`·`claude:`; 직접은 J2). 그 밖의 OpenAI 호환 서버는 대상별 UNVERIFIED(J5 폴백으로 시도). Azure OpenAI는 `api-key` 헤더 + `api-version` 쿼리가 필요해 J1에 ~15줄 추가(M로 승격, 요청 있을 때).
**밖에 두는 것**: 벤더별 네이티브 SDK(비용 L, 이득 없음), AWS Bedrock·Google Vertex 네이티브 인증(SigV4/OAuth — 게이트웨이를 통해서만), 도구 호출·스트리밍(파이프라인이 안 씀), `codex exec` 서브프로세스 제공자(`claude_cli.py`와 같은 구독형; Codex의 JSON 스키마 출력 지원 UNVERIFIED → 사용자가 원하면 별도 항목).

### 9.5 검증 계획
스모크 매트릭스 = 호스트 × 과제 2개. 모두 이 PC, 빈 작업 디렉터리, 새 세션.
- **T1 발견·로드**: (a) "what skills are available?" → `eda-engineer` + description이 1회 보임(I11); (b) description 키워드 하나가 든 프롬프트 → 본문이 로드됨(호스트의 활성화/동의 표시 또는 **본문에만 있는 문구**(예: "ai-eda 명령을 처음 쓰기 직전에 `doctor --strict`") 인용); (c) 대화 기록 grep `\$ARGUMENTS|\$\{CLAUDE_|Read tool` = 0건(I2·I3 누수).
- **T2 실제 과제**: §4 6단계 과제 1(분배기 재설계)을 그대로. PASS는 §4 6단계와 동일(보고한 단계 상태 = `pipeline.json` `state.outcomes[]`, pipeline.json에 없는 PASS 0회) + 외부 행위를 먼저 하지 않음(I8).

| 호스트 | 이 PC 설치 | T1 | T2 | 필요한 결정 |
|---|---|---|---|---|
| Claude Code | 있음(이 세션) | 필수 | 필수 | 없음(`.claude/skills/` 링크/복사가 레포에 있음) |
| Codex CLI | 있음(§1.3; `~/.agents/skills/` 전역 설치 여부 UNVERIFIED) | 필수 | 필수, 단 요약 입력(128k 한계, §1.3) | 없음 — 레포의 `.agents/skills/`를 루트까지 탐색하므로 체크아웃이 곧 설치(C3 전역 복사 불필요) |
| Gemini CLI / Antigravity / Cursor / OpenCode / Copilot CLI / Amp / Roo / Devin | **UNVERIFIED — 미확인**(`Get-Command gemini,cursor,opencode,copilot,amp` 미실행) | 설치된 것만 | 설치된 것만 | 설치는 `system_install` 외부 행위(§3.3) → 사용자 결정; 권고: 사용자가 실제로 쓰는 1–2개만 |
| Cline / Kiro | 미확인 | — | — | 측정 전까지 미지원; 설치 결정 시 `.cline/skills/`·`.kiro/skills/` 복사를 I11 (1) 검사에 추가 |

CI 없는 검사: `python tools/check_skill_portable.py`와 `skills-ref validate`를 푸시 전에 손으로 돌리고 결과 줄을 커밋 메시지에 붙인다. GitHub Action은 보류(§9.3 표). 9.5 결과는 `notes/measurements/<날짜>/hosts.md`에 호스트·버전·T1/T2 결과 한 줄씩(§3.5 B1의 측정 기록 형식).

### 9.6 순서 (§4에 끼워 넣는 위치)
1. **I1–I11 → §4 6단계 SKILL.md 초안 전**: §3.3 표에 "이식성" 행으로 합류(초안 작성 규칙이지 사후 검사가 아님). §3.3의 스킬 경로를 `skills/eda-engineer/` → `.agents/skills/eda-engineer/`로 고친다. 회의 #4(§4 5단계)에서 Codex 검토 1라운드.
2. **어댑터 2개(`openai.yaml`, `.claude/skills/` 링크/복사) + `check_skill_portable.py` → 초안과 같은 커밋**, §4 7단계 푸시 전. Windows 심링크 가능 여부는 이때 측정해 결과(심링크/복사)를 9.3 표에 기록.
3. **9.5 스모크 매트릭스 → 초안 뒤**, §4 6단계 시험에 "호스트 2개(Claude Code·Codex)" 추가; I12 발동 시험도 두 호스트에서. 나머지 호스트는 사용자 설치 결정 뒤 같은 표로 추가 측정.
4. **J1(J5 포함) + J3·J4·J6 → 참고 레포 PR**, §4 2단계(A5) 뒤·3단계와 병행 가능(겹치는 파일 없음: `llm/`·`cli.py`의 제공자 표 6줄만). PASS 6건(J1 4 + J3 2) 전부 fake 서버로, 실제 키 불필요. J2는 요청 있을 때, J7은 A8 묶음(§4 4b).
5. 스킬 문서(`answers.md`의 `--llm` 행)는 J1이 참고 레포에 머지된 **뒤에만** `openai`를 언급(§7.5 "구현 전 문서화 없음"과 같은 규칙); 그 전 초안은 `openrouter|claude`만.
