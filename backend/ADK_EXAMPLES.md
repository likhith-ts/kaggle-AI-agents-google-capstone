# Google ADK Integration - Usage Examples

This file demonstrates how to use the real Google ADK integration in your project.

## Quick Start

### 1. Initialize Services

```python
from app.orchestration import initialize_adk_services

# Initialize once at startup
initialize_adk_services()
```

### 2. Create and Use Agents

```python
from app.orchestration import (
    create_triage_agent,
    create_explain_agent,
    create_runbook_agent,
    create_policy_agent,
)

# These are REAL google.adk.Agent instances
triage_agent = create_triage_agent()
explain_agent = create_explain_agent()
runbook_agent = create_runbook_agent()
policy_agent = create_policy_agent()

print(f"Agent type: {type(triage_agent)}")  # <class 'google.adk.agents.llm_agent.LlmAgent'>
print(f"Agent name: {triage_agent.name}")    # "TriageAgent"
```

## Detailed Examples

### Example 1: Run Triage Agent with Session

```python
import asyncio
from app.orchestration import (
    initialize_adk_services,
    run_triage_with_adk,
    retrieve_memory_entry,
)

async def triage_incident():
    # Initialize once
    initialize_adk_services()

    # Incident features
    features = {
        "failed_logins_last_hour": 50,
        "unique_ips": 15,
        "countries": ["US", "CN", "RU"],
        "target_users": ["admin", "root"],
    }

    # Run triage with session support
    session_id = "incident-12345"
    result = await run_triage_with_adk(
        features=features,
        session_id=session_id,
    )

    print(f"Label: {result.label}")      # "CRITICAL"
    print(f"Score: {result.score}")      # 0.95
    print(f"Factors: {result.contribs}") # {"failed_logins": 0.4, ...}

    # Session automatically stored result
    # Can retrieve from memory later
    stored_result = await retrieve_memory_entry(session_id, "triage_result")
    print(f"Stored: {stored_result}")

# Run
asyncio.run(triage_incident())
```

### Example 2: Multi-Agent Orchestration

```python
import asyncio
from app.orchestration import (
    initialize_adk_services,
    run_triage_with_adk,
    run_explain_with_adk,
    run_runbook_with_adk,
    retrieve_memory_entry,
)

async def full_incident_response():
    initialize_adk_services()

    features = {
        "failed_logins_last_hour": 50,
        "unique_ips": 15,
        "countries": ["US", "CN", "RU"],
        "target_users": ["admin", "root"],
    }

    session_id = "incident-xyz"

    # Step 1: Triage
    print("1️⃣  Running Triage Agent...")
    triage_result = await run_triage_with_adk(features, session_id)
    print(f"   Result: {triage_result.label} ({triage_result.score})")

    # Step 2: Explain (can run in parallel)
    print("2️⃣  Running Explain Agent...")
    explanation = await run_explain_with_adk(
        features=features,
        triage=triage_result,
        session_id=session_id,
    )
    print(f"   Generated {len(explanation.get('reasons', []))} reasons")

    # Step 3: Runbook (can run in parallel)
    print("3️⃣  Running Runbook Agent...")
    runbook = await run_runbook_with_adk(
        features=features,
        triage=triage_result,
        session_id=session_id,
    )
    print(f"   Generated {len(runbook.runbook)} steps")

    # All results stored in session memory
    print("\n4️⃣  Session Memory Contents:")
    triage_mem = await retrieve_memory_entry(session_id, "triage_result")
    explain_mem = await retrieve_memory_entry(session_id, "explanation")
    runbook_mem = await retrieve_memory_entry(session_id, "runbook")

    print(f"   ✅ Triage: {bool(triage_mem)}")
    print(f"   ✅ Explain: {bool(explain_mem)}")
    print(f"   ✅ Runbook: {bool(runbook_mem)}")

asyncio.run(full_incident_response())
```

### Example 3: Direct Agent Access (Advanced)

```python
from app.orchestration import create_triage_agent
from google.adk import Agent

# Get the real ADK agent
agent = create_triage_agent()

# It's a real google.adk.Agent
assert isinstance(agent, Agent)

# Access ADK properties
print(f"Name: {agent.name}")           # "TriageAgent"
print(f"Model: {agent.model}")         # "gemini-3-pro-preview"
print(f"Tools: {len(agent.tools)}")    # 1
print(f"Description: {agent.description}")

# Tools are real google.adk.FunctionTool instances
for tool in agent.tools:
    print(f"Tool: {tool.__class__.__name__}")  # FunctionTool
```

### Example 4: Session Memory Operations

```python
import asyncio
from app.orchestration import (
    initialize_adk_services,
    store_memory_entry,
    retrieve_memory_entry,
    clear_session_memory,
)

async def memory_operations():
    initialize_adk_services()

    session_id = "session-001"

    # Store data
    await store_memory_entry(
        session_id=session_id,
        key="incident_context",
        value={
            "id": "INC-123",
            "severity": "CRITICAL",
            "timestamp": "2025-12-06T09:30:00Z",
        }
    )

    # Retrieve data
    context = await retrieve_memory_entry(session_id, "incident_context")
    print(f"Retrieved: {context}")

    # Clear session
    await clear_session_memory(session_id)

    # Verify cleared
    context = await retrieve_memory_entry(session_id, "incident_context")
    print(f"After clear: {context}")  # None

asyncio.run(memory_operations())
```

