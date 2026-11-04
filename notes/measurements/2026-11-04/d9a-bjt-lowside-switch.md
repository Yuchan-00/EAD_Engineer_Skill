# D9a 구현 검증: bjt_lowside_switch 템플릿 (2026-11-04)

- 날짜·머신: 2026-11-04, robotics-lab (Windows 11)
- 버전: KiCad 10.0.6, ngspice-46, Python 3.12.10, 참고 레포 `work/ead-skill` 커밋 3bf314c(Codex 리뷰 반영 포함)
- 명령: `python -m pytest tests/test_catalog_bjt_lowside_switch.py`, `scripts\aieda-test.ps1 files …`(10파일), `scripts\aieda-test.ps1 full`
- 원본 로그: `B:\0) AI_Project\.logs\pytest-files-20261104-182640.txt`, `.logs\pytest-full-*.txt`(아래), Codex 리뷰 `.logs\codex-review-bjt-20261104.txt`
- 뒷받침하는 행: D9a (§7.3 D9 상세 `bjt_lowside_switch` 행), 결정 ⑯(비켜 감: 부하를 정전류 싱크 스티뮬러스로 둬 시뮬레이션 전용 소자가 필요 없음)

| 검사 | 결과 |
|---|---|
| `tests/test_catalog_bjt_lowside_switch.py` (6): 등록 1회, 표 줄(입력 4·선택값·계산값 i_b = 5 mA·r_b = 860 Ω·clamp_max = 13 V·부품·넷·한계 두 줄), 범위 밖 거부(500 mA → 0.2 A 정격, 1 V 제어 → V_BE+0.5 V, 48 V → V_CEO 40 V), 확인 후 provenance(계산기 tool id·입력 역할·단위, 선택값 user_requirement, `on_drop` nominal = 요구값 그대로(user_requirement)·requirement_id 없음(한계 규칙), Q1 핀 순서 C/B/E = 3/2/1, D1 A/K = 2/1, SW 넷이 `req.max_voltage_drop` 섬김) + `calc.recompute` PASS + 두 빌드 해시 동일, **ngspice: on_drop PASS, off_clamp PASS**, **R_B를 100배로 바꾼 음성 대조는 on_drop FAIL**, 회로도 컴파일(배선) + kicad-cli ERC 0 errors | 6 passed (9.5 s), 첫 실행에서 통과 |
| ngspice 실측 (5 V 제어, 12 V / 50 mA 부하, max_voltage_drop 0.3 V) | `on_drop`: v(SW) 평균 [2 ms, 3 ms] = **0.0680 V** ≤ 0.3 V (측정−한계 −0.232 V); `off_clamp`: v(SW) 최대 = **12.765 V** ≤ 13 V (= 12 V + v_f 1 V; 다이오드 기본 모델의 V_F ≈ 0.765 V @ 50 mA) |
| 묶음 10파일(calc·circuit_templates·si_templates·rf_selection·gui_server·catalog ×2·simulation_stage·spice_netlist·report) | **2 failed / 235 passed, 114 s** — 실패 2건은 `test_astable_verifies_at_the_bounds…[3 V-100 Hz]`·`[3 V-200 Hz]` = 기준선 A3(3·4·6차 전체 실행 로그에 같은 두 건; 단독 재실행도 FAIL 8.4 s; 오늘 astable 코드는 건드리지 않음) |
| 실제 CLI 2-run (`ai-eda new relaydrv --request …` → `run --answer input_voltage=5 V … max_voltage_drop=0.3 V` → `run --answer confirm_design=yes`) | 1차: `architecture USER_INPUT_REQUIRED template bjt_lowside_switch v0.3 can be built: 33 change(s)` 표 제시(선택값 11개 + 보드 결정); 2차: calculation PASS(6 값 재산출), **spice PASS**(tran 1e-5 4m, 426 pt, 기대값 2/2 PASS), schematic PASS, **ERC 0/0**, release NOT_VERIFIED(오프라인: 부품 existence·PCB 등 정상), exit 0 |
| 전체(`full`, `.logs\pytest-full-20261104-182933.txt`, 18:30 시작 — 등록 직후, Codex 리뷰 반영(3bf314c 일부)·A8 후속 커밋 이전 상태) | **8 failed / 2908 passed / 54 skipped, 21분 30초** — 정확히 기준선 8건(A3 ×2, A8 ×4, A9 ×2); KR447 시간 예산 실패 없음; 새 템플릿 관련 실패 0 → 회귀 0 |

