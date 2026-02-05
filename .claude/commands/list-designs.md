# 저장된 요금제 설계 목록 조회

저장된 요금제 설계 목록을 조회합니다.

## 워크플로우

1. `list_designs()` MCP 도구 호출 (storage-mcp)
2. 결과를 테이블 형식으로 사용자에게 표시

## 사용 가능한 MCP 도구

### storage-mcp
- `list_designs()`: 설계 목록 조회
- `get_design(design_id)`: 설계 상세 조회
- `delete_design(design_id)`: 설계 삭제

## 응답 형식

```
저장된 설계 목록:

| ID | 제조사 | 약정 | 할인유형 | 생성일 | 메모 |
|----|--------|------|----------|--------|------|
| design_xxx | Samsung | 24개월 | 선택약정 | 2025-02-05 | ... |
```

설계가 없으면: "저장된 설계가 없습니다. /design-benefit으로 새 설계를 생성하세요."

## 추가 작업 안내

- 상세 조회: `get_design("design_id")` 호출
- PDF 출력: `/export-pdf design_id`
- 삭제: `delete_design("design_id")` 호출
