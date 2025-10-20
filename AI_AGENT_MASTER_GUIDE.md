# AI Agent 구축 마스터 가이드
**Claude Skills, ComfyUI, Pydantic을 활용한 전문 설계 에이전트 구축**

> **작성일**: 2025-10-21
> **대상 독자**: AI 에이전트 개발자, 게임 디자이너, 자동화 시스템 구축자
> **난이도**: 중급~고급

---

## 📋 목차

1. [핵심 개념 및 철학](#1-핵심-개념-및-철학)
2. [Claude Skills v2.0 아키텍처](#2-claude-skills-v20-아키텍처)
3. [ComfyUI 커스텀 노드 개발](#3-comfyui-커스텀-노드-개발)
4. [Pydantic 스키마 설계 전략](#4-pydantic-스키마-설계-전략)
5. [Multi-Agent 워크플로우 구현](#5-multi-agent-워크플로우-구현)
6. [실전 예제: GameDesigner + UXDesigner](#6-실전-예제-gamedesigner--uxdesigner)
7. [Best Practices & Common Pitfalls](#7-best-practices--common-pitfalls)
8. [Ultrathink 분석 및 최적화](#8-ultrathink-분석-및-최적화)

---

## 1. 핵심 개념 및 철학

### 1.1 AI Agent란 무엇인가?

AI Agent는 단순한 프롬프트 실행을 넘어, **자율적으로 작업을 분해하고, 도구를 선택하며, 결과를 검증하는 시스템**입니다.

**전통적 프롬프트 vs AI Agent:**

```
❌ 전통적 프롬프트:
"게임 디자인 문서를 작성해줘"
→ 단일 응답, 맥락 없음, 검증 불가

✅ AI Agent:
1. 요구사항 분석 (GameDesigner Agent)
2. 인과관계 추출 (Causality Analyzer)
3. UX 최적화 (UXDesigner Agent)
4. 스키마 검증 (Pydantic Validator)
5. 반복 개선 (Recursive Meta-Prompting)
```

### 1.2 핵심 설계 원칙

#### 원칙 1: Progressive Disclosure (점진적 공개)
**문제**: 모든 정보를 한 번에 주입하면 토큰 낭비 + 정확도 저하
**해결**: 필요한 시점에만 컨텍스트 로드

```yaml
# Claude Skill 구조
skill_name/
  SKILL.md          # 핵심 지침 (항상 로드)
  resources/        # 상세 자료 (필요시 로드)
    examples/
    schemas/
    templates/
```

#### 원칙 2: Schema-First Design (스키마 우선 설계)
**문제**: 자유형식 LLM 출력 → 파싱 에러, 일관성 부족
**해결**: Pydantic으로 출력 형식 강제

```python
from pydantic import BaseModel, Field

class GameEvent(BaseModel):
    """게임 이벤트 스키마 - LLM 출력 강제"""
    title: str = Field(..., description="이벤트 제목 (20자 이하)")
    triggers: list[str] = Field(..., min_items=1, description="발동 조건")
    consequences: dict[str, int] = Field(..., description="자원 변화 (resource: delta)")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "왕국의 배신",
                "triggers": ["player_loyalty < 30", "turn > 10"],
                "consequences": {"influence": -15, "wealth": 20}
            }
        }
```

#### 원칙 3: Tool Use Over Text Parsing
**문제**: 텍스트 파싱은 취약함 (형식 변화, 언어 차이)
**해결**: Anthropic Tool Use API로 구조화된 출력 강제

```python
# ❌ 나쁜 방법: 텍스트 파싱
response = llm("이벤트 3개 생성해줘")
events = parse_markdown_list(response)  # 깨지기 쉬움

# ✅ 좋은 방법: Tool Use
tools = [{
    "name": "create_event",
    "description": "게임 이벤트 생성",
    "input_schema": GameEvent.model_json_schema()
}]
response = llm(prompt, tools=tools)
events = [GameEvent(**call.input) for call in response.tool_calls]
```

#### 원칙 4: Prompt Chaining with Validation
**문제**: 단일 Agent는 복잡한 작업 처리 불가
**해결**: Agent 체인 + 각 단계 검증

```
GameDesigner → Validator → UXDesigner → Validator → Output
     ↓              ↓             ↓              ↓
  [Pydantic]   [Schema OK?]  [Pydantic]   [UX Score?]
```

---

## 2. Claude Skills v2.0 아키텍처

### 2.1 파일 시스템 기반 설계

Claude Skills는 **파일 시스템을 데이터베이스로 사용**하는 독특한 설계입니다.

**디렉토리 구조:**
```
~/.claude/skills/
├── gamedesigner/
│   ├── SKILL.md                 # 🔑 핵심 프롬프트 (항상 로드)
│   ├── resources/
│   │   ├── gdd_template.md      # 템플릿
│   │   ├── event_schema.json    # JSON 스키마
│   │   └── examples/
│   │       ├── rpg_example.yaml
│   │       └── strategy_example.yaml
│   └── tools/
│       └── validate_gdd.py      # 검증 도구
└── uxdesigner/
    ├── SKILL.md
    └── resources/
        └── ui_patterns.yaml
```

### 2.2 SKILL.md 작성 패턴

**기본 구조 (YAML Frontmatter + Markdown):**

```markdown
---
name: GameDesigner
version: 2.0.0
description: 게임 디자인 문서 생성 및 이벤트 설계
author: YourName
tags: [gamedev, gdd, rpg]
dependencies:
  - pydantic>=2.0
  - anthropic>=0.18
contexts:
  - resources/gdd_template.md
  - resources/event_schema.json
---

# GameDesigner Skill

## 역할 정의
당신은 20년 경력의 게임 디자이너입니다. RPG, 전략 시뮬레이션 게임의 이벤트 시스템을 설계합니다.

## 핵심 작업
1. **이벤트 생성**: 플레이어 선택지, 결과, 자원 변화 설계
2. **인과관계 검증**: 이벤트 간 논리적 연결성 확인
3. **밸런싱**: 자원 변화량 조정

## 출력 형식
반드시 `create_game_event` 도구를 사용하여 출력하세요.

```json
{
  "name": "create_game_event",
  "input": {
    "title": "이벤트 제목",
    "choices": [
      {"label": "선택지 1", "effects": {"wealth": 10}},
      {"label": "선택지 2", "effects": {"influence": -5}}
    ]
  }
}
```

## 제약 조건
- 이벤트 선택지는 2~4개
- 자원 변화는 -20 ~ +20 범위
- 모든 선택지는 명확한 trade-off 포함

## 예제
[resources/examples/rpg_example.yaml 참고]
```

### 2.3 Progressive Disclosure 구현

**문제**: 모든 예제를 SKILL.md에 넣으면 → 10K+ 토큰 낭비
**해결**: 참조 링크 + 필요시 로드

```markdown
# SKILL.md (핵심만)
## 예제
간단한 예제:
- 왕국 관리: [resources/examples/kingdom.yaml]
- 모험 이벤트: [resources/examples/adventure.yaml]

상세한 예제가 필요하면 "예제 로드"를 요청하세요.
```

**Claude Code에서 사용:**
```python
# 초기 로드 (SKILL.md만)
skill = load_skill("gamedesigner")  # ~500 토큰

# 필요시 추가 로드
if user_asks_for_example:
    example = load_resource("gamedesigner/resources/examples/kingdom.yaml")  # +2K 토큰
```

### 2.4 Skills 간 협업 패턴

**시나리오**: GameDesigner가 생성한 이벤트를 UXDesigner가 개선

```python
# 1단계: GameDesigner 실행
gamedesigner_skill = load_skill("gamedesigner")
raw_events = gamedesigner_skill.execute("중세 왕국 배신 이벤트 3개")

# 2단계: UXDesigner로 개선
uxdesigner_skill = load_skill("uxdesigner")
improved_events = uxdesigner_skill.execute(
    f"다음 이벤트들의 UX를 개선하세요:\n{raw_events}"
)
```

---

## 3. ComfyUI 커스텀 노드 개발

### 3.1 ComfyUI가 적합한 이유

**ComfyUI의 특징:**
1. **노드 기반 워크플로우**: 시각적 프로그래밍 (프롬프트 체인 표현에 이상적)
2. **캐싱 시스템**: `IS_CHANGED` 메서드로 불필요한 재실행 방지
3. **타입 안정성**: `INPUT_TYPES`, `RETURN_TYPES`로 연결 검증
4. **Python 네이티브**: 모든 Python 라이브러리 사용 가능

### 3.2 기본 노드 구조

```python
class ClaudeSkill_GameDesigner:
    """ComfyUI 커스텀 노드 - GameDesigner Skill 실행"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "게임 이벤트 생성"}),
                "skill_context": (["minimal", "standard", "full"], {"default": "standard"}),
            },
            "optional": {
                "previous_output": ("STRING", {"default": ""}),  # 체이닝용
            }
        }

    RETURN_TYPES = ("STRING", "DICT")
    RETURN_NAMES = ("raw_output", "structured_data")
    FUNCTION = "execute"
    CATEGORY = "AI Agents/Skills"

    def execute(self, prompt, skill_context, previous_output=""):
        # 1. Skill 로드
        skill = self.load_skill("gamedesigner", context_level=skill_context)

        # 2. 이전 출력 통합 (체이닝)
        if previous_output:
            prompt = f"이전 단계 출력:\n{previous_output}\n\n새 작업:\n{prompt}"

        # 3. Claude API 호출
        response = self.call_claude(skill.system_prompt, prompt)

        # 4. Tool Use 파싱
        structured = self.parse_tool_calls(response)

        return (response.text, structured)

    def load_skill(self, skill_name, context_level):
        """Progressive disclosure 구현"""
        skill_dir = Path(f"~/.claude/skills/{skill_name}").expanduser()

        # 항상 로드
        core = (skill_dir / "SKILL.md").read_text()

        # 컨텍스트 레벨에 따라 추가 로드
        if context_level == "standard":
            core += (skill_dir / "resources/event_schema.json").read_text()
        elif context_level == "full":
            examples = skill_dir / "resources/examples"
            for ex in examples.glob("*.yaml"):
                core += f"\n\n## 예제: {ex.name}\n{ex.read_text()}"

        return Skill(system_prompt=core)

    @classmethod
    def IS_CHANGED(cls, prompt, skill_context, previous_output=""):
        """캐싱 제어 - 입력이 같으면 재실행 안 함"""
        return hash((prompt, skill_context, previous_output))
```

### 3.3 Executor 노드 (Dynamic Skill Loading)

**문제**: Skill마다 노드를 만들면 → 100개 노드 관리 불가
**해결**: 단일 Executor 노드 + Skill 이름을 파라미터로

```python
class ClaudeSkill_Executor:
    """범용 Skill 실행 노드"""

    @classmethod
    def INPUT_TYPES(cls):
        # Skill 목록 동적 생성
        skills = cls.discover_skills()

        return {
            "required": {
                "skill_name": (skills, {"default": "gamedesigner"}),
                "prompt": ("STRING", {"multiline": True}),
            },
            "optional": {
                "context_files": ("STRING", {"default": ""}),  # 쉼표 구분 파일 경로
            }
        }

    RETURN_TYPES = ("STRING", "DICT")
    FUNCTION = "execute"

    @staticmethod
    def discover_skills():
        """~/.claude/skills/ 디렉토리 스캔"""
        skills_dir = Path("~/.claude/skills").expanduser()
        return [d.name for d in skills_dir.iterdir() if d.is_dir()]

    def execute(self, skill_name, prompt, context_files=""):
        # 동적 로드
        skill = self.load_skill(skill_name)

        # 추가 컨텍스트 파일 로드
        if context_files:
            for path in context_files.split(","):
                skill.add_context(Path(path.strip()).read_text())

        # 실행
        response = self.call_claude(skill.system_prompt, prompt)
        return (response.text, self.parse_tool_calls(response))
```

### 3.4 ComfyUI 워크플로우 예제

**시나리오**: GameDesigner → Validator → UXDesigner

```python
# ComfyUI 워크플로우 JSON
{
  "nodes": [
    {
      "id": 1,
      "type": "ClaudeSkill_Executor",
      "inputs": {
        "skill_name": "gamedesigner",
        "prompt": "중세 왕국 배신 이벤트 3개"
      }
    },
    {
      "id": 2,
      "type": "Pydantic_Validator",
      "inputs": {
        "schema": "GameEvent",
        "data": ["1", "structured_data"]  # 노드 1의 출력 연결
      }
    },
    {
      "id": 3,
      "type": "ClaudeSkill_Executor",
      "inputs": {
        "skill_name": "uxdesigner",
        "prompt": "다음 이벤트들의 가독성을 개선하세요",
        "previous_output": ["1", "raw_output"]  # 체이닝
      }
    }
  ],
  "links": [
    [1, "structured_data", 2, "data"],
    [1, "raw_output", 3, "previous_output"]
  ]
}
```

---

## 4. Pydantic 스키마 설계 전략

### 4.1 LLM을 위한 스키마 작성

**일반 개발 vs LLM 개발의 차이:**

```python
# ❌ 일반 개발 스타일 (LLM이 이해 못함)
class Event(BaseModel):
    t: str  # title
    c: list[dict]  # choices

# ✅ LLM 친화적 스타일
class GameEvent(BaseModel):
    """게임 이벤트 - 플레이어 선택과 결과를 정의합니다."""

    title: str = Field(
        ...,
        description="이벤트 제목 (20자 이하, 플레이어가 즉시 이해 가능해야 함)",
        min_length=5,
        max_length=20
    )

    choices: list[EventChoice] = Field(
        ...,
        description="플레이어 선택지 (2~4개, 각 선택지는 명확한 trade-off 포함)",
        min_items=2,
        max_items=4
    )
```

**핵심 원칙:**
1. **명시적 설명**: `description`에 제약 조건, 예제, 의도 명시
2. **중첩 모델**: 복잡한 구조는 별도 클래스로 분리
3. **검증 로직**: `@field_validator`로 비즈니스 룰 강제

### 4.2 Field Description as Embedded Prompts

**아이디어**: Field description을 LLM에게 주는 힌트로 활용

```python
class EventChoice(BaseModel):
    """플레이어 선택지"""

    label: str = Field(
        ...,
        description="""
        선택지 텍스트 (30자 이하)

        작성 가이드:
        - 명확한 동사로 시작 (예: "동맹 제안을 수락한다", "거절하고 전쟁을 선포한다")
        - 결과를 암시하되 명시하지 않음
        - 도덕적으로 중립적 표현 (플레이어가 판단하게)

        좋은 예: "백성의 세금을 인상하여 군비를 확충한다"
        나쁜 예: "세금 올림" (너무 짧음), "세금을 올려서 백성이 힘들어하지만 군대가 강해짐" (결과 명시)
        """
    )

    effects: dict[str, int] = Field(
        ...,
        description="""
        자원 변화 (resource_name: delta)

        사용 가능한 자원: wealth, influence, force, grace, spirit, intellect
        변화량 범위: -20 ~ +20

        설계 원칙:
        - 모든 선택지는 최소 1개 이상의 부정적 효과 포함 (trade-off)
        - 총 변화량 합이 -10 ~ +10 범위 (밸런스)
        - 자원 간 논리적 관계 유지 (예: wealth ↑ → grace ↓)
        """
    )
```

### 4.3 Anthropic Tool Use 통합

```python
from anthropic import Anthropic

client = Anthropic(api_key="...")

# Pydantic 모델을 Tool 스키마로 변환
tools = [
    {
        "name": "create_game_event",
        "description": "새 게임 이벤트 생성",
        "input_schema": GameEvent.model_json_schema()  # 🔑 자동 변환
    }
]

# Claude API 호출
response = client.messages.create(
    model="claude-opus-4-20250514",
    max_tokens=4096,
    tools=tools,
    messages=[{
        "role": "user",
        "content": "중세 왕국 배신 이벤트 3개 만들어줘"
    }]
)

# Tool call 파싱 → Pydantic 검증
for block in response.content:
    if block.type == "tool_use":
        try:
            event = GameEvent(**block.input)  # 🔑 자동 검증
            print(f"✅ Valid event: {event.title}")
        except ValidationError as e:
            print(f"❌ Invalid: {e}")
```

### 4.4 고급 검증 패턴

```python
from pydantic import field_validator, model_validator

class GameEvent(BaseModel):
    title: str
    choices: list[EventChoice]

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

        # 모든 선택지 합이 -10 ~ +10
        if any(abs(v) > 10 for v in total_effects.values()):
            raise ValueError(f"자원 변화 불균형: {total_effects}")

        return self
```

---

## 5. Multi-Agent 워크플로우 구현

### 5.1 Prompt Chaining 기본 패턴

**시퀀스**: Agent 1 → Agent 2 → Agent 3

```python
class PromptChain:
    """순차 Agent 체인"""

    def __init__(self, agents: list[Agent]):
        self.agents = agents

    def execute(self, initial_prompt: str) -> dict:
        context = {"user_input": initial_prompt}

        for agent in self.agents:
            # 이전 출력을 다음 입력으로
            result = agent.execute(context)
            context.update(result)

        return context

# 사용 예시
chain = PromptChain([
    GameDesignerAgent(),
    ValidationAgent(),
    UXDesignerAgent()
])

result = chain.execute("중세 왕국 배신 이벤트")
# result = {
#   "user_input": "...",
#   "gamedesigner_output": {...},
#   "validation_result": {...},
#   "uxdesigner_output": {...}
# }
```

### 5.2 Recursive Meta-Prompting

**개념**: 하위 Agent가 상위 Agent의 의도를 검증

```python
class MetaPromptingChain:
    """재귀적 메타 프롬프팅"""

    def execute(self, task: str) -> dict:
        # 1단계: GameDesigner가 이벤트 생성
        events = self.gamedesigner.execute(task)

        # 2단계: UXDesigner가 개선 (메타 프롬프트 포함)
        meta_prompt = f"""
        다음 이벤트를 개선하세요:
        {events}

        🔍 메타 검증 질문:
        1. 이 이벤트들이 원래 요청 "{task}"를 충족하는가?
        2. GameDesigner의 설계 의도가 명확히 전달되는가?
        3. 개선 과정에서 핵심 의도가 손상되지 않았는가?

        개선안을 제시하되, 위 질문에 대한 답변도 포함하세요.
        """

        improved = self.uxdesigner.execute(meta_prompt)

        # 3단계: 메타 검증 결과 확인
        if not improved["meta_validation_passed"]:
            # 재시도 또는 에러
            raise ValueError("메타 검증 실패: 원래 의도와 불일치")

        return improved
```

### 5.3 Parallel Agent Pattern

**시나리오**: 동일 입력을 여러 Agent가 병렬 처리 → 최적 선택

```python
import asyncio

class ParallelAgentEnsemble:
    """병렬 Agent 앙상블"""

    async def execute(self, prompt: str) -> dict:
        # 3개 Agent 동시 실행
        tasks = [
            self.gamedesigner_v1.execute_async(prompt),
            self.gamedesigner_v2.execute_async(prompt),
            self.gamedesigner_experimental.execute_async(prompt)
        ]

        results = await asyncio.gather(*tasks)

        # 가장 높은 품질 선택
        best = max(results, key=lambda r: r["quality_score"])

        return {
            "selected": best,
            "alternatives": results,
            "selection_reason": "highest quality score"
        }
```

### 5.4 Conditional Branching

**시나리오**: 검증 결과에 따라 다른 경로

```python
class ConditionalChain:
    """조건부 분기 체인"""

    def execute(self, task: str) -> dict:
        # 1단계: 초안 생성
        draft = self.gamedesigner.execute(task)

        # 2단계: 검증
        validation = self.validator.execute(draft)

        # 3단계: 조건부 분기
        if validation["score"] >= 0.8:
            # 고품질 → 바로 UX 개선
            final = self.uxdesigner.execute(draft)
        else:
            # 저품질 → 재생성 요청
            feedback = validation["issues"]
            revised = self.gamedesigner.execute(f"{task}\n\n이전 시도 문제점:\n{feedback}")
            final = self.uxdesigner.execute(revised)

        return final
```

---

## 6. 실전 예제: GameDesigner + UXDesigner

### 6.1 전체 시스템 아키텍처

```
User Input: "중세 왕국 배신 이벤트 3개"
     ↓
┌─────────────────────────────────────────────┐
│  ComfyUI Workflow                           │
├─────────────────────────────────────────────┤
│  [ClaudeSkill_Executor]                     │
│   skill_name: "gamedesigner"                │
│   context: "standard"                       │
│        ↓                                    │
│  [Pydantic_Validator]                       │
│   schema: GameEvent                         │
│   min_score: 0.7                            │
│        ↓                                    │
│  [ClaudeSkill_Executor]                     │
│   skill_name: "uxdesigner"                  │
│   previous_output: [from gamedesigner]      │
│        ↓                                    │
│  [Output_Formatter]                         │
│   format: "yaml"                            │
└─────────────────────────────────────────────┘
     ↓
Final Output: validated_events.yaml
```

### 6.2 GameDesigner Skill 구현

**파일: `~/.claude/skills/gamedesigner/SKILL.md`**

```markdown
---
name: GameDesigner
version: 2.1.0
description: RPG/전략 게임 이벤트 및 선택지 설계
dependencies:
  - pydantic>=2.0
contexts:
  - resources/event_schema.json
  - resources/design_principles.md
---

# GameDesigner Skill

## 역할
당신은 Crusader Kings, Mount & Blade 같은 전략 RPG의 이벤트 디자이너입니다.

## 핵심 원칙
1. **Meaningful Choices**: 모든 선택지는 명확한 trade-off
2. **Causality**: 이벤트는 논리적 선후관계
3. **Resource Tension**: 자원 간 상충 관계 활용

## 작업 프로세스
1. 주제 분석 → 핵심 갈등 식별
2. 선택지 설계 → 2~4개, 각각 장단점
3. 자원 효과 → -20 ~ +20, 합산 -10 ~ +10
4. 검증 → 밸런스, 논리성, 플레이어 이해도

## 출력 도구
반드시 `create_game_event` 도구 사용:

```json
{
  "name": "create_game_event",
  "input": {
    "title": "배신의 대가",
    "narrative": "당신의 충신이 적국과 내통한 증거가 발견되었습니다...",
    "choices": [
      {
        "id": "execute",
        "label": "공개 처형으로 본보기를 보인다",
        "effects": {"force": 5, "grace": -10, "influence": 3}
      }
    ]
  }
}
```

## 제약 조건
- 서사는 200자 이하
- 선택지 라벨은 30자 이하
- 자원 효과는 정수만
```

### 6.3 UXDesigner Skill 구현

**파일: `~/.claude/skills/uxdesigner/SKILL.md`**

```markdown
---
name: UXDesigner
version: 2.0.0
description: 게임 이벤트의 사용자 경험 최적화
contexts:
  - resources/ux_heuristics.md
---

# UXDesigner Skill

## 역할
당신은 게임 UX 전문가입니다. 이벤트의 가독성, 명확성, 감정적 임팩트를 개선합니다.

## 개선 체크리스트
- [ ] 서사가 즉시 상황 이해 가능한가?
- [ ] 선택지가 결과를 암시하지만 명시하지 않는가?
- [ ] 자원 변화가 직관적으로 이해되는가?
- [ ] 텍스트가 플레이어의 감정을 자극하는가?

## 개선 패턴
1. **서사 강화**: 구체적 디테일 추가 (인물, 장소, 시간)
2. **선택지 명확화**: 동사 강조, 결과 암시
3. **감정 유발**: 도덕적 딜레마, 긴박감 조성

## 출력
`improve_event_ux` 도구 사용:

```json
{
  "name": "improve_event_ux",
  "input": {
    "original_event_id": "betrayal_001",
    "improvements": {
      "narrative": "개선된 서사 텍스트",
      "choices": [...]
    },
    "ux_score": 8.5,
    "improvement_notes": "서사에 시간적 긴박감 추가, 선택지 라벨 동사 강조"
  }
}
```
```

### 6.4 ComfyUI 노드 전체 코드

```python
# custom_nodes/claude_skills/nodes.py

import json
from pathlib import Path
from anthropic import Anthropic
from pydantic import BaseModel, Field, ValidationError

class GameEvent(BaseModel):
    """게임 이벤트 스키마"""
    title: str = Field(..., max_length=20)
    narrative: str = Field(..., max_length=200)
    choices: list[dict] = Field(..., min_items=2, max_items=4)

class ClaudeSkill_GameDesigner:
    """GameDesigner Skill 실행 노드"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "task": ("STRING", {"multiline": True, "default": "이벤트 생성 요청"}),
                "num_events": ("INT", {"default": 3, "min": 1, "max": 10}),
            }
        }

    RETURN_TYPES = ("STRING", "LIST")
    RETURN_NAMES = ("raw_output", "validated_events")
    FUNCTION = "execute"
    CATEGORY = "AI Agents"

    def execute(self, task, num_events):
        # Skill 로드
        skill_path = Path("~/.claude/skills/gamedesigner/SKILL.md").expanduser()
        system_prompt = skill_path.read_text()

        # Tool 정의
        tools = [{
            "name": "create_game_event",
            "description": "게임 이벤트 생성",
            "input_schema": GameEvent.model_json_schema()
        }]

        # Claude API 호출
        client = Anthropic()
        response = client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=4096,
            system=system_prompt,
            tools=tools,
            messages=[{
                "role": "user",
                "content": f"{task}\n\n{num_events}개의 이벤트를 생성하세요."
            }]
        )

        # 검증
        validated_events = []
        for block in response.content:
            if block.type == "tool_use":
                try:
                    event = GameEvent(**block.input)
                    validated_events.append(event.model_dump())
                except ValidationError as e:
                    print(f"❌ Validation error: {e}")

        return (response.content[0].text, validated_events)

class ClaudeSkill_UXDesigner:
    """UXDesigner Skill 실행 노드"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "events": ("LIST",),  # GameDesigner 출력
            }
        }

    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("improved_events",)
    FUNCTION = "execute"
    CATEGORY = "AI Agents"

    def execute(self, events):
        skill_path = Path("~/.claude/skills/uxdesigner/SKILL.md").expanduser()
        system_prompt = skill_path.read_text()

        # 개선 요청
        client = Anthropic()
        improved = []

        for event in events:
            response = client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=2048,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": f"다음 이벤트의 UX를 개선하세요:\n{json.dumps(event, ensure_ascii=False)}"
                }]
            )

            # Tool call 파싱
            for block in response.content:
                if block.type == "tool_use" and block.name == "improve_event_ux":
                    improved.append(block.input)

        return (improved,)

# 노드 등록
NODE_CLASS_MAPPINGS = {
    "ClaudeSkill_GameDesigner": ClaudeSkill_GameDesigner,
    "ClaudeSkill_UXDesigner": ClaudeSkill_UXDesigner,
}
```

### 6.5 실행 결과 예시

**입력:**
```
"중세 왕국 배신 이벤트 3개"
```

**GameDesigner 출력:**
```json
[
  {
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
]
```

**UXDesigner 개선:**
```json
{
  "narrative": "새벽 3시, 밀정이 급보를 가져왔습니다. '30년 충신 재상이 적국 대사와 밀회' — 증거는 명확했습니다. 하지만 그가 없으면 왕국 행정이 마비됩니다. 동이 트기 전에 결정해야 합니다.",
  "choices": [
    {
      "label": "광장에서 공개 처형 — 배신의 대가를 만천하에 보인다",
      "effects": {"force": 5, "grace": -10, "influence": 3}
    },
    {
      "label": "증거를 불태우고 야밤에 추방 — 왕국의 치부를 감춘다",
      "effects": {"grace": 5, "influence": -8, "wealth": -5}
    }
  ],
  "ux_score": 8.7,
  "improvement_notes": "시간적 긴박감 추가 (새벽 3시, 동 트기 전), 선택지에 결과 암시 강화 ('만천하에', '치부를 감춘다')"
}
```

---

## 7. Best Practices & Common Pitfalls

### 7.1 Do's (권장 사항)

#### ✅ DO: Schema-First Development
```python
# 1. 먼저 Pydantic 모델 정의
class Quest(BaseModel):
    objective: str
    rewards: dict[str, int]

# 2. 스키마 기반 Tool 생성
tools = [{"name": "create_quest", "input_schema": Quest.model_json_schema()}]

# 3. 검증된 출력만 사용
quest = Quest(**llm_output)  # 자동 검증
```

#### ✅ DO: Progressive Disclosure
```python
# 기본 컨텍스트만 로드
skill = load_skill("gamedesigner", context="minimal")  # 500 tokens

# 필요시 확장
if user_needs_examples:
    skill.load_context("resources/examples/")  # +2000 tokens
```

#### ✅ DO: Explicit Validation Layers
```python
# Agent 출력 → 즉시 검증
result = gamedesigner_agent.execute(task)
validation = validator.validate(result)

if not validation.passed:
    # 재시도 또는 에러
    result = gamedesigner_agent.execute(f"{task}\n\nFix: {validation.issues}")
```

#### ✅ DO: Idempotent Operations
```python
# ComfyUI IS_CHANGED로 캐싱
@classmethod
def IS_CHANGED(cls, prompt):
    return hash(prompt)  # 같은 입력 → 재실행 안 함
```

### 7.2 Don'ts (피해야 할 것)

#### ❌ DON'T: Text Parsing
```python
# 나쁨: 텍스트 파싱
output = llm("이벤트 3개 생성")
events = re.findall(r'제목: (.+)', output)  # 깨지기 쉬움

# 좋음: Tool Use
events = [GameEvent(**call.input) for call in llm_tool_calls]
```

#### ❌ DON'T: Monolithic Prompts
```python
# 나쁨: 거대한 단일 프롬프트 (10K tokens)
prompt = f"""
당신은 게임 디자이너입니다.
{all_examples}  # 100개 예제
{all_rules}  # 모든 규칙
{all_schemas}  # 모든 스키마
"""

# 좋음: Progressive Disclosure
skill = load_skill("gamedesigner")  # 핵심만
if needed:
    skill.add_context("examples/specific_case.yaml")
```

#### ❌ DON'T: Unvalidated Chaining
```python
# 나쁨: 검증 없이 체이닝
result1 = agent1.execute()
result2 = agent2.execute(result1)  # result1이 유효한지 모름

# 좋음: 검증 포함
result1 = agent1.execute()
validate(result1)  # 실패시 에러
result2 = agent2.execute(result1)
```

### 7.3 Common Pitfalls

#### Pitfall 1: Overfitting to Examples
**문제**: 예제와 너무 비슷한 출력만 생성
**해결**:
```markdown
# SKILL.md
## 예제 사용 지침
다음 예제는 **형식 참고용**입니다. 내용은 창의적으로 다르게 만드세요.

❌ 예제와 동일한 "배신" 테마 반복
✅ 동일 형식, 다른 테마 (자연재해, 경제 위기 등)
```

#### Pitfall 2: Token Explosion
**문제**: 컨텍스트가 기하급수적으로 증가
**해결**:
```python
# 컨텍스트 크기 모니터링
def load_skill(name, max_tokens=5000):
    skill = Skill(name)
    if skill.token_count > max_tokens:
        raise ValueError(f"Skill too large: {skill.token_count} tokens")
    return skill
```

#### Pitfall 3: Validation Cascade Failures
**문제**: 검증 실패 → 재시도 → 또 실패 → 무한 루프
**해결**:
```python
MAX_RETRIES = 3

for attempt in range(MAX_RETRIES):
    result = agent.execute(task)
    if validate(result):
        break
    task += f"\n\n재시도 #{attempt+1}: {validation_errors}"
else:
    raise ValueError(f"Failed after {MAX_RETRIES} attempts")
```

---

## 8. Ultrathink 분석 및 최적화

### 8.1 로직 완전성 분석

**질문**: 현재 시스템이 모든 엣지 케이스를 처리하는가?

**체크리스트:**
- [ ] **LLM API 실패 처리**: 타임아웃, 레이트 리밋, 모델 에러
- [ ] **Pydantic 검증 실패**: 재시도 로직, 에러 피드백
- [ ] **Skill 로드 실패**: 파일 없음, 형식 오류
- [ ] **체이닝 중단**: 중간 Agent 실패시 복구

**개선안:**
```python
class RobustAgentChain:
    """에러 복구 기능이 있는 체인"""

    def execute(self, task, max_retries=3):
        context = {"task": task}

        for agent in self.agents:
            for attempt in range(max_retries):
                try:
                    result = agent.execute(context)
                    validate(result)  # Pydantic 검증
                    context.update(result)
                    break
                except ValidationError as e:
                    if attempt == max_retries - 1:
                        raise
                    context["retry_feedback"] = str(e)
                except APIError as e:
                    time.sleep(2 ** attempt)  # Exponential backoff

        return context
```

### 8.2 중복성 분석

**발견된 중복:**

1. **Skill 로딩 코드 중복**:
   ```python
   # 여러 노드에서 반복
   skill_path = Path(f"~/.claude/skills/{name}/SKILL.md").expanduser()
   system_prompt = skill_path.read_text()
   ```

   **개선**: 공통 `SkillLoader` 클래스
   ```python
   class SkillLoader:
       @staticmethod
       def load(skill_name, context_level="standard"):
           # 단일 구현
           ...
   ```

2. **Pydantic 검증 로직 중복**:
   ```python
   # 개선 전: 각 노드에서 반복
   for block in response.content:
       if block.type == "tool_use":
           event = GameEvent(**block.input)

   # 개선 후: 유틸리티 함수
   def extract_validated_tools(response, schema):
       return [schema(**b.input) for b in response.content if b.type == "tool_use"]
   ```

### 8.3 품질 임계값 설정

**현재 문제**: 주관적 판단으로 "좋은" 출력 결정

**해결책**: 정량적 메트릭

```python
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

# 사용
metrics = calculate_metrics(event)
if not metrics.passes_threshold(0.7):
    # 재생성 또는 개선
    event = improve(event, metrics.get_weaknesses())
```

### 8.4 최적화 전략

#### 전략 1: Skill Caching
```python
# 문제: 매번 SKILL.md 파일 읽기 (I/O 비용)
# 해결: 메모리 캐싱

from functools import lru_cache

@lru_cache(maxsize=10)
def load_skill(skill_name: str) -> Skill:
    """LRU 캐시로 최대 10개 Skill 메모리 유지"""
    path = Path(f"~/.claude/skills/{skill_name}/SKILL.md").expanduser()
    return Skill(system_prompt=path.read_text())
```

#### 전략 2: Parallel Validation
```python
# 문제: 순차 검증으로 시간 낭비
# 해결: 병렬 검증

import asyncio

async def validate_all(events: list[GameEvent]) -> list[bool]:
    """여러 이벤트 병렬 검증"""
    tasks = [validate_async(event) for event in events]
    return await asyncio.gather(*tasks)
```

#### 전략 3: Incremental Context Loading
```python
# 문제: 모든 예제를 한 번에 로드 (10K tokens)
# 해결: 점진적 로드

class IncrementalSkill:
    def __init__(self, name):
        self.name = name
        self.core = self.load_core()  # 500 tokens
        self.examples_loaded = False

    def ensure_examples(self):
        """필요시에만 예제 로드"""
        if not self.examples_loaded:
            self.core += self.load_examples()  # +2000 tokens
            self.examples_loaded = True
```

### 8.5 성능 벤치마크

**측정 대상:**
1. **Skill 로딩 시간**: 파일 I/O + 파싱
2. **LLM 응답 시간**: API 호출 → 응답
3. **검증 시간**: Pydantic 검증
4. **전체 체인 시간**: 시작 → 최종 출력

**벤치마크 코드:**
```python
import time

def benchmark_chain():
    times = {}

    start = time.time()
    skill = load_skill("gamedesigner")
    times["skill_load"] = time.time() - start

    start = time.time()
    response = call_claude(skill, "이벤트 3개")
    times["llm_response"] = time.time() - start

    start = time.time()
    events = [GameEvent(**call.input) for call in response.tool_calls]
    times["validation"] = time.time() - start

    return times

# 결과 예시:
# {
#   "skill_load": 0.05,  # 50ms
#   "llm_response": 3.2,  # 3.2초
#   "validation": 0.01  # 10ms
# }
```

**최적화 목표:**
- Skill 로딩: < 100ms (캐싱으로 달성 가능)
- LLM 응답: < 5초 (모델 속도 의존)
- 검증: < 50ms (Pydantic 충분히 빠름)
- 전체: < 10초 (사용자 체감 기준)

---

## 9. 실전 체크리스트

### 9.1 Skill 개발 체크리스트

- [ ] **SKILL.md 작성**
  - [ ] YAML frontmatter (name, version, description)
  - [ ] 역할 정의 명확
  - [ ] 출력 형식 예제 포함
  - [ ] 제약 조건 명시

- [ ] **Pydantic 스키마 정의**
  - [ ] 모든 필드에 `description` 작성
  - [ ] 검증 로직 (`@field_validator`) 구현
  - [ ] 예제 (`Config.json_schema_extra`) 포함

- [ ] **Tool 정의**
  - [ ] `input_schema`를 Pydantic에서 생성
  - [ ] `description`에 사용법 명시

- [ ] **테스트**
  - [ ] 단일 Skill 실행 성공
  - [ ] 검증 실패 케이스 처리
  - [ ] 토큰 사용량 측정 (< 5K)

### 9.2 ComfyUI 노드 체크리스트

- [ ] **INPUT_TYPES 정의**
  - [ ] 모든 필수 파라미터 포함
  - [ ] 기본값 설정
  - [ ] 타입 명시 (STRING, INT, LIST 등)

- [ ] **캐싱 구현**
  - [ ] `IS_CHANGED` 메서드 정의
  - [ ] 입력 해싱으로 재실행 방지

- [ ] **에러 처리**
  - [ ] API 실패 → 재시도
  - [ ] 검증 실패 → 명확한 에러 메시지

- [ ] **테스트**
  - [ ] 단일 노드 실행
  - [ ] 노드 체이닝 (A → B → C)
  - [ ] 병렬 실행 (A + B → C)

### 9.3 프로덕션 배포 체크리스트

- [ ] **보안**
  - [ ] API 키 환경변수 관리
  - [ ] Skill 파일 권한 설정 (읽기 전용)

- [ ] **모니터링**
  - [ ] 응답 시간 로깅
  - [ ] 검증 실패율 추적
  - [ ] 토큰 사용량 모니터링

- [ ] **백업**
  - [ ] Skill 파일 버전 관리 (Git)
  - [ ] 워크플로우 JSON 백업

- [ ] **문서화**
  - [ ] 사용 가이드 작성
  - [ ] API 레퍼런스
  - [ ] 트러블슈팅 가이드

---

## 10. 결론 및 다음 단계

### 10.1 핵심 요약

이 가이드에서 다룬 핵심:

1. **Claude Skills**: 파일 시스템 기반, Progressive Disclosure 구현
2. **ComfyUI**: 노드 기반 시각적 워크플로우, 캐싱 시스템
3. **Pydantic**: 스키마 우선 설계, LLM 출력 강제
4. **Multi-Agent**: Prompt Chaining, Meta-Prompting, Conditional Branching
5. **Best Practices**: Schema-First, Tool Use, Validation Layers

### 10.2 학습 경로

**초급 (1-2주)**:
1. Pydantic 기본 문법 숙달
2. 간단한 Claude Skill 작성 (1개)
3. ComfyUI 기본 노드 개발

**중급 (2-4주)**:
4. Multi-Agent 체인 구현 (2-3개 Agent)
5. Progressive Disclosure 최적화
6. 검증 로직 고도화

**고급 (4주+)**:
7. Recursive Meta-Prompting
8. 병렬 Agent 앙상블
9. 프로덕션 배포 및 모니터링

### 10.3 추가 자료

**공식 문서**:
- [Anthropic Tool Use Guide](https://docs.anthropic.com/claude/docs/tool-use)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [ComfyUI Custom Nodes](https://github.com/comfyanonymous/ComfyUI)

**커뮤니티**:
- Claude Discord 서버
- r/LocalLLaMA (Reddit)
- ComfyUI GitHub Discussions

**오픈소스 예제**:
- [claude-skills-examples](https://github.com/example/claude-skills) (가상)
- [comfyui-agent-nodes](https://github.com/example/agent-nodes) (가상)

---

**문서 버전**: 1.0.0
**최종 수정**: 2025-10-21
**라이선스**: MIT
**기여**: GitHub Issues/PRs 환영
