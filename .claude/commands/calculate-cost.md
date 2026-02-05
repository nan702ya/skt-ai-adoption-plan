# 혜택 연장 비용 빠른 계산

설계 저장 없이 혜택 연장 비용만 빠르게 계산합니다.

## 워크플로우

1. 인자로 받은 값 또는 기본값으로 `calculate_extension_cost()` 호출
2. 결과를 간단히 표시

## 사용 가능한 MCP 도구

### calculator-mcp
- `calculate_extension_cost(monthly_price_krw, free_months, term_months)`
- `compare_with_existing(extension_total_cost_krw, existing_total_cost_krw)`
- `calculate_savings(existing_total_cost_krw, proposed_total_cost_krw)`

## 기본값 참조

| 혜택 | 월 단가 | 무료 기간 |
|------|---------|-----------|
| Gemini (Google One AI Premium) | 29,000원 | 6개월 |
| Apple Music (개인) | 10,900원 | 6개월 |
| Apple Music (가족) | 16,900원 | 6개월 |

| 약정 | 기간 |
|------|------|
| 선택약정 | 24개월 |
| 공시지원금 | 12개월 |
| 무약정 | 0개월 |

## 응답 형식

```
비용 계산 결과:

- 월 단가: XX,XXX원
- 무료 기간: X개월
- 약정 기간: Y개월
- 연장 기간: Z개월
- 총 비용: XXX,XXX원

전체 설계를 진행하려면 /design-benefit을 사용하세요.
```

## 인자

$ARGUMENTS: "[월단가] [무료기간] [약정기간]" 또는 혜택명
- 예: "29000 6 24" → Gemini 24개월 약정
- 예: "gemini" → 기본값 사용 (29,000원, 6개월, 24개월)
- 예: "apple" → Apple Music 개인 기본값 (10,900원, 6개월, 24개월)
