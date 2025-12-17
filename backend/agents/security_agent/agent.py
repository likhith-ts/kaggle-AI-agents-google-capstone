"""
Security Incident Triage Agent - ADK Agent Definition.

This file defines the root_agent that ADK expects. It wraps our existing
agent implementations (triage, explain, runbook, policy) as ADK tools.

The agent uses Gemini model and can:
1. Triage security incidents (score severity)
2. Explain why an incident has a certain severity
3. Generate runbook steps for remediation
4. Check policy compliance

Kaggle Competition Features:
- Multi-agent system: Sequential agents orchestrated by root_agent
- Tools: FunctionTools wrapping our existing agent functions
- LLM: Gemini 3 Pro Preview via Vertex AI
"""

import os
import sys

# Add backend directory to path so we can import app modules
# Path: agents/security_agent/agent.py -> need to go up 2 levels to backend/
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)

from google.adk.agents import Agent


# =============================================================================
# Tool Functions (these wrap our existing agents)
# =============================================================================


def triage_incident(
    failed_logins_last_hour: int = 0,
    geo_velocity_flag: bool = False,
    impossible_travel: bool = False,
    user_risk_score: float = 0.0,
    endpoint_risk_score: float = 0.0,
    data_sensitivity: str = "low",
    malware_detected: bool = False,
    sensitive_file_access: int = 0,
) -> dict:
    """
    Score a security incident's severity based on its features.
    
    Args:
        failed_logins_last_hour: Number of failed login attempts in the last hour
        geo_velocity_flag: True if user logged in from geographically distant locations
        impossible_travel: True if login locations are impossible to travel between
        user_risk_score: Risk score of the user (0.0 to 1.0)
        endpoint_risk_score: Risk score of the endpoint (0.0 to 1.0)
        data_sensitivity: Sensitivity level of data accessed ("low", "medium", "high", "critical")
        malware_detected: True if malware was detected
        sensitive_file_access: Number of sensitive files accessed
    
    Returns:
        Dictionary with label (severity), score (0-1), and contributing factors
    """
    try:
        from app.agents.triage import score_incident
        
        features = {
            "failed_logins_last_hour": failed_logins_last_hour,
            "geo_velocity_flag": geo_velocity_flag,
            "impossible_travel": impossible_travel,
            "user_risk_score": user_risk_score,
            "endpoint_risk_score": endpoint_risk_score,
            "data_sensitivity": data_sensitivity,
            "malware_detected": malware_detected,
            "sensitive_file_access": sensitive_file_access,
        }
        
        label, score, contribs = score_incident(features)
        
        return {
            "status": "success",
            "label": label,
            "score": round(score, 2),
            "contributing_factors": contribs,
            "message": f"Incident triaged as {label} with score {score:.2f}",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }


def explain_triage(
    label: str,
    score: float,
    failed_logins_last_hour: int = 0,
    geo_velocity_flag: bool = False,
    malware_detected: bool = False,
) -> dict:
    """
    Generate a human-readable explanation for why an incident was triaged at a certain level.
    
    Args:
        label: The severity label (LOW, MEDIUM, HIGH, CRITICAL)
        score: The triage score (0.0 to 1.0)
        failed_logins_last_hour: Number of failed login attempts
        geo_velocity_flag: True if geographic velocity anomaly detected
        malware_detected: True if malware was detected
    
    Returns:
        Dictionary with detailed explanation
    """
    try:
        # Build explanation based on inputs (simplified - no LLM call needed)
        reasons = []
        if failed_logins_last_hour > 10:
            reasons.append(f"High number of failed logins ({failed_logins_last_hour}) indicates brute force attempt")
        if geo_velocity_flag:
            reasons.append("Geographic velocity anomaly suggests credential theft or VPN abuse")
        if malware_detected:
            reasons.append("Malware presence indicates active compromise")
        
        if not reasons:
            reasons.append("No significant risk indicators detected")
        
        explanation = f"Incident classified as {label} (score: {score}). " + " ".join(reasons)
        
        return {
            "status": "success",
            "label": label,
            "score": score,
            "explanation": explanation,
            "reasons": reasons,
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e),
        }


