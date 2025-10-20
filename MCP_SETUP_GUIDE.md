# MCP Server Setup Guide for BLOODLINE Project

Complete guide for setting up Model Context Protocol (MCP) servers to enhance Claude Code automation.

---

## Priority 1: Immediate Setup (This Week)

These three MCP servers will be installed first for maximum impact:

### 1. @modelcontextprotocol/server-git

**Purpose**: Automate Git operations with intelligent commit messages and branch management.

**Installation**:
```bash
# Install globally via NPM
npm install -g @modelcontextprotocol/server-git

# Verify installation
which mcp-server-git
```

**Configuration** (`~/.config/claude-code/config.json`):
```json
{
  "mcpServers": {
    "git": {
      "command": "mcp-server-git",
      "args": [],
      "env": {
        "GIT_DIR": "/mnt/e/game_bloodline/godot_project/.git"
      }
    }
  }
}
```

**Use Cases**:
- Auto-generate commit messages from changed files
- Smart feature branch creation
- PR generation with comprehensive descriptions
- Branch management recommendations

**Expected ROI**:
- Commit time: 2-3 minutes → 30 seconds (4-6x faster)
- Commit quality: More detailed and consistent messages
- Branch management: Automated best practices

---

### 2. @modelcontextprotocol/server-memory

**Purpose**: Persist context across sessions, remember decisions and unfinished work.

**Installation**:
```bash
# Install globally via NPM
npm install -g @modelcontextprotocol/server-memory

# Verify installation
which mcp-server-memory
```

**Configuration** (`~/.config/claude-code/config.json`):
```json
{
  "mcpServers": {
    "memory": {
      "command": "mcp-server-memory",
      "args": ["--storage-path", "/mnt/e/game_bloodline/godot_project/.claude/memory"],
      "env": {}
    }
  }
}
```

**Use Cases**:
- Session 1: Start CollectiveMemory tests → interrupted
- Session 2: Memory MCP restores context → "You were implementing test 15/41"
- Store project decisions: "Why did we choose v9.4.0 over v9.5.0?"
- Track technical debt and TODOs

**Expected ROI**:
- Context restoration: 5-10 minutes → instant
- Reduced re-work due to forgetting decisions
- Better long-term project consistency

---

### 3. @modelcontextprotocol/server-sequential-thinking

**Purpose**: Enable complex multi-step reasoning and planning.

**Installation**:
```bash
# Install globally via NPM
npm install -g @modelcontextprotocol/server-sequential-thinking

# Verify installation
which mcp-server-sequential-thinking
```

**Configuration** (`~/.config/claude-code/config.json`):
```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "mcp-server-sequential-thinking",
      "args": [],
      "env": {}
    }
  }
}
```

**Use Cases**:
- CollectiveMemory 41 test planning:
  - Step 1: Categorize tests (CRUD, search, integration)
  - Step 2: Identify dependencies
  - Step 3: Determine optimal implementation order
  - Step 4: Generate test plan with TodoWrite
- Complex refactoring:
  - Analyze impact across multiple files
  - Plan migration strategy
  - Execute systematically

**Expected ROI**:
- Planning quality: 50% better dependency analysis
- Reduced errors: 30% fewer missed edge cases
- Better strategic decisions

---

## 4. Godot MCP Server (Football 프로젝트 필수)

### 개요
Godot 엔진 통합을 위한 MCP 서버로, 에디터 실행, 프로젝트 실행, 디버그 출력 확인 등 Godot 개발 워크플로우를 자동화합니다.

### 설치

#### Windows
```bash
# NPM을 통한 설치
npm install -g godot-mcp-server

# 또는 로컬에서 직접 실행
git clone https://github.com/[godot-mcp-server-repo]
cd godot-mcp-server
npm install
npm link
```

#### macOS/Linux
```bash
npm install -g godot-mcp-server
```

### 설정 (config.json)

#### Windows 설정 예시
```json
{
  "mcpServers": {
    "godot": {
      "command": "godot-mcp-server",
      "args": [],
      "env": {
        "GODOT_EXECUTABLE": "C:\\Program Files\\Godot_v4.4.1-stable\\Godot_v4.4.1-stable_win64.exe"
      }
    }
  }
}
```

#### macOS 설정 예시
```json
{
  "mcpServers": {
    "godot": {
      "command": "godot-mcp-server",
      "args": [],
      "env": {
        "GODOT_EXECUTABLE": "/Applications/Godot.app/Contents/MacOS/Godot"
      }
    }
  }
}
```

#### Linux 설정 예시
```json
{
  "mcpServers": {
    "godot": {
      "command": "godot-mcp-server",
      "args": [],
      "env": {
        "GODOT_EXECUTABLE": "/usr/local/bin/godot"
      }
    }
  }
}
```

### 주요 기능

