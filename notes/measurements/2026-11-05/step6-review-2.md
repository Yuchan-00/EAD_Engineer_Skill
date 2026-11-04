# §4 6단계: 초안 2차 리뷰 (Codex gpt-6-luna + 코드 대조 워크플로) 와 반영 (2026-11-05 새벽)

- 날짜·머신: 2026-11-05 04:35–05:00, robotics-lab
- 대상: `.agents/skills/eda-engineer/` 11250a2(SKILL.md 157줄, pipeline.md 105, answers.md 76, without-cli.md 61) vs 참고 레포 `work/ead-skill` 03bd642
- 리뷰 1: Codex `exec -s read-only -C AI_EDA_Engineer -m gpt-6-luna`(ChatGPT 계정), 프롬프트는 WRONG/MISSING/UNSAFE/결정성 문구/VERDICT 요청 + G9 실측 제공. 원본 `scratchpad/review2/codex-review-2.md`.
- 리뷰 2: Claude 워크플로 `skill-draft-factcheck`(78 에이전트, 19분, 634만 토큰): 파일별 주장 추출(25–70개) → 8개씩 코드 대조(TRUE/WRONG/IMPRECISE/UNCHECKABLE) → WRONG·IMPRECISE마다 반박 에이전트(holds=true면 채택) → 누락 탐색. 원본 `scratchpad/review2/workflow-factcheck.md`.
- 결과 한 줄: 249개 주장 중 TRUE 209, IMPRECISE 36, WRONG 4; 반박을 견딘 것 34(기각 6) + 누락 17 → SKILL.md 181줄, pipeline.md 118, answers.md 92, without-cli.md 68로 수정, 검사기 OK, `.claude/skills` 사본 동기화. Codex VERDICT "needs the listed fixes" → 5건 중 3건 반영, 2건 기각(코드가 Codex 주장을 반박).
- 뒷받침하는 plan 행: §4 6단계(Codex review → 수정), §3.3, G4(줄 수 표)

## 반영한 것 (코드 근거가 확인된 것만)

SKILL.md
- 하드 리밋 1: "다른 요청은 전부 `no template matches…`로 거부" → 템플릿 자체의 거부(범위 밖, 미제공 요구 `leave_out`, `ambiguous`)도 명시(`agents/circuit.py:141-149`, `design/templates.py:1684`).
- 하드 리밋 2(**WRONG**): "제외 부품을 지나는 요구는 전부 NOT_VERIFIED" → 이상 자극이 대신 서면 PASS이며 `verified with <ref> excluded: <reason>`가 붙는다(`review/reviewer.py:669-718`, `tests/test_circuit_templates.py:592-600`). FPGA는 코드에 없어 삭제. 제외는 컴파일러 규칙이 아니라 템플릿의 `SpiceBinding(exclude=True)`; 바인딩 없는 부품은 CompileError.
- 하드 리밋 3: "RELEASE stays NOT_VERIFIED" → RELEASE는 최신 결과의 최악 상태라 FAIL일 수도 있다; "never `evidence-backed release`"로(`orchestrator.py:648-660`). 오프라인에도 이전 `--online` 실행의 아카이브는 읽는다(`regulatory/research.py:171-183`).
- Never do first: 승인은 `--online`·`--llm claude`·예산 플래그뿐, billed answer는 승인이 아니라 예산 소비(`llm/service.py:220-231`, `security/approval.py`); "다른 도구(셸·브라우저·패키지 매니저)로도 12종을 하지 않는다" 추가.
- happy path 2: `kicad tables: MISSING` 줄이 `run ai-eda setup-kicad`로 끝날 때만 setup-kicad 제안; `(no KiCad settings folder: …)`는 환경 변수가 해법(`cli.py:424-441`).
- happy path 4: ARCHITECTURE에서 멈추는 조건(라이브러리에서 빌드 가능할 때) 명시; 표가 안 뜨면 architecture 줄이 이유를 말한다.
- happy path 5: 같은 실행의 **요구 답**(application, scope 답, `output_current=0 A`)이 yes를 무효화 → 첫 실행에 넣으라(`agents/circuit.py:165-171`, `agents/keys.py:53-61`; P1 세션이 사용자에게 정확히 이렇게 설명함); `confirm_design=no`는 표를 다시 안 보임, 다른 말은 재질문(`circuit.py:183-187`).
- happy path 6: `review --json`은 텍스트 14줄+요약 뒤에 JSON(`cli.py:1083-1088`; P4 세션이 실제로 걸림); 한국어 보고서 4종은 ARCHITECTURE(설계 존재 시)·COMPONENT_SELECTION·PCB·RELEASE 통과 시점에 쓰이고 막힌 실행은 도달한 것만(`cli.py:89-95, 981-1013`).
- 출력 읽기: 첫 줄 `sources: …`, 단계 뒤 `COMPONENT EXISTENCE`·`BLOCKED`·`OPTIONAL QUESTIONS` 블록.
- UNRESOLVED 행: 바이어스 브래킷뿐 아니라 스윕 보간 브래킷·허용오차 없음·bound+tolerance(`tools/spice/stage.py:456-531`).
- exit code: `new`는 ir.json이 있으면 2(`cli.py:547-563`), `review`는 FAIL이면 1, `report`/`stage-reports`는 0/2뿐.
- confirm_design 무시 사유 5개를 실제 문구로, `ir.parameters` 충돌 시 "not proposed"(note 없음) 추가.
- 결정성(**WRONG**): G9 실측으로 교체(`ir_hash`·19단계 동일; `at`·`ir_file_sha256`·`results_before`만 변함; 손편집 derived 값 → calculation/review/repair/release FAIL, exit 1).
- UTF-8: 보고서 파일은 항상 UTF-8, 콘솔 파이프는 PYTHONUTF8 없으면 레거시 코드페이지(`cli.py:1358-1372`).
- "When to read" 줄 수 표를 실제 값으로(~120/~90/~70).

