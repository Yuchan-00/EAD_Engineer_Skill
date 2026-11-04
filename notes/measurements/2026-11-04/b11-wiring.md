# B11 회로도 배선 W1+W2 구현 검증 (2026-11-04)

- 날짜·머신: 2026-11-04, robotics-lab (Windows 11)
- 버전: KiCad 10.0.6, ngspice-46, Python 3.12.10, 참고 레포 `work/ead-skill` 커밋 5a5e8a1(직전 925fb58)
- 명령: `scripts\aieda-test.ps1 files …` (회로도·템플릿·KR447·ATmega·GUI·보고서), `ai-eda selftest --dir <tmp> --keep`, 직접 컴파일 타이밍 스크립트
- 원본 로그: `B:\0) AI_Project\.logs\pytest-files-20261104-161730.txt`, `pytest-files-20261104-16xxxx.txt`(큰 보드 묶음, 8:49), `.logs\pytest-full-*.txt`(전체, 아래)
- 뒷받침하는 행: B11 (§3.2 설계, §3.5 PASS 조건)

| 검사 | 결과 |
|---|---|
| `tests/test_schematic_route.py` (라우터 순수 기하 8개: U 경로, trunk+junction, 핀 수 한계, 막히면 배선 0(끊긴 선 없음), 외부 선 끝 vs 중간 교차, 최종 가드, 공선 접촉·코너, 채널 계산) | 8 passed |
| `test_schematic_compiler.py` (구조·결정성·ERC 0·netlist parity 포함 + 새 배선 테스트) / `test_schematic_render.py` / `test_schematic_route.py` | 77 passed, 1 skipped |
| selftest 분배기(`selftest-divider-wired.kicad_sch`, `.svg`, `.png`) | `(wire` 22 = 스텁 7 + 배선 15, `(junction` 1, `global_label` 7; ERC 0/0, DRC 0/0, schematic parity 0; note "wiring: 3 of 3 net(s) drawn as wires" |
| KR447 transceiver (441 부품, 211 넷) | 컴파일 3.7 s, wire 1,243, junction 30, **47/211 넷 배선**(GND 234핀·CLIP·DLY는 핀 수 초과, 나머지는 "no clear path") |
| ATmega128 보드 (31 부품, 64 넷) | 컴파일 0.1 s, wire 243, junction 2, **15/64 넷 배선**(+5V 14핀·GND 21핀 초과, 포트 핀 넷 다수 "no clear path") |
| 큰 보드 묶음 15파일 | 8 failed / 429 passed: 기준선(A3×2, A8 보고서 인용×3) + GUI 10053 flaky 2건 + GUI 미리보기 테스트 1건(스텁 수 단언 → 적응) |
| 전체(`full`, `.logs\pytest-full-20261104-163xxx.txt`) | **12 failed / 2888 passed / 54 skipped, 17분 39초** — 12건 전부 기준선(A3 ×2, A8 ×8 중 GUI 10053 1건 포함, A9 ×2); 회귀 0 |

Codex 리뷰(exec 경로): P2 성능(441 부품에서 extent·선분 전수 스캔) → 측정 3.7 s로 현재 수용, 공간 인덱스는 보류; P2 테스트 2건(공선 접촉, 코너가 외부 선 내부) → 추가. 연결성·결정성·junction 도출은 OK.

관찰: 배선 성공률이 큰 보드에서 낮다(22 %·23 %). 원인은 W1의 후보 집합이 "핀이 향하는 쪽의 가장 가까운 채널"뿐이라 참조번호/블록 순 표에서 먼 행의 핀을 잇는 경로가 다른 셀의 extent에 막히기 때문. 분배기처럼 작은 보드는 3/3. 개선은 W3(후보 확장: 인접 거터 우회, 블록 단위 열 배치)로.
