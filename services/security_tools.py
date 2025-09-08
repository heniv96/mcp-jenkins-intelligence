"""Security and compliance tools."""

from datetime import datetime
from typing import Any

from fastmcp import Context

from services.jenkins_service import JenkinsService


class SecurityTools:
    """Security and compliance tools."""

    def __init__(self, jenkins_service: JenkinsService):
        self.jenkins = jenkins_service

    async def scan_pipeline_security(self, pipeline_name: str, ctx: Context) -> dict[str, Any]:
        """Scan pipeline for security vulnerabilities and best practices."""
        await ctx.info(f"Scanning security for pipeline: {pipeline_name}")

        if not self.jenkins.is_initialized():
            await ctx.error("Jenkins not initialized. Please configure Jenkins connection first.")
            raise ValueError("Jenkins not initialized. Please configure Jenkins connection first.")

        try:
            await ctx.info("Analyzing pipeline configuration...")
            config = self.jenkins.get_job_config(pipeline_name)

            security_issues = []
            security_score = 100

            # Check for hardcoded credentials
            if "password" in config.lower() or "secret" in config.lower():
                security_issues.append({
                    "severity": "HIGH",
                    "issue": "Potential hardcoded credentials detected",
                    "description": "Pipeline configuration may contain hardcoded passwords or secrets"
                })
                security_score -= 30

            # Check for insecure practices
            if "http://" in config and "https://" not in config:
                security_issues.append({
                    "severity": "MEDIUM",
                    "issue": "Insecure HTTP connections detected",
                    "description": "Pipeline uses HTTP instead of HTTPS for connections"
                })
                security_score -= 20

            # Check for proper authentication
            if "auth" not in config.lower() and "credentials" not in config.lower():
                security_issues.append({
                    "severity": "LOW",
                    "issue": "No explicit authentication configuration",
                    "description": "Consider adding explicit authentication mechanisms"
                })
                security_score -= 10

            # Check for proper error handling
            if "catch" not in config.lower() and "error" not in config.lower():
                security_issues.append({
                    "severity": "LOW",
                    "issue": "Limited error handling",
                    "description": "Consider adding comprehensive error handling"
                })
                security_score -= 5

            security_scan = {
                "pipeline_name": pipeline_name,
                "security_score": max(security_score, 0),
                "total_issues": len(security_issues),
                "high_severity": len([i for i in security_issues if i["severity"] == "HIGH"]),
                "medium_severity": len([i for i in security_issues if i["severity"] == "MEDIUM"]),
                "low_severity": len([i for i in security_issues if i["severity"] == "LOW"]),
                "issues": security_issues,
                "scan_date": datetime.now().isoformat()
            }

            await ctx.info(f"Security scan complete: {security_score}/100 score, {len(security_issues)} issues found")
            return security_scan

        except Exception as e:
            await ctx.error(f"Error scanning security for {pipeline_name}: {str(e)}")
            raise
