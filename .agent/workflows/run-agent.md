---
description: How to run the Reflect-and-Heal (RAH) SQL Agent pipeline
---

To run the agent and interact with it via the command line, follow these steps:

1. Activate the virtual environment:
```bash
source .venv/bin/activate
```

2. Go to the `app` directory:
```bash
cd app
```

3. Run the main application:
```bash
python main.py
```

4. Enter your natural language question when prompted. The agent will:
   - Rewrite the query for better retrieval.
   - Perform parallel RAG across DB schema, business logic, and QnA examples.
   - Plan the SQL execution steps.
   - Generate, validate, and execute the SQL query.
   - Heal the query automatically if errors occur.
   - Provide a natural language analysis of the results.