#### 1. 프로젝트 실행 및 테스트
```typescript
// 프로젝트 실행
mcp__godot__run_project({
  projectPath: "F:/Aisaak/Projects/football"
})

// 디버그 출력 확인
mcp__godot__get_debug_output()

// 프로젝트 중지
mcp__godot__stop_project()
```

#### 2. 에디터 실행 및 정보 확인
```typescript
// 에디터 실행
mcp__godot__launch_editor({
  projectPath: "F:/Aisaak/Projects/football"
})

// 프로젝트 정보 조회
mcp__godot__get_project_info({
  projectPath: "F:/Aisaak/Projects/football"
})

// Godot 버전 확인
mcp__godot__get_godot_version()
```

#### 3. 프로젝트 목록 조회
```typescript
// 특정 디렉토리에서 Godot 프로젝트 찾기
mcp__godot__list_projects({
  directory: "F:/Aisaak/Projects",
  recursive: false
})
```

#### 4. 씬 관리 (선택적 기능)
```typescript
// 씬 생성
mcp__godot__create_scene({
  projectPath: "...",
  scenePath: "res://scenes/NewScene.tscn",
  rootNodeType: "Node2D"
})

// 노드 추가
mcp__godot__add_node({
  projectPath: "...",
  scenePath: "res://scenes/NewScene.tscn",
  nodeType: "Label",
  nodeName: "TitleLabel"
})

// 스프라이트 로드
mcp__godot__load_sprite({
  projectPath: "...",
  scenePath: "res://scenes/Player.tscn",
  nodePath: "root/Player/Sprite2D",
  texturePath: "res://assets/player.png"
})
```

### 사용 시나리오

#### 시나리오 1: Phase 완료 검증
```bash
# Phase 구현 완료 후
1. mcp__godot__run_project() - 프로젝트 실행
2. mcp__godot__get_debug_output() - 에러 확인
3. 코드 수정 (Claude Code)
4. mcp__godot__stop_project()
5. 반복
```

#### 시나리오 2: 버그 수정 워크플로우
```bash
1. mcp__godot__get_debug_output() - 버그 발견
2. 에러 메시지 분석
3. 코드 수정 (Claude Code)
4. mcp__godot__run_project() - 재실행
5. mcp__godot__get_debug_output() - 검증
```

#### 시나리오 3: 반응형 UI 테스트
```bash
1. mcp__godot__run_project() - Mobile 해상도 실행
2. UI 검증
3. mcp__godot__stop_project()
4. 코드 수정 (viewport_size 변경)
5. mcp__godot__run_project() - Tablet 해상도 실행
6. UI 검증
```

### 성과 (Football 프로젝트)
- ✅ **Phase 7B 버그 2건 발견 및 수정** (디버그 출력으로 원인 파악)
  - Bug 1: StatusScreen 42개 속성 미표시 (동적 생성 누락)
  - Bug 2: Theme override 문법 오류 (Dictionary 접근 → 함수 호출)
- ✅ **수동 에디터 전환 없이 CI/CD 스타일 개발 가능**
- ✅ **터미널 기반 개발 워크플로우 완성**
- ✅ **코드 품질 점수 9.2/10 달성에 기여**

### 문제 해결

#### 에러: Godot executable not found
```bash
# 환경 변수 확인
echo $GODOT_EXECUTABLE  # Linux/macOS
echo %GODOT_EXECUTABLE%  # Windows

# 경로 업데이트 (Windows)
"GODOT_EXECUTABLE": "C:\\Godot\\Godot_v4.4.1_win64.exe"

# 경로 업데이트 (macOS)
"GODOT_EXECUTABLE": "/Applications/Godot.app/Contents/MacOS/Godot"

# 경로 업데이트 (Linux)
"GODOT_EXECUTABLE": "/usr/local/bin/godot"
```

#### 에러: Project not found
```bash
# 절대 경로 사용 (필수)
projectPath: "/absolute/path/to/project"

# project.godot 파일 존재 확인
ls /path/to/project/project.godot  # Linux/macOS
dir \path\to\project\project.godot  # Windows
```

#### 에러: Failed to run project
```bash
# Godot 버전 확인
mcp__godot__get_godot_version()

# 프로젝트 정보 확인
mcp__godot__get_project_info({ projectPath: "..." })

# 디버그 출력으로 에러 원인 파악
mcp__godot__get_debug_output()
```

#### 에러: MCP server not responding
```bash
# Claude Code 재시작
# config.json 확인
# NPM 패키지 재설치
npm uninstall -g godot-mcp-server
npm install -g godot-mcp-server
```

### 성능 최적화

#### 디버그 출력 필터링
```typescript
// 특정 키워드만 출력
// (현재는 전체 출력만 지원, 향후 업데이트 예정)
mcp__godot__get_debug_output()
```

