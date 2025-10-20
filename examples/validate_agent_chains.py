#!/usr/bin/env python3
"""AI Agent Master Guide - Agent Chain 로직 검증"""

from typing import Dict, List, Any
from dataclasses import dataclass
import time


# ============================================================
# Mock Agent Classes
# ============================================================

@dataclass
class AgentResult:
    """Agent 실행 결과"""
    agent_name: str
    output: Any
    execution_time: float
    metadata: Dict[str, Any]


class MockAgent:
    """테스트용 Mock Agent"""

    def __init__(self, name: str, delay: float = 0.1):
        self.name = name
        self.delay = delay

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        """Agent 실행 (Mock)"""
        time.sleep(self.delay)  # API 호출 시뮬레이션

        output = {
            "agent": self.name,
            "processed_input": context.get("user_input", ""),
            "result": f"{self.name} processed the input"
        }

        return AgentResult(
            agent_name=self.name,
            output=output,
            execution_time=self.delay,
            metadata={"success": True}
        )


# ============================================================
# 1. Prompt Chaining (가이드 Section 5.1)
# ============================================================

class PromptChain:
    """순차 Agent 체인"""

    def __init__(self, agents: List[MockAgent]):
        self.agents = agents

    def execute(self, initial_prompt: str) -> Dict[str, Any]:
        context = {"user_input": initial_prompt}
        results = []

        for agent in self.agents:
            # 이전 출력을 다음 입력으로
            result = agent.execute(context)
            context[f"{agent.name}_output"] = result.output
            results.append(result)

        context["chain_results"] = results
        return context


# ============================================================
# 2. Conditional Branching (가이드 Section 5.4)
# ============================================================

class ConditionalChain:
    """조건부 분기 체인"""

    def __init__(
        self,
        initial_agent: MockAgent,
        validator: callable,
        high_quality_agent: MockAgent,
        low_quality_agent: MockAgent
    ):
        self.initial_agent = initial_agent
        self.validator = validator
        self.high_quality_agent = high_quality_agent
        self.low_quality_agent = low_quality_agent

    def execute(self, task: str) -> Dict[str, Any]:
        # 1단계: 초안 생성
        draft = self.initial_agent.execute({"user_input": task})

        # 2단계: 검증
        validation = self.validator(draft.output)

        # 3단계: 조건부 분기
        if validation["score"] >= 0.8:
            # 고품질 → 바로 개선
            final = self.high_quality_agent.execute({"user_input": draft.output})
            branch_taken = "high_quality"
        else:
            # 저품질 → 피드백 포함 재생성
            context = {
                "user_input": task,
                "feedback": validation["issues"]
            }
            final = self.low_quality_agent.execute(context)
            branch_taken = "low_quality_retry"

        return {
            "draft": draft,
            "validation": validation,
            "final": final,
            "branch_taken": branch_taken
        }


# ============================================================
# 3. Robust Agent Chain with Error Recovery (가이드 Section 8.1)
# ============================================================

class RobustAgentChain:
    """에러 복구 기능이 있는 체인"""

    def __init__(self, agents: List[MockAgent], max_retries: int = 3):
        self.agents = agents
        self.max_retries = max_retries

    def execute(self, task: str) -> Dict[str, Any]:
        context = {"task": task}
        errors = []

        for agent in self.agents:
            for attempt in range(self.max_retries):
                try:
                    result = agent.execute(context)

                    # 간단한 검증 (실제로는 Pydantic)
                    self._validate(result)

                    context[f"{agent.name}_output"] = result.output
                    break
                except ValueError as e:
                    if attempt == self.max_retries - 1:
                        raise
                    context["retry_feedback"] = str(e)
                    errors.append({"agent": agent.name, "attempt": attempt, "error": str(e)})

        context["errors_encountered"] = errors
        return context

    def _validate(self, result: AgentResult):
        """검증 (Mock)"""
        if "processed" not in result.output.get("result", ""):
            raise ValueError("Invalid output format")


# ============================================================
# 4. Meta-Prompting Chain (가이드 Section 5.2)
# ============================================================

class MetaPromptingChain:
    """재귀적 메타 프롬프팅"""

    def __init__(self, designer_agent: MockAgent, reviewer_agent: MockAgent):
        self.designer = designer_agent
        self.reviewer = reviewer_agent

    def execute(self, task: str) -> Dict[str, Any]:
        # 1단계: Designer가 작업 수행
        design = self.designer.execute({"user_input": task})

        # 2단계: Reviewer가 메타 검증 수행
        meta_context = {
            "user_input": design.output,
            "original_task": task,
            "meta_questions": [
                f"이 결과가 원래 요청 '{task}'를 충족하는가?",
                "설계 의도가 명확히 전달되는가?",
                "개선 과정에서 핵심 의도가 손상되지 않았는가?"
            ]
        }

        review = self.reviewer.execute(meta_context)

        # 3단계: 메타 검증 결과 확인
        meta_validation_passed = self._check_meta_validation(review.output)

        if not meta_validation_passed:
            raise ValueError("메타 검증 실패: 원래 의도와 불일치")

        return {
            "design": design,
            "review": review,
            "meta_validation_passed": meta_validation_passed
        }

    def _check_meta_validation(self, review_output: Dict) -> bool:
        """메타 검증 체크 (Mock)"""
        return review_output.get("result", "") != ""


# ============================================================
# 테스트 케이스
# ============================================================

