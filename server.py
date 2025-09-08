"""MCP Jenkins Intelligence Server - Modular Architecture."""

import logging
import os
from typing import Any

from fastmcp import Context, FastMCP

from models import BuildInfo, FailureAnalysis, PipelineHealth, PipelineInfo, QueryResult
from prompts import (
    analyze_pipeline_prompt,
    failure_analysis_prompt,
    optimization_prompt,
    security_audit_prompt,
)
from resources import (
    get_overall_health,
    get_pipeline_dashboard,
    get_pipeline_logs,
    get_pipeline_status,
    get_pipeline_summary,
)
from services import (
    AITools,
    ControlTools,
    CoreTools,
    JenkinsService,
    MonitoringTools,
    SecurityTools,
)
from services.advanced_ai_tools import AdvancedAITools
from services.advanced_security_tools import AdvancedSecurityTools
from services.analytics_tools import AnalyticsTools
from services.jenkinsfile_service import JenkinsfileService
from services.performance_tools import PerformanceTools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get MCP server port from environment variable
MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8000"))

# Create the FastMCP server
mcp = FastMCP(
    name="Pipeline Awareness",
    instructions="Interactive Jenkins Pipeline Analysis for VSCode and Cursor AI. Provides comprehensive pipeline monitoring, analysis, and AI-powered insights.",
    version="3.0.0"
)

# Initialize services
jenkins_service = JenkinsService()
core_tools = CoreTools(jenkins_service)
control_tools = ControlTools(jenkins_service)
monitoring_tools = MonitoringTools(jenkins_service)
ai_tools = AITools(jenkins_service)
security_tools = SecurityTools(jenkins_service)
jenkinsfile_service = JenkinsfileService(jenkins_service)

# Initialize new advanced services
analytics_tools = AnalyticsTools(jenkins_service)
advanced_security_tools = AdvancedSecurityTools(jenkins_service)
advanced_ai_tools = AdvancedAITools(jenkins_service)
performance_tools = PerformanceTools(jenkins_service)

# Auto-configure Jenkins if environment variables are present
def auto_configure_jenkins():
    """Auto-configure Jenkins if environment variables are present."""
    jenkins_url = os.getenv("JENKINS_URL")
    jenkins_username = os.getenv("JENKINS_USERNAME")
    jenkins_token = os.getenv("JENKINS_TOKEN")
    jenkins_verify_ssl = os.getenv("JENKINS_VERIFY_SSL", "true").lower() == "true"

    logger.info(f"Auto-configuration check - URL: {jenkins_url}, Username: {jenkins_username}, Token: {'***' if jenkins_token else 'None'}")

    if jenkins_url and jenkins_username and jenkins_token:
        try:
            jenkins_service.initialize(jenkins_url, jenkins_username, jenkins_token, jenkins_verify_ssl)
            logger.info(f"✅ Auto-configured Jenkins connection to {jenkins_url}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to auto-configure Jenkins: {e}")
            return False
    else:
        logger.warning("⚠️ Jenkins environment variables not found or incomplete")
        return False

# Try to auto-configure Jenkins on startup
auto_configure_jenkins()


# Core Tools
@mcp.tool
async def list_pipelines(ctx: Context, search: str = "", limit: int = 50) -> list[PipelineInfo]:
    """List all available Jenkins pipelines with basic information."""
    if not jenkins_service.is_initialized():
        await ctx.warning("Jenkins not configured. Attempting to auto-configure from environment variables...")
        if not auto_configure_jenkins():
            await ctx.error("Jenkins auto-configuration failed. Please use configure_jenkins tool or check your environment variables.")
            raise ValueError("Jenkins not configured. Please use configure_jenkins tool or check your environment variables.")
        else:
            await ctx.info("Jenkins auto-configured successfully!")

    return await core_tools.list_pipelines(ctx, search, limit)


@mcp.tool
async def get_pipeline_details(pipeline_name: str, ctx: Context) -> PipelineInfo:
    """Get detailed information about a specific pipeline."""
    return await core_tools.get_pipeline_details(pipeline_name, ctx)


