# D9a 구현 검증: Reduce.PP/MEAN + lc_lowpass 템플릿 (2026-11-04)

- 날짜·머신: 2026-11-04, robotics-lab (Windows 11)
- 버전: KiCad 10.0.6, ngspice-46, Python 3.12.10, 참고 레포 `work/ead-skill` 커밋 75ad38e(PP/MEAN), fece446(lc_lowpass), 9368133(등록·이론·부품 노트·종단 선택값)
- 명령: `scripts\aieda-test.ps1 files …`, `python -m pytest tests/test_catalog_lc_lowpass.py`, `scripts\aieda-test.ps1 full`
- 원본 로그: `B:\0) AI_Project\.logs\pytest-files-20261104-165834.txt`, `…-170010.txt`, `.logs\pytest-full-*.txt`(아래)
- 뒷받침하는 행: D9a (§7.3 D9 상세, §3.5 없음 → D9 PASS 조건), M7 후속

| 검사 | 결과 |
|---|---|
| `tests/test_simulation_stage.py` + `test_spice_netlist.py` (PP·MEAN) | 46 passed |
| `tests/test_catalog_lc_lowpass.py` (5): 표 줄, 범위 밖 거부(1 kHz–30 MHz, 10–600 Ω), 확인 후 provenance(계산기 tool id·입력 id·단위, 선택값 user_requirement, 기대값 nominal 출처 `calc.lc.butterworth2.level_db`, `ref`는 `calc.divider.v_out`) + `calc.recompute` PASS + 두 빌드 해시 동일, **ngspice 코너 PASS**(측정 −3.01 dB ± 0.05), **L을 2배로 바꾼 음성 대조는 PASS 아님**, 회로도 컴파일(배선 포함) + kicad-cli ERC 0 errors | 5 passed (13.5 s) |
| 템플릿·단계·보고서·SI 묶음(7파일) | 5 failed(전부 기준선 A3×2, A8×3) / 193 passed |
| 계산기 레지스트리·회귀·GUI(4파일) | 레지스트리 테스트에 새 계산기 3개 샘플 추가 후 통과 (8 passed; 묶음 109 passed) |
| 전체(`full`, 등록 전 상태 fece446) | **11 failed / 2895 passed / 54 skipped, 17분 53초** — 전부 기준선(A3 ×2, A8 ×7, A9 ×2), 회귀 0 |
| 등록 뒤 실제 CLI 2-run (`ai-eda new` → `run --answer …` → `run --answer confirm_design=yes`) | 1차: `architecture USER_INPUT_REQUIRED … template lc_lowpass v0.3 can be built: 25 change(s)` 표 제시; 2차: calculation PASS(14 값 재산출), **spice PASS**(ac dec 500, 2001점, 기대값 1 PASS), schematic PASS, **ERC 0/0**, release NOT_VERIFIED(오프라인: 부품 existence·PCB 등 정상), exit 0 |

설계 사실: 100 kHz / 50 Ω → L = 112.54 µH, C = 45.016 nF, v_pass = 0.5 V(프로브 1 V의 절반, 양단 종단), level_fc = −3.0103 dB. ac 500점/decade로 올린 이유: 100점에서는 f_c를 감싸는 두 표본이 ±0.2 dB 허용치를 벗어나 보간값이 UNRESOLVED(엔진의 정직한 판정)였고, 500점에서 표본 간격 0.46 %가 코너 기울기(−8.7 dB/ln-unit)에서 0.04 dB.

Codex 리뷰(PP/MEAN, 75ad38e): 보고서 라벨·수식 누락(P2) → 반영; ARCHITECTURE 문구(P3) → 반영; 엣지 테스트(P3)는 D9c로. lc_lowpass 리뷰 결과는 아래 추가.

미등록: `TEMPLATES`에 아직 넣지 않았다(README `템플릿은 5종` 카운트 테스트·`gui/page.py` 문구·`test_si_templates` 파라미터가 함께 바뀌어야 하므로 D9c에서 일괄). 테스트는 monkeypatch로 등록해 돌린다.
