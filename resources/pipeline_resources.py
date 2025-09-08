"""MCP Resources for pipeline data."""

import json
from datetime import datetime

from services.jenkins_service import JenkinsService


def get_pipeline_status(jenkins_service: JenkinsService) -> str:
    """Get overall pipeline system status and health summary."""
    if not jenkins_service.is_initialized():
        return "Jenkins not configured. Please configure Jenkins connection first."

    try:
        # Get basic system info
        whoami = jenkins_service.get_whoami()
        jobs = jenkins_service.get_jobs()

        # Count pipeline types
        freestyle_count = len([j for j in jobs if j.get("_class") == "hudson.model.FreeStyleProject"])
        workflow_count = len([j for j in jobs if j.get("_class") == "org.jenkinsci.plugins.workflow.job.WorkflowJob"])

        # Count by status
        enabled_count = len([j for j in jobs if not j.get("disabled", False)])
        disabled_count = len(jobs) - enabled_count

        status = {
            "jenkins_user": whoami.get("id", "unknown"),
            "total_pipelines": len(jobs),
            "freestyle_pipelines": freestyle_count,
            "workflow_pipelines": workflow_count,
            "enabled_pipelines": enabled_count,
            "disabled_pipelines": disabled_count,
            "last_updated": datetime.now().isoformat()
        }

        return json.dumps(status, indent=2)
    except Exception as e:
        return f"Error getting status: {str(e)}"


def get_pipeline_summary(pipeline_name: str, jenkins_service: JenkinsService, core_tools) -> str:
    """Get a comprehensive summary of a specific pipeline."""
    try:
        pipeline = core_tools.get_pipeline_details(pipeline_name, None)
        builds = core_tools.get_pipeline_builds(pipeline_name, None, limit=10)

        summary = {
            "pipeline": {
                "name": pipeline.name,
                "display_name": pipeline.display_name,
                "url": pipeline.url,
                "description": pipeline.description,
                "is_enabled": pipeline.is_enabled,
                "health_score": pipeline.health_score
            },
            "recent_builds": [
                {
                    "number": build.number,
                    "status": build.status,
                    "duration": build.duration,
                    "timestamp": build.timestamp.isoformat() if build.timestamp else None
                }
                for build in builds
            ],
            "summary_generated": datetime.now().isoformat()
        }

        return json.dumps(summary, indent=2)
    except Exception as e:
        return f"Error getting summary for {pipeline_name}: {str(e)}"


def get_pipeline_dashboard(jenkins_service: JenkinsService) -> str:
    """Get a comprehensive dashboard view of all pipelines."""
    if not jenkins_service.is_initialized():
        return "Jenkins not configured. Please configure Jenkins connection first."

    try:
        jobs = jenkins_service.get_jobs()
        dashboard_data = {
            "total_pipelines": len(jobs),
            "enabled_pipelines": len([j for j in jobs if not j.get("disabled", False)]),
            "disabled_pipelines": len([j for j in jobs if j.get("disabled", False)]),
            "freestyle_pipelines": len([j for j in jobs if j.get("_class") == "hudson.model.FreeStyleProject"]),
            "workflow_pipelines": len([j for j in jobs if j.get("_class") == "org.jenkinsci.plugins.workflow.job.WorkflowJob"]),
            "pipelines": [
                {
                    "name": job["name"],
                    "display_name": job.get("displayName", job["name"]),
                    "url": job["url"],
                    "enabled": not job.get("disabled", False),
                    "last_build_status": job.get("lastBuild", {}).get("result"),
                    "health_score": job.get("healthReport", [{}])[0].get("score") if job.get("healthReport") else None
                }
                for job in jobs
            ],
            "dashboard_generated": datetime.now().isoformat()
        }

        return json.dumps(dashboard_data, indent=2)
    except Exception as e:
        return f"Error generating dashboard: {str(e)}"


def get_pipeline_logs(pipeline_name: str, build_number: int, jenkins_service: JenkinsService) -> str:
    """Get build logs for a specific pipeline build."""
    if not jenkins_service.is_initialized():
        return "Jenkins not configured. Please configure Jenkins connection first."

    try:
        console_output = jenkins_service.get_build_console_output(pipeline_name, build_number)
        return console_output
    except Exception as e:
        return f"Error getting logs for {pipeline_name} build #{build_number}: {str(e)}"


def get_overall_health(jenkins_service: JenkinsService) -> str:
    """Get overall system health and alerts."""
    if not jenkins_service.is_initialized():
        return "Jenkins not configured. Please configure Jenkins connection first."

    try:
        jobs = jenkins_service.get_jobs()

        # Calculate health metrics
        total_jobs = len(jobs)
        enabled_jobs = len([j for j in jobs if not j.get("disabled", False)])
        failed_jobs = len([j for j in jobs if j.get("lastBuild", {}).get("result") == "FAILURE"])

        health_data = {
            "overall_health": "GOOD" if failed_jobs < total_jobs * 0.1 else "WARNING" if failed_jobs < total_jobs * 0.3 else "CRITICAL",
            "total_pipelines": total_jobs,
            "enabled_pipelines": enabled_jobs,
            "failed_pipelines": failed_jobs,
            "health_percentage": round((enabled_jobs - failed_jobs) / enabled_jobs * 100, 2) if enabled_jobs > 0 else 0,
            "alerts": [],
            "health_check_date": datetime.now().isoformat()
        }

        # Add alerts
        if failed_jobs > 0:
            health_data["alerts"].append(f"{failed_jobs} pipelines have failed builds")

        if enabled_jobs < total_jobs:
            health_data["alerts"].append(f"{total_jobs - enabled_jobs} pipelines are disabled")

        return json.dumps(health_data, indent=2)
    except Exception as e:
        return f"Error getting health status: {str(e)}"
