# Football 프로젝트 개발 워크플로우

> **프로젝트 타입**: 스포츠 관리 게임 (턴제 전략/관리 시뮬레이션)
> **엔진**: Godot 4.4.1
> **플랫폼**: 크로스플랫폼 (Mobile/Tablet/Desktop)
> **개발 프로세스**: Phase 기반 증분 개발

---

## 1. 프로젝트 개요

### 기술 스택
- **게임 엔진**: Godot 4.4.1
- **언어**: GDScript
- **UI 시스템**: 반응형 UI (AdaptiveLayoutContainer 패턴)
- **플랫폼 타겟**: Android, iOS, Windows, macOS, Linux

### 주요 기술적 특징
- **크로스플랫폼 반응형 UI**: Mobile/Tablet/Desktop 각각 최적화
- **동적 UI 생성**: 540개 노드 자동 생성으로 .tscn 파일 90% 감소
- **자동화된 접근성 검증**: UIStandards 시스템으로 터치 타겟 44px, 폰트 크기 14px 자동 준수
- **Phase 기반 증분 개발**: 명확한 마일스톤으로 100% 완료율 달성

### 품질 지표
- **코드 품질 점수**: 9.2/10 (Phase 7B 기준)
- **리팩토링 효율**: 66% 코드 감소 (72 lines → 24 lines)
- **버그 발견율**: Phase 7B에서 2건 (Godot MCP Server로 발견 및 수정)

---

## 2. 개발 환경 설정

### 필수 도구

#### 2.1 Godot Engine 설치
```bash
# Windows
# https://godotengine.org/download/windows 에서 다운로드
# C:\Program Files\Godot_v4.4.1-stable\Godot_v4.4.1-stable_win64.exe

# macOS
brew install godot

# Linux
sudo snap install godot
```

#### 2.2 Claude Code 설치
```bash
# https://docs.claude.com/claude-code 참고
# Claude Code 설치 및 인증
```

#### 2.3 MCP 서버 설정

**필수 MCP 서버**:
1. **Godot MCP Server**: 에디터 실행, 프로젝트 실행, 디버그 출력
2. **Sequential Thinking Server**: 복잡한 아키텍처 분석
3. **Memory Server** (선택): 세션 간 컨텍스트 유지