@mcp.tool
async def get_pipeline_builds(pipeline_name: str, ctx: Context, limit: int = 20, status: str | None = None) -> list[BuildInfo]:
    """Get recent builds for a pipeline."""
    return await core_tools.get_pipeline_builds(pipeline_name, ctx, limit, status)


@mcp.tool
async def analyze_pipeline_health(pipeline_name: str, ctx: Context, period: str = "last_7d") -> PipelineHealth:
    """Analyze the health and performance of a pipeline."""
    return await core_tools.analyze_pipeline_health(pipeline_name, ctx, period)


@mcp.tool
async def analyze_pipeline_failure(pipeline_name: str, build_number: int, ctx: Context) -> FailureAnalysis:
    """Analyze a specific pipeline failure with AI-powered root cause analysis."""
    return await core_tools.analyze_pipeline_failure(pipeline_name, build_number, ctx)


@mcp.tool
async def ask_pipeline_question(question: str, ctx: Context, pipeline_names: list[str] = None) -> QueryResult:
    """Ask natural language questions about pipelines and get AI-powered answers."""
    return await core_tools.ask_pipeline_question(question, ctx, pipeline_names)


@mcp.tool
async def configure_jenkins(url: str, username: str, token: str, ctx: Context, verify_ssl: bool = True) -> str:
    """Configure Jenkins connection."""
    await ctx.info(f"Configuring Jenkins connection to: {url}")

    try:
        jenkins_service.initialize(url, username, token, verify_ssl)
        await ctx.info("Jenkins connection configured successfully")
        return f"Successfully configured Jenkins connection to {url}"
    except Exception as e:
        await ctx.error(f"Failed to configure Jenkins: {str(e)}")
        return f"Failed to configure Jenkins: {str(e)}"


@mcp.tool
async def test_connection(ctx: Context) -> str:
    """Test Jenkins connection."""
    await ctx.info("Testing Jenkins connection...")

    if not jenkins_service.is_initialized():
        await ctx.warning("Jenkins not configured. Please use configure_jenkins first.")
        return "Jenkins not configured. Please use configure_jenkins first."

    try:
        jenkins_service.get_whoami()
        await ctx.info("Jenkins connection test successful")
        return "Jenkins connection successful"
    except Exception as e:
        await ctx.error(f"Jenkins connection test failed: {str(e)}")
        return f"Jenkins connection failed: {str(e)}"


@mcp.tool
async def get_server_info(ctx: Context) -> dict[str, Any]:
    """Get MCP server information including port configuration."""
    await ctx.info("Getting server information...")

    # Check environment variables
    env_vars = {
        "JENKINS_URL": os.getenv("JENKINS_URL", "Not set"),
        "JENKINS_USERNAME": os.getenv("JENKINS_USERNAME", "Not set"),
        "JENKINS_TOKEN": "***" if os.getenv("JENKINS_TOKEN") else "Not set",
        "MCP_SERVER_PORT": os.getenv("MCP_SERVER_PORT", "8000 (default)")
    }

    # Try to auto-configure if not already configured
    if not jenkins_service.is_initialized():
        await ctx.info("Jenkins not configured, attempting auto-configuration...")
        auto_configure_jenkins()

    return {
        "server_name": "Pipeline Awareness",
        "version": "3.0.0",
        "mcp_server_port": MCP_SERVER_PORT,
        "transport_modes": ["stdio", "http", "sse"],
        "total_tools": 21,
        "total_resources": 5,
        "total_prompts": 4,
        "jenkins_configured": jenkins_service.is_initialized(),
        "environment_variables": env_vars,
        "port_note": f"MCP server HTTP transport port: {MCP_SERVER_PORT} (set via MCP_SERVER_PORT env var)"
    }


