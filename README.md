# Project Swarm: 24/7 Autonomous Development & Self-Healing Harness

This document outlines the technical architecture and operational workflow for an end-to-end autonomous coding engine. The system is designed to operate without human intervention, moving from high-level objectives to researched, tested, and self-healed production code.

---

## 1. System Hierarchy (The "Team")

The harness operates using a functional separation of concerns to prevent context drift and ensure high-fidelity execution.

### A. The Architect (Persistent OpenCode Session)
* **Nature:** A single, long-running session with high-reasoning capabilities (e.g., GPT-4o or Claude 3.5 Sonnet).
* **Responsibility:**
  * Maintains the **Global Strategy**.
  * Decomposes high-level requirements into a **Directed Acyclic Graph (DAG)** of atomic tasks.
  * Manages the **MemPalace** indexing.
  * **Continuity:** Performs a "Context Compression" every 50 turns, summarizing the project state to stay within the token window while retaining long-term logic.

### B. The Research Agents (Internet & Log Enabled)
* **Nature:** Ephemeral workers with access to search engines, documentation, and system telemetry.
* **Responsibility:**
  * Investigates unknown libraries or cryptic error codes.
  * Performs "Code Discovery" on existing legacy modules.
  * Produces a **Research Memo** that the Architect uses to refine the plan.

### C. The Workers (Isolated Sandbox Sessions)
* **Nature:** Disposable Docker/Firecracker containers.
* **Responsibility:**
  * **The Coder:** Implements logic based on the Architect's brief.
  * **The Tester (SDET):** Writes failing tests (TDD) before the Coder begins.
  * **The Auditor:** Scans code for security vulnerabilities and "code smells."

---

## 2. Memory Layer: MemPalace

Unlike standard RAG, **MemPalace** is a multi-dimensional memory system.

| Layer | Technology | Function |
| :--- | :--- | :--- |
| **Graph Memory** | Neo4j / AST | Maps code dependencies (e.g., "Function X is called by File Y"). |
| **Episodic Memory** | Vector DB (Qdrant) | Stores "Lessons Learned" (e.g., "Last time we edited this, the Auth broke"). |
| **Semantic Memory** | Redis | Stores the current project structure, API schemas, and env variables. |
| **Spatial Memory** | File System | A structured "scratchpad" where the Architect organizes active working documents. |

---

## 3. The 0-24 Operational Lifecycle

### Phase I: Discovery & Research
1. **Trigger:** An issue is detected (GitHub Issue, Sentry Error, or a "Proactive Improvement" cron).
2. **Telemetry Analysis:** The Researcher pulls logs, stack traces, and environment state.
3. **Knowledge Retrieval:** The Architect queries **MemPalace** for related code blocks and past similar incidents.

### Phase II: The Master Plan
1. **Drafting:** The Architect creates a `Plan.md` containing:
   * Root cause analysis.
   * Step-by-step implementation DAG.
   * Rollback triggers (if performance degrades).
2. **Simulation:** The Architect runs a mental "dry run" to predict side effects on the dependency graph.

### Phase III: Parallel Execution
1. **Environment Provisioning:** The harness spins up isolated containers for the Coder and Tester.
2. **TDD Loop:**
   * **Tester** writes a test that fails on the current codebase.
   * **Coder** modifies code until the test passes.
   * **LSP/Linter** runs in the background; if it fails, the error is piped directly back to the Coder for self-correction.
3. **Peer Review:** A separate Reviewer worker compares the Coder's output against the `Plan.md` and the security policy.

### Phase IV: Verification & Self-Healing
1. **Integration:** The code is merged into a "Staging" branch.
2. **Shadow Deployment:** The harness deploys code to a "Canary" environment.
3. **Active Monitoring:** The harness watches the telemetry for 10 minutes.
4. **Self-Heal Trigger:**
   * **If Errors Spike:** The harness executes an immediate `git rollback`.
   * **Post-Mortem:** The Architect analyzes the failure logs, updates the **MemPalace** "Hazard Map," and generates a new, improved plan.

---

## 4. Technical Implementation Stack

* **Orchestrator:** Python (AsyncIO) for managing agent handoffs.
* **Agent Communication:** JSON-RPC over NATS (Message Bus).
* **Execution Environment:** Docker SDK for Python.
* **Coding Context:** `lsif` (Layered Semantic Indexing Format) to provide the Architect with a navigational map of the repository.
* **Observability:** LangSmith or Weights & Biases to track agent reasoning and cost.

---

## 5. Safety & Guardrails (The "Immutable Rules")

1. **Financial Kill-Switch:** If token spend exceeds $X/hour, all processes freeze and alert the human.
2. **Sandbox Air-Gapping:** Workers have no network access unless explicitly granted for a "Research" task.
3. **Write Protection:** The harness cannot delete the `.git/` folder or production database backups.
4. **Human-in-the-loop (Optional):** A "High-Impact" flag can be set by the Architect, requiring a Slack/Discord "thumbs up" before merging to the `main` branch.

---

## 6. Continuous Self-Improvement Loop

When the system is not fixing bugs, it enters **"Refactor Mode"**:
* **Step 1:** The Architect identifies the "messiest" module using cyclomatic complexity metrics.
* **Step 2:** Research workers look for modern library replacements or more efficient algorithms.
* **Step 3:** The system proposes, tests, and merges micro-refactors to constantly reduce technical debt.

---

**Status:** *Operational / 24-7 Autonomous*
**Goal:** *Zero-latency development where code evolves as fast as requirements.*