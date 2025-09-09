"""Helper functions for pipeline analysis."""

from datetime import datetime
from typing import Any


def parse_timestamp(timestamp: int | None) -> datetime | None:
    """Parse Jenkins timestamp (milliseconds) to datetime."""
    if not timestamp:
        return None
    
    # Handle different timestamp formats
    try:
        # If timestamp is already in seconds (unlikely but possible)
        if timestamp < 1000000000:  # Less than year 2001 in seconds
            return datetime.fromtimestamp(timestamp)
        else:
            # Assume milliseconds and convert to seconds
            return datetime.fromtimestamp(timestamp / 1000)
    except (ValueError, TypeError, OSError) as e:
        # Log the error for debugging but don't raise
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to parse timestamp {timestamp}: {e}")
        return None


def determine_trend(builds: list[dict[str, Any]]) -> str:
    """Determine if pipeline performance is improving, stable, or declining."""
    if len(builds) < 10:
        return "insufficient_data"

    mid_point = len(builds) // 2
    first_half = builds[:mid_point]
    second_half = builds[mid_point:]

    first_success_rate = len([b for b in first_half if b.get("result") == "SUCCESS"]) / len(first_half)
    second_success_rate = len([b for b in second_half if b.get("result") == "SUCCESS"]) / len(second_half)

    if second_success_rate > first_success_rate + 0.1:
        return "improving"
    elif second_success_rate < first_success_rate - 0.1:
        return "declining"
    else:
        return "stable"


def analyze_issues(success_rate: float, failure_rate: float, builds: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    """Analyze issues and generate recommendations."""
    issues = []
    recommendations = []

    if success_rate < 80:
        issues.append(f"Low success rate: {success_rate:.1f}%")
        recommendations.append("Investigate and fix common failure causes")

    if failure_rate > 20:
        issues.append(f"High failure rate: {failure_rate:.1f}%")
        recommendations.append("Implement better error handling and retry mechanisms")

    consecutive_failures = 0
    for build in builds[:5]:
        if build.get("result") == "FAILURE":
            consecutive_failures += 1
        else:
            break

    if consecutive_failures >= 3:
        issues.append(f"{consecutive_failures} consecutive failures")
        recommendations.append("Immediate investigation required - check recent changes")

    return issues, recommendations


def extract_error_message(console_output: str) -> str:
    """Extract error message from console output."""
    if not console_output:
        return "No console output available"

    lines = console_output.split('\n')
    error_lines = []

    for line in lines:
        if any(keyword in line.lower() for keyword in ['error', 'failed', 'exception', 'fatal']):
            error_lines.append(line.strip())

    return '\n'.join(error_lines[-10:]) if error_lines else "No clear error message found"


def determine_priority(error_message: str, status: str) -> str:
    """Determine priority based on error message and status."""
    if status == "FAILURE":
        if any(keyword in error_message.lower() for keyword in ['fatal', 'critical', 'security']):
            return "critical"
        elif any(keyword in error_message.lower() for keyword in ['timeout', 'memory', 'disk']):
            return "high"
        else:
            return "medium"
    return "low"


def generate_suggested_fixes(error_message: str, status: str) -> list[str]:
    """Generate suggested fixes based on error message."""
    suggestions = []

    if "timeout" in error_message.lower():
        suggestions.append("Increase timeout settings or optimize slow operations")

    if "memory" in error_message.lower():
        suggestions.append("Increase memory allocation or optimize memory usage")

    if "permission" in error_message.lower():
        suggestions.append("Check file permissions and user access rights")

    if "network" in error_message.lower():
        suggestions.append("Check network connectivity and firewall settings")

    if "dependency" in error_message.lower():
        suggestions.append("Verify all dependencies are installed and up to date")

    if not suggestions:
        suggestions.append("Review build logs for specific error details")
        suggestions.append("Check recent changes that might have caused the failure")

    return suggestions


def analyze_root_cause(error_message: str, status: str) -> str | None:
    """Analyze root cause of failure."""
    if "timeout" in error_message.lower():
        return "Build timeout - likely due to slow operations or resource constraints"

    if "memory" in error_message.lower():
        return "Memory issue - insufficient memory or memory leak"

    if "permission" in error_message.lower():
        return "Permission denied - access rights issue"

    if "network" in error_message.lower():
        return "Network connectivity issue"

    if "dependency" in error_message.lower():
        return "Missing or incompatible dependency"

    return "Unknown root cause - requires further investigation"


def answer_question(question: str, pipelines: list[Any]) -> tuple[str, float, list[str]]:
    """Generate AI-powered answer to question."""
    # Simple AI simulation - in real implementation, this would use actual AI
    question_lower = question.lower()

    if "health" in question_lower or "status" in question_lower:
        answer = f"Based on analysis of {len(pipelines)} pipelines, here's the health overview..."
        confidence = 0.8
        sources = ["pipeline_health_analysis"]

    elif "failure" in question_lower or "error" in question_lower:
        answer = f"Analysis of recent failures across {len(pipelines)} pipelines shows..."
        confidence = 0.7
        sources = ["failure_analysis", "build_logs"]

    elif "optimize" in question_lower or "improve" in question_lower:
        answer = f"Optimization recommendations for {len(pipelines)} pipelines include..."
        confidence = 0.75
        sources = ["performance_analysis", "best_practices"]

    else:
        answer = f"Based on analysis of {len(pipelines)} pipelines, here's what I found..."
        confidence = 0.6
        sources = ["general_analysis"]

    return answer, confidence, sources
