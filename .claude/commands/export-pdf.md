# 요금제 설계 PDF 출력

저장된 설계를 PDF 스펙 문서로 출력합니다.

## 워크플로우

1. `get_design(design_id)` MCP 도구로 설계 상세 조회 (storage-mcp)
2. `generate_spec_document(output_path, spec)` MCP 도구로 PDF 생성 (pdf-mcp)
3. 생성된 PDF 경로를 사용자에게 안내

## 사용 가능한 MCP 도구

### storage-mcp
- `get_design(design_id)`: 설계 상세 조회

### pdf-mcp
- `generate_spec_document(output_path, spec)`: PDF 생성

## PDF spec 구조

```json
{
  "title": "요금제 설계 스펙 - [제조사] [혜택명]",
  "sections": {
    "기본 정보": [
      ["설계 ID", "design_xxx"],
      ["제조사", "Samsung"],
      ["할인 유형", "선택약정"]
    ],
    "요금제 정보": [
      ["요금제명", "5GX 플래티넘"],
      ["월정액", "93,750원"]
    ],
    "혜택 정보": [
      ["혜택명", "Google One AI Premium"],
      ["월 단가", "29,000원"],
      ["제조사 무료 기간", "6개월"]
    ],
    "비용 계산": [
      ["약정 기간", "24개월"],
      ["SKT 연장 기간", "18개월"],
      ["총 연장 비용", "522,000원"]
    ]
  },
  "notes": "메모 내용"
}
```

## 출력 경로

- 기본: `data/{design_id}.pdf`
- 예: `data/design_1738745123.pdf`

## 인자

$ARGUMENTS: design_id (필수). /list-designs로 ID 확인 가능.

## 응답 형식

```
PDF 생성 완료: data/design_xxx.pdf

포함 내용:
- 기본 정보 (설계 ID, 제조사, 할인 유형)
- 요금제 정보
- 혜택 정보
- 비용 계산 결과
```
