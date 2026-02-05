# 요금제 설계 시스템 사용 가이드

SKT 요금제 설계 시스템의 MCP 도구 사용법입니다.

---

## 시스템 개요

삼성/애플 플래그십폰 구매 시 제공되는 무료 혜택(Gemini, Apple Music 등)이 종료된 후,
SKT 요금제 유지 고객에게 해당 혜택을 연장 제공하는 요금제 설계를 지원합니다.

### MCP 서버 구성

| 서버 | 역할 |
|------|------|
| `scraper` | 제조사 혜택/SKT 요금제 정보 수집 |
| `storage` | 설계 데이터 저장/조회 (SQLite) |
| `calculator` | 연장 비용 계산, 절감액 산출 |
| `pdf` | 스펙 문서 PDF 생성 |

---

## 환경 설정

```bash
# 가상환경 활성화
source .venv/bin/activate

# 의존성 설치 (최초 1회)
pip install mcp httpx beautifulsoup4 reportlab
```

MCP 서버는 Claude Code에서 자동으로 연결됩니다 (`.mcp.json` 설정 참조).

---

## MCP 도구 레퍼런스

### 1. scraper-mcp

#### `scrape_samsung_benefits()`
삼성 사전예약 혜택 정보를 반환합니다.

**반환 예시:**
```json
{
  "manufacturer": "Samsung",
  "name": "Google One AI Premium",
  "free_months": 6,
  "monthly_price_krw": 29000,
  "notes": "Gemini Advanced + 2TB 포함",
  "fetch_status": "ok",
  "data_source": "hardcoded_mvp"
}
```

#### `scrape_apple_benefits()`
애플 사전예약 혜택 정보를 반환합니다 (개인/가족 요금제).

#### `scrape_skt_plans()`
T-world 5GX 요금제 정보를 반환합니다.

---

### 2. storage-mcp

#### `save_design(design: dict)`
요금제 설계를 저장합니다.

**필수 필드:**
- `manufacturer`: 제조사 (Samsung, Apple)
- `rate_plan`: 요금제 정보 (dict)
- `benefit`: 혜택 정보 (dict)
- `term_months`: 약정 기간

**선택 필드:**
- `design_id`: 설계 ID (자동 생성)
- `discount_type`: 할인 유형 (기본: 선택약정)
- `memo`: 메모

**예시:**
```python
save_design({
    "manufacturer": "Samsung",
    "rate_plan": {"name": "5GX 플래티넘", "monthly_fee_krw": 93750},
    "benefit": {"name": "Google One AI Premium", "monthly_price_krw": 29000},
    "term_months": 24,
    "memo": "갤럭시 S25 사전예약 연장 혜택"
})
```

#### `list_designs()`
저장된 설계 목록을 조회합니다.

#### `get_design(design_id: str)`
특정 설계의 상세 정보를 조회합니다.

#### `delete_design(design_id: str)`
설계를 삭제합니다.

---

### 3. calculator-mcp

#### `calculate_extension_cost(monthly_price_krw, free_months, term_months)`
혜택 연장 비용을 계산합니다.

**파라미터:**
- `monthly_price_krw`: 월 단가 (원)
- `free_months`: 제조사 무료 제공 기간 (개월)
- `term_months`: 총 약정 기간 (개월)

**예시:**
```
calculate_extension_cost(29000, 6, 24)
→ { "extension_months": 18, "total_cost_krw": 522000 }
```

#### `compare_with_existing(extension_total_cost_krw, existing_total_cost_krw)`
기존 제휴 요금제 대비 비용을 비교합니다.

**반환값:**
- `result`: `extension_cheaper` | `existing_cheaper` | `same_cost`
- `difference_krw`: 차액

#### `calculate_savings(existing_total_cost_krw, proposed_total_cost_krw)`
절감액을 산출합니다.

---

### 4. pdf-mcp

#### `generate_spec_document(output_path, spec)`
요금제 스펙 문서 PDF를 생성합니다.

**파라미터:**
- `output_path`: 출력 경로 (예: `data/spec.pdf`)
- `spec`: 문서 내용 (dict)

**spec 구조:**
```json
{
  "title": "요금제 설계 스펙",
  "font_path": null,
  "sections": {
    "기본 정보": [["제조사", "Samsung"], ["요금제", "5GX 플래티넘"]],
    "비용 계산": [["연장 기간", "18개월"], ["총 비용", "522,000원"]]
  },
  "notes": "선택약정 24개월 기준"
}
```

---

## 사용 시나리오

### 시나리오 1: 삼성 갤럭시 + Gemini 연장 설계

```
사용자: "갤럭시 S25 구매 고객이 Gemini 혜택 연장받으면 비용이 얼마나 들어?"

Claude:
1. scrape_samsung_benefits() 호출 → Gemini 29,000원/월, 6개월 무료
2. calculate_extension_cost(29000, 6, 24) → 18개월 × 29,000원 = 522,000원
3. 결과 요약 제공
```

### 시나리오 2: 설계 저장 및 PDF 출력

```
사용자: "방금 계산한 내용으로 설계 저장하고 PDF로 만들어줘"

Claude:
1. save_design({...}) → design_1234 저장
2. generate_spec_document("data/design_1234.pdf", {...}) → PDF 생성
3. 저장 경로 안내
```

### 시나리오 3: 기존 제휴 요금제 비교

```
사용자: "기존 넷플릭스 제휴 요금제랑 비교해줘"

Claude:
1. scrape_skt_plans() → 기존 요금제 정보 확인
2. compare_with_existing(522000, 600000) → 연장이 78,000원 저렴
3. calculate_savings(600000, 522000) → 78,000원 절감
```

---

## 데이터 위치

| 항목 | 경로 |
|------|------|
| SQLite DB | `data/rate_plans.db` |
| PDF 출력 | `data/*.pdf` |
| 스키마 | `mcp_servers/storage/schema.sql` |

---

## 주의사항

1. **MVP 한계**: 현재 scraper는 하드코딩된 데이터 반환 (Phase 2에서 실제 크롤링 구현 예정)
2. **fetch_status 확인**: 스크래퍼 결과의 `fetch_status`가 `ok`가 아니면 데이터 신뢰성 주의
3. **한글 폰트**: PDF에 한글 표시 시 `font_path`에 TTF 파일 경로 지정 필요

---

## 문의

Linear 이슈: [SKT-5](https://linear.app/skt-ai-adoption/issue/SKT-5)