# Control Tools
@mcp.tool
async def trigger_pipeline_build(pipeline_name: str, ctx: Context, parameters: dict[str, Any] = None, confirm: bool = False) -> str:
    """Trigger a new build for a pipeline with optional parameters."""
    return await control_tools.trigger_pipeline_build(pipeline_name, ctx, parameters, confirm)


@mcp.tool
async def stop_pipeline_build(pipeline_name: str, build_number: int, ctx: Context, confirm: bool = False) -> str:
    """Stop a running pipeline build."""
    return await control_tools.stop_pipeline_build(pipeline_name, build_number, ctx, confirm)


@mcp.tool
async def enable_disable_pipeline(pipeline_name: str, enabled: bool, ctx: Context, confirm: bool = False) -> str:
    """Enable or disable a pipeline."""
    return await control_tools.enable_disable_pipeline(pipeline_name, enabled, ctx, confirm)


@mcp.tool
async def get_pipeline_config(pipeline_name: str, ctx: Context) -> str:
    """Get the configuration (Jenkinsfile/XML) of a pipeline."""
    return await control_tools.get_pipeline_config(pipeline_name, ctx)


# Monitoring Tools
@mcp.tool
async def get_pipeline_metrics(pipeline_name: str, ctx: Context, period: str = "last_7d") -> dict[str, Any]:
    """Get detailed metrics for a pipeline."""
    return await monitoring_tools.get_pipeline_metrics(pipeline_name, ctx, period)


@mcp.tool
async def get_pipeline_dependencies(pipeline_name: str, ctx: Context) -> list[dict[str, str]]:
    """Get upstream/downstream pipeline dependencies."""
    return await monitoring_tools.get_pipeline_dependencies(pipeline_name, ctx)


@mcp.tool
async def monitor_pipeline_queue(ctx: Context) -> list[dict[str, Any]]:
    """Monitor Jenkins build queue and pending builds."""
    return await monitoring_tools.monitor_pipeline_queue(ctx)


@mcp.tool
async def analyze_build_trends(pipeline_names: list[str], ctx: Context, period: str = "last_7d") -> dict[str, Any]:
    """Analyze build trends across multiple pipelines."""
    return await monitoring_tools.analyze_build_trends(pipeline_names, ctx, period)


# AI Tools
@mcp.tool
async def predict_pipeline_failure(pipeline_name: str, ctx: Context) -> dict[str, Any]:
    """AI prediction of likely pipeline failures based on patterns."""
    return await ai_tools.predict_pipeline_failure(pipeline_name, ctx)


@mcp.tool
async def suggest_pipeline_optimization(pipeline_name: str, ctx: Context) -> list[dict[str, str]]:
    """AI suggestions for optimizing pipeline performance."""
    return await ai_tools.suggest_pipeline_optimization(pipeline_name, ctx)


# Security Tools
@mcp.tool
async def scan_pipeline_security(pipeline_name: str, ctx: Context) -> dict[str, Any]:
    """Scan pipeline for security vulnerabilities and best practices."""
    return await security_tools.scan_pipeline_security(pipeline_name, ctx)


# MCP Resources
@mcp.resource("pipeline://status")
async def pipeline_status(ctx: Context) -> str:
    """Get overall pipeline system status and health summary."""
    return get_pipeline_status(jenkins_service)


@mcp.resource("pipeline://{pipeline_name}/summary")
async def pipeline_summary(pipeline_name: str, ctx: Context) -> str:
    """Get a comprehensive summary of a specific pipeline."""
    return get_pipeline_summary(pipeline_name, jenkins_service, core_tools)


@mcp.resource("pipeline://dashboard")
async def pipeline_dashboard(ctx: Context) -> str:
    """Get a comprehensive dashboard view of all pipelines."""
    return get_pipeline_dashboard(jenkins_service)


@mcp.resource("pipeline://{pipeline_name}/logs/{build_number}")
async def pipeline_logs(pipeline_name: str, build_number: int, ctx: Context) -> str:
    """Get build logs for a specific pipeline build."""
    return get_pipeline_logs(pipeline_name, build_number, jenkins_service)


