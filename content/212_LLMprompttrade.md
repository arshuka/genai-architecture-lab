Advantages:

- Consistent behavior across all responses
- Clear separation between behavior control and user intent
- Easy to modify and experiment by changing prompts
- Low infrastructure and operational complexity
- Lower latency compared to tool-based or retrieval-based systems

Limitations:

- No access to real-time or external data
- Highly sensitive to prompt quality and wording
- Difficult to manage very large or complex system prompts
- No built-in memory or personalization
- Responses are limited to the model’s training knowledge

Best suited for:

- Domain-specific assistants
- Role-based conversational systems
- Prompt engineering experiments
- Early production GenAI systems
- Scenarios where predictable behavior is required

Not suitable for:

- Applications requiring live data
- Systems needing long-term memory
- Complex workflows or multi-step reasoning
- Tool execution or automation-heavy use cases

Architectural positioning:

This pattern sits between basic LLM usage and advanced architectures:

- Basic LLM
- LLM + System Prompt
- LLM + Tools / RAG / Agents

It is often the first GenAI architecture used in real production environments.
