# Project Swarm: 24/7 Autonomous Development & Self-Healing Harness

This document outlines the technical architecture and operational workflow for an end-to-end autonomous coding engine built on **OpenCode**. The system is designed to operate without human intervention, moving from high-level objectives to researched, tested, and self-healed production code.

---

## 1. System Hierarchy (The "Team") - OPENCODE NATIVE

The harness operates using OpenCode's specialized agents to prevent context drift and ensure high-fidelity execution.

### A. The Architect → **Sisyphus Agent** (OpenCode Native)
* **Nature:** OpenCode's Sisyphus agent - designed for long-running, persistent sessions with automatic context compression
* **Responsibility:**
  * Maintains the **Global Strategy**
  * Decomposes high-level requirements into a **Directed Acyclic Graph (DAG)** of atomic tasks
  * Manages the **MemPalace** indexing
  * **Continuity:** Automatic context compression (built into Sisyphus, ~40 turns)
* **Command:**
  ```bash
  opencode agent start sisyphus --session-name "swarm-architect"
  ```

### B. The Research Agents → **Explore, Librarian, Metis** (OpenCode Native)
* **Nature:** Specialized OpenCode agents for different research needs
* **Responsibility:**
  * **Explore Agent:** Investigates unknown libraries, cryptic error codes, code discovery
  * **Librarian Agent:** Retrieves documentation, best practices, API references
  * **Metis Agent:** Strategic analysis, architecture decisions, trade-off analysis
* **Commands:**
  ```bash
  opencode agent run explore --prompt "Investigate error XYZ"
  opencode agent run librarian --prompt "Research JWT auth patterns"
  opencode agent run metis --prompt "Analyze PostgreSQL vs MongoDB trade-offs"
  ```

### C. The Workers → **Task Categories** (OpenCode Native)
* **Nature:** OpenCode's task categories map directly to worker roles
* **Responsibility:**
  * **Coder (deep):** Hephaestus agent - implements logic based on the Architect's brief
  * **Tester (quick):** Prometheus agent - writes failing tests (TDD) before Coder begins
  * **Auditor (ultrabrain):** Oracle agent - scans code for security vulnerabilities
* **Category Mapping:**
  | Role | OpenCode Category | Agent | Model |
  |------|------------------|-------|-------|
  | Coder | `deep` | Hephaestus | nvidia/moonshotai/kimi-k2.5 |
  | Tester | `quick` | Prometheus | opencode/big-pickle |
  | Auditor | `ultrabrain` | Oracle | anthropic/claude-3.5-sonnet |

---

## 2. Memory Layer: MemPalace MCP (Already Exists!)

**MemPalace is already an MCP server** - no custom Neo4j/Qdrant/Redis needed!

| Layer | MemPalace Feature | Function |
| :--- | :--- | :--- |
| **Graph Memory** | `mempalace_kg_query` + `mempalace_kg_add` | Maps code dependencies (e.g., "Function X is called by File Y"). |
| **Episodic Memory** | `mempalace_search` with context | Stores "Lessons Learned" (e.g., "Last time we edited this, the Auth broke"). |
| **Semantic Memory** | `mempalace_add_drawer` + search | Stores project structure, API schemas, and env variables. |
| **Spatial Memory** | `mempalace_create_tunnel` | Cross-project connections and spatial organization. |

**MCP Configuration:**
```json
{
  "mcpServers": {
    "mempalace": {
      "command": "python",
      "args": ["-m", "mcp_server_mempalace"],
      "env": { "MEMPALACE_DB_PATH": "~/.mempalace/swarm.db" }
    }
  }
}
```

---

## 3. The 0-24 Operational Lifecycle - OPENCODE COMMANDS

### Phase I: Discovery & Research
1. **Trigger:** GitHub Issue, Sentry Error, or "Proactive Improvement" cron
2. **Telemetry Analysis:** Research agents pull logs, stack traces
3. **Knowledge Retrieval:** Architect queries MemPalace

