# src/multi_agent_example.py
"""
Run a simple multi-agent system:
 - ResearchAgent uses google_search tool
 - SummarizerAgent summarizes the research_findings
 - ResearchCoordinator (root_agent) orchestrates the two agents

Run with: python src/multi_agent_example.py
"""
import os
import asyncio
from dotenv import load_dotenv

# load local .env (project root)
project_root = os.path.dirname(os.path.dirname(__file__))
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path)

# make sure API key exists
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY not found in .env. Add it and re-run.")

# Put key in environment for libraries that expect it:
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# ADK / GenAI imports
try:
    from google.adk.agents import Agent
    from google.adk.models.google_llm import Gemini
    from google.adk.runners import InMemoryRunner
    from google.adk.tools import AgentTool, google_search
    from google.genai import types
except Exception as e:
    raise RuntimeError(
        "Failed to import google-adk. Did you install dependencies? pip install -r requirements.txt"
    ) from e


# Retry config (same as your setup)
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)


# --- Define Agents ---------------------------------------------------------
# Research Agent: uses google_search tool and stores results in "research_findings"
research_agent = Agent(
    name="ResearchAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction=(
        "You are ResearchAgent. Use the google_search tool to find 2 short, "
        "relevant pieces of information about the user's topic. Return results "
        "with a short source citation for each finding. Output must be plain text."
    ),
    tools=[google_search],
    output_key="research_findings",
)

# Summarizer Agent: summarizes provided research_findings into 3 bullet points
summarizer_agent = Agent(
    name="SummarizerAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction=(
        "You are SummarizerAgent. Read the provided research findings: {research_findings}\n\n"
        "Create a concise bulleted list of 3 key points that capture the most important"
        " information. Each bullet should be a single sentence."
    ),
    output_key="final_summary",
)

# Root / Coordinator agent that calls the two subagents as tools
root_agent = Agent(
    name="ResearchCoordinator",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction=(
        "You are a research coordinator. Given the user's topic, you MUST:\n"
        "1) Call the ResearchAgent tool to gather research findings.\n"
        "2) Call the SummarizerAgent tool using the findings to produce a final summary.\n"
        "Return only the final summary as your response."
    ),
    tools=[AgentTool(research_agent), AgentTool(summarizer_agent)],
)


# --- Runner & Execution ----------------------------------------------------
async def run_example(topic: str):
    runner = InMemoryRunner(agent=root_agent)
    print(f"\n### Starting session — topic: {topic}\n")
    # run_debug will output a debug trace; use run(...) for normal runs. We'll use run_debug here to see steps.
    try:
        response = await runner.run_debug(topic)
    except Exception as exc:
        print("Error running agents:", exc)
        return

    # The runner returns a session object and final text; print the final text.
    # run_debug prints a debug trace; but we'll also show final result if available:
    try:
        # The runner may attach outputs in the session state; attempt to read final_summary
        session_state = runner._last_session_state  # private, may or may not exist depending on ADK version
        if session_state:
            final = session_state.get("final_summary") or session_state.get("research_findings")
            if final:
                print("\n--- Final (from session state) ---\n")
                print(final)
    except Exception:
        # Not critical — some ADK versions don't expose internal state this way
        pass

    print("\n### Done.\n")


def main():
    topic = "What are the latest advancements in quantum computing and what do they mean for AI?"
    asyncio.run(run_example(topic))


if __name__ == "__main__":
    main()
