# A9: ngspice 43+ AM 소스 문법 (매뉴얼 확인 + ngspice-46 실측 + 컴파일러·단계 수정, 2026-11-04 밤)

- 날짜·머신: 2026-11-04 21:15–21:20, robotics-lab (Windows 11)
- 버전: ngspice-46 (KiCad 10.0.6 동봉), Python 3.12.10, 참고 레포 `work/ead-skill` 03bd642 (196fb9a 위)
- 명령: 프로브 덱 `B:\0) AI_Project\.logs\am46\*.cir`(`NgspiceShared.run(…, TRAN, command="tran 0.1u 3m")`), `pytest tests/test_rf_spice.py tests/test_spice_netlist.py tests/test_simulation_stage.py tests/test_rf_measure.py`
- 원본: ngspice 매뉴얼 47+ (HTML, https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml) §4.1.5–4.1.6; Codex 리뷰 `.logs\codex-review-a9-20261104.txt`
- 뒷받침하는 행: A9 (§3.1-b 표, §3.5 A9), 결정 ⑰과 같은 "엔진 버전 앵커" 계열

## 매뉴얼 (47+, §4.1.6 / §4.1.5)

- AM 일반형 `AM(VO VMO VMA FM FC TD PHASEM PHASEC)`, V(t) = VO + (VMO + VMA·sin(2π·FM·(t−TD) + PHASEM))·sin(2π·FC·(t−TD) + PHASEC); 깊이 = VMA/VMO, VMO = 0이면 DSB-SC. "VO and VMO have to be given always."
- SFFM 일반형 `SFFM(VO VA FC MDI FM TD PHASEM PHASEC)`, V = VO + VA·sin(2π·FC·t + MDI·sin(2π·FM·t)); "MDI is limited to 0 ≤ MDI ≤ FC/FM". 마지막 주파수 이름이 FS → FM으로 바뀌었을 뿐 순서는 컴파일러의 `SFFM(VO VA FC MDI FS)`와 같다.
- 참고 레포의 앵커(ngspice-42, 2026-09-28): `AM(VA VO MF FC TD)`, v = VA·(VO + sin MF)·sin FC. 43에서 번호가 매겨진 새 형식으로 바뀌었고 옛 5값 텍스트는 **위치대로** 읽힌다(VO=1, VMO=2, VMA=1k, FM=100k, FC=0 → sin 0 = 0 → 상수 1 V).

## ngspice-46 실측 (`tran 0.1u 3m`, 1 kΩ 부하)

| 덱 | 결과 |
|---|---|
| `AM(1 2 1k 100k 0)` (옛 철자) | **상수 1.000 V**(0 µs에 0, 이후 1.0) — 테스트의 "no carrier: amplitude (0 .. 0)" 실패 원인 |
| `AM(2 1 1k 100k 0)` / `AM(1 0 …)` / `AM(1 0.5 …)` / 7값 | 전부 첫 값의 상수(2 V / 1 V / 1 V / 1 V) |
| `AM(0 2 1 1k 100k 0)` (새 형식, VA=1·VO=2의 사상) | 포락선 사이클 최대 1.000..2.999, 최소 −2.999..−1.000; 1 ms에 상승 영교차 99회(100 kHz 반송파) — **42 앵커(1..3 V)와 일치** |
| `AM(0 0 1 1k 100k 0)` (VMO=0) | 포락선 0.018..1.000 — DSB-SC |
| `SFFM(0 1 100k 5 1k)` (컴파일러 순서) | 영교차 99회/ms(반송파 100 kHz), ±1 V — 순서 그대로 유효 |
| `SFFM(0 1 1k 5 100k)` | ngspice 오류(MDI 5 > FC/FM = 0.01, 매뉴얼의 제한) — 순서가 바뀐 것이 아니라 제한 위반 |

## 수정 (컴파일러는 IR의 순수 함수이므로 엔진 분기는 단계에서)

