"""AI-powered intelligence tools."""

from datetime import datetime
from typing import Any

from fastmcp import Context

from services.jenkins_service import JenkinsService
from utils import parse_timestamp


class AITools:
    """AI-powered intelligence tools."""

    def __init__(self, jenkins_service: JenkinsService):
        self.jenkins = jenkins_service

    async def predict_pipeline_failure(self, pipeline_name: str, ctx: Context) -> dict[str, Any]:
        """AI prediction of likely pipeline failures based on patterns."""
        await ctx.info(f"Predicting failure risk for pipeline: {pipeline_name}")

        if not self.jenkins.is_initialized():
            await ctx.error("Jenkins not initialized. Please configure Jenkins connection first.")
            raise ValueError("Jenkins not initialized. Please configure Jenkins connection first.")

        try:
            await ctx.info("Analyzing historical patterns...")
            builds = self.jenkins.get_builds(pipeline_name, 50)

            if len(builds) < 10:
                return {"error": "Insufficient data for prediction (need at least 10 builds)"}

            # Analyze recent patterns
            recent_builds = builds[:20]
            failure_count = len([b for b in recent_builds if b.get("result") == "FAILURE"])
            failure_rate = (failure_count / len(recent_builds)) * 100

            # Calculate risk factors
            risk_factors = []
            risk_score = 0

            if failure_rate > 30:
                risk_factors.append("High recent failure rate")
                risk_score += 40
            elif failure_rate > 15:
                risk_factors.append("Moderate recent failure rate")
                risk_score += 20

            # Check for consecutive failures
            consecutive_failures = 0
            for build in recent_builds[:5]:
                if build.get("result") == "FAILURE":
                    consecutive_failures += 1
                else:
                    break

            if consecutive_failures >= 3:
                risk_factors.append(f"{consecutive_failures} consecutive failures")
                risk_score += 30
            elif consecutive_failures >= 2:
                risk_factors.append(f"{consecutive_failures} consecutive failures")
                risk_score += 15

            # Check build frequency (too frequent might indicate instability)
            if len(recent_builds) > 1:
                time_span = (parse_timestamp(recent_builds[0].get("timestamp")) -
                            parse_timestamp(recent_builds[-1].get("timestamp"))).total_seconds() / 3600
                builds_per_hour = len(recent_builds) / time_span if time_span > 0 else 0

                if builds_per_hour > 2:
                    risk_factors.append("Very high build frequency")
                    risk_score += 10

            # Determine risk level
            if risk_score >= 70:
                risk_level = "HIGH"
                recommendation = "Immediate attention required. Consider pausing pipeline and investigating root causes."
            elif risk_score >= 40:
                risk_level = "MEDIUM"
                recommendation = "Monitor closely. Review recent changes and consider implementing better error handling."
            else:
                risk_level = "LOW"
                recommendation = "Pipeline appears stable. Continue monitoring."

            prediction = {
                "pipeline_name": pipeline_name,
                "risk_level": risk_level,
                "risk_score": min(risk_score, 100),
                "failure_probability": min(failure_rate + (risk_score * 0.3), 100),
                "risk_factors": risk_factors,
                "recommendation": recommendation,
                "analysis_date": datetime.now().isoformat(),
                "builds_analyzed": len(recent_builds)
            }

            await ctx.info(f"Prediction complete: {risk_level} risk level")
            return prediction

        except Exception as e:
            await ctx.error(f"Error predicting failure for {pipeline_name}: {str(e)}")
            raise

    async def suggest_pipeline_optimization(self, pipeline_name: str, ctx: Context) -> list[dict[str, str]]:
        """AI suggestions for optimizing pipeline performance."""
        await ctx.info(f"Generating optimization suggestions for pipeline: {pipeline_name}")

        if not self.jenkins.is_initialized():
            await ctx.error("Jenkins not initialized. Please configure Jenkins connection first.")
            raise ValueError("Jenkins not initialized. Please configure Jenkins connection first.")

        try:
            await ctx.info("Analyzing pipeline performance...")
            builds = self.jenkins.get_builds(pipeline_name, 30)
            job_info = self.jenkins.get_job_info(pipeline_name)

            suggestions = []

            # Analyze build duration
            durations = [b.get("duration", 0) for b in builds if b.get("duration")]
            if durations:
                avg_duration = sum(durations) / len(durations)
                max_duration = max(durations)

                if max_duration > avg_duration * 2:
                    suggestions.append({
                        "category": "Performance",
                        "priority": "High",
                        "suggestion": "Consider parallelizing long-running steps or optimizing resource usage",
                        "reason": f"Build duration varies significantly (avg: {avg_duration/1000:.1f}s, max: {max_duration/1000:.1f}s)"
                    })

            # Analyze failure patterns
            failure_rate = len([b for b in builds if b.get("result") == "FAILURE"]) / len(builds) * 100
            if failure_rate > 20:
                suggestions.append({
                    "category": "Reliability",
                    "priority": "High",
                    "suggestion": "Implement retry mechanisms and better error handling",
                    "reason": f"High failure rate: {failure_rate:.1f}%"
                })

            # Check for resource optimization
            if job_info.get("nextBuildNumber", 1) > 100:
                suggestions.append({
                    "category": "Maintenance",
                    "priority": "Medium",
                    "suggestion": "Consider cleaning up old build artifacts and logs",
                    "reason": f"Pipeline has {job_info.get('nextBuildNumber', 1)} builds - may be consuming excessive storage"
                })

            # Check build frequency
            if len(builds) > 1:
                time_span = (parse_timestamp(builds[0].get("timestamp")) -
                            parse_timestamp(builds[-1].get("timestamp"))).total_seconds() / 3600
                builds_per_hour = len(builds) / time_span if time_span > 0 else 0

                if builds_per_hour > 1:
                    suggestions.append({
                        "category": "Efficiency",
                        "priority": "Medium",
                        "suggestion": "Consider implementing build batching or reducing trigger frequency",
                        "reason": f"High build frequency: {builds_per_hour:.1f} builds/hour"
                    })

            # General suggestions
            suggestions.append({
                "category": "Best Practices",
                "priority": "Low",
                "suggestion": "Add pipeline health checks and monitoring",
                "reason": "Proactive monitoring helps prevent issues"
            })

            await ctx.info(f"Generated {len(suggestions)} optimization suggestions")
            return suggestions

        except Exception as e:
            await ctx.error(f"Error generating suggestions for {pipeline_name}: {str(e)}")
            raise
