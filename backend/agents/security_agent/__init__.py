"""
Security Incident Triage Agent for Google ADK.

This is the main ADK agent module that integrates with our existing
FastAPI backend agents. It exposes a root_agent for use with
`adk web` and `adk run` commands.

Structure following ADK conventions:
    security_agent/
        __init__.py     # This file - exports root_agent
        agent.py        # Agent definition
        .env            # API keys (symlinked to parent)

Run with:
    cd backend
    adk web --port 8080
    
    # Then select "security_agent" from dropdown
"""

from .agent import root_agent

__all__ = ["root_agent"]
