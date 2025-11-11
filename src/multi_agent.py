# src/multi_agent.py
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables from .env
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# ADK imports
from google.adk.agents import Agent
from google.adk.tools import google_search, AgentTool
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types


retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)



research_agent = Agent(
    name="ResearchAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""
You are a specialized research agent. Your only job is to use google_search
to find 2-3 relevant pieces of information on the topic and present findings with citations.
""",
    tools=[google_search],
    output_key="research_findings"
)

print("✅ research_agent created.")


summarizer_agent = Agent(
    name="SummarizerAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""
Read the provided research findings: {research_findings}
Create a concise summary as a bulleted list with 3-5 key points.
""",
    output_key="final_summary"
)

print("✅ summarizer_agent created.")

fact_checker_agent = Agent(
    name="FactCheckerAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""
Verify the research findings in {research_findings}.
Highlight any inaccurate or doubtful statements clearly.
""",
    output_key="fact_checked_findings"
)

print("✅ fact_checker_agent created.")


translator_agent = Agent(
    name="TranslatorAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""
Translate the final summary {final_summary} into Spanish.
""",
    output_key="translated_summary"
)

print("✅ translator_agent created.")


formatter_agent = Agent(
    name="FormatterAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""
Format {final_summary} (or {translated_summary} if available) into a clean report
with headings, bullet points, and proper structure.
""",
    output_key="formatted_report"
)

print("✅ formatter_agent created.")


root_agent = Agent(
    name="ResearchCoordinator",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""
You are a research coordinator. Your goal is to answer the user's query by orchestrating this workflow:
1. Call ResearchAgent to gather information.
2. Pass results to FactCheckerAgent to verify accuracy.
3. Summarize the fact-checked findings using SummarizerAgent.
4. Optionally, translate the summary using TranslatorAgent.
5. Format the final output using FormatterAgent.
6. Present the formatted final report to the user.
""",
    tools=[
        AgentTool(research_agent),
        AgentTool(fact_checker_agent),
        AgentTool(summarizer_agent),
        AgentTool(translator_agent),
        AgentTool(formatter_agent)
    ]
)

print("✅ root_agent created.")



runner = InMemoryRunner(agent=root_agent)

query = "Explain the impact of AI on cybersecurity in 2025."
response = asyncio.run(runner.run_debug(query))

print("\n--- Final Response ---\n")
print(response)

