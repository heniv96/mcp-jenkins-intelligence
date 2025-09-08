"""Performance Optimization Tools for Jenkins Pipeline Intelligence."""

import hashlib
import logging
import re
from datetime import datetime
from typing import Any

import numpy as np
from fastmcp import Context

logger = logging.getLogger(__name__)


class PerformanceTools:
    """Performance optimization tools for Jenkins pipelines."""

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

    async def analyze_build_time_optimization(
        self,
        pipeline_name: str,
        ctx: Context,
        period: str = "last_30d"
    ) -> dict[str, Any]:
        """Analyze build time optimization opportunities using Jenkins data (no external metrics plugins)."""
        await ctx.info(f"Analyzing build time optimization for {pipeline_name} ({period}) - Using Jenkins data")

        try:
            # Determine number of builds to analyze based on period
            build_limit = 50 if period == "last_30d" else 20 if period == "last_7d" else 10

            # Get pipeline builds from Jenkins
            builds = self.jenkins.get_builds(pipeline_name, build_limit)

            if not builds:
                return {
                    "pipeline_name": pipeline_name,
                    "error": "No build data available",
                    "message": "Pipeline has no builds or Jenkins connection failed"
                }

            # Get detailed build information
            detailed_builds = []
            for build in builds:
                try:
                    build_info = self.jenkins.get_build_info(pipeline_name, build['number'])
                    detailed_builds.append(build_info)
                except Exception as e:
                    await ctx.warning(f"Could not get details for build {build['number']}: {str(e)}")
                    detailed_builds.append(build)

            # Analyze build times
            build_times = [build.get('duration', 0) for build in detailed_builds if build.get('duration') and build.get('duration') > 0]

            if not build_times:
                return {
                    "pipeline_name": pipeline_name,
                    "error": "No valid build time data",
                    "message": "No builds with valid duration found"
                }

            # Calculate time statistics
            build_times_seconds = [bt / 1000 for bt in build_times]
            avg_build_time = np.mean(build_times_seconds)
            median_build_time = np.median(build_times_seconds)
            std_build_time = np.std(build_times_seconds)
            min_build_time = np.min(build_times_seconds)
            max_build_time = np.max(build_times_seconds)

            # Analyze build time patterns
            time_patterns = self._analyze_time_patterns(detailed_builds, build_times_seconds)

            # Identify optimization opportunities
            optimizations = self._identify_optimization_opportunities(detailed_builds, build_times_seconds, time_patterns)

            # Calculate potential savings
            potential_savings = self._calculate_potential_savings(build_times_seconds, optimizations)

            # Generate AI-powered suggestions
            ai_suggestions = self._generate_ai_suggestions(detailed_builds, build_times_seconds, time_patterns)

            result = {
                "pipeline_name": pipeline_name,
                "period": period,
                "analyzed_builds": len(detailed_builds),
                "data_source": "Jenkins build history (no external metrics plugins)",
                "build_time_analysis": {
                    "average_seconds": round(avg_build_time, 2),
                    "median_seconds": round(median_build_time, 2),
                    "standard_deviation": round(std_build_time, 2),
                    "min_seconds": round(min_build_time, 2),
                    "max_seconds": round(max_build_time, 2),
                    "coefficient_of_variation": round(std_build_time / avg_build_time, 2) if avg_build_time > 0 else 0
                },
                "time_patterns": time_patterns,
                "optimization_opportunities": optimizations,
                "potential_savings": potential_savings,
                "ai_suggestions": ai_suggestions,
                "optimization_score": self._calculate_optimization_score(build_times_seconds, optimizations),
                "status": "completed"
            }

            await ctx.info(f"✅ Build time optimization analysis completed - {len(optimizations)} opportunities identified")

            # Protect sensitive data before returning to AI
            protected_result = self._protect_sensitive_data_in_dict(result)
            return protected_result

        except Exception as e:
            await ctx.error(f"Error analyzing build time optimization: {str(e)}")
            raise

    def _analyze_time_patterns(self, builds: list[dict], build_times: list[float]) -> dict[str, Any]:
        """Analyze build time patterns for optimization insights."""
        patterns = {
            "trends": {},
            "distribution": {},
            "outliers": {},
            "time_based": {}
        }

        if not build_times:
            return patterns

        # Time trends
        if len(build_times) > 5:
            # Calculate trend over time
            x = np.arange(len(build_times))
            z = np.polyfit(x, build_times, 1)
            patterns["trends"]["slope"] = z[0]
            patterns["trends"]["trend"] = "increasing" if z[0] > 0 else "decreasing" if z[0] < 0 else "stable"

        # Distribution analysis
        patterns["distribution"]["skewness"] = self._calculate_skewness(build_times)
        patterns["distribution"]["kurtosis"] = self._calculate_kurtosis(build_times)
        patterns["distribution"]["is_normal"] = abs(patterns["distribution"]["skewness"]) < 0.5

        # Outlier detection
        q1 = np.percentile(build_times, 25)
        q3 = np.percentile(build_times, 75)
        iqr = q3 - q1
        outlier_threshold = 1.5 * iqr
        outliers = [bt for bt in build_times if bt < q1 - outlier_threshold or bt > q3 + outlier_threshold]
        patterns["outliers"]["count"] = len(outliers)
        patterns["outliers"]["percentage"] = len(outliers) / len(build_times) * 100

        # Time-based patterns
        if builds:
            build_hours = [datetime.fromtimestamp(build.get('timestamp', 0) / 1000).hour
                          for build in builds if build.get('timestamp')]
            if build_hours:
                patterns["time_based"]["peak_hour"] = max(set(build_hours), key=build_hours.count)
                patterns["time_based"]["hour_variance"] = np.var(build_hours)

        return patterns

    def _calculate_skewness(self, data: list[float]) -> float:
        """Calculate skewness of data."""
        if len(data) < 3:
            return 0.0

        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0.0

        skewness = np.mean([(x - mean) ** 3 for x in data]) / (std ** 3)
        return skewness

    def _calculate_kurtosis(self, data: list[float]) -> float:
        """Calculate kurtosis of data."""
        if len(data) < 4:
            return 0.0

        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0.0

        kurtosis = np.mean([(x - mean) ** 4 for x in data]) / (std ** 4) - 3
        return kurtosis

    def _identify_optimization_opportunities(self, builds: list[dict], build_times: list[float], patterns: dict[str, Any]) -> list[dict[str, Any]]:
        """Identify specific optimization opportunities."""
        opportunities = []

        # High variance optimization
        cv = patterns["distribution"].get("coefficient_of_variation", 0)
        if cv > 0.3:
            opportunities.append({
                "type": "standardization",
                "title": "Standardize Build Environment",
                "description": "High build time variance indicates inconsistent environment",
                "impact": "high",
                "effort": "medium",
                "reasoning": f"Build time variance is {cv:.1%}",
                "potential_savings": "20-30%"
            })

        # Outlier optimization
        outlier_pct = patterns["outliers"].get("percentage", 0)
        if outlier_pct > 20:
            opportunities.append({
                "type": "outlier_analysis",
                "title": "Investigate Build Outliers",
                "description": "Many builds have unusual execution times",
                "impact": "medium",
                "effort": "low",
                "reasoning": f"{outlier_pct:.1f}% of builds are outliers",
                "potential_savings": "10-20%"
            })

        # Trend-based optimization
        if patterns["trends"].get("trend") == "increasing":
            opportunities.append({
                "type": "trend_optimization",
                "title": "Address Increasing Build Times",
                "description": "Build times are trending upward - investigate causes",
                "impact": "high",
                "effort": "high",
                "reasoning": "Build times are increasing over time",
                "potential_savings": "30-50%"
            })

        return opportunities

    def _calculate_potential_savings(self, build_times: list[float], optimizations: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate potential time savings from optimizations."""
        if not build_times or not optimizations:
            return {"total_savings": 0, "breakdown": []}

        current_avg = np.mean(build_times)
        total_savings = 0
        breakdown = []

        for opt in optimizations:
            savings_percentage = float(opt.get("potential_savings", "0%").replace("%", "")) / 100
            savings_seconds = current_avg * savings_percentage
            total_savings += savings_seconds

            breakdown.append({
                "type": opt["type"],
                "savings_seconds": round(savings_seconds, 2),
                "savings_percentage": round(savings_percentage * 100, 1)
            })

        return {
            "total_savings_seconds": round(total_savings, 2),
            "total_savings_percentage": round((total_savings / current_avg) * 100, 1),
            "breakdown": breakdown
        }

    def _generate_ai_suggestions(self, builds: list[dict], build_times: list[float], patterns: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate AI-powered optimization suggestions."""
        suggestions = []

        # Analyze build configuration for optimization hints
        config_analysis = self._analyze_build_configuration(builds)

        # Generate suggestions based on analysis
        if config_analysis.get("has_sequential_steps"):
            suggestions.append({
                "type": "parallelization",
                "title": "Implement Parallel Execution",
                "description": "Pipeline appears to have sequential steps that could run in parallel",
                "confidence": 0.8,
                "implementation": "Review pipeline steps and identify independent operations",
                "expected_improvement": "30-50% reduction in build time"
            })

        if config_analysis.get("has_dependency_downloads"):
            suggestions.append({
                "type": "caching",
                "title": "Implement Dependency Caching",
                "description": "Pipeline downloads dependencies that could be cached",
                "confidence": 0.9,
                "implementation": "Set up build cache for dependencies and artifacts",
                "expected_improvement": "20-40% reduction in build time"
            })

        return suggestions

    def _analyze_build_configuration(self, builds: list[dict]) -> dict[str, Any]:
        """Analyze build configuration for optimization hints."""
        analysis = {
            "has_sequential_steps": False,
            "has_dependency_downloads": False,
            "has_compilation": False,
            "has_testing": False
        }

        # This is a simplified analysis - in a real implementation,
        # you would parse the actual pipeline configuration
        for build in builds:
            # Check console output for common patterns
            try:
                console_output = self.jenkins.get_build_console_output(build.get('name', ''), build.get('number', 0))
                if console_output:
                    console_lower = console_output.lower()

                    if any(keyword in console_lower for keyword in ['npm install', 'pip install', 'maven dependency', 'gradle dependency']):
                        analysis["has_dependency_downloads"] = True

                    if any(keyword in console_lower for keyword in ['compiling', 'building', 'make', 'gcc', 'javac']):
                        analysis["has_compilation"] = True

                    if any(keyword in console_lower for keyword in ['testing', 'test', 'pytest', 'junit', 'mocha']):
                        analysis["has_testing"] = True

                    # Check for sequential execution patterns
                    if any(keyword in console_lower for keyword in ['step 1', 'step 2', 'stage 1', 'stage 2']):
                        analysis["has_sequential_steps"] = True
            except Exception:
                # If we can't get console output, skip this build
                continue

        return analysis

    def _calculate_optimization_score(self, build_times: list[float], optimizations: list[dict[str, Any]]) -> float:
        """Calculate overall optimization score (0-100)."""
        if not build_times:
            return 0.0

        base_score = 50.0  # Start with neutral score

        # Adjust based on build time consistency
        cv = np.std(build_times) / np.mean(build_times) if np.mean(build_times) > 0 else 1.0
        if cv < 0.1:
            base_score += 20  # Very consistent
        elif cv < 0.3:
            base_score += 10  # Moderately consistent
        elif cv > 0.5:
            base_score -= 20  # Very inconsistent

        # Adjust based on number of optimization opportunities
        if len(optimizations) == 0:
            base_score += 30  # No issues found
        elif len(optimizations) <= 2:
            base_score += 10  # Few issues
        elif len(optimizations) >= 5:
            base_score -= 20  # Many issues

        # Adjust based on average build time
        avg_time = np.mean(build_times)
        if avg_time < 60:  # Less than 1 minute
            base_score += 20
        elif avg_time < 300:  # Less than 5 minutes
            base_score += 10
        elif avg_time > 1800:  # More than 30 minutes
            base_score -= 30

        return max(0.0, min(100.0, base_score))
