# Project Swarm: OpenCode Platform Enrichment Guide

## Executive Summary

This document provides specific recommendations for implementing Project Swarm using **OpenCode's native capabilities** rather than building a custom Python/AsyncIO stack. OpenCode v1.4.11 already provides most of the infrastructure described in the original plan.

---

## 1. REPLACING "THE ARCHITECT" WITH OPENCODE'S SISYPHUS AGENT

### Current Plan (Custom)
- Single, long-running session with high-reasoning capabilities
- Manual context compression every 50 turns
- Custom DAG task management

### OpenCode Native Solution

#### **Sisyphus Agent - The Continuity Engine**

OpenCode's **Sisyphus agent** is specifically designed for long-running, persistent sessions with automatic context management:

```bash
# Start a Sisyphus session (persistent, auto-compressing)
opencode agent start sisyphus --session-name "swarm-architect-$(date +%s)"

# Or via the headless server API
curl -X POST http://localhost:8080/api/agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "sisyphus",
    "prompt": "Initialize Project Swarm Architect for repository: /path/to/repo",
    "session_id": "swarm-architect-main"
  }'
```

#### **Key OpenCode Features to Leverage**

| Feature | OpenCode Command | Replaces Custom Code |
|---------|-----------------|---------------------|
| **Session Persistence** | `opencode attach <session-url>` | Custom session manager |
| **Context Compression** | Built into Sisyphus agent | Manual compression logic |
| **Session Forking** | `opencode session fork <id>` | Custom branching logic |
| **Token Management** | Automatic via provider APIs | Custom token counting |
| **DAG Execution** | `runTasks(team, tasks)` with dependencies | Custom AsyncIO orchestrator |

#### **Recommended Architecture**

```yaml
# .opencode/agents/sisyphus-architect.yaml
name: swarm-architect
agent: sisyphus
model: anthropic/claude-3.5-sonnet  # High-reasoning model
session:
  persistent: true
  auto_compress: true
  compression_threshold: 40  # turns (better than 50)
  memory_layer: mempalace     # Native MCP integration
context:
  system_prompt: |
    You are the Architect of Project Swarm. Your responsibilities:
    1. Decompose high-level goals into atomic tasks
    2. Maintain the global project DAG
    3. Query MemPalace for context
    4. Coordinate worker agents via OpenMultiAgent
```

---

## 2. REPLACING "RESEARCH AGENTS" WITH OPENCODE'S SPECIALIZED AGENTS

### Current Plan (Custom)
- Ephemeral workers with search/documentation access
- Produce "Research Memos"

### OpenCode Native Solution

OpenCode provides **three specialized research agents** that map directly to your needs:

### A. Explore Agent - Code Discovery & Investigation

```bash
# For investigating unknown libraries or cryptic errors
opencode agent run explore \
  --prompt "Investigate error: 'ModuleNotFoundError: No module named "chromadb"' in /home/user/project. Find installation requirements and compatibility issues."
```


### B. Librarian Agent - Documentation & Knowledge Retrieval

```bash
# For documentation lookup and knowledge synthesis
opencode agent run librarian \
  --prompt "Research best practices for implementing JWT authentication in FastAPI. Include token refresh patterns and security considerations."
```

### C. Metis Agent - Strategic Planning & Analysis

```bash
# For high-level strategic research
opencode agent run metis \
  --prompt "Analyze the trade-offs between PostgreSQL and MongoDB for a real-time analytics dashboard. Consider query patterns, scaling, and operational complexity."
```

---

## 3. REPLACING "WORKERS" WITH OPENCODE TASK CATEGORIES

### Current Plan (Custom)
- Docker/Firecracker containers for isolation
- Three roles: Coder, Tester, Auditor
- Manual TDD loop

### OpenCode Native Solution

OpenCode's **task categories** map directly to your worker roles:

| Your Role | OpenCode Category | Agent | Model Tier |
|-----------|------------------|-------|------------|
| **Coder** | `deep` | Hephaestus | nvidia/moonshotai/kimi-k2.5 |
| **Tester** | `quick` + `deep` | Prometheus | opencode/big-pickle |
| **Auditor** | `ultrabrain` | Oracle | anthropic/claude-3.5-sonnet |

---

## 4. MEMORY LAYER: MemPalace MCP INTEGRATION

### Current Plan (Custom)
- Neo4j for graph memory
- Qdrant for episodic memory
- Redis for semantic memory
- File system for spatial memory

### OpenCode Native Solution

**MemPalace is already an MCP server** - no custom implementation needed!

