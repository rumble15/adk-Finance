from google.adk.agents import LlmAgent # Corrected import from google.adk.agent to google.adk.agents

from .prompt import INTRADAY_DATA_ANALYST_PROMPT

MODEL = "gemini-1.5-pro-latest"

intraday_data_analyst_agent = LlmAgent(
    prompt=INTRADAY_DATA_ANALYST_PROMPT,
    # No tools are needed for this agent as it only synthesizes provided data.
    # tools=[], # Explicitly empty or omitted
    model=MODEL,
    output_key="intraday_analysis_summary",
)
