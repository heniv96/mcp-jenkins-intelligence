"""Advanced Analytics & Reporting Tools for Jenkins Pipeline Intelligence."""

import hashlib
import logging
import re
from datetime import datetime
from typing import Any

from fastmcp import Context

logger = logging.getLogger(__name__)


class AnalyticsTools:
    """Advanced analytics and reporting tools for Jenkins pipelines."""

    def __init__(self, jenkins_service):
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

    def _generate_chart_data(self, builds: list[dict], chart_type: str = "build_timeline") -> dict[str, Any]:
        """Generate chart data for visualization."""
        if not builds:
            return {"error": "No build data available"}

        if chart_type == "build_timeline":
            # Timeline chart data
            timeline_data = []
            for build in builds:
                if build.get('timestamp') and build.get('result'):
                    timeline_data.append({
                        "x": datetime.fromtimestamp(build['timestamp'] / 1000).isoformat(),
                        "y": build['duration'] / 1000 if build.get('duration') else 0,
                        "status": build['result'],
                        "build_number": build['number']
                    })

            return {
                "type": "line",
                "title": "Build Duration Timeline",
                "data": sorted(timeline_data, key=lambda x: x['x']),
                "x_label": "Time",
                "y_label": "Duration (seconds)"
            }

        elif chart_type == "success_rate":
            # Success rate over time
            success_data = []
            window_size = 5  # 5 builds per window
            for i in range(0, len(builds), window_size):
                window_builds = builds[i:i + window_size]
                success_count = sum(1 for b in window_builds if b.get('result') == 'SUCCESS')
                success_rate = (success_count / len(window_builds)) * 100
                success_data.append({
                    "x": f"Builds {i+1}-{min(i+window_size, len(builds))}",
                    "y": success_rate
                })

            return {
                "type": "bar",
                "title": "Success Rate by Build Window",
                "data": success_data,
                "x_label": "Build Range",
                "y_label": "Success Rate (%)"
            }

        return {"error": "Unknown chart type"}

    async def generate_pipeline_report(
        self,
        pipeline_name: str,
        ctx: Context,
        period: str = "last_30d",
        format: str = "html"
    ) -> dict[str, Any]:
        """Generate comprehensive pipeline report based on Jenkins build history (no external metrics plugins)."""
        await ctx.info(f"Generating {format.upper()} report for {pipeline_name} ({period}) - Based on Jenkins build history")

        try:
            # Determine number of builds to analyze based on period
            build_limit = 50 if period == "last_30d" else 20 if period == "last_7d" else 10

            # Get pipeline builds from Jenkins
            await ctx.info(f"Fetching last {build_limit} builds from Jenkins...")
            builds = self.jenkins.get_builds(pipeline_name, build_limit)

            if not builds:
                return {
                    "pipeline_name": pipeline_name,
                    "error": "No build data available",
                    "message": "Pipeline has no builds or Jenkins connection failed"
                }

            # Get detailed build information for each build
            detailed_builds = []
            for build in builds:
                try:
                    build_info = self.jenkins.get_build_info(pipeline_name, build['number'])
                    detailed_builds.append(build_info)
                except Exception as e:
                    await ctx.warning(f"Could not get details for build {build['number']}: {str(e)}")
                    detailed_builds.append(build)

            # Calculate real metrics from build history
            total_builds = len(detailed_builds)
            successful_builds = sum(1 for build in detailed_builds if build.get('result') == 'SUCCESS')
            failed_builds = sum(1 for build in detailed_builds if build.get('result') == 'FAILURE')
            aborted_builds = sum(1 for build in detailed_builds if build.get('result') == 'ABORTED')
            success_rate = (successful_builds / total_builds * 100) if total_builds > 0 else 0

            # Calculate build times from actual data
            build_times = []
            for build in detailed_builds:
                if build.get('duration') and build.get('duration') > 0:
                    build_times.append(build['duration'])

            avg_build_time = sum(build_times) / len(build_times) if build_times else 0
            min_build_time = min(build_times) if build_times else 0
            max_build_time = max(build_times) if build_times else 0

            # Analyze failure patterns from build logs
            failure_patterns = []
            for build in detailed_builds:
                if build.get('result') == 'FAILURE':
                    try:
                        # Get build console output
                        console_output = self.jenkins.get_build_console_output(pipeline_name, build['number'])
                        # Look for common failure patterns
                        if "ERROR" in console_output:
                            failure_patterns.append("Build errors detected")
                        if "timeout" in console_output.lower():
                            failure_patterns.append("Timeout issues")
                        if "permission" in console_output.lower():
                            failure_patterns.append("Permission issues")
                    except Exception:
                        failure_patterns.append("Unknown failure")

            # Generate chart data
            timeline_chart = self._generate_chart_data(detailed_builds, "build_timeline")
            success_chart = self._generate_chart_data(detailed_builds, "success_rate")

            # Create comprehensive report
            report_data = {
                "pipeline_name": pipeline_name,
                "period": period,
                "generated_at": datetime.now().isoformat(),
                "data_source": "Jenkins build history (no external metrics plugins)",
                "summary": {
                    "total_builds": total_builds,
                    "successful_builds": successful_builds,
                    "failed_builds": failed_builds,
                    "aborted_builds": aborted_builds,
                    "success_rate": round(success_rate, 2),
                    "average_build_time_seconds": round(avg_build_time / 1000, 2),
                    "min_build_time_seconds": round(min_build_time / 1000, 2),
                    "max_build_time_seconds": round(max_build_time / 1000, 2)
                },
                "analysis": {
                    "build_frequency": f"Analyzed {total_builds} builds",
                    "failure_patterns": list(set(failure_patterns)),
                    "performance_trend": "stable" if success_rate > 80 else "needs_attention",
                    "build_time_trend": "stable" if avg_build_time < 300000 else "slow"
                },
                "charts": {
                    "timeline": timeline_chart,
                    "success_rate": success_chart
                },
                "recommendations": self._generate_recommendations(detailed_builds, success_rate, avg_build_time)
            }

            await ctx.info(f"✅ Report generated successfully - {total_builds} builds analyzed")

            # Protect sensitive data before returning to AI
            protected_report = self._protect_sensitive_data_in_dict(report_data)
            return protected_report

        except Exception as e:
            await ctx.error(f"Error generating report: {str(e)}")
            raise

    def _generate_recommendations(self, builds: list[dict], success_rate: float, avg_build_time: float) -> list[str]:
        """Generate recommendations based on real build data analysis."""
        recommendations = []

        if success_rate < 80:
            recommendations.append("Low success rate detected - investigate failure patterns and improve pipeline reliability")

        if avg_build_time > 600000:  # 10 minutes
            recommendations.append("Build times are slow - consider parallel execution or dependency optimization")

        if avg_build_time > 300000:  # 5 minutes
            recommendations.append("Moderate build times - review build steps for optimization opportunities")

        # Check for frequent failures
        recent_failures = sum(1 for build in builds[-10:] if build.get('result') == 'FAILURE')
        if recent_failures > 3:
            recommendations.append("Recent build failures detected - review recent changes and error logs")

        # Check for build time variance
        build_times = [b.get('duration', 0) for b in builds if b.get('duration')]
        if build_times:
            variance = max(build_times) - min(build_times)
            if variance > 300000:  # 5 minutes variance
                recommendations.append("High build time variance - standardize build environment and dependencies")

        if not recommendations:
            recommendations.append("Pipeline performance looks good - continue monitoring")

        return recommendations

    async def compare_pipeline_performance(
        self,
        pipeline_names: list[str],
        ctx: Context,
        period: str = "last_7d"
    ) -> dict[str, Any]:
        """Compare performance across multiple pipelines based on Jenkins build history (no external metrics plugins)."""
        await ctx.info(f"Comparing performance for {len(pipeline_names)} pipelines ({period}) - Based on Jenkins build history")

        try:
            # Determine number of builds to analyze based on period
            build_limit = 20 if period == "last_7d" else 10 if period == "last_3d" else 5

            comparison_data = {
                "period": period,
                "data_source": "Jenkins build history (no external metrics plugins)",
                "pipelines": {},
                "rankings": {
                    "fastest": None,
                    "most_reliable": None,
                    "most_efficient": None
                },
                "statistical_analysis": {}
            }

            pipeline_metrics = []

            for pipeline_name in pipeline_names:
                await ctx.info(f"Analyzing {pipeline_name}...")
                builds = self.jenkins.get_builds(pipeline_name, build_limit)

                if not builds:
                    await ctx.warning(f"No builds found for {pipeline_name}")
                    continue

                # Get detailed build information
                detailed_builds = []
                for build in builds:
                    try:
                        build_info = self.jenkins.get_build_info(pipeline_name, build['number'])
                        detailed_builds.append(build_info)
                    except Exception as e:
                        await ctx.warning(f"Could not get details for {pipeline_name} build {build['number']}: {str(e)}")
                        detailed_builds.append(build)

                # Calculate real metrics from build history
                total_builds = len(detailed_builds)
                successful_builds = sum(1 for build in detailed_builds if build.get('result') == 'SUCCESS')
                failed_builds = sum(1 for build in detailed_builds if build.get('result') == 'FAILURE')
                success_rate = (successful_builds / total_builds * 100) if total_builds > 0 else 0

                # Calculate build times from actual data
                build_times = [build.get('duration', 0) for build in detailed_builds if build.get('duration') and build.get('duration') > 0]
                avg_build_time = sum(build_times) / len(build_times) if build_times else 0
                min_build_time = min(build_times) if build_times else 0
                max_build_time = max(build_times) if build_times else 0

                # Calculate efficiency score (success rate weighted by build speed)
                efficiency_score = success_rate * (1 / (avg_build_time / 1000 + 1)) if avg_build_time > 0 else 0

                # Calculate build frequency (builds per day)
                if detailed_builds:
                    first_build_time = min(build.get('timestamp', 0) for build in detailed_builds if build.get('timestamp'))
                    last_build_time = max(build.get('timestamp', 0) for build in detailed_builds if build.get('timestamp'))
                    time_span_days = (last_build_time - first_build_time) / (1000 * 60 * 60 * 24) if last_build_time > first_build_time else 1
                    builds_per_day = total_builds / time_span_days if time_span_days > 0 else total_builds
                else:
                    builds_per_day = 0

                pipeline_metric = {
                    "pipeline_name": pipeline_name,
                    "total_builds": total_builds,
                    "successful_builds": successful_builds,
                    "failed_builds": failed_builds,
                    "success_rate": round(success_rate, 2),
                    "average_build_time_seconds": round(avg_build_time / 1000, 2),
                    "min_build_time_seconds": round(min_build_time / 1000, 2),
                    "max_build_time_seconds": round(max_build_time / 1000, 2),
                    "efficiency_score": round(efficiency_score, 2),
                    "builds_per_day": round(builds_per_day, 2),
                    "build_time_variance": round((max_build_time - min_build_time) / 1000, 2) if build_times else 0
                }

                comparison_data["pipelines"][pipeline_name] = pipeline_metric
                pipeline_metrics.append(pipeline_metric)

            # Find rankings
            if pipeline_metrics:
                fastest = min(pipeline_metrics, key=lambda x: x["average_build_time_seconds"])
                most_reliable = max(pipeline_metrics, key=lambda x: x["success_rate"])
                most_efficient = max(pipeline_metrics, key=lambda x: x["efficiency_score"])

                comparison_data["rankings"] = {
                    "fastest": fastest["pipeline_name"],
                    "most_reliable": most_reliable["pipeline_name"],
                    "most_efficient": most_efficient["pipeline_name"]
                }

                # Statistical analysis
                success_rates = [p["success_rate"] for p in pipeline_metrics]
                build_times = [p["average_build_time_seconds"] for p in pipeline_metrics]
                efficiency_scores = [p["efficiency_score"] for p in pipeline_metrics]

                comparison_data["statistical_analysis"] = {
                    "success_rate": {
                        "average": round(sum(success_rates) / len(success_rates), 2),
                        "min": round(min(success_rates), 2),
                        "max": round(max(success_rates), 2),
                        "variance": round(sum((x - sum(success_rates)/len(success_rates))**2 for x in success_rates) / len(success_rates), 2)
                    },
                    "build_time": {
                        "average": round(sum(build_times) / len(build_times), 2),
                        "min": round(min(build_times), 2),
                        "max": round(max(build_times), 2),
                        "variance": round(sum((x - sum(build_times)/len(build_times))**2 for x in build_times) / len(build_times), 2)
                    },
                    "efficiency": {
                        "average": round(sum(efficiency_scores) / len(efficiency_scores), 2),
                        "min": round(min(efficiency_scores), 2),
                        "max": round(max(efficiency_scores), 2)
                    }
                }

            await ctx.info(f"✅ Performance comparison completed - {len(pipeline_metrics)} pipelines analyzed")

            # Protect sensitive data before returning to AI
            protected_comparison = self._protect_sensitive_data_in_dict(comparison_data)
            return protected_comparison

        except Exception as e:
            await ctx.error(f"Error comparing pipelines: {str(e)}")
            raise