## Kaggle Competition Checklist

Using this real Google ADK integration, you satisfy these competition requirements:

### ✅ Multi-Agent System

- **Triage Agent**: Scores incident severity
- **Explain Agent**: Generates explanations
- **Runbook Agent**: Creates response steps
- **Policy Agent**: Validates safety

```python
# Sequential execution via orchestration
await run_triage_with_adk(...)     # Step 1
await run_explain_with_adk(...)    # Step 2 (parallel possible)
await run_runbook_with_adk(...)    # Step 3 (parallel possible)
```

### ✅ Tools / Function Calling

- Each agent uses real `google.adk.tools.FunctionTool`
- Tools are defined with `FunctionTool(callable_function)`

```python
from google.adk.tools import FunctionTool

tool = FunctionTool(score_incident)  # Real ADK tool
```

### ✅ MCP Protocol

- Real google.adk handles MCP envelope protocol internally
- Your agents are MCP-compatible by default

### ✅ Sessions & Memory

- `InMemorySessionService`: Manages session state
- `InMemoryMemoryService`: Stores long-term memory
- Session state preserved across agent calls

```python
await store_memory_entry(session_id, "key", value)
await retrieve_memory_entry(session_id, "key")
```

### ✅ Observability

- Structured JSON logging via `app/core/observability.py`
- Trace IDs for request correlation
- Agent callbacks for before/after hooks

### ✅ Long-Running Operations

- Async/await throughout
- Agents run asynchronously
- Parallel execution support via `asyncio.gather()`

### ✅ Agent Evaluation

- `app/services/agent_evaluation.py`: Metrics collection
- Evaluation framework with safety metrics

### ✅ Vertex AI Integration

- **Model**: `gemini-3-pro-preview` on Vertex AI
- **Embeddings**: `text-embedding-004` via Vertex AI
- **Location**: Global (required for Gemini models)

### ✅ Deployment

- Google Cloud Run (serverless)
- All agents containerized
- Auto-scaling via Cloud Run

## Integration with Existing Code

### Old Pattern (Still Works)

```python
from app.orchestration import register_adk_tool, adk_tool

@adk_tool("my_tool")
async def my_tool(inputs, context):
    return {"result": "done"}
```

### New Pattern (Real ADK - Recommended)

```python
from google.adk.tools import FunctionTool

def my_function(value: int) -> int:
    return value * 2

tool = FunctionTool(my_function)
# Use in: Agent(tools=[tool])
```

## Testing

### Unit Test Example

```python
import pytest
from app.orchestration import initialize_adk_services, run_triage_with_adk

@pytest.mark.asyncio
async def test_triage_agent():
    initialize_adk_services()

    features = {"failed_logins_last_hour": 10}
    result = await run_triage_with_adk(features, "test-session-001")

    assert result is not None
    assert result.label in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert 0.0 <= result.score <= 1.0
```

## Common Patterns

### Pattern 1: Session-Based Workflow

```python
async def handle_incident(incident_data):
    session_id = f"incident-{incident_data['id']}"
    initialize_adk_services()

    # All operations use same session
    triage = await run_triage_with_adk(incident_data['features'], session_id)
    explain = await run_explain_with_adk(..., session_id)
    runbook = await run_runbook_with_adk(..., session_id)

    # All results available in session memory
    return session_id
```

### Pattern 2: Parallel Agents

```python
async def parallel_processing(features, triage_result, session_id):
    # Run explain and runbook in parallel
    explain_task = run_explain_with_adk(features, triage_result, session_id)
    runbook_task = run_runbook_with_adk(features, triage_result, session_id)

    explain_result, runbook_result = await asyncio.gather(
        explain_task,
        runbook_task,
    )

    return explain_result, runbook_result
```

### Pattern 3: Agent Chain

```python
async def agent_chain():
    session_id = "chain-001"

    # Each agent's output feeds into next agent
    triage = await run_triage_with_adk(features, session_id)
    explain = await run_explain_with_adk(features, triage, session_id)
    runbook = await run_runbook_with_adk(features, triage, session_id)

    # Results in order
    return {
        "triage": triage,
        "explain": explain,
        "runbook": runbook,
    }
```

## Troubleshooting

### Issue: "instructions field not recognized"

**Solution:** Use `instruction` (singular), not `instructions`

```python
Agent(
    instruction="Your system prompt here",  # ✅ Correct
    # instructions="..."  # ❌ Wrong
)
```

### Issue: "Tool not callable"

**Solution:** Wrap function with `FunctionTool`

```python
from google.adk.tools import FunctionTool

def my_func(x):
    return x * 2

tool = FunctionTool(my_func)  # ✅ Correct
# agent_tool = my_func  # ❌ Wrong
```

### Issue: "Session not found"

**Solution:** Use same session_id consistently

```python
session_id = "incident-123"
# Use same session_id for all calls
await run_triage_with_adk(..., session_id)
await run_explain_with_adk(..., session_id)
```

## References

- **Google ADK GitHub**: https://github.com/google/ai-agent-kit
- **google-adk PyPI**: https://pypi.org/project/google-adk/
- **Our Implementation**: `app/orchestration/adk_agents.py`
- **Documentation**: `backend/ADK_INTEGRATION.md`
- **Kaggle Competition**: Agents-Intensive-Capstone-Project
