"""Advanced AI Features for Jenkins Pipeline Intelligence."""

import hashlib
import logging
import re
from datetime import datetime
from typing import Any

import numpy as np
from fastmcp import Context
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)


class AdvancedAITools:
    """Advanced AI-powered tools for Jenkins pipeline intelligence."""

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

    def _prepare_build_data(self, builds: list[dict]) -> np.ndarray:
        """Prepare build data for ML analysis."""
        if not builds:
            return np.array([])

        features = []
        for build in builds:
            # Extract features from build data
            duration = build.get('duration', 0) / 1000 if build.get('duration') else 0  # Convert to seconds
            timestamp = build.get('timestamp', 0) / 1000 if build.get('timestamp') else 0  # Convert to seconds
            result = 1 if build.get('result') == 'SUCCESS' else 0
            number = build.get('number', 0)

            # Calculate time-based features
            hour_of_day = datetime.fromtimestamp(timestamp).hour if timestamp > 0 else 0
            day_of_week = datetime.fromtimestamp(timestamp).weekday() if timestamp > 0 else 0

            features.append([duration, result, number, hour_of_day, day_of_week])

        return np.array(features)

    async def detect_pipeline_anomalies(
        self,
        pipeline_name: str,
        ctx: Context,
        sensitivity: str = "medium"
    ) -> dict[str, Any]:
        """Detect unusual patterns and anomalies in pipeline behavior using ML (analyzes last 5-20 builds)."""
        await ctx.info(f"Detecting anomalies in {pipeline_name} (sensitivity: {sensitivity}) - Using ML analysis of recent builds")

        try:
            # Get recent builds (5-20 based on sensitivity)
            build_limit = 20 if sensitivity == "high" else 15 if sensitivity == "medium" else 10 if sensitivity == "low" else 5

            builds = self.jenkins.get_builds(pipeline_name, build_limit)

            if len(builds) < 3:
                return {
                    "pipeline_name": pipeline_name,
                    "anomalies": [],
                    "status": "insufficient_data",
                    "message": f"Need at least 3 builds for anomaly detection, found {len(builds)}"
                }

            # Prepare data for ML analysis
            build_data = self._prepare_build_data(builds)

            if build_data.size == 0:
                return {
                    "pipeline_name": pipeline_name,
                    "anomalies": [],
                    "status": "no_data",
                    "message": "No valid build data for analysis"
                }

            # Configure anomaly detection based on sensitivity
            contamination = 0.1 if sensitivity == "high" else 0.2 if sensitivity == "medium" else 0.3

            # Use Isolation Forest for anomaly detection
            iso_forest = IsolationForest(contamination=contamination, random_state=42)
            anomaly_labels = iso_forest.fit_predict(build_data)

            # Identify anomalies
            anomalies = []
            for i, (build, is_anomaly) in enumerate(zip(builds, anomaly_labels, strict=False)):
                if is_anomaly == -1:  # Anomaly detected
                    anomaly_type = self._classify_anomaly_type(build, build_data[i])
                    anomalies.append({
                        "build_number": build.get('number'),
                        "timestamp": build.get('timestamp'),
                        "anomaly_type": anomaly_type,
                        "severity": self._calculate_anomaly_severity(build, build_data[i]),
                        "description": self._describe_anomaly(build, anomaly_type)
                    })

            # Calculate anomaly score
            anomaly_score = len(anomalies) / len(builds) * 100

            result = {
                "pipeline_name": pipeline_name,
                "analyzed_builds": len(builds),
                "anomalies": anomalies,
                "anomaly_score": round(anomaly_score, 2),
                "sensitivity": sensitivity,
                "data_source": "Jenkins build history (ML analysis)",
                "status": "completed"
            }

            if anomalies:
                await ctx.warning(f"⚠️  {len(anomalies)} anomalies detected in {pipeline_name}")
            else:
                await ctx.info(f"✅ No anomalies detected in {pipeline_name}")

            # Protect sensitive data before returning to AI
            protected_result = self._protect_sensitive_data_in_dict(result)
            return protected_result

        except Exception as e:
            await ctx.error(f"Error detecting anomalies: {str(e)}")
            raise

    def _classify_anomaly_type(self, build: dict, build_features: np.ndarray) -> str:
        """Classify the type of anomaly based on build features."""
        duration, result, number, hour, day = build_features

        if duration > 600:  # More than 10 minutes
            return "unusually_long_build"
        elif duration < 30:  # Less than 30 seconds
            return "unusually_short_build"
        elif result == 0 and duration > 300:  # Failed build that took long
            return "long_failed_build"
        elif hour < 6 or hour > 22:  # Outside normal hours
            return "off_hours_build"
        elif day in [5, 6]:  # Weekend
            return "weekend_build"
        else:
            return "general_anomaly"

    def _calculate_anomaly_severity(self, build: dict, build_features: np.ndarray) -> str:
        """Calculate anomaly severity."""
        duration, result, number, hour, day = build_features

        if result == 0:  # Failed build
            return "high"
        elif duration > 600:  # Very long build
            return "high"
        elif duration < 30:  # Very short build
            return "medium"
        else:
            return "low"

    def _describe_anomaly(self, build: dict, anomaly_type: str) -> str:
        """Generate human-readable description of anomaly."""
        descriptions = {
            "unusually_long_build": f"Build #{build.get('number')} took unusually long ({build.get('duration', 0)/1000:.1f}s)",
            "unusually_short_build": f"Build #{build.get('number')} completed unusually quickly ({build.get('duration', 0)/1000:.1f}s)",
            "long_failed_build": f"Build #{build.get('number')} failed after running for a long time",
            "off_hours_build": f"Build #{build.get('number')} ran outside normal business hours",
            "weekend_build": f"Build #{build.get('number')} ran on weekend",
            "general_anomaly": f"Build #{build.get('number')} shows unusual patterns"
        }
        return descriptions.get(anomaly_type, "Unknown anomaly type")

    async def intelligent_retry_logic(
        self,
        pipeline_name: str,
        ctx: Context,
        failure_reason: str = "unknown"
    ) -> dict[str, Any]:
        """Analyze failure patterns and suggest intelligent retry logic using ML (analyzes last 5-20 builds)."""
        await ctx.info(f"Analyzing retry logic for {pipeline_name} - Using ML analysis of recent builds")

        try:
            # Get recent builds for analysis
            builds = self.jenkins.get_builds(pipeline_name, 20)

            if len(builds) < 3:
                return {
                    "pipeline_name": pipeline_name,
                    "retry_suggestions": [],
                    "status": "insufficient_data",
                    "message": "Need at least 3 builds for retry analysis"
                }

            # Analyze failure patterns
            failed_builds = [build for build in builds if build.get('result') == 'FAILURE']
            successful_builds = [build for build in builds if build.get('result') == 'SUCCESS']

            if not failed_builds:
                return {
                    "pipeline_name": pipeline_name,
                    "retry_suggestions": [],
                    "status": "no_failures",
                    "message": "No recent failures to analyze"
                }

            # Analyze failure patterns using ML
            failure_patterns = self._analyze_failure_patterns(failed_builds, successful_builds)

            # Generate retry suggestions
            retry_suggestions = self._generate_retry_suggestions(failure_patterns, failure_reason)

            # Calculate retry confidence
            retry_confidence = self._calculate_retry_confidence(failure_patterns)

            result = {
                "pipeline_name": pipeline_name,
                "analyzed_builds": len(builds),
                "failed_builds": len(failed_builds),
                "failure_patterns": failure_patterns,
                "retry_suggestions": retry_suggestions,
                "retry_confidence": retry_confidence,
                "data_source": "Jenkins build history (ML analysis)",
                "status": "completed"
            }

            await ctx.info(f"✅ Retry analysis completed - {len(retry_suggestions)} suggestions generated")

            # Protect sensitive data before returning to AI
            protected_result = self._protect_sensitive_data_in_dict(result)
            return protected_result

        except Exception as e:
            await ctx.error(f"Error analyzing retry logic: {str(e)}")
            raise

    def _analyze_failure_patterns(self, failed_builds: list[dict], successful_builds: list[dict]) -> dict[str, Any]:
        """Analyze failure patterns using ML techniques."""
        patterns = {
            "time_based": {},
            "duration_based": {},
            "frequency_based": {},
            "recovery_patterns": {}
        }

        # Time-based patterns
        failure_hours = [datetime.fromtimestamp(b.get('timestamp', 0) / 1000).hour for b in failed_builds if b.get('timestamp')]
        if failure_hours:
            patterns["time_based"]["peak_failure_hour"] = max(set(failure_hours), key=failure_hours.count)
            patterns["time_based"]["failure_hour_variance"] = np.var(failure_hours)

        # Duration-based patterns
        failure_durations = [b.get('duration', 0) / 1000 for b in failed_builds if b.get('duration')]
        success_durations = [b.get('duration', 0) / 1000 for b in successful_builds if b.get('duration')]

        if failure_durations and success_durations:
            patterns["duration_based"]["avg_failure_duration"] = np.mean(failure_durations)
            patterns["duration_based"]["avg_success_duration"] = np.mean(success_durations)
            patterns["duration_based"]["duration_ratio"] = np.mean(failure_durations) / np.mean(success_durations)

        # Frequency patterns
        patterns["frequency_based"]["failure_rate"] = len(failed_builds) / (len(failed_builds) + len(successful_builds))
        patterns["frequency_based"]["consecutive_failures"] = self._count_consecutive_failures(failed_builds)

        # Recovery patterns
        patterns["recovery_patterns"]["avg_recovery_time"] = self._calculate_avg_recovery_time(failed_builds, successful_builds)

        return patterns

    def _count_consecutive_failures(self, failed_builds: list[dict]) -> int:
        """Count maximum consecutive failures."""
        if not failed_builds:
            return 0

        # Sort by build number
        sorted_failures = sorted(failed_builds, key=lambda x: x.get('number', 0))
        max_consecutive = 1
        current_consecutive = 1

        for i in range(1, len(sorted_failures)):
            if sorted_failures[i]['number'] == sorted_failures[i-1]['number'] + 1:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 1

        return max_consecutive

    def _calculate_avg_recovery_time(self, failed_builds: list[dict], successful_builds: list[dict]) -> float:
        """Calculate average time to recovery after failure."""
        if not failed_builds or not successful_builds:
            return 0.0

        recovery_times = []
        for failure in failed_builds:
            failure_time = failure.get('timestamp', 0)
            if failure_time:
                # Find next successful build after this failure
                for success in successful_builds:
                    success_time = success.get('timestamp', 0)
                    if success_time > failure_time:
                        recovery_times.append((success_time - failure_time) / (1000 * 60))  # Convert to minutes
                        break

        return np.mean(recovery_times) if recovery_times else 0.0

    def _generate_retry_suggestions(self, patterns: dict[str, Any], failure_reason: str) -> list[dict[str, Any]]:
        """Generate intelligent retry suggestions based on patterns."""
        suggestions = []

        # Time-based suggestions
        if patterns["time_based"].get("peak_failure_hour"):
            peak_hour = patterns["time_based"]["peak_failure_hour"]
            suggestions.append({
                "type": "timing",
                "priority": "medium",
                "suggestion": f"Consider avoiding builds during peak failure hour ({peak_hour}:00)",
                "reasoning": "Failures are more common at this time"
            })

        # Duration-based suggestions
        if patterns["duration_based"].get("duration_ratio", 0) > 2:
            suggestions.append({
                "type": "timeout",
                "priority": "high",
                "suggestion": "Increase build timeout - failed builds take much longer than successful ones",
                "reasoning": f"Failed builds take {patterns['duration_based']['duration_ratio']:.1f}x longer on average"
            })

        # Frequency-based suggestions
        failure_rate = patterns["frequency_based"].get("failure_rate", 0)
        if failure_rate > 0.3:
            suggestions.append({
                "type": "reliability",
                "priority": "high",
                "suggestion": "Implement exponential backoff retry strategy",
                "reasoning": f"High failure rate ({failure_rate:.1%}) indicates unstable pipeline"
            })

        consecutive_failures = patterns["frequency_based"].get("consecutive_failures", 0)
        if consecutive_failures > 2:
            suggestions.append({
                "type": "circuit_breaker",
                "priority": "high",
                "suggestion": "Implement circuit breaker pattern to prevent cascading failures",
                "reasoning": f"Observed {consecutive_failures} consecutive failures"
            })

        # Recovery-based suggestions
        avg_recovery = patterns["recovery_patterns"].get("avg_recovery_time", 0)
        if avg_recovery > 60:  # More than 1 hour
            suggestions.append({
                "type": "monitoring",
                "priority": "medium",
                "suggestion": "Improve monitoring and alerting for faster failure detection",
                "reasoning": f"Average recovery time is {avg_recovery:.1f} minutes"
            })

        return suggestions

    def _calculate_retry_confidence(self, patterns: dict[str, Any]) -> float:
        """Calculate confidence score for retry suggestions."""
        confidence_factors = []

        # More data = higher confidence
        if patterns["frequency_based"].get("failure_rate", 0) > 0:
            confidence_factors.append(0.8)

        # Clear patterns = higher confidence
        if patterns["time_based"].get("peak_failure_hour"):
            confidence_factors.append(0.7)

        if patterns["duration_based"].get("duration_ratio", 0) > 1.5:
            confidence_factors.append(0.6)

        return np.mean(confidence_factors) if confidence_factors else 0.3

    async def generate_ai_insights(
        self,
        pipeline_name: str,
        ctx: Context,
        insight_type: str = "comprehensive"
    ) -> dict[str, Any]:
        """Generate comprehensive AI-powered insights about the pipeline using real data analysis."""
        await ctx.info(f"Generating AI insights for {pipeline_name} ({insight_type}) - Using real data analysis")

        try:
            # Get recent builds for analysis
            builds = self.jenkins.get_builds(pipeline_name, 50)

            if not builds:
                return {
                    "pipeline_name": pipeline_name,
                    "insights": [],
                    "status": "no_data",
                    "message": "No build data available for analysis"
                }

            # Generate various insights
            insights = []

            # Performance insights
            build_times = [build.get('duration', 0) for build in builds if build.get('duration')]
            if build_times:
                avg_time = np.mean(build_times) / 1000
                std_time = np.std(build_times) / 1000
                insights.append({
                    "category": "performance",
                    "title": "Build Time Analysis",
                    "description": f"Average build time: {avg_time:.1f}s (σ={std_time:.1f}s)",
                    "recommendation": "Consider parallel execution" if avg_time > 300 else "Build times are optimal",
                    "impact": "high" if avg_time > 600 else "medium" if avg_time > 300 else "low",
                    "confidence": 0.9
                })

            # Reliability insights
            success_rate = sum(1 for build in builds if build.get('result') == 'SUCCESS') / len(builds) * 100
            insights.append({
                "category": "reliability",
                "title": "Pipeline Stability",
                "description": f"Success rate: {success_rate:.1f}%",
                "recommendation": "Investigate failure patterns" if success_rate < 90 else "Pipeline is stable",
                "impact": "high" if success_rate < 80 else "low",
                "confidence": 0.95
            })

            # Efficiency insights
            recent_builds = builds[-10:]
            if recent_builds:
                recent_success_rate = sum(1 for build in recent_builds if build.get('result') == 'SUCCESS') / len(recent_builds) * 100
                insights.append({
                    "category": "efficiency",
                    "title": "Recent Performance Trend",
                    "description": f"Recent success rate: {recent_success_rate:.1f}%",
                    "recommendation": "Monitor recent changes" if recent_success_rate < success_rate else "Performance is improving",
                    "impact": "medium",
                    "confidence": 0.8
                })

            # Resource utilization insights
            if build_times:
                time_variance = np.var(build_times) / 1000
                insights.append({
                    "category": "resource_utilization",
                    "title": "Build Time Consistency",
                    "description": f"Build time variance: {time_variance:.1f}s²",
                    "recommendation": "Standardize build environment" if time_variance > 10000 else "Build times are consistent",
                    "impact": "medium",
                    "confidence": 0.7
                })

            # Generate overall health score
            health_score = self._calculate_health_score(builds, insights)

            result = {
                "pipeline_name": pipeline_name,
                "analyzed_builds": len(builds),
                "insights": insights,
                "health_score": health_score,
                "data_source": "Jenkins build history (AI analysis)",
                "generated_at": datetime.now().isoformat(),
                "status": "completed"
            }

            await ctx.info(f"✅ AI insights generated - Health score: {health_score:.1f}/100")

            # Protect sensitive data before returning to AI
            protected_result = self._protect_sensitive_data_in_dict(result)
            return protected_result

        except Exception as e:
            await ctx.error(f"Error generating AI insights: {str(e)}")
            raise

    def _calculate_health_score(self, builds: list[dict], insights: list[dict]) -> float:
        """Calculate overall pipeline health score."""
        if not builds:
            return 0.0

        # Base score
        success_rate = sum(1 for build in builds if build.get('result') == 'SUCCESS') / len(builds) * 100
        base_score = success_rate

        # Adjust based on insights
        adjustments = 0
        for insight in insights:
            if insight["category"] == "performance" and insight["impact"] == "high":
                adjustments -= 10
            elif insight["category"] == "reliability" and insight["impact"] == "high":
                adjustments -= 15
            elif insight["category"] == "efficiency" and "improving" in insight["recommendation"]:
                adjustments += 5

        return max(0, min(100, base_score + adjustments))

    async def predict_pipeline_failure(
        self,
        pipeline_name: str,
        ctx: Context
    ) -> dict[str, Any]:
        """Predict pipeline failure using ML models based on historical data."""
        await ctx.info(f"Predicting failure probability for {pipeline_name} - Using ML models")

        try:
            # Get recent builds for training
            builds = self.jenkins.get_builds(pipeline_name, 30)

            if len(builds) < 10:
                return {
                    "pipeline_name": pipeline_name,
                    "prediction": "insufficient_data",
                    "message": "Need at least 10 builds for failure prediction"
                }

            # Prepare features for prediction
            build_data = self._prepare_build_data(builds)

            # Simple failure prediction based on recent trends
            recent_builds = builds[-5:]
            recent_failures = sum(1 for build in recent_builds if build.get('result') == 'FAILURE')
            recent_failure_rate = recent_failures / len(recent_builds)

            # Calculate failure probability
            failure_probability = self._calculate_failure_probability(build_data, recent_failure_rate)

            # Generate prediction confidence
            confidence = self._calculate_prediction_confidence(builds)

            result = {
                "pipeline_name": pipeline_name,
                "failure_probability": round(failure_probability, 2),
                "confidence": round(confidence, 2),
                "risk_level": "high" if failure_probability > 0.7 else "medium" if failure_probability > 0.4 else "low",
                "factors": self._identify_risk_factors(builds, failure_probability),
                "data_source": "Jenkins build history (ML prediction)",
                "status": "completed"
            }

            await ctx.info(f"✅ Failure prediction completed - Risk: {result['risk_level']} ({failure_probability:.1%})")

            # Protect sensitive data before returning to AI
            protected_result = self._protect_sensitive_data_in_dict(result)
            return protected_result

        except Exception as e:
            await ctx.error(f"Error predicting failure: {str(e)}")
            raise

    def _calculate_failure_probability(self, build_data: np.ndarray, recent_failure_rate: float) -> float:
        """Calculate failure probability using ML techniques."""
        if build_data.size == 0:
            return 0.5

        # Use recent failure rate as base
        base_probability = recent_failure_rate

        # Adjust based on build patterns
        if len(build_data) > 1:
            # Check for increasing failure trend
            recent_results = build_data[-5:, 1] if len(build_data) >= 5 else build_data[:, 1]
            if len(recent_results) > 1:
                failure_trend = np.mean(recent_results[:-1]) - np.mean(recent_results[1:])
                if failure_trend > 0.2:  # Increasing failures
                    base_probability += 0.2
                elif failure_trend < -0.2:  # Decreasing failures
                    base_probability -= 0.1

        # Adjust based on build duration patterns
        durations = build_data[:, 0] if build_data.size > 0 else []
        if len(durations) > 1:
            duration_trend = np.mean(durations[-3:]) - np.mean(durations[:-3]) if len(durations) > 3 else 0
            if duration_trend > 60:  # Increasing build times
                base_probability += 0.1

        return max(0.0, min(1.0, base_probability))

    def _calculate_prediction_confidence(self, builds: list[dict]) -> float:
        """Calculate confidence in failure prediction."""
        if len(builds) < 10:
            return 0.3
        elif len(builds) < 20:
            return 0.6
        else:
            return 0.8

    def _identify_risk_factors(self, builds: list[dict], failure_probability: float) -> list[str]:
        """Identify risk factors contributing to failure prediction."""
        factors = []

        if failure_probability > 0.7:
            factors.append("High recent failure rate")

        # Check for time-based patterns
        failure_hours = [datetime.fromtimestamp(b.get('timestamp', 0) / 1000).hour
                        for b in builds if b.get('result') == 'FAILURE' and b.get('timestamp')]
        if failure_hours:
            peak_hour = max(set(failure_hours), key=failure_hours.count)
            factors.append(f"Failures concentrated around {peak_hour}:00")

        # Check for duration patterns
        build_times = [b.get('duration', 0) for b in builds if b.get('duration')]
        if build_times:
            avg_time = np.mean(build_times) / 1000
            if avg_time > 300:
                factors.append("Long average build times")

        return factors

    async def suggest_pipeline_optimization(
        self,
        pipeline_name: str,
        ctx: Context
    ) -> dict[str, Any]:
        """Suggest pipeline optimizations based on AI analysis of build data."""
        await ctx.info(f"Analyzing optimization opportunities for {pipeline_name} - Using AI analysis")

        try:
            # Get recent builds for analysis
            builds = self.jenkins.get_builds(pipeline_name, 30)

            if not builds:
                return {
                    "pipeline_name": pipeline_name,
                    "optimizations": [],
                    "status": "no_data",
                    "message": "No build data available for optimization analysis"
                }

            # Analyze build patterns
            build_analysis = self._analyze_build_patterns(builds)

            # Generate optimization suggestions
            optimizations = self._generate_optimization_suggestions(build_analysis)

            # Calculate potential impact
            total_impact = sum(opt.get('impact_score', 0) for opt in optimizations)

            result = {
                "pipeline_name": pipeline_name,
                "analyzed_builds": len(builds),
                "optimizations": optimizations,
                "total_impact_score": total_impact,
                "data_source": "Jenkins build history (AI analysis)",
                "status": "completed"
            }

            await ctx.info(f"✅ Optimization analysis completed - {len(optimizations)} suggestions generated")

            # Protect sensitive data before returning to AI
            protected_result = self._protect_sensitive_data_in_dict(result)
            return protected_result

        except Exception as e:
            await ctx.error(f"Error analyzing optimizations: {str(e)}")
            raise

    def _analyze_build_patterns(self, builds: list[dict]) -> dict[str, Any]:
        """Analyze build patterns for optimization opportunities."""
        analysis = {
            "timing": {},
            "duration": {},
            "reliability": {},
            "efficiency": {}
        }

        # Timing analysis
        build_hours = [datetime.fromtimestamp(b.get('timestamp', 0) / 1000).hour
                      for b in builds if b.get('timestamp')]
        if build_hours:
            analysis["timing"]["peak_hour"] = max(set(build_hours), key=build_hours.count)
            analysis["timing"]["hour_distribution"] = np.histogram(build_hours, bins=24)[0].tolist()

        # Duration analysis
        durations = [b.get('duration', 0) for b in builds if b.get('duration')]
        if durations:
            analysis["duration"]["mean"] = np.mean(durations) / 1000
            analysis["duration"]["std"] = np.std(durations) / 1000
            analysis["duration"]["min"] = np.min(durations) / 1000
            analysis["duration"]["max"] = np.max(durations) / 1000

        # Reliability analysis
        results = [b.get('result') for b in builds]
        success_count = results.count('SUCCESS')
        analysis["reliability"]["success_rate"] = success_count / len(results)
        analysis["reliability"]["failure_rate"] = 1 - analysis["reliability"]["success_rate"]

        # Efficiency analysis
        if durations:
            analysis["efficiency"]["throughput"] = len(builds) / (np.sum(durations) / (1000 * 60 * 60))  # builds per hour
            analysis["efficiency"]["consistency"] = 1 - (np.std(durations) / np.mean(durations)) if np.mean(durations) > 0 else 0

        return analysis

    def _generate_optimization_suggestions(self, analysis: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate optimization suggestions based on analysis."""
        suggestions = []

        # Duration-based optimizations
        duration = analysis.get("duration", {})
        if duration.get("mean", 0) > 300:  # More than 5 minutes
            suggestions.append({
                "type": "parallel_execution",
                "title": "Implement Parallel Execution",
                "description": "Build takes too long - consider parallelizing independent steps",
                "impact_score": 8,
                "effort": "medium",
                "reasoning": f"Average build time is {duration['mean']:.1f}s"
            })

        if duration.get("std", 0) > 60:  # High variance
            suggestions.append({
                "type": "standardization",
                "title": "Standardize Build Environment",
                "description": "High build time variance - standardize dependencies and environment",
                "impact_score": 6,
                "effort": "high",
                "reasoning": f"Build time variance is {duration['std']:.1f}s"
            })

        # Reliability-based optimizations
        reliability = analysis.get("reliability", {})
        if reliability.get("failure_rate", 0) > 0.2:  # More than 20% failure rate
            suggestions.append({
                "type": "error_handling",
                "title": "Improve Error Handling",
                "description": "High failure rate - add better error handling and retry logic",
                "impact_score": 9,
                "effort": "medium",
                "reasoning": f"Failure rate is {reliability['failure_rate']:.1%}"
            })

        # Efficiency-based optimizations
        efficiency = analysis.get("efficiency", {})
        if efficiency.get("consistency", 0) < 0.7:  # Low consistency
            suggestions.append({
                "type": "caching",
                "title": "Implement Build Caching",
                "description": "Low build consistency - implement caching for dependencies",
                "impact_score": 7,
                "effort": "medium",
                "reasoning": f"Build consistency is {efficiency['consistency']:.1%}"
            })

        # Timing-based optimizations
        timing = analysis.get("timing", {})
        if timing.get("peak_hour"):
            peak_hour = timing["peak_hour"]
            suggestions.append({
                "type": "scheduling",
                "title": "Optimize Build Scheduling",
                "description": f"Consider distributing builds - peak usage at {peak_hour}:00",
                "impact_score": 4,
                "effort": "low",
                "reasoning": "Builds are concentrated in specific hours"
            })

        return suggestions
