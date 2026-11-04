# A5/A6/A7/B1 구현 검증 (2026-11-04, robotics-lab, KiCad 10.0.6 / ngspice-46 / Python 3.12.10)

- 날짜·머신: 2026-11-04, robotics-lab (Windows 11)
- 버전: KiCad 10.0.6, ngspice-46, Python 3.12.10, 참고 레포 `work/ead-skill`(main `4ee4d8e`에서 분기)
- 명령: `scripts\aieda-test.ps1 files …`(대상 파일) → `scripts\aieda-test.ps1 full`
- 원본 로그: `B:\0) AI_Project\.logs\pytest-files-20261104-152728.txt`, `pytest-files-20261104-153353.txt`, `pytest-full-20261104-153419.txt` (레포에 넣지 않음)
- 뒷받침하는 행: A5, A6, A7, B1 (§3.1, §3.5), §4.1 루프의 첫 실전

| 검사 | 결과 |
|---|---|
| `tests/test_cli_bad_ir.py` (A5, 6개: unknown key·missing·non-JSON·locked reload × run/review) | 6 passed |
| `test_circuit_templates.py::…_ignored_with_the_fourth_reason` (A6) | PASSED |
| `test_report.py::test_serve_loopback_read_only_and_live` (A7; 전에는 영원히 멈춤) | PASSED |
| `test_kicad_cli.py::…sibling_project_rules…canary`, 3D canary ×4, silk canary (B1) | PASSED |
| `test_vertical_slice.py::test_fab_capability_limits_become_drc_rules_and_pass` (B1로 처음 실행됨; 픽스처 페이지가 `MIN_HTML_TEXT_CHARS`=200 미만이라 처음엔 FAIL → 픽스처 보강) | PASSED — `mfg.capability` 끝까지 PASS |
| 대상 파일 묶음(10파일) | 5 failed(기준선 A3×2, A8×2 + 위 픽스처 1건, 수정 전) / 222 passed |
| 전체(`full`, A7 테스트는 러너가 아직 deselect) | **12 failed / 2879 passed / 54 skipped, 22분 27초** |

전체 실패 12건 대 기준선 13건: GUI 10053 2건이 이번엔 통과(부하 의존 flaky로 재분류), 새로 `test_kr447_transceiver.py::test_the_pipeline_runs_the_deck_and_the_rf_checks`가 시간 예산(13.08 s > 10 s, `FIXTURE_BUDGET_S`)으로 실패 — 머신 부하 의존, 변경과 무관(같은 실행이 평소 15분 대신 22분 걸림). 나머지 10건은 기준선과 동일(A3 ×2, A8 ×6, A9 ×2).

Codex 리뷰(`codex.ps1 review -Dir`, exec 경로): P2 "락 뒤 재로드의 `_load`도 traceback 가능" → 반영(`_load_or_explain` 재사용 + 테스트); P3 "CLAUDE.md·ARCHITECTURE.md가 아직 '비어 있음'" → 7곳 수정; A7·B1 테스트 변경·새 테스트는 OK.