@mcp.resource("pipeline://health")
async def pipeline_health(ctx: Context) -> str:
    """Get overall system health and alerts."""
    return get_overall_health(jenkins_service)


# Jenkinsfile Tools
@mcp.tool
async def reconstruct_jenkinsfile(pipeline_name: str, ctx: Context) -> dict[str, Any]:
    """Reconstruct Jenkinsfile content from pipeline execution data."""
    return await jenkinsfile_service.reconstruct_jenkinsfile(pipeline_name, ctx)


@mcp.tool
async def suggest_pipeline_improvements(pipeline_name: str, ctx: Context) -> dict[str, Any]:
    """Get improvement suggestions for a pipeline based on reconstructed Jenkinsfile."""
    return await jenkinsfile_service.suggest_improvements(pipeline_name, ctx)


# ===== ADVANCED ANALYTICS & REPORTING TOOLS =====

@mcp.tool
async def generate_pipeline_report(
    pipeline_name: str,
    ctx: Context,
    period: str = "last_30d",
    format: str = "html"
) -> dict[str, Any]:
    """Generate comprehensive pipeline report based on Jenkins build history (no external metrics plugins)."""
    return await analytics_tools.generate_pipeline_report(pipeline_name, ctx, period, format)


@mcp.tool
async def compare_pipeline_performance(
    pipeline_names: list[str],
    ctx: Context,
    period: str = "last_7d"
) -> dict[str, Any]:
    """Compare performance across multiple pipelines based on Jenkins build history (no external metrics plugins)."""
    return await analytics_tools.compare_pipeline_performance(pipeline_names, ctx, period)




# ===== ADVANCED SECURITY & COMPLIANCE TOOLS =====



@mcp.tool
async def audit_access_controls(
    pipeline_name: str,
    ctx: Context
) -> dict[str, Any]:
    """Audit pipeline access controls and permissions using Jenkins security API (no LDAP/AD integration)."""
    return await advanced_security_tools.audit_access_controls(pipeline_name, ctx)




# ===== ADVANCED AI FEATURES =====

@mcp.tool
async def detect_pipeline_anomalies(
    pipeline_name: str,
    ctx: Context,
    sensitivity: str = "medium"
) -> dict[str, Any]:
    """Detect unusual patterns and anomalies in pipeline behavior using ML (analyzes last 5-20 builds)."""
    return await advanced_ai_tools.detect_pipeline_anomalies(pipeline_name, ctx, sensitivity)


@mcp.tool
async def intelligent_retry_logic(
    pipeline_name: str,
    ctx: Context,
    failure_reason: str = "unknown"
) -> dict[str, Any]:
    """Analyze failure patterns and suggest intelligent retry logic using ML (analyzes last 5-20 builds)."""
    return await advanced_ai_tools.intelligent_retry_logic(pipeline_name, ctx, failure_reason)




@mcp.tool
async def generate_ai_insights(
    pipeline_name: str,
    ctx: Context,
    insight_type: str = "comprehensive"
) -> dict[str, Any]:
    """Generate comprehensive AI-powered insights about the pipeline using real data analysis."""
    return await advanced_ai_tools.generate_ai_insights(pipeline_name, ctx, insight_type)


# ===== PERFORMANCE OPTIMIZATION TOOLS =====

@mcp.tool
async def analyze_build_time_optimization(
    pipeline_name: str,
    ctx: Context,
    period: str = "last_30d"
) -> dict[str, Any]:
    """Analyze build time optimization opportunities using Jenkins data (no external metrics plugins)."""
    return await performance_tools.analyze_build_time_optimization(pipeline_name, ctx, period)




