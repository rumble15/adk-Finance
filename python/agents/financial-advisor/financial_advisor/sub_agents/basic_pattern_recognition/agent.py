from google.adk.agent import Agent
from google.adk.tools import Tool

from .prompt import BASIC_PATTERN_RECOGNITION_PROMPT

MODEL = "gemini-1.5-pro-latest"

def analyze_price_volume_tool_mock(intraday_prices: list):
    """Simulates finding price/volume surges."""
    if not intraday_prices:
        return {"detected": False, "details": "Insufficient price data."}
    # Simulate finding a surge
    return {"detected": True, "timestamp": "2023-10-27 10:30:00", "details": "Simulated surge: Significant volume increase observed with a 2% price jump."}

def analyze_news_correlation_tool_mock(intraday_prices: list, news_articles: list):
    """Simulates correlating price moves with news."""
    if not news_articles:
        return {"detected": False, "details": "No news articles provided."}
    if not intraday_prices: # Added check for intraday_prices as it's an input
        return {"detected": False, "details": "Insufficient price data for news correlation."}
    # Simulate finding a correlation
    return {"detected": True, "details": "Simulated correlation: Price movement correlates with positive sentiment in news article X."}

def analyze_time_of_day_volatility_tool_mock(intraday_prices: list):
    """Simulates identifying time-of-day volatility patterns."""
    if not intraday_prices:
        return {"detected": False, "details": "Insufficient price data."}
    # Simulate identifying a pattern
    return {"period": "first_hour", "avg_volatility": "0.5%", "details": "Simulated: Average volatility in the first hour is 0.5%."}

basic_pattern_recognition_agent = Agent(
    prompt=BASIC_PATTERN_RECOGNITION_PROMPT,
    tools=[
        Tool.from_function(analyze_price_volume_tool_mock),
        Tool.from_function(analyze_news_correlation_tool_mock),
        Tool.from_function(analyze_time_of_day_volatility_tool_mock),
    ],
    model=MODEL,
    output_key="pattern_recognition_output",
)
