# src/sequential_workflow.py

import os
import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types


load_dotenv()

# ✅ (Optional sanity check)
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY not found! Check your .env file.")
else:
    print("✅ GOOGLE_API_KEY loaded successfully.")


# Retry configuration for LLM calls
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# -------------------------------
# 1. Outline Agent
# -------------------------------
outline_agent = Agent(
    name="OutlineAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction="""Create a blog outline for the given topic with:
    1. A catchy headline
    2. An introduction hook
    3. 3-5 main sections with 2-3 bullet points for each
    4. A concluding thought""",
    output_key="blog_outline",
)
print("✅ outline_agent created.")

# -------------------------------
# 2. Writer Agent
# -------------------------------
writer_agent = Agent(
    name="WriterAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction="""Following this outline strictly: {blog_outline}
    Write a brief, 200 to 300-word blog post with an engaging and informative tone.""",
    output_key="blog_draft",
)
print("✅ writer_agent created.")

# -------------------------------
# 3. Editor Agent
# -------------------------------
editor_agent = Agent(
    name="EditorAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction="""Edit this draft: {blog_draft}
    Your task is to polish the text by fixing any grammatical errors, improving flow and sentence structure, and enhancing overall clarity.""",
    output_key="final_blog",
)
print("✅ editor_agent created.")

# -------------------------------
# 4. Sequential Agent: Pipeline
# -------------------------------
root_agent = SequentialAgent(
    name="BlogPipeline",
    sub_agents=[outline_agent, writer_agent, editor_agent],
)
print("✅ Sequential Agent created.")

# -------------------------------
# 5. Run the pipeline
# -------------------------------
runner = InMemoryRunner(agent=root_agent)

# Example topic
topic = "Benefits of multi-agent systems for software developers"

# Run the workflow (correct async call)
response = asyncio.run(runner.run_debug(topic))

print("✅ Workflow complete.")
print("\n--- Final Blog Output ---\n")
print(response)
