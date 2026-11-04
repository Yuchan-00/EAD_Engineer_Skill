# 결정 ⑯(b) 구현 + i2c_pullup 템플릿 검증 (2026-11-04 저녁)

- 날짜·머신: 2026-11-04 19:35–20:10, robotics-lab (Windows 11)
- 버전: KiCad 10.0.6, ngspice-46, Python 3.12.10, 참고 레포 `work/ead-skill` fdd6657(⑯ 요소) + 다음 커밋(i2c_pullup)
- 명령: `python -m pytest tests/test_spice_netlist.py`, `tests/test_catalog_i2c_pullup.py`, 등록 영향 10파일 묶음, 실제 CLI 2-run
- 원본 로그: Codex 리뷰 `.logs\codex-review-d16-20261104.txt`, `.logs\codex-review-i2c-20261104.txt`; 설계 전 조사는 워크플로 `map-sim-only-elements`(독자 4명, 5분, 55만 토큰)
- 뒷받침하는 행: 결정 ⑯, D9a(i2c_pullup 행), §7.3 D9 상세

## ⑯(b): `SimulationSetup.elements` / `.nodes` (fdd6657)

| 검사 | 결과 |
|---|---|
| IR: `SimElement`(2단자 R/C/L 값 또는 D 모델 카드, 넷→넷, reason, provenance), `SIM_ELEMENT_DEVICES`, `SimulationSetup.elements`·`.nodes`가 비어 있는 동안 설계 뷰에서 빠짐 | 고정 해시 픽스처 4종 테스트(test_rf_ir·rf_checks·stackup·silkscreen·si_checks·leave_out) 통과 |
| 컴파일러: 전용 노드 검증(평범한 이름, 넷·접지와 충돌 금지), 요소는 부품 뒤·자극 앞에 id 순, 부품과 같은 규칙(llm_generated 거부, 양수 값, 단일 토큰 모델, 카드는 공용 `register_card`, `claim()`으로 이름 고유), 자극도 전용 노드 사용 가능, 요소가 닿는 넷은 stimulated로 취급, 보고서 `sim_elements`/`sim_nodes` | `tests/test_spice_netlist.py` 21개 신규(배치·거부 13·노드 가림·해시·recompute/assumption 걷기·이론 보고서 절) 포함 48 passed |
| 소비자: recompute `derived_values`, structural `simulation_assumptions`, 이론 보고서 "### 시뮬레이션 전용 요소" | 296 passed (핀 해시·보고서·IR·calc·stage·tline·md 회귀) + validation/report 60 passed |
| Codex 리뷰 | **actionable 없음** — 이름 충돌·값 검증·카드·노드 중복·해시/로드 정책·소비자 모두 OK |

## i2c_pullup (8번째 템플릿)

| 검사 | 결과 |
|---|---|
| `tests/test_catalog_i2c_pullup.py` (6): 등록 1회, 표(창 R_max 2360 Ω·R_min 966.7 Ω·R 1888 Ω, 전용 요소 줄, 한계 줄, "not verified: V_OL"), 거부(400 pF/100 ns → R_max 295 < R_min 967; 12 V → 1.2..5.5 V 밖), 확인 후 provenance(계산기 tool id·역할, CBUS 값 = 요구값 user_requirement·serves, DOD 카드 = 확인 선택값, `rise` 한계 at_least·requirement_id 없음·nominal `calc.i2c.v_ih`·at `calc.i2c.t_check`) + recompute PASS + 넷리스트에 `CBUS SDA 0 150p`·`DOD SDA DRV DOD`·`VDRV DRV 0 PULSE(`·`.model DOD D` + 두 빌드 해시 동일, **ngspice rise PASS**, **R 3배 음성 대조 FAIL**, 회로도에 CBUS/DOD/DRV 없음 + ERC 0 errors | 6 passed (4.6 s) |
| 설계 변경(ERC 경고 1건 → 수정): 4핀 헤더의 GND 핀 하나뿐인 넷에 KiCad `isolated_pin_label` 경고 → 헤더 3핀(VDD/SDA/SCL), GND는 핀 없는 넷(시뮬레이션 기준; 풀업 보드에 접지 핀 없음)으로 바꾸고 docstring·부품 노트에 명시 | ERC 0/0 |
| 등록 영향 10파일(calc·circuit_templates·si_templates·rf_selection·gui_server·catalog ×2·atmega·spice_netlist·report) | 262 passed (99 s) |
| 실제 CLI 2-run (`ai-eda new i2cbus` → `run --answer …` → `run --answer confirm_design=yes`) | 1차: `template i2c_pullup v0.3 can be built: 29 change(s)` 표(전용 요소 줄·한계 줄); 2차: calculation PASS(22 값), **spice PASS**(tran 6 ns .. 2.95 µs, 507 pt, 1/1), schematic PASS, **ERC 0/0**, release NOT_VERIFIED(오프라인), exit 0; BOM·회로도에 CBUS/DOD/DRV 없음 |

