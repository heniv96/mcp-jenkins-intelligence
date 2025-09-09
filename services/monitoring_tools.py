"""Monitoring and analytics tools."""

from datetime import datetime, timedelta
from typing import Any

from fastmcp import Context

from services.jenkins_service import JenkinsService
from utils import parse_timestamp


class MonitoringTools:
    """Monitoring and analytics tools."""

    def __init__(self, jenkins_service: JenkinsService):
        self.jenkins = jenkins_service

    async def get_pipeline_metrics(self, pipeline_name: str, ctx: Context, period: str = "last_7d") -> dict[str, Any]:
        """Get detailed metrics for a pipeline."""
        await ctx.info(f"Getting metrics for pipeline: {pipeline_name} (period: {period})")

        if not self.jenkins.is_initialized():
            await ctx.error("Jenkins not initialized. Please configure Jenkins connection first.")
            raise ValueError("Jenkins not initialized. Please configure Jenkins connection first.")

        try:
            # Calculate days based on period
            days = {"last_24h": 1, "last_7d": 7, "last_30d": 30}.get(period, 7)
            cutoff_date = datetime.now() - timedelta(days=days)

            await ctx.info("Fetching build data...")
            builds = self.jenkins.get_builds(pipeline_name, 100)  # Get more builds for better metrics

            # Filter builds by date
            recent_builds = []
            for b in builds:
                timestamp = parse_timestamp(b.get("timestamp"))
                if timestamp and timestamp >= cutoff_date:
                    recent_builds.append(b)

            if not recent_builds:
                return {"error": f"No builds found in the {period} period"}

            # Calculate metrics
            total_builds = len(recent_builds)
            successful_builds = len([b for b in recent_builds if b.get("result") == "SUCCESS"])
            failed_builds = len([b for b in recent_builds if b.get("result") == "FAILURE"])
            unstable_builds = len([b for b in recent_builds if b.get("result") == "UNSTABLE"])

            success_rate = (successful_builds / total_builds) * 100 if total_builds > 0 else 0
            failure_rate = (failed_builds / total_builds) * 100 if total_builds > 0 else 0

            # Calculate duration metrics
            durations = [b.get("duration", 0) for b in recent_builds if b.get("duration")]
            avg_duration = sum(durations) / len(durations) if durations else 0
            min_duration = min(durations) if durations else 0
            max_duration = max(durations) if durations else 0

            # Calculate build frequency
            if len(recent_builds) > 1:
                # Get builds with valid timestamps for time span calculation
                valid_timestamp_builds = [b for b in recent_builds if parse_timestamp(b.get("timestamp"))]
                if len(valid_timestamp_builds) > 1:
                    first_build = min(valid_timestamp_builds, key=lambda x: parse_timestamp(x.get("timestamp")))
                    last_build = max(valid_timestamp_builds, key=lambda x: parse_timestamp(x.get("timestamp")))
                    first_time = parse_timestamp(first_build.get("timestamp"))
                    last_time = parse_timestamp(last_build.get("timestamp"))
                    if first_time and last_time:
                        time_span = (last_time - first_time).total_seconds() / 3600  # hours
                        builds_per_day = (total_builds / time_span) * 24 if time_span > 0 else 0
                    else:
                        builds_per_day = 0
                else:
                    builds_per_day = 0
            else:
                builds_per_day = 0

            metrics = {
                "pipeline_name": pipeline_name,
                "period": period,
                "total_builds": total_builds,
                "successful_builds": successful_builds,
                "failed_builds": failed_builds,
                "unstable_builds": unstable_builds,
                "success_rate": round(success_rate, 2),
                "failure_rate": round(failure_rate, 2),
                "avg_duration_seconds": round(avg_duration / 1000, 2),
                "min_duration_seconds": round(min_duration / 1000, 2),
                "max_duration_seconds": round(max_duration / 1000, 2),
                "builds_per_day": round(builds_per_day, 2),
                "analysis_date": datetime.now().isoformat()
            }

            await ctx.info(f"Metrics calculated: {success_rate:.1f}% success rate, {builds_per_day:.1f} builds/day")
            return metrics

        except Exception as e:
            await ctx.error(f"Error getting metrics for {pipeline_name}: {str(e)}")
            raise

    async def get_pipeline_dependencies(self, pipeline_name: str, ctx: Context) -> list[dict[str, str]]:
        """Get upstream/downstream pipeline dependencies."""
        await ctx.info(f"Getting dependencies for pipeline: {pipeline_name}")

        if not self.jenkins.is_initialized():
            await ctx.error("Jenkins not initialized. Please configure Jenkins connection first.")
            raise ValueError("Jenkins not initialized. Please configure Jenkins connection first.")

        try:
            await ctx.info("Analyzing pipeline dependencies...")
            job_info = self.jenkins.get_job_info(pipeline_name)

            dependencies = []

            # Check for upstream projects
            upstream_projects = job_info.get("upstreamProjects", [])
            for upstream in upstream_projects:
                dependencies.append({
                    "name": upstream.get("name", ""),
                    "type": "upstream",
                    "url": upstream.get("url", ""),
                    "relationship": "triggers this pipeline"
                })

            # Check for downstream projects
            downstream_projects = job_info.get("downstreamProjects", [])
            for downstream in downstream_projects:
                dependencies.append({
                    "name": downstream.get("name", ""),
                    "type": "downstream",
                    "url": downstream.get("url", ""),
                    "relationship": "triggered by this pipeline"
                })

            await ctx.info(f"Found {len(dependencies)} dependencies")
            return dependencies

        except Exception as e:
            await ctx.error(f"Error getting dependencies for {pipeline_name}: {str(e)}")
            raise

    async def monitor_pipeline_queue(self, ctx: Context) -> list[dict[str, Any]]:
        """Monitor Jenkins build queue and pending builds."""
        await ctx.info("Monitoring Jenkins build queue...")

        if not self.jenkins.is_initialized():
            await ctx.error("Jenkins not initialized. Please configure Jenkins connection first.")
            raise ValueError("Jenkins not initialized. Please configure Jenkins connection first.")

        try:
            await ctx.info("Fetching queue information...")
            queue_info = self.jenkins.get_queue_info()

            queue_items = []
            for item in queue_info:
                queue_items.append({
                    "id": item.get("id"),
                    "task_name": item.get("task", {}).get("name", ""),
                    "task_url": item.get("task", {}).get("url", ""),
                    "why": item.get("why", ""),
                    "in_queue_since": parse_timestamp(item.get("inQueueSince")),
                    "blocked": item.get("blocked", False),
                    "stuck": item.get("stuck", False)
                })

            await ctx.info(f"Found {len(queue_items)} items in queue")
            return queue_items

        except Exception as e:
            await ctx.error(f"Error monitoring queue: {str(e)}")
            raise

    async def analyze_build_trends(self, pipeline_names: list[str], ctx: Context, period: str = "last_7d") -> dict[str, Any]:
        """Analyze build trends across multiple pipelines."""
        await ctx.info(f"Analyzing trends for {len(pipeline_names)} pipelines (period: {period})")

        if not self.jenkins.is_initialized():
            await ctx.error("Jenkins not initialized. Please configure Jenkins connection first.")
            raise ValueError("Jenkins not initialized. Please configure Jenkins connection first.")

        try:
            # Calculate days based on period
            days = {"last_24h": 1, "last_7d": 7, "last_30d": 30}.get(period, 7)
            cutoff_date = datetime.now() - timedelta(days=days)

            all_metrics = []
            total_builds = 0
            total_successful = 0
            total_failed = 0

            for pipeline_name in pipeline_names:
                await ctx.info(f"Analyzing {pipeline_name}...")
                builds = self.jenkins.get_builds(pipeline_name, 50)
                recent_builds = []
                for b in builds:
                    timestamp = parse_timestamp(b.get("timestamp"))
                    if timestamp and timestamp >= cutoff_date:
                        recent_builds.append(b)

                if recent_builds:
                    successful = len([b for b in recent_builds if b.get("result") == "SUCCESS"])
                    failed = len([b for b in recent_builds if b.get("result") == "FAILURE"])

                    all_metrics.append({
                        "pipeline_name": pipeline_name,
                        "builds": len(recent_builds),
                        "successful": successful,
                        "failed": failed,
                        "success_rate": (successful / len(recent_builds)) * 100 if recent_builds else 0
                    })

                    total_builds += len(recent_builds)
                    total_successful += successful
                    total_failed += failed

            overall_success_rate = (total_successful / total_builds) * 100 if total_builds > 0 else 0

            # Find best and worst performing pipelines
            best_pipeline = max(all_metrics, key=lambda x: x["success_rate"]) if all_metrics else None
            worst_pipeline = min(all_metrics, key=lambda x: x["success_rate"]) if all_metrics else None

            trends = {
                "period": period,
                "total_pipelines": len(pipeline_names),
                "total_builds": total_builds,
                "overall_success_rate": round(overall_success_rate, 2),
                "pipeline_metrics": all_metrics,
                "best_performer": best_pipeline,
                "worst_performer": worst_pipeline,
                "analysis_date": datetime.now().isoformat()
            }

            await ctx.info(f"Trend analysis complete: {overall_success_rate:.1f}% overall success rate")
            return trends

        except Exception as e:
            await ctx.error(f"Error analyzing trends: {str(e)}")
            raise
