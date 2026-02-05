# 시뮬레이션 리포트 PDF 출력

저장된 시뮬레이션 시나리오를 PDF 리포트로 출력합니다. 요금제 스펙, 경쟁사 비교, 시나리오별 결과를 포함합니다.

## 워크플로우

1. `get_scenario(scenario_id)` MCP 도구로 시나리오 상세 조회 (storage-mcp)
2. 여러 시나리오 ID가 제공되면 모두 조회하여 비교
3. `generate_simulation_report(output_path, report_data)` MCP 도구로 PDF 생성 (pdf-mcp)
4. 생성된 PDF 경로를 사용자에게 안내

## 사용 가능한 MCP 도구

### storage-mcp
- `get_scenario(scenario_id)`: 시나리오 상세 조회
- `list_scenarios()`: 저장된 시나리오 목록 조회

### pdf-mcp
- `generate_simulation_report(output_path, report_data)`: 시뮬레이션 리포트 PDF 생성

## 리포트 구조

```json
{
  "title": "5G 저가 요금제 시뮬레이션 리포트",
  "sections": {
    "요약": [
      ["신규 요금제명", "5G 저가 플랜"],
      ["월정액", "35,000원"],
      ["주요 결과", "ARPU -X.XX% (기준 시나리오)"]
    ],
    "신규 요금제 스펙": [
      ["요금제명", "..."],
      ["월정액", "..."],
      ["데이터", "..."],
      ["음성", "..."],
      ["문자", "..."],
      ["속도제한", "..."],
      ["타겟 세그먼트", "..."],
      ["채널", "..."]
    ],
    "경쟁사 비교": [
      ["항목", "신규 요금제", "MVNO 평균", "타 통신사"],
      ["월정액", "...", "...", "..."],
      ["데이터", "...", "...", "..."]
    ],
    "시나리오 분석": {
      "보수적": [
        ["ARPU 변화", "-X.XX%"],
        ["연간 매출 영향", "-XXX,XXX,XXX원"],
        ["신규 가입자", "XX,XXX명"],
        ["다운그레이드", "XX,XXX명"],
        ["Win-back", "X,XXX명"]
      ],
      "기준": [...],
      "낙관적": [...]
    },
    "고가 요금제 옵션": [
      ["요금제명", "..."],
      ["월정액", "..."],
      ["예상 효과", "..."]
    ],
    "권고사항": [
      ["결론", "..."],
      ["다음 단계", "..."]
    ]
  }
}
```

## 출력 경로

- 기본: `data/simulation_report_{scenario_id}.pdf`
- 여러 시나리오: `data/simulation_report_comparison.pdf`

## 인자

$ARGUMENTS: 
- scenario_id (필수): 시나리오 ID 하나 또는 여러 개 (쉼표 구분)
- 예: "scenario_123" 또는 "scenario_123,scenario_456"

## 응답 형식

```
PDF 생성 완료: data/simulation_report_xxx.pdf

포함 내용:
- 요약 (Executive Summary)
- 신규 요금제 스펙
- 경쟁사 비교표
- 시나리오별 결과 (보수/기준/낙관)
- 고가 요금제 옵션 (있는 경우)
- 권고사항
```