@mcp.tool
async def get_jenkinsfile(pipeline_name: str, ctx: Context) -> str:
    """Get the Jenkinsfile for a pipeline, automatically reconstructing if needed."""
    await ctx.info(f"Getting Jenkinsfile for pipeline: {pipeline_name}")

    if not jenkins_service.is_initialized():
        await ctx.error("Jenkins not initialized. Please configure Jenkins connection first.")
        raise ValueError("Jenkins not initialized. Please configure Jenkins connection first.")

    try:
        # First try to get the pipeline config to check if it's a Pipeline job
        await ctx.info("Checking pipeline configuration...")
        config = jenkins_service.get_job_config(pipeline_name)

        # Check if this is a Pipeline job with external Jenkinsfile
        if 'pipeline' in config.lower() and 'scriptpath' in config.lower():
            import re
            script_path_match = re.search(r'<scriptPath>(.*?)</scriptPath>', config)
            if script_path_match:
                script_path = script_path_match.group(1)
                await ctx.info(f"Pipeline uses external Jenkinsfile: {script_path}")

                # This is a Git-based pipeline, reconstruct the Jenkinsfile
                await ctx.warning("Jenkinsfile is stored in Git repository, not accessible directly.")
                await ctx.info("🔍 Reconstructing Jenkinsfile from execution data...")

                reconstruction = await jenkinsfile_service.reconstruct_jenkinsfile(pipeline_name, ctx)

                if 'reconstructed_jenkinsfile' in reconstruction:
                    await ctx.info("✅ Successfully reconstructed Jenkinsfile!")

                    jenkinsfile = reconstruction['reconstructed_jenkinsfile']
                    analysis = reconstruction.get('analysis', {})

                    result = f"""# Jenkinsfile for {pipeline_name}
# Reconstructed from execution data (Build #{reconstruction.get('build_analyzed', 'Unknown')})
# Pipeline Analysis:
#   - Total Stages: {analysis.get('total_stages', 'Unknown')}
#   - Duration: {analysis.get('total_duration_formatted', 'Unknown')}
#   - Technologies: {', '.join(analysis.get('technologies_used', []))}
#   - Source: {script_path}

{jenkinsfile}"""

                    return result
                else:
                    await ctx.error("Failed to reconstruct Jenkinsfile from execution data.")
                    return f"# Error: Could not reconstruct Jenkinsfile for {pipeline_name}\n# Original config shows Jenkinsfile at: {script_path}\n# Please check the Git repository for the actual Jenkinsfile content."
        else:
            # This might be a freestyle job or pipeline with inline script
            await ctx.info("Pipeline configuration retrieved (may contain inline script)")
            return config

    except Exception as e:
        await ctx.error(f"Error getting Jenkinsfile for {pipeline_name}: {str(e)}")
        raise


# MCP Prompts
@mcp.prompt
async def analyze_pipeline_prompt_mcp(pipeline_name: str, ctx: Context, analysis_type: str = "comprehensive") -> str:
    """Generate a prompt for analyzing a specific pipeline."""
    return analyze_pipeline_prompt(pipeline_name, core_tools, monitoring_tools)


@mcp.prompt
async def failure_analysis_prompt_mcp(pipeline_name: str, build_number: int, ctx: Context) -> str:
    """Generate a prompt for analyzing a specific pipeline failure."""
    return failure_analysis_prompt(pipeline_name, build_number, jenkins_service)


@mcp.prompt
async def optimization_prompt_mcp(pipeline_name: str, ctx: Context) -> str:
    """Generate a prompt for pipeline optimization analysis."""
    return optimization_prompt(pipeline_name, core_tools, monitoring_tools)


@mcp.prompt
async def security_audit_prompt_mcp(pipeline_name: str, ctx: Context) -> str:
    """Generate a prompt for security audit analysis."""
    return security_audit_prompt(pipeline_name, jenkins_service)


