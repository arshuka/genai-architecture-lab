The LLM + Memory architecture extends the basic LLM pattern by introducing a memory layer that allows the system to retain, retrieve, and reuse information across interactions.

In this architecture, the user interacts through a UI or API. Each request is sent to the Large Language Model (LLM) along with relevant context retrieved from the memory store.

The memory layer typically stores:
- Conversation history
- User preferences
- Important facts or summaries
- Long-term contextual information

When a new request arrives, the system retrieves relevant memory entries and injects them into the prompt before calling the LLM. This enables the model to produce responses that are more contextual, consistent, and personalized.

After generating a response, selected information from the interaction can be written back to memory for future use. This creates a feedback loop that improves continuity over time.

The memory store can be implemented using databases, vector stores, key-value stores, or a combination of short-term and long-term memory mechanisms.

This architecture enables persistent context without retraining the model and without relying solely on the prompt window.

Common use cases include:
- Conversational assistants with continuity
- Personalized AI applications
- Coaching, tutoring, or mentoring systems
- Customer support with session awareness

This pattern does not inherently include external tools or live data access unless explicitly extended.
