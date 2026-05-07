# Execution Logs

This file is updated after each milestone with console output that demonstrates the assignment phases.

## Milestone 1: Phase 1 Persona Routing

Command:

```powershell
$env:PYTHONPATH='D:\AI_Agents\1rag_ai_agent\src'
python -m grid07_ai_agent.cli route 'OpenAI just released a new model that might replace junior developers.' --threshold 0.35
```

Output:

```json
{
  "post_content": "OpenAI just released a new model that might replace junior developers.",
  "matched_bots": [
    {
      "bot_id": "bot_a",
      "name": "Tech Maximalist",
      "similarity": 0.4806
    },
    {
      "bot_id": "bot_b",
      "name": "Doomer / Skeptic",
      "similarity": 0.374
    }
  ]
}
```

Command:

```powershell
$env:PYTHONPATH='D:\AI_Agents\1rag_ai_agent\src'
python -m grid07_ai_agent.cli route 'The Fed held interest rates while trading algorithms chased market ROI.' --threshold 0.45
```

Output:

```json
{
  "post_content": "The Fed held interest rates while trading algorithms chased market ROI.",
  "matched_bots": [
    {
      "bot_id": "bot_c",
      "name": "Finance Bro",
      "similarity": 0.9712
    }
  ]
}
```

Test command:

```powershell
$env:PYTHONPATH='D:\AI_Agents\1rag_ai_agent\src'
python -m unittest discover -s tests
```

Result:

```text
Ran 3 tests in 0.006s

OK
```
