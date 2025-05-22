# Agent Communication Protocol for Dynamic Data Sharing and Event Subscription

**Version:** 1.0
**Date:** October 28, 2023

## 1. Introduction

This document outlines a design for an agent communication protocol to enable more dynamic, event-driven collaboration between agents within the ADK framework. The current model primarily relies on sequential data handoffs. This protocol aims to allow agents to proactively share and react to data and events in real-time, fostering more responsive and intelligent multi-agent systems.

## 2. Proposed Approach: Internal Asynchronous Message Bus/Broker

We propose an **Internal Asynchronous Message Bus/Broker** integrated within the ADK framework. This approach is chosen for the following reasons:

*   **Decoupling:** Agents do not need direct knowledge of each other. They publish messages to the bus and subscribe to topics of interest. This promotes modularity and scalability.
*   **Asynchronous Operation:** Aligns with the need for non-blocking operations, allowing agents to continue processing while waiting for or publishing messages.
*   **Centralized Management (within ADK):** Simplifies integration, deployment, and monitoring as part of the existing ADK infrastructure.
*   **Flexibility:** Can support various communication patterns (publish/subscribe, potentially point-to-point if needed later).
*   **Control:** As an internal component, ADK can manage message persistence, delivery guarantees (e.g., at-least-once), and resource allocation.

A distributed event queue (like Kafka or RabbitMQ) could be considered for very large-scale, inter-application communication, but for intra-application agent collaboration as described, an internal bus offers a good balance of features and integration simplicity. A shared memory model might be more complex to manage safely across potentially distributed agent processes and less flexible for event-driven architectures.

## 3. Data and Event Structure

Messages published to the bus will consist of a header and a payload.

**Message Header:**
*   `message_id`: Unique identifier for the message.
*   `topic`: A string defining the "channel" or type of data/event (e.g., `data.stock.intraday_bar`, `event.pattern.price_volume_surge`).
*   `publisher_agent_id`: Identifier of the agent publishing the message.
*   `timestamp`: UTC timestamp of when the message was published.
*   `content_type`: (e.g., `application/json`, `pydantic/model_name`)
*   `version`: Version of the payload schema.

**Message Payload:**
The payload will be structured data, ideally using Pydantic models for validation and clear schema definition within the Python-based ADK.

**Example Data/Event Structures (using Pydantic-like syntax for illustration):**

```python
# Example Pydantic Models
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import datetime

class StockPriceBar(BaseModel):
    ticker: str
    timestamp: datetime.datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    interval_minutes: int = Field(default=1)

class NewsArticle(BaseModel):
    source: str
    headline: str
    summary: str
    url: str
    published_at: datetime.datetime
    tickers_mentioned: List[str] = []

class EconomicIndicator(BaseModel):
    indicator_name: str
    country: str
    value: Any
    unit: str
    release_date: datetime.datetime

# --- Event Payloads ---
class PriceVolumeSurgePattern(BaseModel):
    ticker: str
    detected_at: datetime.datetime
    surge_price: float
    surge_volume: int
    details: str

class NewsCorrelationEvent(BaseModel):
    ticker: str
    news_article_id: str # ID of the correlated NewsArticle message
    price_change_percentage: float
    correlation_strength: float # e.g., 0.0 to 1.0
    details: str
```

**Topics:**
Topics will be hierarchical strings, allowing for wildcard subscriptions (if supported by the bus implementation).
*   `data.stock.intraday_bar.{ticker}` (e.g., `data.stock.intraday_bar.AAPL`)
*   `data.news.{source}.{ticker_or_keyword}` (e.g., `data.news.bloomberg.AAPL`)
*   `data.economic.{country}.{indicator_name}`
*   `event.pattern.price_volume_surge.{ticker}`
*   `event.pattern.news_correlation.{ticker}`
*   `event.system.agent_status.{agent_id}`

## 4. API/Interface Ideas (Conceptual)

Agents would interact with the message bus via methods provided by the ADK framework.

**Publishing:**
```python
class Agent:
    # ... other ADK agent properties and methods ...

    async def publish_message(self, topic: str, payload: BaseModel, version: str = "1.0"):
        """
        Publishes a structured message (Pydantic model) to a specific topic on the bus.
        The ADK would handle serialization, header creation, and sending.
        """
        # bus_instance = self.adk_context.get_message_bus()
        # await bus_instance.publish(topic=topic, publisher_id=self.id, payload=payload, version=version)
        pass
```

**Subscribing:**
Subscription could happen declaratively or programmatically.

*   **Declarative Subscription (Preferred for simplicity):**
    Agents could declare their subscriptions as part of their configuration or initialization. The ADK would manage registering these with the bus.

    ```python
    class MyListeningAgent(Agent):
        # ...
        SUBSCRIPTIONS = [
            {"topic": "data.stock.intraday_bar.AAPL", "handler_method": "handle_aapl_price_bar"},
            {"topic": "event.pattern.#", "handler_method": "handle_any_pattern_event"} # Wildcard example
        ]

        async def handle_aapl_price_bar(self, message_header: Dict, payload: StockPriceBar):
            # Process the AAPL price bar
            print(f"Received AAPL price: {payload.close}")

        async def handle_any_pattern_event(self, message_header: Dict, payload: BaseModel):
            # Process any pattern event
            if isinstance(payload, PriceVolumeSurgePattern):
                print(f"Price surge for {payload.ticker}!")
            # ...
    ```
    The ADK's agent runner would route incoming messages to the appropriate handler method.

