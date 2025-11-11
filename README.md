## Section 6: Summary - Choosing the Right Pattern

### Decision Tree: Which Workflow Pattern?

| Pattern     | When to Use                     | Example                     | Key Feature                    |
|------------|--------------------------------|----------------------------|--------------------------------|
| LLM-based  | Dynamic orchestration needed     | Research + Summarize       | LLM decides what to call       |
| Sequential | Order matters, linear pipeline   | Outline → Write → Edit     | Deterministic order            |
| Parallel   | Independent tasks, speed matters| Multi-topic research       | Concurrent execution           |
| Loop       | Iterative improvement needed    | Writer + Critic refinement | Repeated cycles                |

---

### ✅ Congratulations! You're Now an Agent Orchestrator

In this project, you advanced from a single agent to a **multi-agent system**.

- You learned why a team of specialized agents is easier to build, debug, and maintain than a single "do-it-all" agent.
- You mastered `SequentialAgent`, `ParallelAgent`, and `LoopAgent` to create deterministic workflows.
- You saw how an LLM can act as a 'manager' to make dynamic decisions.
- You practiced using `output_key` to pass state between agents, enabling collaboration.

> ℹ️ Note: This is for **hands-on practice only**, no submission required.

### 📚 Learn More
- [Agents in ADK](#)
- [Sequential Agents in ADK](#)
- [Parallel Agents in ADK](#)
- [Loop Agents in ADK](#)
- [Custom Agents in ADK](#)

### 🎯 Next Steps
Stay tuned for upcoming notebooks where you will:
- Create Custom Functions
- Use MCP Tools
- Manage Long-Running operations
