# src/agent_setup.py
import os
from dotenv import load_dotenv

# load .env (local dev)
project_root = os.path.dirname(os.path.dirname(__file__))
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path)

# Validate API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError(
        "GOOGLE_API_KEY not found. Add it to .env or set environment variable."
    )

# Place the key in env for libraries that read it
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# ADK imports
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import AgentTool, FunctionTool, google_search
from google.genai import types

def get_retry_config():
    # Configure retries (exponential backoff)
    retry_config = types.HttpRetryOptions(
        attempts=5,
        exp_base=7,
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504],
    )
    return retry_config

def make_gemini_model():
    # Example: instantiate Gemini model wrapper (adjust model name/args per docs)
    gemini = Gemini(api_key=GOOGLE_API_KEY, retry=get_retry_config())
    return gemini

def main():
    print("✅ Environment and API key loaded.")
    print("✅ ADK components available.")
    # Example usage (placeholder) — adapt to your agents
    model = make_gemini_model()
    # Build a simple agent example (adjust for your real agent code)
    # agent = Agent(model=model, tools=[...])
    # runner = InMemoryRunner(agent)
    print("You can now instantiate agents. Edit src/agent_setup.py to build your agents.")

if __name__ == "__main__":
    main()
