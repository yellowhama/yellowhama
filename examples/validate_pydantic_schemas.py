#!/usr/bin/env python3
"""AI Agent Master Guide - Pydantic 스키마 검증 스크립트"""

from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator
from typing import List, Dict
import json

# ============================================================
# 1. GameEvent 스키마 (가이드 Section 4.1)
# ============================================================

class EventChoice(BaseModel):
    """플레이어 선택지"""

    id: str = Field(..., description="선택지 고유 ID")
    label: str = Field(
        ...,
        description="""
        선택지 텍스트 (30자 이하)

        작성 가이드:
        - 명확한 동사로 시작
        - 결과를 암시하되 명시하지 않음
        - 도덕적으로 중립적 표현

        좋은 예: "백성의 세금을 인상하여 군비를 확충한다"
        나쁜 예: "세금 올림" (너무 짧음)
        """,
        min_length=10,
        max_length=30
    )

    effects: Dict[str, int] = Field(
        ...,
        description="""
        자원 변화 (resource_name: delta)

        사용 가능한 자원: wealth, influence, force, grace, spirit, intellect
        변화량 범위: -20 ~ +20
        """
    )

    @field_validator("effects")
    @classmethod
    def validate_effects_range(cls, v: Dict[str, int]) -> Dict[str, int]:
        """자원 변화량 범위 검증"""
        for resource, delta in v.items():
            if not -20 <= delta <= 20:
                raise ValueError(f"자원 {resource} 변화량 {delta}가 범위 [-20, 20] 초과")
        return v


class GameEvent(BaseModel):
    """게임 이벤트 스키마"""

    title: str = Field(
        ...,
        description="이벤트 제목 (20자 이하, 플레이어가 즉시 이해 가능해야 함)",
        min_length=5,
        max_length=20
    )

    narrative: str = Field(
        ...,
        description="이벤트 서사 (200자 이하)",
        max_length=200
    )

    choices: List[EventChoice] = Field(
        ...,
        description="플레이어 선택지 (2~4개, 각 선택지는 명확한 trade-off 포함)",
        min_items=2,
        max_items=4
    )

    @field_validator("title")
    @classmethod
    def title_must_be_descriptive(cls, v: str) -> str:
        """제목에 금지어 체크"""
        forbidden = ["이벤트", "선택", "테스트"]
        if any(word in v for word in forbidden):
            raise ValueError(f"제목에 일반적인 단어 사용 금지: {forbidden}")
        return v

    @model_validator(mode="after")
    def validate_balance(self) -> "GameEvent":
        """전체 밸런스 검증"""
        total_effects = {}
        for choice in self.choices:
            for resource, delta in choice.effects.items():
                total_effects[resource] = total_effects.get(resource, 0) + delta

        # 모든 선택지 합이 자원당 -10 ~ +10
        for resource, total in total_effects.items():
            if abs(total) > 10:
                raise ValueError(
                    f"자원 {resource}의 총 변화량 {total}이 불균형 (허용 범위: -10 ~ +10)"
                )

        return self

    class Config:
        json_schema_extra = {
            "example": {
                "title": "배신의 대가",
                "narrative": "당신의 충신이 적국과 내통한 증거가 발견되었습니다.",
                "choices": [
                    {
                        "id": "execute",
                        "label": "공개 처형으로 본보기를 보인다",
                        "effects": {"force": 5, "grace": -10, "influence": 3}
                    },
                    {
                        "id": "exile",
                        "label": "증거를 숨기고 조용히 추방한다",
                        "effects": {"grace": 5, "influence": -8, "wealth": -5}
                    }
                ]
            }
        }


# ============================================================
# 2. QualityMetrics 스키마 (가이드 Section 8.3)
# ============================================================

class QualityMetrics(BaseModel):
    """이벤트 품질 메트릭"""

    schema_valid: bool = Field(..., description="Pydantic 검증 통과")
    balance_score: float = Field(..., ge=0, le=1, description="자원 밸런스 (0~1)")
    clarity_score: float = Field(..., ge=0, le=1, description="텍스트 명확성")
    creativity_score: float = Field(..., ge=0, le=1, description="창의성")

    @property
    def overall_score(self) -> float:
        """가중 평균"""
        return (
            0.3 * float(self.schema_valid) +
            0.3 * self.balance_score +
            0.2 * self.clarity_score +
            0.2 * self.creativity_score
        )

    def passes_threshold(self, threshold=0.7) -> bool:
        return self.overall_score >= threshold


# ============================================================
# 3. 테스트 케이스
# ============================================================

def test_valid_event():
    """✅ 유효한 이벤트"""
    print("\n=== 테스트 1: 유효한 이벤트 ===")
    event_data = {
        "title": "충신의 배신",
        "narrative": "30년을 함께한 재상이 적국 대사와 밀회하는 모습이 목격되었습니다. 증거는 확실하지만, 그는 왕국의 모든 행정을 담당하고 있습니다.",
        "choices": [
            {
                "id": "execute",
                "label": "공개 처형으로 본보기를 보인다",
                "effects": {"force": 5, "grace": -10, "influence": 3}
            },
            {
                "id": "exile",
                "label": "증거를 숨기고 조용히 추방한다",
                "effects": {"grace": 5, "influence": -8, "wealth": -5}
            }
        ]
    }

    try:
        event = GameEvent(**event_data)
        print(f"✅ 검증 성공: {event.title}")
        print(f"   선택지 수: {len(event.choices)}")
        print(f"   서사 길이: {len(event.narrative)}자")
        return True
    except ValidationError as e:
        print(f"❌ 검증 실패: {e}")
        return False


