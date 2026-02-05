# 5G 저가 요금제 설계

지방선거 대응 정부/국회 요구에 맞춘 **3만원대 5G 저가 요금제**를 설계합니다.

## 워크플로우

1. **타겟 가격대 입력**: 사용자로부터 목표 가격대 확인 (예: 35,000원)
2. **경쟁사 벤치마크 조회**: `scrape_skt_plans()` 또는 경쟁사 요금제 정보 수집
3. **스펙 설계**: data_gb, voice_minutes, sms_count, throttle_speed_kbps 결정
4. **저장**: `save_scenario()` 또는 별도 저장 로직으로 설계 저장

## 사용 가능한 MCP 도구

### scraper-mcp
- `scrape_skt_plans()`: SKT 5GX 요금제 정보 조회

### storage-mcp
- `save_scenario(scenario)`: 시나리오 저장 (필수: scenario_type, new_plan, migration_rates, winback_rate, results)

## 설계 기준

### 기본 스펙 가이드라인
- **데이터**: 50GB 이상 (3만원대 기준)
- **음성**: 무제한 또는 충분한 분량
- **문자**: 무제한 또는 충분한 건수
- **속도제한**: 소진 후 1Mbps 이상
- **타겟 세그먼트**: "general" | "youth" | "senior"
- **채널**: "online" | "offline" | "both"

### 경쟁사 벤치마크
- MVNO 평균: 30,000원, 50GB
- 타 통신사 저가 요금제: 35,000~40,000원

## 응답 형식

설계 결과를 다음 형식으로 요약:

```
5G 저가 요금제 설계 완료

- 요금제명: [이름]
- 월정액: XX,XXX원
- 데이터: XX GB
- 음성: 무제한 / XX분
- 문자: 무제한 / XX건
- 속도제한: XX Mbps
- 타겟 세그먼트: [general/youth/senior]
- 채널: [online/offline/both]

다음 단계: /simulate-migration으로 시뮬레이션 실행
```

## 인자

$ARGUMENTS: 목표 가격대 (예: "35000", "3만원대", "35,000원") 및 선택적 옵션 (타겟 세그먼트, 채널 등)
