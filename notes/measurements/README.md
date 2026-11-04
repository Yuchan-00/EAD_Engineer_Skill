# 측정 기록 규칙

plan의 "측정됨" 주장은 전부 이 폴더의 날짜 폴더(`YYYY-MM-DD/`)가 뒷받침한다. 다른 PC에서 다른 값이 나오면 무엇이 움직였는지(앵커인지 엔진인지) 가릴 수 있어야 한다.

## 날짜 폴더마다 필수

1. `README.md` — 측정 파일마다 아래 헤더 6줄:
   - 날짜(ISO) · 머신(호스트명/OS)
   - 버전: KiCad(kicad-cli), ngspice, Python, 참고 레포 커밋
   - 정확한 명령(복사해 다시 돌릴 수 있는 형태, 경로 포함)
   - 원본 로그 위치(레포에 넣지 않았으면 "없음(크기)")
   - 결과 한 줄(숫자 포함)
   - 뒷받침하는 plan 행 id(A7, B1, §7.1 …)
2. `env.txt` — `ai-eda doctor --strict`의 전체 출력, 참고 레포 커밋 해시, `ngspice.dll`의 sha256.

## 지금 있는 것

- `2026-11-04/` — 첫 측정(robotics-lab, KiCad 10.0.6, ngspice-46, Python 3.12.10, 참고 커밋 `4ee4d8e`). `env.txt`는 다음 측정 때 추가한다.
- `2026-11-05/` — A단계 마무리(robotics-lab, 참고 커밋 `03bd642`, 스킬 11250a2 → 2차 리뷰 반영본): `env.txt`(doctor 전체 출력·ngspice.dll sha256), `g9-determinism-seeded-defect.md`, `step6-trigger-test-2.md`, `step6-review-2.md`.
