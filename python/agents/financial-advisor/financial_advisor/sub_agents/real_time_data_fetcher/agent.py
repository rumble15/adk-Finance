from google.adk.agent import Agent
from google.adk.tools import Tool

from .prompt import REAL_TIME_DATA_FETCHER_PROMPT

MODEL = "gemini-1.5-pro-latest" # Using the specified model, though the task description mentioned gemini-2.5-pro-preview-05-06, this one is more likely to be available.

def fetch_intraday_prices_tool_mock(ticker: str, interval: str, count: int):
    """Simulates fetching intraday price bars for a given ticker."""
    return f"Simulated {count} {interval} price bars for {ticker}"

def fetch_news_tool_mock(keywords: list[str], sources: list[str], max_articles: int):
    """Simulates fetching news articles based on keywords and sources."""
    return f"Simulated {max_articles} news articles for keywords: {keywords} from sources: {sources}"

def fetch_economic_data_tool_mock(indicator_name: str, country: str):
    """Simulates fetching economic data for a given indicator and country."""
    return f"Simulated economic data for {indicator_name} in {country}"

real_time_data_fetcher_agent = Agent(
    prompt=REAL_TIME_DATA_FETCHER_PROMPT,
    tools=[
        Tool.from_function(fetch_intraday_prices_tool_mock),
        Tool.from_function(fetch_news_tool_mock),
        Tool.from_function(fetch_economic_data_tool_mock),
    ],
    model=MODEL, # Using the specific model as requested
    output_key="real_time_data_output",
)