pipeline.md
- 1단계: `requirements.extraction`은 `--llm`에서만 기록; LLM 없으면 결과 없음→NOT_VERIFIED(`agents/requirement.py:413-433`, `orchestrator.py:351-355`).
- 3단계(**WRONG**): PASS 불가(compliance 항상 NOT_VERIFIED가 worst_status로 올라옴; `research.py:538-545`); 검사 단위 PASS 조건과 FAIL(인용문 누락) 명시; check id 5+1개 나열.
- 5단계: 서브체크 6개(catalog 포함), 아카이브 사본은 오프라인에도 PASS(`parts/existence.py:190-222`), `component.facts.<ref>.llm`.
- 7단계: 파일 없으면 IR의 authoritative 한계를 재검증(PASS 가능; `agents/manufacturing.py:128-183`, `tests/test_fab_capability.py:465-474, 915-918`).
- 8단계: 도메인이 맞는 검증기만(`validation/registry.py:27-30`, `base.py:37-42`).
- 14단계: parity 소견도 FAIL, 경고 포함(`tools/kicad/cli.py:373-380, 323`).
- UNRESOLVED 정의 확장; 증거 스탬프(`artifact_hash`는 산출물을 읽은 결과만; gerber/drill evidence는 해시 없음 `report/data.py:66`); 보고서의 aggregate 라벨(`data.py:612, 81`); review --json stdout 형식; ngspice 탐색 3단계(`ngspice_shared.py:245-260`); astable 앵커는 테스트 시점 검사(`test_circuit_templates.py:937-941`; 스테이지는 10 %만 본다); conditions는 요약·기대 결과에만; 승인은 실행당 1회 소비 후 세션 전체가 탄다(`sources/policy.py:155-159`, `llm/service.py:220-231`); 소켓 문장(`--llm openrouter`는 `--online` 없이도 outbound, `serve`/`gui`는 loopback listen; `cli.py:158-168`).

answers.md
- ambiguous 메시지의 `leave_out` 안내는 leavable 키가 있는 템플릿에만(`templates.py:1721-1739`); 필수 입력 질문 문구와 "범위 밖 거부가 먼저"(`templates.py:833, 1166-1171`).
- 별칭 표를 `design/inputs.py:85-195` 전체로(dc_input, vin_dc, iout, fc, vf, if, fosc, fclk, vce_sat, switch_drop, c_b, cb, t_r, tr, rf_frequency, f_carrier, tx_frequency, modulation_type, emission_mode, layer_count; vbat은 의도적으로 별칭 아님) + 라디오 전용 키.
- `confirm_design=no`/미인식 답 동작; 확인 어휘 전체(`llm/extraction.py:127-132`); 같은 실행에서 함께 가도 되는 제어 키.
- 규제 scope 질문의 관할 태그(highest_rated_voltage EU/KR, evaluation_kit·finished_apparatus EU; `regulatory/candidates.json:28-48`).
- 모델 선택 플래그는 `run --help`에만; `--llm-model` 변경 시 exit 2(`cli.py:886-890`).

without-cli.md
- `kicad tables` 두 가지 MISSING 문구; kicad-cli 없을 때 3D export는 "note만"(`orchestrator.py:586-599`); 손으로 돌리는 명령에서 `sch export netlist` 줄 삭제(**WRONG**: 파이프라인은 `.cir`를 IR에서 직접 컴파일, kicad-cli 넷리스트는 쓰지 않음; `compilers/spice.py:1191`, `docs/ARCHITECTURE.md:237-241`); 설치 스크립트의 selftest는 조건부(`install.sh:695-704`, `install.ps1:522-531`).

## 기각한 것 (반박 에이전트 또는 내 확인으로 코드가 리뷰 주장을 부정)

- Codex "Warnings are findings는 근거 없음" → `tools/kicad/cli.py:47-48, 136` `WARNING_POLICY = "any violation (error or warning, excluded or not) is FAIL"`. 유지.
- Codex "exit 1 의미가 불명확" → `cli.py:1044` docstring과 SKILL.md 문장이 같다. 유지(명령별 추가만).
- Codex MISSING "answer control keys·doctor strict 범위 누락" → answers.md 51-56·without-cli.md 7-8에 이미 있음.
- 워크플로 SKILLmd-23(`ai-eda new divider`의 `divider`가 템플릿을 고른다는 인상) → 문장은 그렇게 말하지 않고, 제안된 대체문("output_current 부재로 선택")이 오히려 틀림(`templates.py:463-465`).
- SKILLmd-65("IR version"이 부정확) → 코드 자체의 용어(`agents/manufacturing.py:193`, `review/reviewer.py:92`).
- without-cli-15/-28/-32/-44/-56 → 문장이 하지 않는 주장을 반박한 것(답변 형식 헤더, 인용 없는 doctor 줄, 손으로 돌리는 명령 절, "existing" 파일, 엔진 부재 절).

## 하지 않은 것

- 누락 17건 중 relocate 세부, 락 변형, 보고서 PDF 타임아웃 문구, doctor 줄 전체 형식, selftest 옵션, IR_BUILD 질문 답법, LLM 전용 표의 무시 문구는 넣지 않음 — SKILL.md 250줄 상한과 references 3개 상한을 지키기 위해 "에이전트가 happy path에서 부딪히는 것"만 골랐다. 필요해지면 pipeline.md에 절을 추가한다.
- G9 실측 외의 새 측정은 없음(모든 수정은 코드 읽기 근거).
