The LLM + System Prompt architecture extends the basic LLM pattern by introducing
a persistent system-level instruction that governs how the model behaves for
every interaction.

In this architecture, each request sent to the LLM consists of two parts:

1. The system prompt defines the role, tone, rules, and constraints of the model.
2. The user prompt defines the actual question or task.

The system prompt is always applied first and remains constant across all user
interactions. This ensures consistent behavior regardless of how users phrase
their inputs.

This pattern allows developers to control the model’s personality, boundaries,
and response style without changing application code.

It is commonly used to enforce professional tone, domain boundaries, safety
constraints, and role-based behavior.

Typical examples include defining the model as a cloud architect, financial
advisor, tutor, interviewer, or customer support agent.

This architecture does not include memory, tools, or external data sources unless
explicitly extended.