# 제조사 혜택 연장 요금제 설계

사용자가 요청한 제조사(Samsung 또는 Apple)의 혜택 연장 요금제를 설계합니다.

## 워크플로우

1. **혜택 정보 조회**: `scrape_samsung_benefits()` 또는 `scrape_apple_benefits()` MCP 도구 호출
2. **SKT 요금제 조회**: `scrape_skt_plans()` MCP 도구 호출
3. **비용 계산**: `calculate_extension_cost()` MCP 도구로 연장 비용 산출
4. **결과 요약**: 제조사 무료 기간, 연장 기간, 총 비용을 사용자에게 안내

## 사용 가능한 MCP 도구

### scraper-mcp
- `scrape_samsung_benefits()`: 삼성 사전예약 혜택 (Gemini, Google One 등)
- `scrape_apple_benefits()`: 애플 사전예약 혜택 (Apple Music 개인/가족)
- `scrape_skt_plans()`: SKT 5GX 요금제 정보

### calculator-mcp
- `calculate_extension_cost(monthly_price_krw, free_months, term_months)`: 연장 비용 계산
- `compare_with_existing(extension_total_cost_krw, existing_total_cost_krw)`: 기존 요금제 비교
- `calculate_savings(existing_total_cost_krw, proposed_total_cost_krw)`: 절감액 산출

### storage-mcp
- `save_design(design)`: 설계 저장 (design에 manufacturer, rate_plan, benefit, term_months 필수)

## 기본값

- 약정 기간: 24개월 (선택약정)
- 제조사 무료 기간: 6개월
- 삼성 Gemini: 29,000원/월
- 애플 Apple Music (개인): 10,900원/월

## 응답 형식

설계 결과를 다음 형식으로 요약:

```
[제조사] [혜택명] 연장 설계

- 제조사 무료 기간: X개월
- SKT 연장 기간: Y개월 (약정 Z개월 - 무료 X개월)
- 월 단가: XX,XXX원
- 총 연장 비용: XXX,XXX원

저장하시겠습니까? (저장 시 /export-pdf로 PDF 출력 가능)
```

## 인자

$ARGUMENTS: 제조사명 또는 혜택명 (예: "삼성", "Samsung", "Gemini", "Apple", "애플뮤직")