if __name__ == "__main__":
    print("MCP Pipeline Awareness Server v3.0 - Modular Architecture")
    print(f"\n🌐 MCP Server Port: {MCP_SERVER_PORT} (HTTP transport)")
    print("   Set MCP_SERVER_PORT environment variable to change port")
    print("   Example: MCP_SERVER_PORT=9000 fastmcp run server.py --transport http")

    print("\n=== CORE TOOLS (9) ===")
    print("- list_pipelines: List all Jenkins pipelines")
    print("- get_pipeline_details: Get details for a specific pipeline")
    print("- get_pipeline_builds: Get recent builds for a pipeline")
    print("- analyze_pipeline_health: Analyze pipeline health and performance")
    print("- analyze_pipeline_failure: Analyze a specific pipeline failure")
    print("- ask_pipeline_question: Ask questions about pipelines")
    print("- configure_jenkins: Configure Jenkins connection")
    print("- test_connection: Test Jenkins connection")
    print("- get_server_info: Get MCP server information and port config")

    print("\n=== PIPELINE CONTROL TOOLS (4) ===")
    print("- trigger_pipeline_build: Trigger a new build (with safety confirmation)")
    print("- stop_pipeline_build: Stop a running build (with safety confirmation)")
    print("- enable_disable_pipeline: Enable/disable pipeline (with safety confirmation)")
    print("- get_pipeline_config: Get pipeline configuration")

    print("\n=== MONITORING & ANALYTICS TOOLS (4) ===")
    print("- get_pipeline_metrics: Get detailed pipeline metrics")
    print("- get_pipeline_dependencies: Get upstream/downstream dependencies")
    print("- monitor_pipeline_queue: Monitor Jenkins build queue")
    print("- analyze_build_trends: Analyze trends across multiple pipelines")

    print("\n=== AI INTELLIGENCE TOOLS (2) ===")
    print("- predict_pipeline_failure: AI prediction of failure risk")
    print("- suggest_pipeline_optimization: AI optimization suggestions")

    print("\n=== SECURITY TOOLS (1) ===")
    print("- scan_pipeline_security: Security vulnerability scan")

    print("\n=== JENKINSFILE TOOLS (3) ===")
    print("- get_jenkinsfile: Get Jenkinsfile (auto-reconstructs if needed)")
    print("- reconstruct_jenkinsfile: Reconstruct Jenkinsfile from execution data")
    print("- suggest_pipeline_improvements: Get improvement suggestions for pipeline")

    print("\n=== ADVANCED ANALYTICS & REPORTING TOOLS (2) ===")
    print("- generate_pipeline_report: Generate comprehensive pipeline report")
    print("- compare_pipeline_performance: Compare performance across pipelines")

    print("\n=== ADVANCED SECURITY & COMPLIANCE TOOLS (1) ===")
    print("- audit_access_controls: Audit pipeline access controls")

    print("\n=== ADVANCED AI FEATURES (3) ===")
    print("- detect_pipeline_anomalies: Detect unusual patterns in pipeline behavior")
    print("- intelligent_retry_logic: Suggest intelligent retry logic")
    print("- generate_ai_insights: Generate comprehensive AI-powered insights")

    print("\n=== PERFORMANCE OPTIMIZATION TOOLS (1) ===")
    print("- analyze_build_time_optimization: Analyze and suggest build time optimizations")

    print("\n=== MCP RESOURCES (5) ===")
    print("- pipeline://status: Get overall system status")
    print("- pipeline://{name}/summary: Get pipeline summary")
    print("- pipeline://dashboard: Get comprehensive dashboard")
    print("- pipeline://{name}/logs/{build_number}: Get build logs")
    print("- pipeline://health: Get overall health status")

    print("\n=== MCP PROMPTS (4) ===")
    print("- analyze_pipeline_prompt: Generate analysis prompts")
    print("- failure_analysis_prompt: Generate failure analysis prompts")
    print("- optimization_prompt: Generate optimization prompts")
    print("- security_audit_prompt: Generate security audit prompts")

    print("\n=== TOTAL: 30 TOOLS, 5 RESOURCES, 4 PROMPTS ===")
    print("\n🚀 Run with:")
    print("   fastmcp run server.py --transport stdio")
    print(f"   fastmcp run server.py --transport http --port {MCP_SERVER_PORT}")
    print("   MCP_SERVER_PORT=9000 fastmcp run server.py --transport http")
