# D9 템플릿 카탈로그 확정용 측정 (2026-11-04, robotics-lab, KiCad 10.0.6 / ngspice-46 / Python 3.12.10, 참고 커밋 4ee4d8e)

| # | 명령/방법 | 결과 | 뒷받침 행 |
|---|---|---|---|
| M1 | 참고 레포 venv에서 `KicadLibrary().load_symbol()`로 BC547, 1N4148, 1N4001, IRLZ44N, LM358, 2N3904 | extends 재귀 해석, 핀 전부 정상(BC547←Q_NPN_CBE C/B/E; 1N4148←1N4001 K/A; IRLZ44N←BUZ11 G/D/S; LM358←LM2904 8핀; 2N3904←Q_NPN_EBC E/B/C) | D9 bjt_lowside_switch, rectifier_cfilter |
| M6 | `rectifier.cir`, `NgspiceShared.run(…, TRAN, command="tran 50u 200m")` | 수렴 4,012점; 160–200 ms 평균 14.557 V, max 15.136, min 13.943, 리플 1.194 Vpp; 돌입 |i(v1)| 5.13 A @ 1.0 ms, 정상 최대 1.51 A | D9 rectifier_cfilter |
| M7 | `ai_eda/ir/simulation.py:251-297` 읽기 | Reduce 11종: value, at, final, max, min, frequency, db_at, rms, db_rms, harmonic_dbc, am_depth — PP·MEAN 없음 | D9a 전제(Reduce.PP/MEAN 추가) |
| M8 | `kicad-cli sch erc --format json --severity-all` on selftest-divider.kicad_sch | 7.24 s, 위반 0 | D9c ERC 예산 |
| M9 | `grep` tests/ for UNIT_OF/KEY_ALIASES coverage | RF 키만 프롬프트 커버리지 테스트(`tests/test_rf_requirement_keys.py:245`); 비RF 새 키는 테스트 요건 없음(프롬프트 `llm/prompts.py:34` 예시 목록 추가는 선택) | D9 새 키 6개 |
| M10 | `opamp.cir`(KiCad `Simulation_SPICE.sp:14-31` 매크로 인라인), `run(…, AC, command="ac dec 10 1 1meg")` | 래퍼 검증 통과(params:·{} 허용), 61점 수렴; \|out/in\| 10.994 @10 Hz, 10.994 @100 Hz, 10.990 @1 kHz, 10.600 @10 kHz, 3.754 @100 kHz | D9 opamp_noninverting |