#### 프로젝트 실행 타임아웃
```typescript
// 기본 타임아웃: 120초
// 특정 씬 실행
mcp__godot__run_project({
  projectPath: "...",
  scene: "res://tests/TestScene.tscn"
})
```

### 다른 MCP 서버와의 통합

#### Sequential Thinking + Godot
```bash
1. Sequential Thinking으로 버그 분석
2. Godot MCP Server로 재현 확인
3. 코드 수정
4. Godot MCP Server로 검증
```

#### Memory + Godot
```bash
1. Memory Server에 Phase 진행 상황 저장
2. Godot MCP Server로 테스트
3. 결과를 Memory Server에 기록
4. 다음 세션에서 컨텍스트 복원
```

### 참고 자료
- [Godot MCP Server GitHub](https://github.com/[repo])
- [Football 프로젝트 Godot 패턴](projects/football/GODOT_PATTERNS.md)
- [Godot 공식 문서](https://docs.godotengine.org/)

### 롤백 (필요 시)

Godot MCP Server를 비활성화하려면:

```json
{
  "mcpServers": {
    // "godot": { ... }  <- 주석 처리 또는 삭제
  }
}
```

Claude Code 재시작 후 적용됩니다.

---

## Complete Configuration File

### Full `~/.config/claude-code/config.json`

```json
{
  "mcpServers": {
    "git": {
      "command": "mcp-server-git",
      "args": [],
      "env": {
        "GIT_DIR": "/mnt/e/game_bloodline/godot_project/.git"
      }
    },
    "memory": {
      "command": "mcp-server-memory",
      "args": ["--storage-path", "/mnt/e/game_bloodline/godot_project/.claude/memory"],
      "env": {}
    },
    "sequential-thinking": {
      "command": "mcp-server-sequential-thinking",
      "args": [],
      "env": {}
    }
  },
  "anthropic": {
    "apiKey": "YOUR_API_KEY_HERE"
  }
}
```

**IMPORTANT**: Replace `YOUR_API_KEY_HERE` with actual Anthropic API key.

---

## Setup Procedure

### Step 1: Install NPM Packages

```bash
# Install all three MCP servers
npm install -g \
  @modelcontextprotocol/server-git \
  @modelcontextprotocol/server-memory \
  @modelcontextprotocol/server-sequential-thinking

# Verify installations
which mcp-server-git
which mcp-server-memory
which mcp-server-sequential-thinking
```

### Step 2: Create Memory Storage Directory

```bash
cd /mnt/e/game_bloodline/godot_project
mkdir -p .claude/memory
```

### Step 3: Backup Existing Config (if exists)

```bash
cd ~/.config/claude-code
if [ -f config.json ]; then
  cp config.json config.json.backup.$(date +%Y%m%d-%H%M%S)
fi
```

### Step 4: Create/Update Configuration

```bash
# Create directory if doesn't exist
mkdir -p ~/.config/claude-code

# Create config.json (manual edit required for API key)
cat > ~/.config/claude-code/config.json <<'EOF'
{
  "mcpServers": {
    "git": {
      "command": "mcp-server-git",
      "args": [],
      "env": {
        "GIT_DIR": "/mnt/e/game_bloodline/godot_project/.git"
      }
    },
    "memory": {
      "command": "mcp-server-memory",
      "args": ["--storage-path", "/mnt/e/game_bloodline/godot_project/.claude/memory"],
      "env": {}
    },
    "sequential-thinking": {
      "command": "mcp-server-sequential-thinking",
      "args": [],
      "env": {}
    }
  },
  "anthropic": {
    "apiKey": "YOUR_API_KEY_HERE"
  }
}
EOF

# Edit to add API key
# nano ~/.config/claude-code/config.json
# or
# code ~/.config/claude-code/config.json
```

### Step 5: Verify Configuration

```bash
# Check JSON syntax
jq empty ~/.config/claude-code/config.json

# If no errors, configuration is valid
echo "✅ Configuration valid"
```

### Step 6: Restart Claude Code

```bash
# Exit current session (if running)
# Type: /exit

# Start new session
claude

# Verify MCP servers loaded
# You should see messages about MCP server connections
```

---

## Testing MCP Servers

### Test 1: Git MCP

```bash
# In Claude Code session:
# User: "Analyze current git status and suggest next steps"

# Expected: Claude uses git MCP to check status, branches, commits
# Output: Detailed analysis with actionable suggestions
```

### Test 2: Memory MCP

```bash
# Session 1:
# User: "Remember: We decided to use GUT v9.4.0 because v9.5.0 has circular dependency bug"

# Session 2 (new session):
# User: "Why are we using GUT v9.4.0?"

# Expected: Claude retrieves from memory MCP
# Output: "You stored this decision: v9.5.0 has circular dependency bug"
```

### Test 3: Sequential Thinking MCP

```bash
# User: "Plan the implementation of CollectiveMemory 41 tests with detailed dependency analysis"

# Expected: Claude uses sequential-thinking for multi-step planning
# Output: Structured plan with dependencies, order, and rationale
```

---

## Troubleshooting

### Issue 1: MCP Server Not Found

**Symptom**: `command not found: mcp-server-git`

**Solution**:
```bash
# Check NPM global bin directory
npm config get prefix

# Add to PATH if needed (add to ~/.bashrc or ~/.zshrc)
export PATH="$PATH:$(npm config get prefix)/bin"

# Reload shell
source ~/.bashrc
```

### Issue 2: Permission Errors

**Symptom**: `EACCES: permission denied`

**Solution**:
```bash
# Fix NPM permissions
npm config set prefix ~/.npm-global
export PATH=~/.npm-global/bin:$PATH

# Reinstall globally
npm install -g @modelcontextprotocol/server-git
```

### Issue 3: Config.json Not Loaded

**Symptom**: Claude Code doesn't use MCP servers

**Solution**:
```bash
# Verify file location
ls -la ~/.config/claude-code/config.json

# Check JSON syntax
jq empty ~/.config/claude-code/config.json

# Check Claude Code version (needs recent version with MCP support)
claude --version
```

### Issue 4: Memory Storage Path Issues

**Symptom**: Memory MCP can't write to storage

**Solution**:
```bash
# Ensure directory exists and is writable
mkdir -p /mnt/e/game_bloodline/godot_project/.claude/memory
chmod 755 /mnt/e/game_bloodline/godot_project/.claude/memory

# Check ownership
ls -la /mnt/e/game_bloodline/godot_project/.claude/
```

---

## Priority 2 & 3: Future MCP Servers

### Priority 2 (1-2 Weeks)

**@modelcontextprotocol/server-playwright**:
```bash
npm install -g @modelcontextprotocol/server-playwright
```

**@modelcontextprotocol/server-postgres**:
```bash
npm install -g @modelcontextprotocol/server-postgres
```

### Priority 3 (1+ Month)

**Community Servers**:
- `godot-mcp-server` (if available)
- Custom BLOODLINE-specific MCP servers

**Configuration Pattern**:
```json
{
  "mcpServers": {
    "playwright": {
      "command": "mcp-server-playwright",
      "args": ["--browser", "chromium"],
      "env": {}
    },
    "postgres": {
      "command": "mcp-server-postgres",
      "args": ["--connection-string", "postgresql://localhost/bloodline"],
      "env": {}
    }
  }
}
```

---

## Expected Workflow with MCP Servers

### Before MCP (Current):

```
User: "Check git status and create commit"
Claude: [runs git status] → [analyzes output] → [suggests commit message]
User: "OK, commit with that message"
Claude: [runs git commit] → [runs git push]

Time: 3-5 minutes
Manual steps: 3
```

### After MCP (With Git + Memory + Sequential):

```
User: "Commit and push current work"
Claude: [git MCP analyzes changes] → [memory MCP recalls project context] →
        [sequential MCP plans commit strategy] → [generates perfect commit message] →
        [commits and pushes] → [stores commit context in memory]

Time: 30 seconds
Manual steps: 1
Speedup: 6-10x
```

### Complex Planning (With Sequential-Thinking MCP):

```
User: "Plan CollectiveMemory 41 tests"
Claude: [sequential MCP performs deep analysis] →
        [generates dependency graph] →
        [determines optimal order] →
        [creates TodoWrite plan] →
        [stores plan in memory MCP]

Output: Structured plan with:
- Test categories and dependencies
- Implementation order with rationale
- Risk assessment for each phase
- Expected timeline and blockers
```

---

## Rollback Procedure

If MCP servers cause issues:

```bash
# Stop Claude Code
# Exit session

# Disable MCP servers
cd ~/.config/claude-code
mv config.json config.json.mcp-disabled
cat > config.json <<EOF
{
  "anthropic": {
    "apiKey": "YOUR_API_KEY_HERE"
  }
}
EOF

# Restart Claude Code
claude

# MCP servers now disabled, back to standard functionality
```

---

## Success Metrics

Track these metrics to measure MCP effectiveness:

| Metric | Before MCP | Target After MCP | Measurement |
|--------|------------|------------------|-------------|
| **Git Commit Time** | 2-3 min | 30 sec | Time from "commit" to pushed |
| **Context Restoration** | 5-10 min | Instant | New session startup time |
| **Planning Quality** | 7/10 | 9/10 | Subjective assessment |
| **Dependency Miss Rate** | 20% | 5% | Issues found in testing |
| **Development Speed** | 3-4x | 5-6x | Overall task completion |

---

**Last Updated**: 2025-10-19
**Status**: Priority 1 servers ready for installation
**Next Step**: Execute Step-by-Step setup procedure above
