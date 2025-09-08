"""Pydantic models for pipeline data structures."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PipelineInfo(BaseModel):
    """Basic pipeline information."""
    name: str
    display_name: str
    url: str
    description: str = ""
    is_enabled: bool = True
    last_build_number: int | None = None
    last_build_status: str | None = None
    last_build_time: datetime | None = None
    health_score: int | None = None


class BuildInfo(BaseModel):
    """Build information."""
    number: int
    status: str
    url: str
    duration: int | None = None  # in milliseconds
    timestamp: datetime
    description: str = ""


class PipelineHealth(BaseModel):
    """Pipeline health metrics."""
    pipeline_name: str
    success_rate: float = Field(ge=0.0, le=100.0)
    failure_rate: float = Field(ge=0.0, le=100.0)
    average_duration: float  # in seconds
    total_builds: int
    successful_builds: int
    failed_builds: int
    trend: str  # "improving", "stable", "declining"
    issues: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class FailureAnalysis(BaseModel):
    """Pipeline failure analysis."""
    build_number: int
    pipeline_name: str
    failure_time: datetime
    status: str
    error_message: str = ""
    root_cause: str | None = None
    suggested_fixes: list[str] = Field(default_factory=list)
    priority: str = "medium"  # low, medium, high, critical


class QueryResult(BaseModel):
    """Query result wrapper."""
    query: str
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    sources: list[str] = Field(default_factory=list)
    data: dict[str, Any] | None = None
