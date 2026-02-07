The LLM + Tools architecture extends the LLM + System Prompt pattern by allowing the model to actively invoke external tools during response generation.

In this architecture, the user interacts through a UI or API, and the request is forwarded to the LLM along with the system prompt. Based on the task, the LLM can decide to call one or more tools to fetch data, execute logic, or perform actions before generating the final response.

Tools can include:
- Web search
- Database queries
- API calls
- Code execution
- Calculations
- Internal services

The LLM does not directly access these tools. Instead, it produces a structured tool-call request, which is executed by the application or orchestration layer. The results from the tools are then passed back to the LLM as context, allowing it to reason over real-world or computed data.

This architecture enables the LLM to go beyond its static training knowledge and produce accurate, up-to-date, and actionable responses.

The system prompt still governs behavior, tone, and constraints, while tools extend the model’s capabilities.

This pattern is commonly used in production-grade AI systems where reasoning alone is insufficient and real-world interaction is required.