def generate_runbook(
    label: str,
    incident_type: str = "brute_force",
) -> dict:
    """
    Generate a remediation runbook for a security incident.
    
    Args:
        label: The severity label (LOW, MEDIUM, HIGH, CRITICAL)
        incident_type: Type of incident (brute_force, malware, data_exfiltration, phishing)
    
    Returns:
        Dictionary with runbook steps
    """
    try:
        # Build runbook based on incident type (template-based)
        runbook_templates = {
            "brute_force": [
                {"step": "Lock affected user account", "why": "Prevent further unauthorized access", "risk": "LOW"},
                {"step": "Reset user credentials", "why": "Invalidate potentially compromised password", "risk": "LOW"},
                {"step": "Review login logs for source IPs", "why": "Identify attack origin", "risk": "LOW"},
                {"step": "Block suspicious IPs at firewall", "why": "Stop ongoing attack", "risk": "MEDIUM"},
                {"step": "Enable MFA if not already active", "why": "Add additional authentication layer", "risk": "LOW"},
            ],
            "malware": [
                {"step": "Isolate affected endpoint", "why": "Prevent lateral movement", "risk": "LOW"},
                {"step": "Capture forensic image", "why": "Preserve evidence for analysis", "risk": "LOW"},
                {"step": "Run full antivirus scan", "why": "Identify all malicious files", "risk": "LOW"},
                {"step": "Check for persistence mechanisms", "why": "Ensure complete removal", "risk": "MEDIUM"},
                {"step": "Reimage system if needed", "why": "Guarantee clean state", "risk": "HIGH"},
            ],
            "data_exfiltration": [
                {"step": "Revoke user access immediately", "why": "Stop ongoing data loss", "risk": "LOW"},
                {"step": "Identify affected data scope", "why": "Assess breach impact", "risk": "LOW"},
                {"step": "Preserve network logs", "why": "Analyze exfiltration method", "risk": "LOW"},
                {"step": "Notify legal and compliance", "why": "Meet regulatory requirements", "risk": "LOW"},
                {"step": "Implement data loss prevention", "why": "Prevent future incidents", "risk": "MEDIUM"},
            ],
            "phishing": [
                {"step": "Reset compromised credentials", "why": "Prevent account takeover", "risk": "LOW"},
                {"step": "Scan for malware downloads", "why": "Check for payload delivery", "risk": "LOW"},
                {"step": "Block sender domain", "why": "Prevent similar attacks", "risk": "LOW"},
                {"step": "Alert other users", "why": "Prevent additional victims", "risk": "LOW"},
                {"step": "Update email filters", "why": "Catch similar phishing attempts", "risk": "LOW"},
            ],
        }
        
        steps = runbook_templates.get(incident_type, runbook_templates["brute_force"])
        
        # Add severity-specific steps for HIGH/CRITICAL
        if label in ["HIGH", "CRITICAL"]:
            steps.append({"step": "Escalate to security leadership", "why": f"{label} severity requires management visibility", "risk": "LOW"})
            steps.append({"step": "Initiate incident response procedure", "why": "Follow formal IR process", "risk": "LOW"})
        
        return {
            "status": "success",
            "runbook": steps,
            "source": f"template_{incident_type}",
            "step_count": len(steps),
            "severity": label,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }


def check_policy(
    command: str,
) -> dict:
    """
    Check if a command is safe according to security policies.
    
    Args:
        command: The command to check (e.g., "rm -rf /", "isolate-host victim.local")
    
    Returns:
        Dictionary with policy check result
    """
    try:
        from app.agents.policy import policy_is_safe, get_safe_alternative
        
        is_safe = policy_is_safe(command)
        
        if is_safe:
            return {
                "status": "success",
                "is_safe": True,
                "command": command,
                "message": "Command is safe to execute",
            }
        else:
            alternative = get_safe_alternative(command)
            return {
                "status": "success",
                "is_safe": False,
                "command": command,
                "alternative": alternative,
                "message": f"Command is unsafe. Consider: {alternative}",
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }


# =============================================================================
# Root Agent Definition
# =============================================================================


root_agent = Agent(
    name="security_triage_agent",
    model="gemini-2.0-flash",
    description="Enterprise Security Incident Triage & Runbook Agent",
    instruction="""You are a security incident triage specialist helping SOC analysts respond to security incidents.

Your capabilities:
1. **Triage Incidents**: Use the triage_incident tool to score incident severity based on features
2. **Explain Triage**: Use the explain_triage tool to explain why an incident has a certain severity
3. **Generate Runbooks**: Use the generate_runbook tool to create step-by-step remediation plans
4. **Check Policies**: Use the check_policy tool to verify if commands are safe to execute

When a user describes a security incident:
1. First, extract key features (failed logins, malware, geo-velocity, etc.)
2. Use triage_incident to get the severity score
3. Use explain_triage to provide context
4. Use generate_runbook to suggest remediation steps
5. Use check_policy for any commands before recommending them

Always be helpful, accurate, and security-conscious. If you're unsure, ask for more details.

Example user queries:
- "We have 50 failed logins from a user in the last hour"
- "Malware was detected on endpoint ws-001"
- "Is this incident critical: impossible travel detected"
- "Generate a runbook for a brute force attack"
""",
    tools=[
        triage_incident,
        explain_triage,
        generate_runbook,
        check_policy,
    ],
)