*   **Programmatic Subscription:**
    ```python
    class Agent:
        # ...
        async def subscribe(self, topic: str, callback_method: callable):
            """
            Programmatically subscribes to a topic and registers a callback.
            """
            # bus_instance = self.adk_context.get_message_bus()
            # await bus_instance.subscribe(topic=topic, agent_id=self.id, callback=callback_method)
            pass

        async def on_message(self, message_header: Dict, payload: BaseModel):
            # Generic message handler if not using specific callbacks per topic
            pass
    ```

**Receiving Messages:**
As shown above, messages would be delivered to registered handler methods or a generic `on_message` method. The handler would receive the deserialized payload (ideally as a Pydantic model instance) and the message header.

## 5. Workflow Example

**Agents:**
1.  `RealTimeDataFetcherAgent` (RTDF): Fetches stock prices.
2.  `BasicPatternRecognitionAgent` (BPR): Identifies price/volume surges.
3.  `IntradayStrategyAgent` (ISA): Consumes patterns to suggest strategies (simplified for this example).

**Flow:**

1.  **Initialization:**
    *   `BPR` subscribes to `data.stock.intraday_bar.{ticker}` (e.g., for "AAPL"). Its handler is `bpr.handle_price_update`.
    *   `ISA` subscribes to `event.pattern.price_volume_surge.{ticker}` (e.g., for "AAPL"). Its handler is `isa.handle_pattern_detected`.

2.  **Data Publishing:**
    *   `RTDF` fetches a new 1-minute bar for AAPL.
    *   `RTDF` calls: `await self.publish_message(topic="data.stock.intraday_bar.AAPL", payload=StockPriceBar(...))`

3.  **Pattern Recognition Consumes and Publishes:**
    *   The message bus delivers the `StockPriceBar` message to `BPR.handle_price_update`.
    *   `BPR` analyzes the new bar along with recent history. It detects a price/volume surge.
    *   `BPR` calls: `await self.publish_message(topic="event.pattern.price_volume_surge.AAPL", payload=PriceVolumeSurgePattern(...))`

4.  **Strategy Agent Consumes:**
    *   The message bus delivers the `PriceVolumeSurgePattern` message to `ISA.handle_pattern_detected`.
    *   `ISA` processes the pattern: "A price/volume surge has been detected for AAPL. This might be an opportunity for a momentum strategy."
    *   `ISA` might then publish another event (e.g., `event.strategy.new_opportunity.AAPL`) or update its internal state to inform the `FinancialCoordinator` when next polled.

This workflow allows `BPR` and `ISA` to react to data as it becomes available, without `RTDF` needing to know about them, or the `FinancialCoordinator` having to orchestrate each micro-step explicitly.

## 6. Considerations for ADK Integration

*   **Message Bus Implementation:**
    *   ADK could provide a default, in-memory asynchronous message bus for single-process deployments.
    *   For multi-process or distributed agent deployments, ADK could offer adapters for robust message brokers (e.g., Redis Pub/Sub, RabbitMQ, NATS). The choice of broker could be a configuration option.
*   **Agent Lifecycle:**
    *   Subscription registration would occur during agent initialization.
    *   Unsubscription would occur during agent shutdown.
    *   The ADK agent's main execution loop would need to `await` or `select` on incoming messages from its subscriptions, alongside its other tasks (like handling direct requests from the coordinator). This could be managed by the ADK runtime, which invokes registered handlers.
*   **State Management:** This protocol focuses on event passing. If shared *state* (not just events) is needed, it would be complementary. For instance, an agent might receive an event and then update a shared state object (perhaps managed via ADK's existing state mechanisms, or a dedicated state store if complexity warrants it).
*   **Data Persistence:**
    *   The message bus itself might offer short-term persistence (e.g., replay last N messages on a topic for late subscribers).
    *   For longer-term data logging or audit, messages could be archived to a database by a dedicated logging agent subscribing to relevant topics (e.g., `data.#`, `event.#`).
    *   This design assumes data within messages is self-contained or references other identifiable data. It does not inherently provide a distributed database for agents.
*   **Agent Discovery (Future Enhancement):**
    *   A "service registry" pattern could be implemented on top of the bus. Agents could publish their "capabilities" (topics they publish to, services they offer) to a well-known topic (e.g., `system.registry.agent_announce`).
    *   Other agents could subscribe to this topic to discover peers.
*   **Error Handling and Delivery Guarantees:**
    *   The bus should define what happens if an agent is unavailable or fails to process a message (e.g., dead-letter queues, retry mechanisms). This would be part of the bus implementation choice.
    *   For critical events, "at-least-once" delivery would be important.
*   **Security:**
    *   If ADK supports multi-tenancy or external agent communication, topic-level access controls might be needed. For the current internal financial advisor scope, this is likely less critical.

## 7. Conclusion

An internal asynchronous message bus offers a robust and flexible way to enhance inter-agent communication within the ADK. By enabling dynamic data sharing and event subscription, it can lead to more responsive, decoupled, and intelligent agent systems. The proposed API and data structures aim to integrate smoothly with the existing Pydantic-based ADK patterns, providing a powerful yet manageable extension to its capabilities.
```
