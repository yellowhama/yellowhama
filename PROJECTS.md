# 프로젝트 카탈로그

yellowhama 저장소는 여러 게임 개발 프로젝트의 개발 경험과 자동화 도구 활용 노하우를 공유합니다.

---

## 프로젝트 비교

| 항목 | BLOODLINE | Football |
|------|-----------|----------|
| **장르** | 중세 판타지 오픈월드 RPG | 스포츠 관리 게임 (턴제 전략) |
| **엔진** | *[BLOODLINE 엔진 명시 필요]* | Godot 4.4.1 |
| **플랫폼** | *[BLOODLINE 플랫폼 명시 필요]* | 크로스플랫폼 (Mobile/Tablet/Desktop) |
| **주요 기술** | *[BLOODLINE 기술 스택 명시 필요]* | GDScript, 반응형 UI, 동적 생성 |
| **개발 프로세스** | TDD 중심 | Phase 기반 증분 개발 |
| **MCP 서버** | Git, Memory, Sequential | Godot, Sequential, Memory |
| **개발 속도** | 4.3배 향상 | - |
| **테스트 작성** | 70% 단축 | - |
| **버그 수정** | 60% 단축 | - |
| **문서화** | 80% 단축 | - |
| **코드 품질** | - | 9.2/10 |
| **리팩토링** | - | 66% 코드 감소 |

---

## 재사용 가능 패턴

### BLOODLINE 유래
*[BLOODLINE 프로젝트에서 추출한 재사용 패턴들을 여기에 추가]*

예시:
- **TDD 워크플로우** (★★★★★): 테스트 작성 시간 70% 단축
- **Git 자동화** (★★★★☆): 커밋 시간 4-6배 향상
- **메모리 기반 컨텍스트** (★★★★★): 세션 간 즉시 컨텍스트 복원

### Football 유래

#### 1. AdaptiveLayoutContainer (★★★★★)
**목적**: 크로스플랫폼 반응형 UI 기반 클래스 패턴

**재사용성**: 모든 Godot 크로스플랫폼 프로젝트에 즉시 적용 가능

**문서**: [projects/football/GODOT_PATTERNS.md#1-adaptivelayoutcontainer-패턴](projects/football/GODOT_PATTERNS.md)

#### 2. Dynamic UI Generation (★★★★☆)
**목적**: 런타임 노드 생성으로 .tscn 파일 크기 90% 감소, 유지보수성 향상

**재사용성**: 반복 UI 요소 10개 이상 시 적용 권장

**문서**: [projects/football/GODOT_PATTERNS.md#2-dynamic-ui-generation-패턴](projects/football/GODOT_PATTERNS.md)

#### 3. UIStandards Validation (★★★★★)
**목적**: 자동화된 접근성 검증 시스템 (터치 타겟 44px, 폰트 크기 14px)

**재사용성**: 모든 Godot 프로젝트에 즉시 적용 가능, 게임 장르 독립적

**문서**: [projects/football/GODOT_PATTERNS.md#3-uistandards-validation-시스템](projects/football/GODOT_PATTERNS.md)

#### 4. Phase-based Development (★★★★☆)
**목적**: 대규모 기능을 작은 Phase로 분할하여 증분 개발, 100% 완료율 달성

**재사용성**: 프로젝트 관리 프로세스로 모든 프로젝트 적용 가능

**문서**: [projects/football/GODOT_PATTERNS.md#4-phase-based-development-프로세스](projects/football/GODOT_PATTERNS.md)

#### 5. Code Review Checklist (★★★★☆)
**목적**: 12개 섹션 체계적 리뷰로 코드 품질 9.2/10 달성

**재사용성**: Godot 외 일반 소프트웨어 개발에도 적용 가능

**문서**: [projects/football/GODOT_PATTERNS.md#5-코드-리뷰-체크리스트](projects/football/GODOT_PATTERNS.md)

#### 6. Refactoring Strategies (★★★★☆)
**목적**: DRY 원칙 적용으로 66% 코드 감소 (72 lines → 24 lines)

**재사용성**: Base class 추출 패턴은 모든 OOP 프로젝트에 적용 가능

**문서**: [projects/football/GODOT_PATTERNS.md#6-refactoring-전략](projects/football/GODOT_PATTERNS.md)

---

## 문서 구조

### 공통 가이드
- [CLAUDE_CODE_MASTER_GUIDE.md](CLAUDE_CODE_MASTER_GUIDE.md): Claude Code 종합 가이드 (66KB, 14개 섹션)
- [MCP_SETUP_GUIDE.md](MCP_SETUP_GUIDE.md): MCP 서버 설정 가이드 (Git, Memory, Sequential, Godot)

### 프로젝트별 문서
- [projects/bloodline/DEVELOPMENT.md](projects/bloodline/DEVELOPMENT.md): BLOODLINE 워크플로우 및 TDD 프로세스
- [projects/football/DEVELOPMENT.md](projects/football/DEVELOPMENT.md): Football 워크플로우 및 Phase 기반 개발
- [projects/football/GODOT_PATTERNS.md](projects/football/GODOT_PATTERNS.md): Godot 특화 재사용 패턴 6가지

---

## 프로젝트별 MCP 서버 설정

### BLOODLINE 필수 MCP 서버
1. **Git Server**: 자동 커밋 메시지 생성, 브랜치 관리
2. **Memory Server**: 세션 간 컨텍스트 유지
3. **Sequential Thinking Server**: 복잡한 다단계 추론

### Football 필수 MCP 서버
1. **Godot Server**: 에디터 실행, 프로젝트 실행, 디버그 출력 확인
2. **Sequential Thinking Server**: 아키텍처 분석, 복잡한 디버깅
3. **Memory Server** (선택적): 세션 간 컨텍스트 유지

자세한 설정 방법은 [MCP_SETUP_GUIDE.md](MCP_SETUP_GUIDE.md)를 참고하세요.

---

## 성과 비교

### BLOODLINE 성과
- ⚡ 개발 속도: **4.3배** 향상
- 📝 테스트 작성: **70%** 시간 단축
- 🐛 버그 수정: **60%** 시간 단축
- 📚 문서화: **80%** 시간 단축

### Football 성과
- 🏆 코드 품질: **9.2/10** 점수 달성
- ♻️ 리팩토링: **66%** 코드 감소
- ✅ Phase 7B 완료율: **100%**
- 🐛 버그 발견: **2건** (디버그 출력으로 원인 파악)
- 🔧 자동 검증: UIStandards로 접근성 기준 **100%** 준수

---

## 적용 우선순위

### 즉시 적용 가능 (모든 프로젝트)
1. **Phase-based Development** ★★★★★ - 프로젝트 관리 프로세스
2. **Code Review Checklist** ★★★★☆ - 코드 품질 향상

### Godot 프로젝트 전용
3. **UIStandards Validation** ★★★★★ - 접근성 자동 검증
4. **AdaptiveLayoutContainer** ★★★★★ - 크로스플랫폼 UI
5. **Dynamic UI Generation** ★★★★☆ - 반복 UI 10개 이상 시

### 범용 소프트웨어 개발
6. **Refactoring Strategies** ★★★★☆ - DRY 원칙 실전 적용
7. **TDD Workflow** (BLOODLINE) ★★★★★ - 테스트 주도 개발

---

**마지막 업데이트**: 2025-10-20
