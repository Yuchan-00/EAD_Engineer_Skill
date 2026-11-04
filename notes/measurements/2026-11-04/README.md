# 2026-11-04 측정 파일 (PLAN.md §3.1-b, §7.1의 근거)

- `measure_cosim.md` — 측정 결과 요약(ngspice 코드 모델 목록, 혼성 덱, d_cosim, 툴체인 유무).
- `mixed.cir` — XSPICE 혼성 덱. `NgspiceShared.run(path, SpiceAnalysis.TRAN, workdir, command="tran 10u 5m")`로 실행(참고 레포 venv). 결과: 795점, `vout`는 `in`의 반전.
- `d_cosim_probe.py` — ctypes로 KiCad `ngspice.dll`에 직접 d_cosim 카드를 넣는 프로브. 실행: 참고 레포 venv의 python으로.
- `am.cir`, `am2.cir` — ngspice-46 AM 소스 프로브(`tran 1u 3m`): `AM(1 0 1k 20k 0)` → 0…1 V, `AM(1 0 1k 20k)` → ±970 V.
- `blink.c` — simavr VCD 실측용 ATmega128 펌웨어. 빌드/실행(PlatformIO 패키지 경로):
  `avr-gcc -mmcu=atmega128 -Os -I<tool-simavr>/include/simavr -o blink.elf blink.c` → `simavr -m atmega128 -f 16000000 blink.elf` → `blink.vcd`(401 에지, 에지 간격 ≈ 501 µs).
- 전체 pytest 로그는 크기 때문에 넣지 않음(요약은 PLAN.md §3.1-b).
- `selftest-divider.kicad_sch` — `ai-eda selftest --dir <tmp> --keep`가 만든 분배기 회로도(B11 기준: 심볼 3, 스텁 wire 7, global_label 7, junction 0, 심볼 간 배선 0).
- `env.txt` — 참고 커밋, Python, `ngspice.dll` sha256, `ai-eda doctor --strict` 전체 출력.
- 항목별 검증 기록(같은 머리 형식): `d16-sim-elements-i2c-pullup.md`(결정 ⑯(b) 구현 + i2c_pullup), `a5-a7-b1-tests.md`(exit code·serve bind·KiCad 10.0.6), `b11-wiring.md`(배선 컴파일러), `templates-measurements.md`(D9 사전 측정 M1·M6–M10), `d9a-lc-lowpass.md`, `d9a-bjt-lowside-switch.md`, `a8-windows-fixes.md`(Windows 실패 9건 처리), `a3-astable-ngspice46.md`(astable 격자 재측정 → 결정 ⑰), `d9c-erc-sweep.md`(내장 7종 배선·ERC 일괄), `a9-am-source-ngspice46.md`(AM 소스 문법 43+·SFFM MDI 한계 실측 → 컴파일러·단계 수정).
