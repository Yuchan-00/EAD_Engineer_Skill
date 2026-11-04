# G9: 결정성 가드 + 심은 결함 (2026-11-05 새벽)

- 날짜·머신: 2026-11-05 04:30–04:50, robotics-lab (Windows 11)
- 버전: ai-eda 0.0.1 (`work/ead-skill` 03bd642), KiCad 10.0.6, ngspice-46 (dll sha256 `3238d82f…`, `env.txt`), Python 3.12.10
- 명령(세션 scratchpad `g9/`에서, `PYTHONUTF8=1`, `AIEDA=B:\0) AI_Project\AI_EDA_Engineer\.venv\Scripts\ai-eda.exe`):
  1. `ai-eda new divider --dir ./divider --request "12 V to 5 V unloaded divider"`
  2. run 1: `ai-eda run ./divider/ir.json --answer application="bench reference" --answer jurisdiction=EU --answer input_voltage="12 V" --answer output_voltage="5 V" --no-pdf` → exit 1, `[confirm_design]` 표
  3. run 2: `ai-eda run ./divider/ir.json --answer confirm_design=yes --no-pdf` → exit 0, 19단계(calculation/spice/schematic/erc/pcb/drc/manufacturing_outputs PASS, 나머지 NOT_VERIFIED)
  4. run 3, run 4: `ai-eda run ./divider/ir.json --no-pdf` (답 없이, 같은 ir.json) → 둘 다 exit 0
  5. 결함: `parameters.r1.value`를 14000 → 12000으로 손으로 편집(derived 값) → run 5: `ai-eda run ./divider/ir.json --no-pdf`
- 원본 로그: 세션 scratchpad `g9/run1..5.txt`, `pipeline-run2..5.json`, `ir-run2..4.json` (레포에 넣지 않음, 합계 ~3 MB)
- 결과 한 줄: run3 vs run4 — `ir_hash` 동일, 19개 (stage, status, message) 전부 동일, pipeline.json 차이는 `at`·`ir_file_sha256`·`results_before`뿐; 결함 심은 run5 — calculation **FAIL**("3 derived value(s) do not match their calculator: r1: stored 12000.0, calc.divider.r1_for_v_out recomputes 14000.0 …"), independent_review FAIL(review.calculations_vs_design), repair FAIL(수리 불가, human), release FAIL, **exit 1**
- 뒷받침하는 plan 행: G9(§8.2), §4 6단계 PASS 조건, SKILL.md "Determinism" 불변식

## 1. 결정성 (같은 ir.json 두 번 실행)

| 비교 | 결과 |
|---|---|
| run2(확인 실행) vs run3 | **다름**이 정상: 확인 실행은 IR을 바꾼다(템플릿 적용·배치·배선). architecture `NOT_VERIFIED "17 proposal(s) applied … confirmed by the user"` → run3 `PASS "design content already present … design.inputs_vs_requirements PASS"`, placement 메시지 `"1 proposal(s) applied"` → `"not placed: ir.pcb already has 3 placement(s); the agent never replaces a layout …"`, `output_current` 선택 질문은 run3부터 없음 |
| run3 vs run4 (설계가 이미 있는 같은 ir.json) | `ir_hash` 동일(`sha256:b3eb73655d…`); `state.outcomes[]` 19개의 (stage, status, message) **전부 동일**; 차이는 `at`(타임스탬프), `ir_file_sha256`(실행마다 `validation.results[]`에 결과가 덧붙어 파일 해시가 바뀜: results_before 77 → 151), `results_before`뿐 |
| ir.json run3 vs run4 | 파일은 다름(결과 로그 누적 + 산출물 5개의 `content_hash` 변경: `.kicad_sch`/`.kicad_pcb` 등이 실행마다 재컴파일되고 내용 해시가 바뀜). 설계 내용(`ir_hash`가 덮는 부분)은 동일 |

→ SKILL.md "Determinism" 불변식의 원문 "the same `ir.json` run twice gives the same `pipeline.json` except timestamps"는 **정밀화 필요**: "except timestamps"만으로는 틀리다(ir_file_sha256·results_before도 바뀐다). 측정에 맞는 문장: *같은 설계(ir_hash)를 다시 실행하면 19단계의 status·message가 같다; pipeline.json에서 달라지는 것은 `at`, `ir_file_sha256`, `results_before`뿐(실행마다 ir.json에 결과가 덧붙는다). 확인 실행(confirm_design=yes)은 설계를 바꾸므로 그 전후는 비교 대상이 아니다.* — 2차 리뷰 반영 때 SKILL.md에 적용.

## 2. 심은 결함 (derived 값을 손으로 바꿈)

`parameters.r1.value` 14000 → 12000 (component R1의 14k, spice 값은 그대로) 뒤 run5:

```
calculation              FAIL   3 derived value(s) do not match their calculator: r1: stored 12000.0, calc.divider.r1_for_v_out recomputes 14000.0 from {'v_in': 12.0, 'v_out_target': 5.0, 'r2': 10000.0}; v_out: stored 5.0, calc.divider.v_out reco…
spice                    PASS   (회로의 실제 부품값 14k는 그대로라 v(VOUT) 5 V 기대는 통과 — 결함은 파라미터 장부에만 있음)
independent_review       FAIL   review FAIL: FAIL=1, NOT_VERIFIED=3, PASS=10
repair                   FAIL   repair: 1 iteration(s), 0/0 action(s) succeeded, 1 unresolved; stopped: no repairable failures remain
release                  FAIL   not releasable: overall validation is FAIL (calc.recompute, repair.loop, review.calculations_vs_design)
exit 1
```

PASS→FAIL 뒤집힘 확인: 같은 프로젝트가 run4에서 calculation PASS·release NOT_VERIFIED·exit 0이었다. 수리 루프는 설계 결함(human)이라 손대지 않고 멈춘다(SKILL.md "repair: regenerate/rerun_tool만"과 일치). 주의: spice는 PASS로 남는다 — 파라미터 장부와 부품값이 따로 놀 때 SPICE는 부품값을 믿는다; 에이전트는 calculation FAIL을 "minor"로 부르면 안 된다(상태표).
