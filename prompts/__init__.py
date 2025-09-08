"""Prompts package for MCP Pipeline Awareness."""

from .pipeline_prompts import (
    analyze_pipeline_prompt,
    failure_analysis_prompt,
    optimization_prompt,
    security_audit_prompt,
)

__all__ = [
    "analyze_pipeline_prompt",
    "failure_analysis_prompt",
    "optimization_prompt",
    "security_audit_prompt"
]
