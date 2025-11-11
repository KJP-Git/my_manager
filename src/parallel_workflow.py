import os
import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types

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
# 3. Researcher Agents
# -------------------------------
tech_researcher = Agent(
    name="TechResearcher",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""Research the latest AI/ML trends.
Include 3 key developments, the main companies involved,
and the potential impact. Keep the report concise (≈100 words).""",
    output_key="tech_research",
)
print("✅ tech_researcher created.")

health_researcher = Agent(
    name="HealthResearcher",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""Research recent medical breakthroughs.
Include 3 major advances, their practical uses, and estimated timelines.
Keep the report concise (≈100 words).""",
    output_key="health_research",
)
print("✅ health_researcher created.")

finance_researcher = Agent(
    name="FinanceResearcher",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""Research current fintech trends.
Include 3 key trends, their market implications, and future outlook.
Keep the report concise (≈100 words).""",
    output_key="finance_research",
)
print("✅ finance_researcher created.")

# -------------------------------
# 4. Aggregator Agent
# -------------------------------
aggregator_agent = Agent(
    name="AggregatorAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""Combine these three research findings into a single executive summary:

**Technology Trends:**
{tech_research}

**Health Breakthroughs:**
{health_research}

**Finance Innovations:**
{finance_research}

Highlight common themes, surprising links, and key takeaways.
Keep the summary around 200 words.""",
    output_key="executive_summary",
)
print("✅ aggregator_agent created.")

# -------------------------------
# 5. Combine agents
# -------------------------------
parallel_research_team = ParallelAgent(
    name="ParallelResearchTeam",
    sub_agents=[tech_researcher, health_researcher, finance_researcher],
)

root_agent = SequentialAgent(
    name="ResearchSystem",
    sub_agents=[parallel_research_team, aggregator_agent],
)
print("✅ Parallel and Sequential Agents created.")

# -------------------------------
# 6. Run the workflow
# -------------------------------
runner = InMemoryRunner(agent=root_agent)

async def main():
    response = await runner.run_debug(
        "Run the daily executive briefing on Tech, Health, and Finance"
    )
    print("✅ Workflow complete.\n\n--- Final Executive Summary ---\n")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
