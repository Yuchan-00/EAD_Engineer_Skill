# A8 제품 결함 2건 수정 검증 (2026-11-04)

- 날짜·머신: 2026-11-04, robotics-lab (Windows 11)
- 버전: KiCad 10.0.6, ngspice-46, Python 3.12.10, 참고 레포 `work/ead-skill` 커밋 13cdb5b
- 명령: `scripts\aieda-test.ps1 files tests/test_rf_selection.py tests/test_leave_out.py tests/test_report.py tests/test_gui_server.py tests/test_catalog_lc_lowpass.py tests/test_cli_bad_ir.py`; 전체는 아래
- 원본 로그: `B:\0) AI_Project\.logs\pytest-files-20261104-174536.txt`, `.logs\pytest-full-*.txt`(아래)
- 뒷받침하는 행: A8 (§3.1-b 표의 보고서 인용 3건 + GUI 10053 2건), §3.5 A8/A9

| 검사 | 결과 |
|---|---|
| `shell_path()` 손 확인 | `C:\Users\…\ir.json` → 그대로; `p\ir.json` → 그대로; `C:\My Docs\ir.json` → `"C:\My Docs\ir.json"` |
| `test_report.py::test_report_of_offline_divider_run`, `…::test_questions_have_answer_commands_and_model_labels` | PASSED(이전 FAILED) |
| `test_leave_out.py::…leave_out_in_the_report…` | 테스트의 `Path("p/ir.json")` 기대 문자열을 OS 중립(`str(Path(...))`)으로 고친 뒤 PASSED |
| `test_gui_server.py::test_post_needs_the_pages_own_origin_and_a_json_body`, `…::test_the_run_endpoints_need…`, `…::test_host_guard_answers_only_for_this_machine` | PASSED(이전 10053로 간헐 FAILED) — 거부 전 본문 소진 |
| 묶음 6파일 | 134 passed / 1 failed(두 번째 경로 단언 → 같은 방식으로 수정 뒤 29 passed) |
| 전체(`full`, 13cdb5b) | **10 failed / 2898 passed / 54 skipped, 21분 07초** — 기준선 8건(A3 ×1, A8 잔여 4건: claude_cli ×2·snap·벽시계, A9 ×2) + KR447 시간 예산 2건(부하 의존: Codex 리뷰와 동시 실행으로 21분 소요); 보고서 인용 3건·GUI 10053 3건은 통과 → **Windows 기준선 13 → 8(+부하 의존)** |

Codex 리뷰(13cdb5b) 반영(후속 커밋): POSIX에서 역슬래시 경로는 bare로 쓰지 않음; Windows에서 `$`·백틱·`%`·`"`·셸 연산자가 든 경로는 `"…"` 대신 PowerShell `'…'`(cmd.exe는 못 읽음 — 독스트링에 명시); 본문 소진 읽기에 2초 소켓 타임아웃(`DRAIN_TIMEOUT_S`); 인용 규칙 단위 테스트 1개 추가(OS별 6경우).

남은 A8 실패(Windows 분기로 처리할 것): `test_claude_cli_client` 2건(자식 종료 경로 WinError 87, 인코딩 불가 인수 분류), `test_report_pdf` snap 판정, `test_md_review_findings_regressions::test_7`(벽시계 동일성).