상세 설정 방법은 [MCP_SETUP_GUIDE.md](../../MCP_SETUP_GUIDE.md#4-godot-mcp-server-football-프로젝트-필수)를 참고하세요.

### 프로젝트 클론

```bash
# Git 저장소 클론
git clone https://github.com/[your-username]/football.git
cd football

# Godot 프로젝트 확인
ls project.godot  # 파일 존재 확인
```

---

## 3. Claude Code + Godot MCP 워크플로우

### 3.1 기본 워크플로우

#### Phase 개발 사이클
```bash
1. 명세 읽기: PHASE_X_SPEC.md 검토
2. Claude Code 시작: claude
3. 코드 작성: GDScript 구현
4. 실시간 테스트: mcp__godot__run_project()
5. 디버그 확인: mcp__godot__get_debug_output()
6. 반복: 수정 → 재실행 → 검증
7. 코드 리뷰: 12개 섹션 체크리스트
8. Phase 완료: PHASE_X_COMPLETION_DECLARATION.md 작성
```

#### 일일 개발 루틴
```bash
# 1. 세션 시작
git status && git branch  # 항상 feature 브랜치 확인
claude

# 2. 컨텍스트 로드 (Memory MCP Server 사용 시)
# list_memories() → read_memory("current_phase")

# 3. 코드 작성
# GDScript 구현

# 4. 실시간 검증
mcp__godot__run_project({ projectPath: "F:/Aisaak/Projects/football" })
mcp__godot__get_debug_output()

# 5. 수정 반복
# 에러 발견 → 코드 수정 → 재실행 → 검증

# 6. 세션 종료 (Memory MCP Server 사용 시)
# write_memory("session_summary", "Phase X progress: ...")
git commit -m "feat(phase-X): implement feature Y"
```

### 3.2 Godot MCP Server 활용

#### 프로젝트 실행 및 테스트
```bash
# 프로젝트 실행
mcp__godot__run_project({ projectPath: "절대/경로/football" })

# 디버그 출력 확인 (에러 발견)
mcp__godot__get_debug_output()

# 프로젝트 중지
mcp__godot__stop_project()
```

#### 에디터 실행 (씬 편집 필요 시)
```bash
# Godot 에디터 실행
mcp__godot__launch_editor({ projectPath: "절대/경로/football" })

# .tscn 파일 수동 편집 후 Claude Code로 복귀
```

#### 프로젝트 정보 확인
```bash
# 프로젝트 메타데이터 확인
mcp__godot__get_project_info({ projectPath: "절대/경로/football" })

# Godot 버전 확인
mcp__godot__get_godot_version()
```

### 3.3 Phase 7B 실제 사례

#### Bug 1: StatusScreen 42개 속성 미표시 수정
```bash
1. mcp__godot__run_project() 실행
2. mcp__godot__get_debug_output() → "GridContainer has no children" 에러 발견
3. 동적 Panel 생성 코드 추가 (StatusScreenImproved_Responsive.gd:109-231)
4. mcp__godot__run_project() 재실행
5. mcp__godot__get_debug_output() → 에러 없음 확인
6. ✅ 버그 수정 완료
```

#### Bug 2: Theme override 문법 오류 수정
```bash
1. mcp__godot__get_debug_output() → "Invalid access to 'theme_override_font_sizes'" 에러
2. Dictionary 접근 → 함수 호출로 수정
   Before: label.theme_override_font_sizes["font_size"] = 18
   After:  label.add_theme_font_size_override("font_size", 18)
3. mcp__godot__run_project() 재실행
4. ✅ 버그 수정 완료
```

---

## 4. Phase 기반 개발 프로세스

### 4.1 Phase 구조

#### Phase 정의 기준
- **1 Phase = 1-2주 분량**
- **명확한 마일스톤** (반응형 UI 완성, Manager 통합 등)
- **독립적 테스트 가능**
- **코드 품질 9/10 이상**

#### Phase 예시 (Phase 7B)
```
Phase 7B: 반응형 UI (2주)
├─ AdaptiveLayoutContainer 패턴 도입
├─ Mobile/Tablet/Desktop 레이아웃 구현
├─ 동적 UI 생성 시스템 (540개 노드 자동 생성)
├─ UIStandards 검증 시스템 (자동 접근성 검증)
└─ 3개 화면 리팩토링 (66% 코드 감소)

결과: 100% 완료, 품질 9.2/10, 버그 2건 수정
```

### 4.2 Phase 워크플로우

#### Step 1: 명세 작성
```bash
# PHASE_X_SPEC.md 생성
- 목표: 이번 Phase에서 달성할 기능
- 요구사항: 상세 기술 요구사항
- 성공 기준: 완료 판단 기준
- 추정 시간: 1-2주

예시: PHASE7B_SPEC.md (상세 요구사항 포함)
```

#### Step 2: 구현
```bash
# Feature branch 생성
git checkout -b feature/phase-7b-responsive-ui

# Claude Code로 개발
- AdaptiveLayoutContainer.gd 구현
- 3개 화면에 적용
- 동적 UI 생성 시스템 추가
- UIStandards 검증 시스템 통합
```

#### Step 3: 테스트 (Godot MCP Server 활용)
```bash
# 실시간 테스트
mcp__godot__run_project()
mcp__godot__get_debug_output()

# 반복: 에러 발견 → 수정 → 재실행
# Phase 7B에서 2건 버그 발견 및 수정
```

#### Step 4: 코드 리뷰
```bash
# 12개 섹션 체크리스트 실행
1. 패턴 일관성 검증: AdaptiveLayoutContainer 상속 확인
2. Public API 검증: 3개 화면 모두 동일 API 제공
3. TODO 분석: Phase 8 scope만 남음
4. 코드 중복 감지: 72 lines → 24 lines 리팩토링
5-12. 품질 평가: 9.2/10 점수 달성
```

#### Step 5: 완료 선언
```bash
# PHASE_X_COMPLETION_DECLARATION.md 작성
- 완료율: 100%
- 품질 점수: 9.2/10
- 버그 수정: 2건
- 리팩토링: 66% 코드 감소
- 다음 단계: Phase 8 계획

# Git 커밋
git add .
git commit -m "feat(phase-7b): complete responsive UI implementation

- Add AdaptiveLayoutContainer base class
- Implement Mobile/Tablet/Desktop layouts
- Add dynamic UI generation (540 nodes)
- Add UIStandards validation system
- Refactor 66% code reduction

Quality score: 9.2/10
Bugs fixed: 2

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

#### Step 6: 다음 Phase 계획
```bash
# PHASE_X+1_PLANNING.md 작성
- 목표: Manager 통합
- 타임라인: 1-1.5주
- 필수 작업: TrainingManager, MatchManager 통합
- 선택 작업: GlobalCharacterData 동기화
```

---

## 5. 코드 리뷰 및 품질 관리

### 5.1 12개 섹션 코드 리뷰 체크리스트

#### 1. 패턴 일관성 검증
```yaml
AdaptiveLayoutContainer 상속: ✅ 모든 화면
super._ready() 호출: ✅ 모든 화면
layout_activated signal 연결: ✅ 모든 화면
_populate_current_layout() 구현: ✅ 모든 화면
```

#### 2. Public API 검증
```yaml
모든 화면 동일 API:
  - set_available_XXX(Array)
  - select_XXX(String)
  - get_selected_XXX() -> String
```

#### 3. TODO 분석
```yaml
Phase 8 scope: 허용
잘못된 TODO: 0개 (금지)
구현 누락: 0개 (금지)
```

#### 4. 코드 중복 감지
```yaml
기준: 10 lines 이상 중복 금지
발견 시: 즉시 리팩토링 (base class 추출 등)
```

#### 5-12. 품질 평가 (10점 만점)
- **네이밍 일관성**: 10/10 (camelCase, 명확한 의미)
- **에러 처리**: 8/10 (push_warning 사용)
- **문서화 품질**: 9/10 (docstring 포함)
- **테스트 용이성**: 9/10 (Public API 제공)
- **유지보수성**: 9/10 (패턴 일관성)
- **확장성**: 9/10 (base class 활용)
- **퍼포먼스 고려**: 9/10 (동적 생성 최소화)
- **접근성 준수**: 10/10 (UIStandards 자동 검증)

**총점 기준**:
- 9.0-10.0: 우수 (Phase 완료 가능)
- 8.0-8.9: 양호 (일부 개선 필요)
- 7.0-7.9: 보통 (리팩토링 권장)
- 7.0 미만: 불합격 (재작업 필수)

### 5.2 리팩토링 전략

#### 코드 중복 제거 (DRY 원칙)
```bash
Before: 72 lines 중복
After: Base class 추출 → 24 lines (66% 감소)

효과:
- 유지보수성 향상
- 버그 수정 용이 (한 곳만 수정)
- 코드 품질 점수 9.2/10 달성
```

#### API 일관성 확보
```bash
Before: TrainingScreen만 Public API 부재
After: 3개 화면 모두 동일 API 패턴 제공

효과:
- Manager 통합 용이
- 테스트 작성 간소화
- 코드 가독성 향상
```

---

## 6. 크로스머신 작업 체크리스트

### 6.1 새 머신에서 프로젝트 시작

```bash
# 1. Git 클론
git clone https://github.com/[username]/football.git
cd football

# 2. Godot 설치 확인
godot --version  # 4.4.1 확인

# 3. Claude Code 설정
# config.json에 Godot MCP Server 추가
{
  "mcpServers": {
    "godot": {
      "command": "godot-mcp-server",
      "env": {
        "GODOT_EXECUTABLE": "[로컬 Godot 경로]"
      }
    }
  }
}

# 4. 프로젝트 실행 테스트
claude
mcp__godot__run_project({ projectPath: "절대/경로/football" })
mcp__godot__get_debug_output()

# 5. 컨텍스트 복원 (Memory MCP Server 사용 시)
# list_memories()
# read_memory("current_phase")
```

### 6.2 작업 종료 시 체크리스트

```bash
# 1. 변경 사항 커밋
git status
git add .
git commit -m "feat(phase-X): ..."

# 2. 컨텍스트 저장 (Memory MCP Server 사용 시)
# write_memory("session_summary", "Phase X progress: ...")
# write_memory("next_steps", "Next: implement Y")

# 3. Phase 진행 상황 업데이트
# PHASE_X_SPEC.md 업데이트 (완료율, 발견된 이슈 등)

# 4. 푸시
git push origin feature/phase-X
```

---

## 7. 재사용 가능 패턴

상세한 패턴 설명은 [GODOT_PATTERNS.md](GODOT_PATTERNS.md)를 참고하세요.

### 즉시 적용 가능
1. **UIStandards Validation** (★★★★★) - 모든 Godot 프로젝트
2. **AdaptiveLayoutContainer** (★★★★★) - 크로스플랫폼 UI 필요 시
3. **Phase-based Development** (★★★★☆) - 모든 프로젝트 관리

### 조건부 적용
4. **Dynamic UI Generation** (★★★★☆) - 반복 UI 10개 이상 시
5. **Code Review Checklist** (★★★★☆) - 팀 개발 환경

---

## 8. 성과 및 학습

### Phase 7B 성과
- ✅ **완료율**: 100%
- ✅ **품질 점수**: 9.2/10
- ✅ **버그 수정**: 2건 (Godot MCP Server로 발견)
- ✅ **리팩토링**: 66% 코드 감소
- ✅ **접근성**: 100% 기준 준수 (자동 검증)

### 주요 학습
1. **Godot MCP Server의 가치**: 수동 에디터 전환 없이 CI/CD 스타일 개발
2. **Phase 기반 개발**: 명확한 마일스톤으로 100% 완료율 달성
3. **리팩토링의 중요성**: 66% 코드 감소로 유지보수성 향상
4. **자동화된 검증**: UIStandards로 접근성 기준 100% 준수

---

## 9. 다음 단계

### Phase 8 계획 (Manager 통합)
- **TrainingManager 통합** (3.5시간)
- **MatchManager 통합** (7시간)
- **GlobalCharacterData 동기화** (2시간)

상세 계획은 [PHASE8_PLANNING.md](../../PHASE8_PLANNING.md)를 참고하세요.

---

**마지막 업데이트**: 2025-10-20
**현재 Phase**: Phase 7B 완료
**다음 Phase**: Phase 8 (Manager 통합)
**품질 점수**: 9.2/10
