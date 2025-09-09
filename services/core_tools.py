"""Core pipeline management tools."""

import hashlib
import re
from datetime import datetime
from typing import Any

from fastmcp import Context

from models import BuildInfo, FailureAnalysis, PipelineHealth, PipelineInfo, QueryResult
from services.jenkins_service import JenkinsService
from utils import (
    analyze_issues,
    analyze_root_cause,
    answer_question,
    determine_priority,
    determine_trend,
    extract_error_message,
    generate_suggested_fixes,
    parse_timestamp,
)


class CoreTools:
    """Core pipeline management tools."""

    def __init__(self, jenkins_service: JenkinsService):
        self.jenkins = jenkins_service

    def _detect_sensitive_data(self, text: str) -> str:
        """Detect and hash sensitive data for AI communication while keeping real data locally."""
        if not text:
            return text

        # Patterns for sensitive data
        patterns = {
            'password': r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']?([^"\'\s]{3,})["\']?',
            'token': r'(?i)(token|bearer|api[_-]?key)\s*[:=]\s*["\']?([a-zA-Z0-9._-]{10,})["\']?',
            'secret': r'(?i)(secret|key)\s*[:=]\s*["\']?([a-zA-Z0-9._-]{10,})["\']?',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'ip': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            'url': r'https?://[^\s<>"{}|\\^`\[\]]+',
            'pipeline_name': r'\b(?:pipeline|job|build)[_-]?name\s*[:=]\s*["\']?([a-zA-Z0-9._-]{3,})["\']?',
            'cluster_name': r'\b(?:cluster|eks|gke|aks)[_-]?name\s*[:=]\s*["\']?([a-zA-Z0-9._-]{3,})["\']?',
            'environment': r'\b(?:env|environment)\s*[:=]\s*["\']?(prod|production|staging|stage|dev|development|test|qa|uat)["\']?',
            'project_name': r'\b(?:project|repo|repository)[_-]?name\s*[:=]\s*["\']?([a-zA-Z0-9._-]{3,})["\']?',
            'namespace': r'\b(?:namespace|ns)\s*[:=]\s*["\']?([a-zA-Z0-9._-]{3,})["\']?',
            'service_name': r'\b(?:service|svc)[_-]?name\s*[:=]\s*["\']?([a-zA-Z0-9._-]{3,})["\']?',
            'user_name': r'\b(?:user|username)[_-]?name\s*[:=]\s*["\']?([a-zA-Z0-9._-]{3,})["\']?',
            'team_name': r'\b(?:team|group)[_-]?name\s*[:=]\s*["\']?([a-zA-Z0-9._-]{3,})["\']?',
            'company_name': r'\b(?:company|org|organization)[_-]?name\s*[:=]\s*["\']?([a-zA-Z0-9._-]{3,})["\']?',
        }

        protected_text = text
        for pattern_name, pattern in patterns.items():
            matches = re.finditer(pattern, protected_text)
            for match in matches:
                if match.group(2) if len(match.groups()) > 1 else match.group(0):
                    sensitive_value = match.group(2) if len(match.groups()) > 1 else match.group(0)
                    # Create a hash for AI communication
                    hash_value = hashlib.sha256(sensitive_value.encode()).hexdigest()[:8]
                    protected_text = protected_text.replace(sensitive_value, f"[{pattern_name.upper()}_HASH_{hash_value}]")

        # Also protect identifying names
        protected_text = self._protect_identifying_names(protected_text)

        return protected_text

    def _protect_identifying_names(self, text: str) -> str:
        """Protect identifying names like pipeline names, cluster names, etc."""
        if not text:
            return text

        # Common naming patterns that might contain sensitive information
        name_patterns = {
            'pipeline_name': r'\b(?:eks|gke|aks|k8s|kube)[-_]?[a-zA-Z0-9]{2,}\b',  # eks-prod, gke-staging, etc.
            'cluster_name': r'\b(?:cluster|eks|gke|aks)[-_]?[a-zA-Z0-9]{2,}\b',  # cluster-prod, eks-dev, etc.
            'environment_name': r'\b(?:prod|production|staging|stage|dev|development|test|qa|uat)[-_]?[a-zA-Z0-9]{0,}\b',
            'project_name': r'\b(?:project|repo|app)[-_]?[a-zA-Z0-9]{2,}\b',  # project-abc, repo-xyz, etc.
            'service_name': r'\b(?:svc|service)[-_]?[a-zA-Z0-9]{2,}\b',  # svc-api, service-web, etc.
            'team_name': r'\b(?:team|group)[-_]?[a-zA-Z0-9]{2,}\b',  # team-devops, group-backend, etc.
            'company_name': r'\b(?:company|org|corp)[-_]?[a-zA-Z0-9]{2,}\b',  # company-abc, org-xyz, etc.
            'folder_name': r'\b(?:folder|dir|directory)[-_]?[a-zA-Z0-9]{2,}\b',  # folder-abc, dir-xyz, etc.
            'app_name': r'\b(?:app|application)[-_]?[a-zA-Z0-9]{2,}\b',  # app-web, application-api, etc.
            'branch_name': r'\b(?:branch|br)[-_]?[a-zA-Z0-9]{2,}\b',  # branch-feature, br-main, etc.
            'org_name': r'\b(?:org|organization)[-_]?[a-zA-Z0-9]{2,}\b',  # org-company, organization-abc, etc.
            'repo_name': r'\b(?:repo|repository)[-_]?[a-zA-Z0-9]{2,}\b',  # repo-backend, repository-frontend, etc.
            'file_name': r'\b(?:file|src|lib)[-_]?[a-zA-Z0-9]{2,}\.(?:py|js|ts|java|go|rs|cpp|c|h|hpp|cs|php|rb|swift|kt|scala|sh|bash|ps1|yaml|yml|json|xml|html|css|sql|md|txt)\b',  # file-utils.py, src-main.js, etc.
        }

        protected_text = text
        for pattern_name, pattern in name_patterns.items():
            matches = re.finditer(pattern, protected_text)
            for match in matches:
                name_value = match.group(0)
                # Create a hash for AI communication
                hash_value = hashlib.sha256(name_value.encode()).hexdigest()[:8]
                protected_text = protected_text.replace(name_value, f"[{pattern_name.upper()}_HASH_{hash_value}]")

        return protected_text

    def _protect_sensitive_data_in_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """Recursively protect sensitive data in dictionaries and lists."""
        if isinstance(data, dict):
            protected = {}
            for key, value in data.items():
                if isinstance(value, str):
                    protected[key] = self._detect_sensitive_data(value)
                elif isinstance(value, dict | list):
                    protected[key] = self._protect_sensitive_data_in_dict(value)
                else:
                    protected[key] = value
            return protected
        elif isinstance(data, list):
            return [self._protect_sensitive_data_in_dict(item) for item in data]
        else:
            return data

    def _protect_pydantic_model(self, model) -> dict[str, Any]:
        """Convert Pydantic model to dict and protect sensitive data."""
        if hasattr(model, 'model_dump'):
            # Pydantic v2
            data = model.model_dump()
        elif hasattr(model, 'dict'):
            # Pydantic v1
            data = model.dict()
        else:
            # Fallback
            data = model.__dict__

        return self._protect_sensitive_data_in_dict(data)

    async def list_pipelines(self, ctx: Context, search: str = "", limit: int = 50) -> list[PipelineInfo]:
        """List all available Jenkins pipelines with basic information."""
        await ctx.info(f"Listing pipelines with search='{search}', limit={limit}")

        if not self.jenkins.is_initialized():
            await ctx.error("Jenkins not initialized. Please configure Jenkins connection first.")
            raise ValueError("Jenkins not initialized. Please configure Jenkins connection first.")

        try:
            await ctx.info("Fetching jobs from Jenkins...")
            jobs = self.jenkins.get_jobs()
            pipelines = []

            for i, job in enumerate(jobs):
                if job.get("_class") in ["hudson.model.FreeStyleProject", "org.jenkinsci.plugins.workflow.job.WorkflowJob"]:
                    name = job["name"]

                    if search and search.lower() not in name.lower() and search.lower() not in job.get("description", "").lower():
                        continue

                    pipeline = PipelineInfo(
                        name=name,
                        display_name=job.get("displayName", name),
                        url=job["url"],
                        description=job.get("description", ""),
                        is_enabled=not job.get("disabled", False),
                        last_build_number=job.get("lastBuild", {}).get("number"),
                        last_build_status=job.get("lastBuild", {}).get("result"),
                        last_build_time=parse_timestamp(job.get("lastBuild", {}).get("timestamp")),
                        health_score=job.get("healthReport", [{}])[0].get("score") if job.get("healthReport") else None,
                    )
                    pipelines.append(pipeline)

                    # Report progress every 10 pipelines
                    if (i + 1) % 10 == 0:
                        await ctx.report_progress(i + 1, len(jobs), f"Processed {i + 1} jobs")

            await ctx.info(f"Found {len(pipelines)} matching pipelines")
            return pipelines[:limit]

        except Exception as e:
            await ctx.error(f"Error listing pipelines: {str(e)}")
            raise

    async def get_pipeline_details(self, pipeline_name: str, ctx: Context) -> PipelineInfo:
        """Get detailed information about a specific pipeline."""
        await ctx.info(f"Getting details for pipeline: {pipeline_name}")

        if not self.jenkins.is_initialized():
            await ctx.error("Jenkins not initialized. Please configure Jenkins connection first.")
            raise ValueError("Jenkins not initialized. Please configure Jenkins connection first.")

        try:
            await ctx.info("Fetching pipeline details from Jenkins...")
            job_info = self.jenkins.get_job_info(pipeline_name)

            pipeline = PipelineInfo(
                name=job_info["name"],
                display_name=job_info.get("displayName", job_info["name"]),
                url=job_info["url"],
                description=job_info.get("description", ""),
                is_enabled=not job_info.get("disabled", False),
                last_build_number=job_info.get("lastBuild", {}).get("number"),
                last_build_status=job_info.get("lastBuild", {}).get("result"),
                last_build_time=parse_timestamp(job_info.get("lastBuild", {}).get("timestamp")),
                health_score=job_info.get("healthReport", [{}])[0].get("score") if job_info.get("healthReport") else None,
            )

            await ctx.info(f"Successfully retrieved details for pipeline: {pipeline_name}")
            return pipeline

        except Exception as e:
            await ctx.error(f"Error getting pipeline details for {pipeline_name}: {str(e)}")
            raise

    async def get_pipeline_builds(self, pipeline_name: str, ctx: Context, limit: int = 20, status: str | None = None) -> list[BuildInfo]:
        """Get recent builds for a pipeline."""
        await ctx.info(f"Getting builds for pipeline: {pipeline_name} (limit={limit}, status={status})")

        if not self.jenkins.is_initialized():
            await ctx.error("Jenkins not initialized. Please configure Jenkins connection first.")
            raise ValueError("Jenkins not initialized. Please configure Jenkins connection first.")

        try:
            await ctx.info("Fetching build data from Jenkins...")
            builds_data = self.jenkins.get_builds(pipeline_name, limit)
            builds = []
            skipped_builds = 0

            for i, build_data in enumerate(builds_data):
                try:
                    build_number = build_data.get("number")
                    if not build_number:
                        await ctx.warning(f"Skipping build with missing number: {build_data}")
                        skipped_builds += 1
                        continue

                    # Get detailed build information
                    await ctx.info(f"Fetching details for build #{build_number}...")
                    try:
                        detailed_build = self.jenkins.get_build_info(pipeline_name, build_number)
                    except Exception as detail_error:
                        await ctx.warning(f"Could not get details for build #{build_number}: {str(detail_error)}")
                        # Fall back to basic build data
                        detailed_build = build_data

                    # Extract build information with fallbacks
                    build_status = detailed_build.get("result") or build_data.get("result") or "UNKNOWN"
                    
                    # Handle different status representations
                    if build_status == "null" or build_status is None:
                        build_status = "UNKNOWN"
                    
                    # Check if build is still running
                    if detailed_build.get("building", False):
                        build_status = "RUNNING"

                    if status and build_status != status:
                        continue

                    # Parse timestamp and handle invalid timestamps gracefully
                    timestamp = parse_timestamp(detailed_build.get("timestamp") or build_data.get("timestamp"))
                    if timestamp is None and (detailed_build.get("timestamp") or build_data.get("timestamp")):
                        await ctx.warning(f"Build #{build_number} has invalid timestamp, but including with null timestamp...")

                    # Get duration (convert from milliseconds to seconds if needed)
                    duration = detailed_build.get("duration") or build_data.get("duration")
                    if duration and duration > 0:
                        # Duration is typically in milliseconds, convert to seconds for display
                        duration_seconds = duration / 1000 if duration > 1000 else duration
                    else:
                        duration_seconds = None

                    build = BuildInfo(
                        number=build_number,
                        status=build_status,
                        url=detailed_build.get("url") or build_data.get("url", ""),
                        duration=duration,
                        timestamp=timestamp,
                        description=detailed_build.get("description") or build_data.get("description", ""),
                    )
                    builds.append(build)

                    # Report progress every 3 builds (since we're doing more work per build)
                    if (i + 1) % 3 == 0:
                        await ctx.report_progress(i + 1, len(builds_data), f"Processed {i + 1} builds")

                except Exception as build_error:
                    await ctx.warning(f"Error processing build #{build_data.get('number', 'unknown')}: {str(build_error)}")
                    skipped_builds += 1
                    continue

            if skipped_builds > 0:
                await ctx.warning(f"Skipped {skipped_builds} builds due to errors or missing data")

            await ctx.info(f"Retrieved {len(builds)} builds for pipeline: {pipeline_name}")
            return builds

        except Exception as e:
            await ctx.error(f"Error getting builds for {pipeline_name}: {str(e)}")
            raise

    async def analyze_pipeline_health(self, pipeline_name: str, ctx: Context, period: str = "last_7d") -> PipelineHealth:
        """Analyze the health and performance of a pipeline."""
        await ctx.info(f"Analyzing health for pipeline: {pipeline_name} (period: {period})")

        if not self.jenkins.is_initialized():
            await ctx.error("Jenkins not initialized. Please configure Jenkins connection first.")
            raise ValueError("Jenkins not initialized. Please configure Jenkins connection first.")

        try:
            # Calculate days based on period
            days = {"last_24h": 1, "last_7d": 7, "last_30d": 30}.get(period, 7)
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)

            await ctx.info("Fetching build data...")
            builds_data = self.jenkins.get_builds(pipeline_name, 100)

            # Filter builds by date
            recent_builds = [b for b in builds_data if parse_timestamp(b.get("timestamp")) and parse_timestamp(b.get("timestamp")) >= cutoff_date]

            if not recent_builds:
                await ctx.warning(f"No builds found in the {period} period")
                return PipelineHealth(
                    pipeline_name=pipeline_name,
                    success_rate=0.0,
                    failure_rate=0.0,
                    average_duration=0.0,
                    total_builds=0,
                    successful_builds=0,
                    failed_builds=0,
                    trend="no_data"
                )

            # Calculate metrics
            total_builds = len(recent_builds)
            successful_builds = len([b for b in recent_builds if b.get("result") == "SUCCESS"])
            failed_builds = len([b for b in recent_builds if b.get("result") == "FAILURE"])

            success_rate = (successful_builds / total_builds) * 100
            failure_rate = (failed_builds / total_builds) * 100

            # Calculate average duration
            durations = [b.get("duration", 0) for b in recent_builds if b.get("duration")]
            avg_duration = (sum(durations) / len(durations)) / 1000 if durations else 0  # Convert to seconds

            # Determine trend
            trend = determine_trend(recent_builds)

            # Analyze issues and generate recommendations
            issues, recommendations = analyze_issues(success_rate, failure_rate, recent_builds)

            health = PipelineHealth(
                pipeline_name=pipeline_name,
                success_rate=success_rate,
                failure_rate=failure_rate,
                average_duration=avg_duration,
                total_builds=total_builds,
                successful_builds=successful_builds,
                failed_builds=failed_builds,
                trend=trend,
                issues=issues,
                recommendations=recommendations
            )

            await ctx.info(f"Health analysis complete. Success rate: {success_rate:.1f}%, Trend: {trend}")
            return health

        except Exception as e:
            await ctx.error(f"Error analyzing health for {pipeline_name}: {str(e)}")
            raise

    async def analyze_pipeline_failure(self, pipeline_name: str, build_number: int, ctx: Context) -> FailureAnalysis:
        """Analyze a specific pipeline failure with AI-powered root cause analysis."""
        await ctx.info(f"Analyzing failure for pipeline: {pipeline_name} build #{build_number}")

        if not self.jenkins.is_initialized():
            await ctx.error("Jenkins not initialized. Please configure Jenkins connection first.")
            raise ValueError("Jenkins not initialized. Please configure Jenkins connection first.")

        try:
            await ctx.info("Fetching build information...")
            build_info = self.jenkins.get_build_info(pipeline_name, build_number)

            await ctx.info("Fetching console output...")
            console_output = self.jenkins.get_build_console_output(pipeline_name, build_number)

            await ctx.info("Analyzing failure...")
            status = build_info.get("result", "UNKNOWN")
            timestamp = parse_timestamp(build_info.get("timestamp"))
            error_message = extract_error_message(console_output)
            priority = determine_priority(error_message, status)
            suggested_fixes = generate_suggested_fixes(error_message, status)

            analysis = FailureAnalysis(
                build_number=build_number,
                pipeline_name=pipeline_name,
                failure_time=timestamp or datetime.now(),
                status=status,
                error_message=error_message,
                root_cause=analyze_root_cause(error_message, status),
                suggested_fixes=suggested_fixes,
                priority=priority
            )

            await ctx.info(f"Failure analysis complete. Priority: {priority}")
            return analysis

        except Exception as e:
            await ctx.error(f"Error analyzing failure for {pipeline_name}#{build_number}: {str(e)}")
            raise

    async def ask_pipeline_question(self, question: str, ctx: Context, pipeline_names: list[str] = None) -> QueryResult:
        """Ask natural language questions about pipelines and get AI-powered answers."""
        await ctx.info(f"Processing question: {question[:100]}...")

        if not self.jenkins.is_initialized():
            await ctx.error("Jenkins not initialized. Please configure Jenkins connection first.")
            raise ValueError("Jenkins not initialized. Please configure Jenkins connection first.")

        try:
            if pipeline_names:
                await ctx.info(f"Analyzing specific pipelines: {pipeline_names}")
                pipelines = []
                for name in pipeline_names:
                    try:
                        pipeline = await self.get_pipeline_details(name, ctx)
                        pipelines.append(pipeline)
                    except Exception:
                        await ctx.warning(f"Could not get details for pipeline: {name}")
                        continue
            else:
                await ctx.info("Analyzing recent pipelines...")
                pipelines = await self.list_pipelines(ctx, limit=10)

            await ctx.info("Generating AI-powered answer...")
            answer, confidence, sources = answer_question(question, pipelines)

            result = QueryResult(
                query=question,
                answer=answer,
                confidence=confidence,
                sources=sources,
                data={"pipelines_analyzed": len(pipelines)}
            )

            await ctx.info(f"Question answered with confidence: {confidence:.2f}")
            return result

        except Exception as e:
            await ctx.error(f"Error answering question: {str(e)}")
            raise