설계 사실: 트리거 `output_current` + `max_voltage_drop`(새 키, V; 별칭 on_voltage_drop·v_ce_sat·vce_sat·switch_drop), 필요 입력 4개(`input_voltage` = 제어 레벨, `output_voltage` = 부하 전원). 계산기 3개 `calc.bjt_switch.base_current`(I_B = I_C/β_forced)·`base_resistor`(R_B = (V_ctl − V_BE)/I_B)·`clamp_max`(V_load + V_F). 선택값 11개: v_be 0.7 V, beta_forced 10, v_f 1.0 V, i_c_rating 0.2 A, 모델 카드(`.model QSW NPN (BF=100 TR=200n)` + `.model DFW D`), tran_step 10 µs, t_delay 1 ms, t_on 2 ms, t_period 4 ms, on_window 2..3 ms. 부품 R1(축형 THT)·Q1 2N3904·D1 1N4001(DO-41)·J1 1x2·J2 1x3. DividerTemplate는 `max_voltage_drop`이 있으면 물러난다(ambiguous 방지, 표 테스트에서 확인).

**부하 모델 결정**: 부하(릴레이 코일 등)는 보드 부품이 아니므로 R+L로 넷리스트에 넣으려면 "시뮬레이션 전용 소자"(결정 ⑯)가 먼저 필요했다. 대신 `Stimulus(source="current", DC)`로 VLOAD→SW 정전류 싱크를 두었다 = 이상적인 유도성 부하(전류 불변). OFF 상태는 항상 환류 상태(다이오드가 I_load를 받음), ON 상태는 정확히 요구 전류. 턴온 상승·환류 감쇠(실제 코일의 R·L)는 두 판정에 필요 없어 모델에 없고, 템플릿 docstring·표·이론 절에 그렇게 적었다. i2c_pullup은 여전히 ⑯ 뒤(버스 용량은 정전류로 대신할 수 없음).

한계(bound) 기대값은 requirement_id를 들 수 없다(컴파일러 규칙) → `on_drop`의 nominal은 요구사항 값 자체(user_requirement provenance)이고, SW 넷의 serves_requirements와 제약 `c.bjt_lowside_switch.on_drop`이 요구사항을 가리킨다. 구동 부족(β_forced 과대, V_ctl 저하)은 거부가 아니라 on_drop FAIL로 드러난다(음성 대조로 확인).

Codex 리뷰(`exec -s read-only`, `.logs\codex-review-bjt-20261104.txt`) 4건과 처리:
- P2 V_load ≤ 40 V 거부가 OFF 전압 V_load + v_f 가 V_CEO 를 넘는 경우를 놓침 → **반영**: 거부 조건을 `V_load + v_f > V_CEO` 로 바꿈(테스트 39.5 V → "40.5 V exceeds V_CEO 40 V").
- P2 max_voltage_drop 을 창 **평균**으로 판정하는데 이름은 '최대' → **반영(의미 명시)**: 창 안 최대 축약은 엔진에 없고(MAX 는 전체 과도) 정전류 부하에서 ON 레벨이 평탄해 평균=최대, 창은 양쪽 에지 제외 — docstring·기대값 provenance·제약·표 줄·이론 절에 적음. 코드 변경 없음.
- P2 DividerTemplate 가 `max_voltage_drop` 이 파싱 실패(unusable)일 때 물러나지 않음 → **검증 후 변경 없음**: `max_voltage_drop="0.3 ohm"` 으로 실행하면 "not usable … leave_out" 메모와 함께 closed-world 규칙이 분배기를 거부(`template divider not proposed: req.max_voltage_drop … is not served`), 부품 0개, 질문 0개(18:36 실측).
- P3 "ideal inductive load" 표현이 물리적으로 오도(인덕터 전류는 변함) → **반영**: "simplified steady-current load model, not a coil"(한글: 단순화한 정전류 부하 모델)로 전부 바꾸고 코일의 L/R 상승·환류 감쇠가 생략됐음을 적음.
- OK 판정: 펄스(1 ms 지연, 10 µs 에지, 2 ms 폭)와 창 2..3 ms 정합; on_drop 은 구성상 통과가 아님(음성 대조); 부품 노트의 데이터시트 수치는 선정 기준으로만 제시.
