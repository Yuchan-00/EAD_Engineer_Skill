# A3 원인 확인: astable 유효 범위 격자 재측정 (ngspice-46, 2026-11-04)

- 날짜·머신: 2026-11-04 18:42, robotics-lab (Windows 11)
- 버전: ngspice-46 (KiCad 10.0.6 동봉 `ngspice.dll`), Python 3.12.10, 참고 레포 `work/ead-skill` 7ebfb6a (astable 코드는 main 4ee4d8e 그대로)
- 명령: `scratchpad/a3/measure_astable_grid.py` (템플릿 파이프라인을 ARCHITECTURE→confirm→SPICE까지 돌려 `spice.f_osc`의 measured/nominal을 읽음; 3..6 V 7단계 × 100 Hz..20 kHz 로그 10단계 = 70점 + 테스트의 (3 V, 200 Hz)·(6 V, 200 Hz))
- 원본 로그: `B:\0) AI_Project\.logs\astable-grid-ngspice46-20261104.txt`
- 뒷받침하는 행: A3 (§3.1-b 표, §3.5 A3) — "먼저 원인 확인" 완료

| 검사 | 결과 |
|---|---|
| 72점 모두 과도 해석 완료·`spice.f_osc` PASS (허용차 10 %) | 예 (36 s) |
| 편차 범위 (measured − nominal)/nominal | **+1.680 % (6 V, 20 kHz) .. +5.032 % (3 V, 200 Hz)**; 3 V 행은 100 Hz~1 kHz 전부 4.94~5.03 % |
| 기록된 앵커(ngspice-42, 템플릿 개발 시 70점): +1.6 % .. +4.9 % (3 V, 100 Hz), `MEASURED_DEVIATION_MAX = 0.049` | ngspice-46에서는 6점이 0.049를 넘음: (3 V, 100 Hz) 4.94 %, 180 Hz 5.02 %, 200 Hz 5.03 %, 325 Hz 5.02 %, 585 Hz 4.99 %, 1.05 kHz 4.95 % |
| 최악점 위치 | ngspice-42는 코너 (3 V, 100 Hz); ngspice-46은 (3 V, 200 Hz) — 템플릿 이론 절의 "V_CE(sat) 비중 최대 = 100 Hz" 문장은 42 기준 |

**결론**: 실패 2건(`[3 V-100 Hz]`, `[3 V-200 Hz]`)은 assertion 반올림이 아니라 **엔진 버전 드리프트**(+0.04~+0.13 %p). 템플릿의 두 규칙이 46에서 깨진다: (1) `편차 ≤ MEASURED_DEVIATION_MAX(0.049)`, (2) `편차 ≤ 허용차의 절반`(5.03 % > 5.00 %; `TOL_REL ≥ 2 × MAX`). 허용차 10 %의 PASS 자체는 모든 점에서 유지된다.

**선택지(사용자 결정 ⑰)**: (a) `TOL_REL` 10 % → 11 %와 버전별 앵커(`{"ngspice-42": 0.049, "ngspice-46": 0.051}`): 절반 규칙 유지, 사용자에게 보이는 허용차가 바뀜(README·표·테스트 문구); (b) 허용차 10 % 유지, 앵커만 버전별로 두고 절반 규칙을 "측정 최악점 ≤ 허용차 × 0.55"처럼 완화: 규칙의 근거가 약해짐; (c) 유효 범위 하한을 3 V → 3.5 V로 올려(3.5 V 행 최악 ≈ 4.5 %) 두 규칙을 그대로 두기: 적용 범위가 줄어듦. 어느 쪽이든 테스트가 `NgspiceShared().version()`으로 앵커를 고르고, 미측정 버전은 PASS로 연극하지 않고 SKIP/FAIL로 드러내야 한다.