### Phase II: The Master Plan
1. **Drafting:** Sisyphus creates `Plan.md`
2. **Simulation:** Dry run to predict side effects

### Phase III: Parallel Execution
1. **TDD Loop:** Native OpenCode task dependencies
   ```python
   from opencodemultiagent import runTasks
   
   tasks = [
       {"agent": "prometheus", "category": "quick", "prompt": "Write failing test"},
       {"agent": "hephaestus", "category": "deep", "prompt": "Implement to pass test", "depends_on": [...]},
       {"agent": "oracle", "category": "ultrabrain", "prompt": "Security review", "depends_on": [...]}
   ]
   results = await runTasks(team, tasks)
   ```

### Phase IV: Verification & Self-Healing
1. **Integration:** Code merged to staging
2. **Shadow Deployment:** Canary environment
3. **Active Monitoring:** Watch telemetry for 10 minutes
4. **Self-Heal:** Git rollback if errors spike

---

## 4. Technical Implementation Stack - OPENCODE NATIVE

| Component | Original Plan | OpenCode Native |
| :--- | :--- | :--- |
| **Orchestrator** | Python/AsyncIO | `runTeam()` / `runTasks()` ✅ |
| **Agent Communication** | JSON-RPC/NATS | Built-in ACP ✅ |
| **Execution Environment** | Docker SDK | Native process isolation ✅ |
| **Session Management** | Custom | `opencode session` commands ✅ |
| **Context Compression** | Manual (50 turns) | Automatic in Sisyphus ✅ |
| **Memory System** | Neo4j/Qdrant/Redis | MemPalace MCP ✅ |
| **Observability** | LangSmith/W&B | Built-in tracing ✅ |
| **Coding Context** | Custom LSIF | LSP integration ✅ |

**Estimated Code Reduction: ~80%**

---

## 5. Essential MCP Servers

```bash
# Install MCP servers
opencode mcp add mempalace    # Memory layer (already configured!)
opencode mcp add github       # Git operations
opencode mcp add context7     # Documentation lookup
opencode mcp add chrome-devtools  # Browser testing
```

---

## 6. Safety & Guardrails - OPENCODE CONFIGURABLE

| Guardrail | OpenCode Feature | Configuration |
| :--- | :--- | :--- |
| **Financial Kill-Switch** | Token budget limits | `max_tokens_per_hour: 1000000` |
| **Sandbox Air-Gapping** | MCP permissions | `network_access: false` |
| **Write Protection** | File policies | `protected_paths: [".git/", "*.backup"]` |
| **Human-in-the-Loop** | Slack MCP | `approval_required: true` |

---

## 7. Quick Start

```bash
# 1. Start headless server
opencode serve --port 8080

# 2. Initialize Architect (Sisyphus)
curl -X POST http://localhost:8080/api/agent/start \
  -d '{"agent": "sisyphus", "session_name": "swarm-architect"}'

# 3. Submit first goal
curl -X POST http://localhost:8080/api/agent/message \
  -d '{"session_id": "swarm-architect", "message": "Implement user auth with JWT"}'
```

---

## 8. Continuous Self-Improvement

```bash
# Cron job for refactor mode
0 */6 * * * opencode run "Enter refactor mode: analyze complexity and propose improvements"
```

---

## CONCLUSION

**Build on OpenCode, not around it.**

By leveraging OpenCode's native capabilities:
- **Sisyphus agent** for Architect
- **Explore/Librarian/Metis** for research
- **Task categories** (deep/quick/ultrabrain) for workers
- **MemPalace MCP** for memory
- **runTeam/runTasks** for orchestration
- **MCP ecosystem** for integrations

You can reduce custom code by **~80%** and focus on unique business logic.

---

**Status:** *Operational / 24-7 Autonomous*
**Goal:** *Zero-latency development where code evolves as fast as requirements.*
**Platform:** *OpenCode v1.4.11*
**Memory:** *MemPalace MCP*
