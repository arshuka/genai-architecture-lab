## ⚖️ LLM + Moderation — Trade-offs

### Advantages

- Enables enterprise and public-facing AI deployments
- Reduces legal, ethical, and reputational risk
- Improves trust and adoption of AI systems
- Supports compliance audits and governance reviews
- Prevents common misuse and jailbreak scenarios

### Limitations

- Adds latency due to additional moderation checks
- Increases per-request operational cost
- Can produce false positives that block valid user queries
- Requires ongoing policy tuning and maintenance
- Does not guarantee complete safety in all scenarios

### Failure Modes

- Overly strict moderation reduces usability
- Missing output moderation allows unsafe hallucinations
- Storing raw prompts can introduce privacy risks
- Inconsistent policy versions cause audit gaps

### Best Suited For

- Public-facing AI applications
- Enterprise copilots and assistants
- Regulated industries such as finance and healthcare
- Customer support and decision-support systems

### Not Suited For

- Internal experimentation or quick POCs
- Offline batch processing with no user exposure
- One-shot scripts without persistence or compliance needs

### Taxonomy Alignment

- Intelligence Model: LLM
- Capability: Moderation
- Application Archetype: Assistant / Copilot
- Enterprise Layer: Governance and Compliance