- IR `StimulusKind.AM` 매개변수(va, vo, mf, fc, td)와 물리는 그대로(저장된 IR 해시 불변). 컴파일러 `_stimulus_spec`이 43+ 형식 `AM(0 VA·VO VA MF FC TD)`로 쓴다(VO_new = 0, VMO = VA·VO, VMA = VA; 곱은 ledger 숫자 포맷을 거침). 양수 검사(mf·fc > 0, td ≥ 0)는 재배열 전 값에 그대로.
- SPICE 단계 `run_spice_for`: AM 자극이 있고 `runner.version()`이 `ngspice-NN`, NN < 43이면 실행 전에 `ToolUnavailableError`("… reads it as a zero source; run it on ngspice 43 or newer"). 42가 새 형식을 0 소스로 읽는 것은 42의 문서화된 식에서 추론(VA=0)이며 이 PC에 42가 없어 실측은 아님. 버전 문자열이 `ngspice-NN`이 아닌 엔진(가짜 러너 등)은 게이트하지 않음.
- 테스트: 철자(`AM(0 2 1 1k 100k 0)`, DSB-SC `AM(0 0 1 …)`, 0.5 → `500m`), 게이트(가짜 ngspice-42 러너, 실행 전 거부), 기존 AM depth 2건 **통과**(49.969 % 측정, 편향 괄호 UNRESOLVED 사례 그대로). 결과: `test_rf_spice.py` 전부 통과, 묶음 4파일 98 passed.
- README `AM(VA VO MF FC TD)` 문구 갱신. 제품 코드(템플릿·RF 픽스처)에 AM 자극을 내는 곳은 없음(grep) → 게이트는 AM을 직접 쓰는 IR에만 닿는다. Ubuntu 24.04의 libngspice0(ngspice-42)에서는 AM 자극 IR이 SPICE 단계에서 NOT_VERIFIED로 멈춘다(의도).

## Codex 리뷰 반영 (같은 커밋)

- **P1 SFFM MDI 한계**: 매뉴얼 "0 ≤ MDI ≤ FC/FM"을 컴파일러가 강제하지 않음 → 실측: ngspice-46은 `SFFM(0 1 1k 5 10k)`에 **"Warning: MDI in v1 limited to FC/FM"을 프로세스당 한 번** 내고 MDI를 0.1로 잘라 다른 파형을 돌린다(첫 실행은 경고로 `succeeded=False`, 같은 프로세스의 다음 실행은 경고 없이 성공 — 잘린 값으로). 42 앵커 문구(`SFFM(0 1 1k 5 10k)` 영교차 일치)는 42에서만 참 → IR docstring에 명시, 컴파일러가 `mdi > fc/fs` 거부(테스트: 1k/5/10k 거부, 100k/5/1k 통과), 테스트 픽스처 덱 교체.
- **P2 버전 미해독**: `engine_major()`가 None이면 게이트를 지나침 → `runner.engine`이 `ngspice…`이고 버전이 안 읽히면 fail-closed(`ToolUnavailableError "… could not be read"`), 가짜 러너 등 다른 엔진은 게이트 없음. 테스트에 `Unknown` 러너 추가.
- **P2 42 기준선에서 AM 통합 테스트가 ToolUnavailableError로 실패** → `needs_ngspice43` 마커로 43 미만에서는 skip(42 Linux 기준선은 이 두 테스트가 SKIP으로 보임).
- OK: VA·VO 곱은 두 IR 값 수용 뒤 ledger 숫자 포맷을 거침; 양수 검사는 IR 이름 기준이라 재배열과 무관; 게이트는 `fresh_artifact` 앞이고 `SimulationAgent`가 `ToolUnavailableError`를 사유 포함 NOT_VERIFIED로 바꿈; CLAUDE.md의 42 AM 예시는 측정 기록이라 모순 아님.
- 재검증: `test_rf_spice.py`·`test_spice_netlist.py`·`test_simulation_stage.py`·`test_rf_measure.py`·`test_rf_fixture.py` **136 passed**(15 s); 인접 묶음(rf_ir·rf_checks·stage_reports·report·catalog·circuit_templates·md 회귀) 251 passed.
