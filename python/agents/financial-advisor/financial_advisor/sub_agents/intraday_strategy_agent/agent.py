from google.adk.agents import LlmAgent

from .prompt import INTRADAY_STRATEGY_AGENT_PROMPT

MODEL = "gemini-1.5-pro-latest"

intraday_strategy_agent = LlmAgent(
    prompt=INTRADAY_STRATEGY_AGENT_PROMPT,
    tools=[], # No tools needed for this agent
    model=MODEL,
    output_key="intraday_strategy_proposals",
)