def test_prompt_chain():
    """✅ 순차 체인 테스트"""
    print("\n=== 테스트 1: Prompt Chain ===")

    agents = [
        MockAgent("GameDesigner", delay=0.05),
        MockAgent("Validator", delay=0.02),
        MockAgent("UXDesigner", delay=0.05)
    ]

    chain = PromptChain(agents)
    result = chain.execute("중세 왕국 배신 이벤트")

    print(f"✅ 체인 실행 성공")
    print(f"   실행된 Agent 수: {len(result['chain_results'])}")
    print(f"   최종 컨텍스트 키: {list(result.keys())}")

    # 검증: 각 Agent 출력이 컨텍스트에 포함되어야 함
    for agent in agents:
        assert f"{agent.name}_output" in result, f"{agent.name} 출력 누락"

    return True


def test_conditional_chain():
    """✅ 조건부 분기 테스트"""
    print("\n=== 테스트 2: Conditional Chain ===")

    def mock_validator(output: Dict) -> Dict:
        """Mock 검증 함수"""
        # 짝수 초에는 고품질, 홀수 초에는 저품질
        score = 0.9 if int(time.time()) % 2 == 0 else 0.5
        return {
            "score": score,
            "issues": [] if score >= 0.8 else ["품질 미달"]
        }

    chain = ConditionalChain(
        initial_agent=MockAgent("InitialDesigner"),
        validator=mock_validator,
        high_quality_agent=MockAgent("UXImprover"),
        low_quality_agent=MockAgent("Redesigner")
    )

    result = chain.execute("이벤트 생성")

    print(f"✅ 조건부 체인 실행 성공")
    print(f"   초안 품질: {result['validation']['score']:.2f}")
    print(f"   선택된 분기: {result['branch_taken']}")

    assert "branch_taken" in result
    assert result["branch_taken"] in ["high_quality", "low_quality_retry"]

    return True


def test_robust_chain():
    """✅ 에러 복구 체인 테스트"""
    print("\n=== 테스트 3: Robust Chain with Error Recovery ===")

    agents = [
        MockAgent("Agent1"),
        MockAgent("Agent2"),
        MockAgent("Agent3")
    ]

    chain = RobustAgentChain(agents, max_retries=3)

    try:
        result = chain.execute("테스트 작업")
        print(f"✅ 에러 복구 체인 실행 성공")
        print(f"   발생한 에러 수: {len(result['errors_encountered'])}")

        assert "errors_encountered" in result
        return True
    except Exception as e:
        print(f"❌ 에러 복구 실패: {e}")
        return False


def test_meta_prompting():
    """✅ 메타 프롬프팅 테스트"""
    print("\n=== 테스트 4: Meta-Prompting Chain ===")

    chain = MetaPromptingChain(
        designer_agent=MockAgent("Designer"),
        reviewer_agent=MockAgent("Reviewer")
    )

    try:
        result = chain.execute("복잡한 이벤트 설계")
        print(f"✅ 메타 프롬프팅 실행 성공")
        print(f"   메타 검증 통과: {result['meta_validation_passed']}")

        assert result["meta_validation_passed"] == True
        return True
    except Exception as e:
        print(f"❌ 메타 프롬프팅 실패: {e}")
        return False


def test_chaining_performance():
    """⏱️ 체인 성능 테스트"""
    print("\n=== 테스트 5: Chaining Performance ===")

    agents = [MockAgent(f"Agent{i}", delay=0.05) for i in range(5)]
    chain = PromptChain(agents)

    start = time.time()
    result = chain.execute("성능 테스트")
    elapsed = time.time() - start

    total_agent_time = sum(r.execution_time for r in result["chain_results"])

    print(f"✅ 성능 측정 완료")
    print(f"   전체 실행 시간: {elapsed:.3f}초")
    print(f"   Agent 실행 시간 합: {total_agent_time:.3f}초")
    print(f"   오버헤드: {(elapsed - total_agent_time):.3f}초")

    # 오버헤드가 10% 미만이어야 함
    overhead_ratio = (elapsed - total_agent_time) / total_agent_time
    assert overhead_ratio < 0.1, f"오버헤드 과다: {overhead_ratio:.1%}"

    return True


def test_context_preservation():
    """✅ 컨텍스트 보존 테스트"""
    print("\n=== 테스트 6: Context Preservation ===")

    agents = [
        MockAgent("Agent1"),
        MockAgent("Agent2"),
        MockAgent("Agent3")
    ]

    chain = PromptChain(agents)
    result = chain.execute("컨텍스트 테스트")

    # 모든 중간 결과가 보존되어야 함
    print(f"✅ 컨텍스트 보존 확인")
    print(f"   보존된 출력 수: {len([k for k in result.keys() if '_output' in k])}")

    for agent in agents:
        key = f"{agent.name}_output"
        assert key in result, f"{key} 누락"
        print(f"   ✓ {key} 보존됨")

    return True


# ============================================================
# 메인 실행
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("AI Agent Master Guide - Agent Chain 로직 검증")
    print("=" * 60)

    results = []
    results.append(("Prompt Chain", test_prompt_chain()))
    results.append(("Conditional Chain", test_conditional_chain()))
    results.append(("Robust Chain", test_robust_chain()))
    results.append(("Meta-Prompting", test_meta_prompting()))
    results.append(("Performance", test_chaining_performance()))
    results.append(("Context Preservation", test_context_preservation()))

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
        print("\n🎉 모든 Agent Chain 검증 성공!")
        exit(0)
    else:
        print("\n⚠️  일부 테스트 실패")
        exit(1)