설계 사실: 트리거 `bus_capacitance` + `bus_rise_time`(새 키; 별칭 line_capacitance·c_bus·c_b·cb / rise_time·t_rise·t_r·tr), 필요 입력 4개. 계산기 9개 `calc.i2c.*`(r_max = t_r/(ln(0.7/0.3)·C_b), r_min = (V_DD−V_OL)/I_OL, r_pullup = fraction·r_max, v_ih = 0.7 V_DD, t_low = 1/(2 f), t_30 = R C ln((V_DD−V_OL)/(0.7 V_DD)), t_check = t_low+t_30+t_r, tran_step = t_r/50, tran_stop = t_low+6RC). 선택값 v_ol 0.4 V·i_ol 3 mA·pullup_fraction 0.8·driver_model. Atmega128DevboardTemplate는 버스 키가 있으면 물러남(표 테스트에서 ambiguous 없음 확인). 판정 원리: RC 충전의 30→70 % 상승 시간은 출발 레벨과 무관하므로 다이오드 전압(≈0.6 V)이 판정을 치우치게 하지 않음; 큰 R은 t_check에 V_IH 미달로 FAIL.

Codex 리뷰(i2c, `.logs\codex-review-i2c-20261104.txt`) P2 3건 → 전부 반영(196fb9a):
- P2 "판정이 구성상 통과 가능 + t_30이 V_OL 0.4 V 가정인데 다이오드는 ≈0.6 V에 잡아 관대함(R_max 9 % 초과도 통과)" → **잡힌 레벨을 계산하고 측정**: `calc.i2c.v_low_diode`(일반 다이오드 IS=1e-14·N=1·27 °C 고정점, 풀업 전류에서의 순방향 전압)로 V_low를 구해 t_30의 출발 레벨로 쓰고, 새 기대값 `held_low`(0.9·t_low에서 v(SDA) = V_low ±50 mV)가 시뮬레이션이 실제로 그 레벨을 잡는지 측정. 실측: **held_low 0.6637 V vs 계산 0.6634 V (PASS)**, rise 2.499 V ≥ 2.31 V (PASS); 음성 대조를 R×3에서 **R×1.3(= 1.04·R_max)**로 좁혀도 **FAIL**(2.243 V, −67 mV). 판정은 이제 "넷리스트의 R·C_b ≤ t_r/0.8473"과 동치(한 표본 간격 안).
- P2 "0.8·R_max < R_min ≤ R_max인데 '어떤 풀업도 불가'라고 거부" → `calc.i2c.r_pullup(r_max, r_min, fraction)` = max(fraction·R_max, R_min), 거부는 R_min > R_max일 때만; 테스트에 경계 사례(150 pF/150 ns → R = R_min 966.7 Ω) 추가.
- P2 "1.2 V 공급은 V_OL 0.4 V가 0.3·V_DD 이상이라 t_30이 거부" → 하한 **2.5 V**(다이오드 전압 ≈0.66 V가 30 % 점 아래여야; 1.8 V 버스는 드라이버 모델이 필요한 후속 항목), 테스트 12 V·1.8 V 거부.
- 추가로 CLI 실측의 넷리스트 숫자 17자리(`2.9495204016471134u`, 보고서 unmodelled 3건) → `tran_step`(내림)·`tran_stop`(올림)을 유효숫자 2자리로 반올림하는 계산기(3 µs, 6 ns).
- 재검증: 계산기·카탈로그 14 passed, 등록 영향 10파일 **307 passed / 1 skipped**(127 s).