def test_invalid_title():
    """❌ 금지어 포함 제목"""
    print("\n=== 테스트 2: 금지어 포함 제목 ===")
    event_data = {
        "title": "배신 이벤트",  # "이벤트" 금지어
        "narrative": "테스트 서사입니다.",
        "choices": [
            {
                "id": "c1",
                "label": "선택지 1을 선택한다",
                "effects": {"wealth": 5}
            },
            {
                "id": "c2",
                "label": "선택지 2를 선택한다",
                "effects": {"wealth": -5}
            }
        ]
    }

    try:
        event = GameEvent(**event_data)
        print(f"❌ 검증이 통과되어서는 안 됨: {event.title}")
        return False
    except ValidationError as e:
        print(f"✅ 예상대로 검증 실패: {e.errors()[0]['msg']}")
        return True


def test_unbalanced_resources():
    """❌ 자원 불균형"""
    print("\n=== 테스트 3: 자원 불균형 ===")
    event_data = {
        "title": "대규모 전쟁",
        "narrative": "전쟁이 발발했습니다.",
        "choices": [
            {
                "id": "c1",
                "label": "전쟁에 참전하여 승리한다",
                "effects": {"force": 15}  # 큰 증가
            },
            {
                "id": "c2",
                "label": "중립을 지킨다",
                "effects": {"force": -5}  # 작은 감소
            }
        ]
    }
    # 총 force 변화: 15 + (-5) = 10 (경계값)

    event_data_unbalanced = {
        "title": "대규모 전쟁",
        "narrative": "전쟁이 발발했습니다.",
        "choices": [
            {
                "id": "c1",
                "label": "전쟁에 참전하여 승리한다",
                "effects": {"force": 18}  # 큰 증가
            },
            {
                "id": "c2",
                "label": "중립을 지킨다",
                "effects": {"force": -5}  # 작은 감소
            }
        ]
    }
    # 총 force 변화: 18 + (-5) = 13 (불균형)

    try:
        event = GameEvent(**event_data)
        print(f"✅ 경계값 통과: force 총합 10")
    except ValidationError as e:
        print(f"❌ 경계값이 실패함: {e}")

    try:
        event = GameEvent(**event_data_unbalanced)
        print(f"❌ 불균형이 통과되어서는 안 됨")
        return False
    except ValidationError as e:
        print(f"✅ 예상대로 불균형 검출: {e.errors()[0]['msg']}")
        return True


def test_choice_length():
    """❌ 선택지 라벨 길이 제한"""
    print("\n=== 테스트 4: 선택지 라벨 길이 ===")
    event_data = {
        "title": "간단한 결정",
        "narrative": "결정이 필요합니다.",
        "choices": [
            {
                "id": "c1",
                "label": "짧음",  # 10자 미만
                "effects": {"wealth": 5}
            },
            {
                "id": "c2",
                "label": "일반적인 선택지입니다",
                "effects": {"wealth": -5}
            }
        ]
    }

    try:
        event = GameEvent(**event_data)
        print(f"❌ 짧은 라벨이 통과되어서는 안 됨")
        return False
    except ValidationError as e:
        print(f"✅ 예상대로 라벨 길이 검증 실패: {e.errors()[0]['msg']}")
        return True


def test_json_schema_generation():
    """JSON 스키마 생성 테스트"""
    print("\n=== 테스트 5: JSON 스키마 생성 ===")
    schema = GameEvent.model_json_schema()

    print("✅ JSON 스키마 생성 성공")
    print(f"   Properties: {list(schema['properties'].keys())}")
    print(f"   Required: {schema.get('required', [])}")

    # Anthropic Tool Use 형식 확인
    tool_schema = {
        "name": "create_game_event",
        "description": "게임 이벤트 생성",
        "input_schema": schema
    }

    print(f"   Tool name: {tool_schema['name']}")
    print(f"   Input schema type: {schema.get('type')}")

    return True


def test_quality_metrics():
    """품질 메트릭 테스트"""
    print("\n=== 테스트 6: 품질 메트릭 ===")

    # 고품질 이벤트
    high_quality = QualityMetrics(
        schema_valid=True,
        balance_score=0.9,
        clarity_score=0.85,
        creativity_score=0.8
    )

    print(f"고품질 이벤트: {high_quality.overall_score:.2f}")
    print(f"  임계값 0.7 통과: {high_quality.passes_threshold(0.7)}")

    # 저품질 이벤트
    low_quality = QualityMetrics(
        schema_valid=True,
        balance_score=0.5,
        clarity_score=0.4,
        creativity_score=0.3
    )

    print(f"저품질 이벤트: {low_quality.overall_score:.2f}")
    print(f"  임계값 0.7 통과: {low_quality.passes_threshold(0.7)}")

    return True


# ============================================================
# 메인 실행
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("AI Agent Master Guide - Pydantic 스키마 검증")
    print("=" * 60)

    results = []
    results.append(("유효한 이벤트", test_valid_event()))
    results.append(("금지어 제목", test_invalid_title()))
    results.append(("자원 불균형", test_unbalanced_resources()))
    results.append(("라벨 길이", test_choice_length()))
    results.append(("JSON 스키마", test_json_schema_generation()))
    results.append(("품질 메트릭", test_quality_metrics()))

    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print(f"\n총 {passed}/{total} 테스트 통과 ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 모든 스키마 검증 성공!")
        exit(0)
    else:
        print("\n⚠️  일부 테스트 실패")
        exit(1)
