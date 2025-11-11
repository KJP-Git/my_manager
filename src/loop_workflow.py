# src/loop_workflow.py

import os
import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent, LoopAgent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types
from google.adk.tools import FunctionTool  # Needed to wrap exit_loop

# -------------------------------
# 1. Environment setup
# -------------------------------
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY not found. Check your .env file.")
else:
    print("✅ GOOGLE_API_KEY loaded successfully.")

# -------------------------------
# 2. Retry configuration
# -------------------------------
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# -------------------------------
# 3. Agents
# -------------------------------

# Initial writer agent
initial_writer_agent = Agent(
    name="InitialWriterAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""Based on the user's prompt, write the first draft of a short story
(around 100-150 words). Output only the story text.""",
    output_key="current_story",
)
print("✅ initial_writer_agent created.")

# Critic agent
critic_agent = Agent(
    name="CriticAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""You are a constructive story critic. Review the story below.

Story: {current_story}

- If the story is well-written and complete, respond exactly with "APPROVED".
- Otherwise, provide 2-3 actionable suggestions for improvement.""",
    output_key="critique",
)
print("✅ critic_agent created.")

# Exit function for the loop
def exit_loop():
    """Call only when critique == 'APPROVED' to stop the loop."""
    return {"status": "approved", "message": "Story approved. Exiting refinement loop."}

print("✅ exit_loop function created.")

# Refiner agent
refiner_agent = Agent(
    name="RefinerAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""You are a story refiner.

Story Draft: {current_story}
Critique: {critique}

- IF critique == "APPROVED", call `exit_loop` and do nothing else.
- ELSE, rewrite the story to fully incorporate the critique.""",
    output_key="current_story",  # overwrites the draft
    tools=[FunctionTool(exit_loop)],
)
print("✅ refiner_agent created.")

# -------------------------------
# 4. Loop Agent
# -------------------------------
story_refinement_loop = LoopAgent(
    name="StoryRefinementLoop",
    sub_agents=[critic_agent, refiner_agent],
    max_iterations=2,  # prevents infinite loops
)

# Sequential agent: initial draft → loop
root_agent = SequentialAgent(
    name="StoryPipeline",
    sub_agents=[initial_writer_agent, story_refinement_loop],
)
print("✅ Loop and Sequential Agents created.")

# -------------------------------
# 5. Run the workflow
# -------------------------------
runner = InMemoryRunner(agent=root_agent)

async def main():
    prompt = "Write a short story about a lighthouse keeper who discovers a mysterious, glowing map"
    response = await runner.run_debug(prompt)
    print("✅ Workflow complete.\n\n--- Final Story ---\n")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