#### **Memory Layer Mapping**

| Your Layer | MemPalace Feature | Usage |
|------------|------------------|-------|
| **Graph Memory** | `mempalace_kg_query` + `mempalace_kg_add` | Code dependencies, relationships |
| **Episodic Memory** | `mempalace_search` with context | Lessons learned, past incidents |
| **Semantic Memory** | `mempalace_add_drawer` + search | Project structure, schemas |
| **Spatial Memory** | `mempalace_create_tunnel` | Cross-project connections |

---

## 5. IMPLEMENTATION STACK: OpenCode vs Custom Python

### Comparison Matrix

| Component | Custom Plan | OpenCode Native | Recommendation |
|-----------|-------------|-----------------|----------------|
| **Orchestrator** | Python/AsyncIO | `runTeam()` / `runTasks()` | ✅ Use OpenCode |
| **Agent Communication** | JSON-RPC over NATS | Built-in ACP | ✅ Use OpenCode |
| **Execution Environment** | Docker SDK | Native process isolation | ✅ Use OpenCode |
| **Session Management** | Custom | `opencode session` commands | ✅ Use OpenCode |
| **Context Compression** | Manual every 50 turns | Automatic in Sisyphus | ✅ Use OpenCode |
| **Memory System** | Neo4j/Qdrant/Redis | MemPalace MCP | ✅ Use OpenCode |
| **Observability** | LangSmith/W&B | Built-in tracing | ✅ Use OpenCode |
| **Coding Context** | Custom LSIF | LSP integration | ✅ Use OpenCode |

---

## 6. MCP INTEGRATION RECOMMENDATIONS

### Essential MCP Servers for Project Swarm

```bash
opencode mcp add mempalace    # Memory layer (essential)
opencode mcp add github       # Git operations (essential)
opencode mcp add context7     # Documentation (essential)
opencode mcp add chrome-devtools  # Testing (optional)
```

---

## 7. OPERATIONAL LIFECYCLE: OpenCode Commands

### Phase I: Discovery & Research

```bash
# Trigger from GitHub webhook or cron
opencode run "Analyze GitHub issue #123 and create research tasks"
```

### Phase II: Master Plan Creation

```bash
# Sisyphus creates the DAG
opencode agent run sisyphus \
  --session-id "swarm-architect-main" \
  --prompt "Create execution plan for auth performance fix. Query MemPalace for related code."
```


### Phase III: Parallel Execution

```bash
# Native parallel execution
opencode team run \
  --team "swarm-workers" \
  --tasks tasks.json \
  --parallel 5
```


### Phase IV: Verification & Self-Healing

```bash
# Automated verification via MCP
opencode run "Verify deployment at http://localhost:3000 and rollback if errors > threshold"
```

---

## 8. SAFETY & GUARDRAILS

| Guardrail | OpenCode Feature | Configuration |
|-----------|-----------------|---------------|
| **Financial Kill-Switch** | Token budget limits | `max_tokens_per_hour: 1000000` |
| **Sandbox Air-Gapping** | MCP server permissions | `network_access: false` |
| **Write Protection** | File system policies | `protected_paths: [".git/", "*.backup"]` |
| **Human-in-the-Loop** | Slack/Discord MCP | `approval_required: true` |

---

## 9. QUICK START: Minimal Viable Swarm

```bash
# 1. Start headless server
opencode serve --port 8080 --config swarm-config.yaml

# 2. Initialize Swarm
curl -X POST http://localhost:8080/api/agent/start \
  -d '{
    "agent": "sisyphus",
    "session_name": "swarm-architect",
    "system_prompt": "You are the Architect of Project Swarm..."
  }'

# 3. Submit First Goal
curl -X POST http://localhost:8080/api/agent/message \
  -d '{
    "session_id": "swarm-architect",
    "message": "Implement user authentication with JWT tokens"
  }'
```

---


## CONCLUSION

**Recommendation: Build on OpenCode, not around it.**

The original Project Swarm plan describes building a custom orchestration layer that largely duplicates OpenCode's existing capabilities. By leveraging:

1. **Sisyphus agent** for the Architect role
2. **Explore/Librarian/Metis agents** for research
3. **Task categories** (deep/quick/ultrabrain) for workers
4. **MemPalace MCP** for memory
5. **runTeam/runTasks** for orchestration
6. **Built-in MCP ecosystem** for integrations

You can reduce the custom code by ~80% and focus on the unique business logic of your autonomous development harness.


---

*Document Version: 1.0*
*OpenCode Version: 1.4.11*
*Generated: 2026-04-22*
