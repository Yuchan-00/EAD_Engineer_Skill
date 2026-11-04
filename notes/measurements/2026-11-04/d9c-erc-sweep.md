# D9c: 내장 템플릿 7종 회로도 컴파일·배선·ERC 일괄 실측 (2026-11-04)

- 날짜·머신: 2026-11-04 18:53, robotics-lab (Windows 11)
- 버전: KiCad 10.0.6 (kicad-cli), Python 3.12.10, 참고 레포 `work/ead-skill` 7ebfb6a
- 명령: `scratchpad/d9c/erc_sweep.py` — 템플릿마다 GUI 예시 입력으로 ARCHITECTURE(표) → `confirm_design=yes` → CALCULATION, `SchematicCompiler.compile`, `KicadCli.run_erc`
- 원본 로그: `B:\0) AI_Project\.logs\erc-sweep-20261104.txt`
- 뒷받침하는 행: D9c("전 템플릿 ERC 실측"), B11 W3(템플릿별 배선 커버리지)

| 템플릿 | 부품 | 넷 | 배선(B11) | ERC | 시간 |
|---|---|---|---|---|---|
| divider | 3 | 3 | 3/3 | PASS 0/0 | 3.8 s |
| led | 3 | 3 | 3/3 | PASS 0/0 | 3.2 s |
| rc_lowpass | 3 | 3 | 3/3 | PASS 0/0 | 3.1 s |
| lc_lowpass | 6 | 4 | 4/4 | PASS 0/0 | 3.6 s |
| bjt_lowside_switch | 5 | 5 | 4/5 | PASS 0/0 | 3.5 s |
| astable | 9 | 6 | 5/6 | PASS 0/0 | 4.2 s |
| atmega128_devboard | 31 | 64 | 17/64 | **FAIL 3 errors** 0 warnings | 5.2 s |

ATmega의 3건은 모두 `Input Power pin not driven by any Output Power pins`(U2 L7805 IN, U1 GND, U1 AVCC): 회로도 컴파일러가 POWER/GROUND 넷에 `power:*` 심볼·PWR_FLAG를 내지 않는 **알려진 미구현**(참고 레포 `docs/ARCHITECTURE.md` "아직 아닌 것" 3번; `tests/test_selftest.py`가 `power_pin_not_driven`을 알고 있음). 전원 입력 핀이 있는 부품(레귤레이터·MCU)을 쓰는 템플릿만 걸리고, 수동 소자·커넥터만 있는 6종은 걸리지 않는다. 회귀 아님.

배선 커버리지: 작은 보드는 전 넷 또는 1개 미배선(bjt의 GND 3핀·astable의 VCC 5핀 — `MAX_WIRED_PINS=4` 초과 넷), ATmega는 17/64(오늘 오전 B11 측정 15/64에서 배치 순서 변경으로 +2). W3 범위 그대로.
