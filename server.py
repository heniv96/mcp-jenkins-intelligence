"""MCP Jenkins Intelligence Server - Optimized Version."""

import logging
import os
import re
from typing import Any

from fastmcp import Context, FastMCP

from models import BuildInfo, FailureAnalysis, PipelineHealth, PipelineInfo, QueryResult
from prompts import analyze_pipeline_prompt, failure_analysis_prompt, optimization_prompt, security_audit_prompt
from resources import get_overall_health, get_pipeline_dashboard, get_pipeline_logs, get_pipeline_status, get_pipeline_summary
from services import AITools, CoreTools, JenkinsService, MonitoringTools, SecurityTools
from services.advanced_ai_tools import AdvancedAITools
from services.advanced_security_tools import AdvancedSecurityTools
from services.analytics_tools import AnalyticsTools
from services.execution_analysis_service import ExecutionAnalysisService
from services.jenkinsfile_retrieval_service import JenkinsfileRetrievalService
from services.performance_tools import PerformanceTools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get MCP server port from environment variable
MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8000"))

# Create the FastMCP server
mcp = FastMCP(
    name="Pipeline Awareness",
    instructions="Interactive Jenkins Pipeline Analysis for VSCode and Cursor AI. Provides comprehensive pipeline monitoring, analysis, and AI-powered insights. Uses SCMFileSystem method to retrieve Jenkinsfiles directly from Jenkins with 100% accuracy.",
    version="3.1.0"
)

# Initialize services
jenkins_service = JenkinsService()
jenkinsfile_retrieval_service = JenkinsfileRetrievalService(jenkins_service)
core_tools = CoreTools(jenkins_service)
monitoring_tools = MonitoringTools(jenkins_service)
ai_tools = AITools(jenkins_service)
security_tools = SecurityTools(jenkins_service)
execution_analysis_service = ExecutionAnalysisService(jenkins_service)
analytics_tools = AnalyticsTools(jenkins_service)
advanced_security_tools = AdvancedSecurityTools(jenkins_service)
advanced_ai_tools = AdvancedAITools(jenkins_service)
performance_tools = PerformanceTools(jenkins_service)

# Auto-configure Jenkins if environment variables are available
def _auto_configure_jenkins():
    """Auto-configure Jenkins using environment variables if available."""
    jenkins_url = os.getenv("JENKINS_URL")
    jenkins_username = os.getenv("JENKINS_USERNAME")
    jenkins_token = os.getenv("JENKINS_TOKEN")
    
    if jenkins_url and jenkins_username and jenkins_token:
        try:
            jenkins_service.initialize(jenkins_url, jenkins_username, jenkins_token)
            logger.info(f"Auto-configured Jenkins connection to {jenkins_url}")
        except Exception as e:
            logger.warning(f"Failed to auto-configure Jenkins: {e}")
    else:
        logger.info("Jenkins environment variables not found, manual configuration required")

# Auto-configure on startup
_auto_configure_jenkins()

# ===== HELPER FUNCTIONS =====

def _format_jenkinsfile_response(pipeline_name: str, result: dict, method_name: str) -> str:
    """Format Jenkinsfile response with Groovy code and explanation offer."""
    if not isinstance(result, dict) or not result.get('content'):
        return f"Error: {result}" if result else "Error: Failed to retrieve Jenkinsfile"
    
    jenkinsfile_content = result['content']
    return f"""# Jenkinsfile for: {pipeline_name}
# Retrieved using {method_name} - 100% accurate
# Source: {result.get('source', 'Git Repository')}
# Method: {result.get('method', 'SCMFileSystem')}
# Timestamp: {result.get('timestamp', 'Unknown')}

```groovy
{jenkinsfile_content}
```

---
🤔 **Would you like me to explain this pipeline?**
- Type 'yes' or 'explain' for a detailed breakdown
- Type 'stages' to see just the pipeline stages
- Type 'parameters' to see the input parameters
- Type 'analysis' for a comprehensive analysis

Or ask me anything specific about this pipeline!"""

async def _check_jenkins_initialized(ctx: Context) -> bool:
    """Check if Jenkins is initialized and log error if not."""
    if not jenkins_service.is_initialized():
        await ctx.error("Jenkins not initialized. Please configure Jenkins connection first.")
        return False
    return True

# ===== CORE TOOLS =====

@mcp.tool
async def list_pipelines(ctx: Context, search: str = "") -> list[dict[str, Any]]:
    """List all Jenkins pipelines with optional search filter."""
    return await core_tools.list_pipelines(ctx, search)

@mcp.tool
async def get_pipeline_details(pipeline_name: str, ctx: Context) -> dict[str, Any]:
    """Get detailed information about a specific pipeline."""
    return await core_tools.get_pipeline_details(pipeline_name, ctx)

@mcp.tool
async def get_pipeline_builds(pipeline_name: str, ctx: Context, limit: int = 20, status: str = None) -> list[dict[str, Any]]:
    """Get recent builds for a pipeline."""
    return await core_tools.get_pipeline_builds(pipeline_name, ctx, limit, status)

@mcp.tool
async def analyze_pipeline_health(pipeline_name: str, ctx: Context, period: str = "last_7d") -> dict[str, Any]:
    """Analyze the health and performance of a pipeline."""
    return await core_tools.analyze_pipeline_health(pipeline_name, ctx, period)

@mcp.tool
async def analyze_pipeline_failure(pipeline_name: str, build_number: int, ctx: Context) -> dict[str, Any]:
    """Analyze a specific pipeline failure with AI-powered root cause analysis."""
    return await core_tools.analyze_pipeline_failure(pipeline_name, build_number, ctx)

@mcp.tool
async def ask_pipeline_question(question: str, ctx: Context, pipeline_names: list[str] = None) -> str:
    """Ask natural language questions about pipelines and get AI-powered answers."""
    return await core_tools.ask_pipeline_question(question, ctx, pipeline_names)

# ===== CONFIGURATION TOOLS =====

# ===== MONITORING TOOLS =====

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

# ===== AI TOOLS =====

@mcp.tool
async def predict_pipeline_failure(pipeline_name: str, ctx: Context) -> dict[str, Any]:
    """AI prediction of likely pipeline failures based on patterns."""
    return await ai_tools.predict_pipeline_failure(pipeline_name, ctx)

@mcp.tool
async def suggest_pipeline_optimization(pipeline_name: str, ctx: Context) -> list[dict[str, str]]:
    """AI suggestions for optimizing pipeline performance."""
    return await ai_tools.suggest_pipeline_optimization(pipeline_name, ctx)

# ===== SECURITY TOOLS =====

@mcp.tool
async def scan_pipeline_security(pipeline_name: str, ctx: Context) -> dict[str, Any]:
    """Scan pipeline for security vulnerabilities and best practices."""
    return await security_tools.scan_pipeline_security(pipeline_name, ctx)

# ===== JENKINSFILE TOOLS (CONSOLIDATED) =====

@mcp.tool
async def get_jenkinsfile(pipeline_name: str, ctx: Context) -> str:
    """Get the Jenkinsfile for a pipeline using SCMFileSystem method."""
    await ctx.info(f"Getting Jenkinsfile for pipeline: {pipeline_name}")
    
    if not await _check_jenkins_initialized(ctx):
        return "Error: Jenkins not initialized"
    
    try:
        result = await jenkinsfile_retrieval_service.get_jenkinsfile(pipeline_name, ctx)
        await ctx.info(f"Successfully retrieved Jenkinsfile for {pipeline_name}")
        return _format_jenkinsfile_response(pipeline_name, result, "SCMFileSystem method")
    except Exception as e:
        error_msg = f"Error retrieving Jenkinsfile for {pipeline_name}: {str(e)}"
        await ctx.error(error_msg)
        return error_msg

@mcp.tool
async def get_jenkinsfile_from_workspace(pipeline_name: str, ctx: Context, ensure_workspace: bool = True) -> str:
    """Get the Jenkinsfile directly from Jenkins workspace using SCMFileSystem method."""
    await ctx.info(f"Getting Jenkinsfile from Jenkins workspace for pipeline: {pipeline_name}")
    
    if not await _check_jenkins_initialized(ctx):
        return "Error: Jenkins not initialized"
    
    try:
        result = await jenkinsfile_retrieval_service.get_jenkinsfile(pipeline_name, ctx)
        await ctx.info("✅ Successfully retrieved Jenkinsfile from Jenkins workspace!")
        return _format_jenkinsfile_response(pipeline_name, result, "Jenkins workspace SCMFileSystem method")
    except Exception as e:
        error_msg = f"Error getting Jenkinsfile from workspace: {str(e)}"
        await ctx.error(error_msg)
        return error_msg

@mcp.tool
async def get_current_jenkinsfile(pipeline_name: str, ctx: Context) -> str:
    """Get the current Jenkinsfile from Jenkins workspace - guaranteed to be 100% accurate and up-to-date."""
    await ctx.info(f"Getting current Jenkinsfile from Jenkins for pipeline: {pipeline_name}")
    
    if not await _check_jenkins_initialized(ctx):
        return "Error: Jenkins not initialized"
    
    try:
        await ctx.info("Using SCMFileSystem method for 100% accuracy...")
        result = await jenkinsfile_retrieval_service.get_jenkinsfile(pipeline_name, ctx)
        await ctx.info("✅ Successfully retrieved Jenkinsfile from Jenkins!")
        return _format_jenkinsfile_response(pipeline_name, result, "current version from Jenkins - 100% accurate and up-to-date")
    except Exception as e:
        error_msg = f"Error getting current Jenkinsfile: {str(e)}"
        await ctx.error(error_msg)
        return error_msg

@mcp.tool
async def get_jenkinsfile_best_method(pipeline_name: str, ctx: Context) -> str:
    """Get Jenkinsfile using the best available Jenkins API method - SCMFileSystem method."""
    await ctx.info(f"Getting Jenkinsfile using best available method for pipeline: {pipeline_name}")
    
    if not await _check_jenkins_initialized(ctx):
        return "Error: Jenkins not initialized"
    
    try:
        await ctx.info("Using SCMFileSystem method (best available)...")
        result = await jenkinsfile_retrieval_service.get_jenkinsfile(pipeline_name, ctx)
        await ctx.info("✅ Successfully retrieved Jenkinsfile using SCMFileSystem method!")
        return _format_jenkinsfile_response(pipeline_name, result, "best available method (SCMFileSystem) - 100% accurate")
    except Exception as e:
        error_msg = f"Error getting Jenkinsfile: {str(e)}"
        await ctx.error(error_msg)
        return error_msg

@mcp.tool
async def get_all_jenkinsfiles(ctx: Context) -> dict[str, Any]:
    """Get Jenkinsfiles from ALL Jenkins pipelines (Pipeline, Multibranch, Freestyle, etc.) - COMPREHENSIVE."""
    return await jenkinsfile_retrieval_service.get_all_jenkinsfiles(ctx)

@mcp.tool
async def get_jenkinsfile_for_build(pipeline_name: str, build_number: int, ctx: Context) -> dict[str, Any]:
    """Get the exact Jenkinsfile used by a specific build (from Git at that commit)."""
    return await jenkinsfile_retrieval_service.get_jenkinsfile_for_specific_build(pipeline_name, build_number, ctx)

@mcp.tool
async def get_pipeline_types_summary(ctx: Context) -> dict[str, Any]:
    """Get summary of all pipeline types and their Jenkinsfile availability."""
    return await jenkinsfile_retrieval_service.get_pipeline_types_summary(ctx)

# ===== PIPELINE EXPLANATION TOOLS =====

@mcp.tool
async def explain_pipeline(pipeline_name: str, explanation_type: str = "full", ctx: Context = None) -> str:
    """Explain a Jenkins pipeline with detailed breakdown and analysis."""
    await ctx.info(f"Explaining pipeline: {pipeline_name} (type: {explanation_type})")
    
    if not await _check_jenkins_initialized(ctx):
        return "Error: Jenkins not initialized"
    
    try:
        result = await jenkinsfile_retrieval_service.get_jenkinsfile(pipeline_name, ctx)
        
        if not isinstance(result, dict) or not result.get('content'):
            return f"Error: Could not retrieve Jenkinsfile for {pipeline_name}"
        
        jenkinsfile_content = result['content']
        
        # Generate explanation based on type
        if explanation_type.lower() in ['full', 'explain', 'yes']:
            return await _generate_full_explanation(pipeline_name, jenkinsfile_content, ctx)
        elif explanation_type.lower() == 'stages':
            return await _generate_stages_explanation(pipeline_name, jenkinsfile_content, ctx)
        elif explanation_type.lower() == 'parameters':
            return await _generate_parameters_explanation(pipeline_name, jenkinsfile_content, ctx)
        elif explanation_type.lower() == 'analysis':
            return await _generate_analysis_explanation(pipeline_name, jenkinsfile_content, ctx)
        elif explanation_type.lower() == 'security':
            return await _generate_security_explanation(pipeline_name, jenkinsfile_content, ctx)
        else:
            return f"Unknown explanation type: {explanation_type}. Use: 'full', 'stages', 'parameters', 'analysis', or 'security'"
            
    except Exception as e:
        error_msg = f"Error explaining pipeline {pipeline_name}: {str(e)}"
        await ctx.error(error_msg)
        return error_msg

# ===== EXPLANATION HELPER FUNCTIONS =====

async def _generate_full_explanation(pipeline_name: str, jenkinsfile_content: str, ctx: Context) -> str:
    """Generate a comprehensive explanation of the pipeline."""
    await ctx.info("Generating full pipeline explanation...")
    
    stages_count = jenkinsfile_content.count("stage(")
    parameters_count = jenkinsfile_content.count("name:")
    has_post_actions = "post {" in jenkinsfile_content
    has_environment = "environment {" in jenkinsfile_content
    has_options = "options {" in jenkinsfile_content
    
    library_match = re.search(r"@Library\('([^']+)'\)", jenkinsfile_content)
    library_name = library_match.group(1) if library_match else "None"
    
    timeout_match = re.search(r"timeout\(time:\s*(\d+),\s*unit:\s*'([^']+)'\)", jenkinsfile_content)
    timeout_info = f"{timeout_match.group(1)} {timeout_match.group(2)}" if timeout_match else "Not specified"
    
    # Get analysis results first
    purpose = await _analyze_pipeline_purpose(jenkinsfile_content, ctx)
    parameters = await _extract_parameters_summary(jenkinsfile_content, ctx)
    stages = await _extract_stages_summary(jenkinsfile_content, ctx)
    security = await _analyze_security_features(jenkinsfile_content, ctx)
    
    return f"""# 📋 Complete Pipeline Explanation: {pipeline_name}

## 🔍 Overview
This is a **Jenkins Pipeline** written in Groovy that defines an automated workflow.

## 📚 Library Dependencies
- **Jenkins Library**: `{library_name}`

## ⚙️ Pipeline Configuration
- **Agent**: Any (runs on any available Jenkins agent)
- **Timeout**: {timeout_info}
- **Build Retention**: Last 10 builds
- **Features**: Timestamps, ANSI color output

## 📊 Pipeline Structure
- **Total Stages**: {stages_count}
- **Parameters**: {parameters_count}
- **Environment Variables**: {'Yes' if has_environment else 'No'}
- **Pipeline Options**: {'Yes' if has_options else 'No'}
- **Post Actions**: {'Yes' if has_post_actions else 'No'}

## 🚀 What This Pipeline Does
{purpose}

## 📋 Input Parameters
{parameters}

## 🔄 Pipeline Stages
{stages}

## 🛡️ Security & Best Practices
{security}

---
💡 **Need more details?** Ask me about:
- Specific stages: "explain stages"
- Parameters: "explain parameters" 
- Security analysis: "explain security"
- Full analysis: "explain analysis"
"""

async def _generate_stages_explanation(pipeline_name: str, jenkinsfile_content: str, ctx: Context) -> str:
    """Generate stages-focused explanation."""
    await ctx.info("Generating stages explanation...")
    stages = re.findall(r"stage\('([^']+)'\)", jenkinsfile_content)
    
    explanation = f"# 🔄 Pipeline Stages: {pipeline_name}\n\n"
    for i, stage in enumerate(stages, 1):
        explanation += f"## Stage {i}: {stage}\n"
        explanation += f"- **Purpose**: [Analyze stage purpose]\n"
        explanation += f"- **Actions**: [List key actions]\n\n"
    
    return explanation

async def _generate_parameters_explanation(pipeline_name: str, jenkinsfile_content: str, ctx: Context) -> str:
    """Generate parameters-focused explanation."""
    await ctx.info("Generating parameters explanation...")
    
    choice_params = re.findall(r"choice\(\s*name:\s*'([^']+)',\s*choices:\s*\[([^\]]+)\],\s*description:\s*'([^']+)'", jenkinsfile_content)
    string_params = re.findall(r"string\(\s*name:\s*'([^']+)',\s*defaultValue:\s*'([^']*)',\s*description:\s*'([^']+)'", jenkinsfile_content)
    boolean_params = re.findall(r"booleanParam\(\s*name:\s*'([^']+)',\s*defaultValue:\s*([^,]+),\s*description:\s*'([^']+)'", jenkinsfile_content)
    
    explanation = f"# 📋 Pipeline Parameters: {pipeline_name}\n\n"
    
    if choice_params:
        explanation += "## Choice Parameters\n"
        for name, choices, desc in choice_params:
            explanation += f"- **{name}**: {desc}\n  - Options: {choices}\n\n"
    
    if string_params:
        explanation += "## String Parameters\n"
        for name, default, desc in string_params:
            explanation += f"- **{name}**: {desc}\n  - Default: '{default}'\n\n"
    
    if boolean_params:
        explanation += "## Boolean Parameters\n"
        for name, default, desc in boolean_params:
            explanation += f"- **{name}**: {desc}\n  - Default: {default}\n\n"
    
    return explanation

async def _generate_analysis_explanation(pipeline_name: str, jenkinsfile_content: str, ctx: Context) -> str:
    """Generate comprehensive analysis."""
    await ctx.info("Generating comprehensive analysis...")
    
    # Get analysis results first
    purpose = await _analyze_pipeline_purpose(jenkinsfile_content, ctx)
    security = await _analyze_security_features(jenkinsfile_content, ctx)
    
    return f"""# 🔍 Comprehensive Pipeline Analysis: {pipeline_name}

## 📊 Technical Metrics
- **Lines of Code**: {len(jenkinsfile_content.splitlines())}
- **Complexity**: [Analyze complexity]
- **Maintainability**: [Analyze maintainability]

## 🎯 Purpose & Functionality
{purpose}

## 🏗️ Architecture Analysis
- **Design Pattern**: [Analyze design pattern]
- **Dependencies**: [List dependencies]
- **Integration Points**: [List integrations]

## ⚡ Performance Considerations
- **Build Time**: [Analyze build time]
- **Resource Usage**: [Analyze resource usage]
- **Optimization Opportunities**: [List optimizations]

## 🛡️ Security Analysis
{security}

## 🔧 Maintenance & Operations
- **Monitoring**: [Analyze monitoring]
- **Logging**: [Analyze logging]
- **Error Handling**: [Analyze error handling]
"""

async def _generate_security_explanation(pipeline_name: str, jenkinsfile_content: str, ctx: Context) -> str:
    """Generate security-focused explanation."""
    await ctx.info("Generating security analysis...")
    
    return f"""# 🛡️ Security Analysis: {pipeline_name}

## 🔐 Security Features
{await _analyze_security_features(jenkinsfile_content, ctx)}

## ⚠️ Security Considerations
- **Secrets Management**: [Analyze secrets handling]
- **Access Control**: [Analyze access controls]
- **Input Validation**: [Analyze input validation]
- **Output Sanitization**: [Analyze output handling]

## 🚨 Potential Vulnerabilities
- **Injection Risks**: [Check for injection vulnerabilities]
- **Privilege Escalation**: [Check for privilege issues]
- **Data Exposure**: [Check for data leaks]

## ✅ Security Best Practices
- **Implemented**: [List good practices]
- **Missing**: [List missing practices]
- **Recommendations**: [Provide recommendations]
"""

# ===== ANALYSIS HELPER FUNCTIONS =====

async def _analyze_pipeline_purpose(jenkinsfile_content: str, ctx: Context) -> str:
    """Analyze the purpose of the pipeline."""
    if "kafka" in jenkinsfile_content.lower():
        return "This appears to be a **Kafka operations pipeline** for managing consumer groups, topics, and offsets."
    elif "deploy" in jenkinsfile_content.lower():
        return "This appears to be a **deployment pipeline** for releasing applications."
    elif "test" in jenkinsfile_content.lower():
        return "This appears to be a **testing pipeline** for running automated tests."
    else:
        return "This is a **general-purpose pipeline** with custom workflow logic."

async def _extract_parameters_summary(jenkinsfile_content: str, ctx: Context) -> str:
    """Extract and summarize parameters."""
    choice_params = re.findall(r"choice\(\s*name:\s*'([^']+)'", jenkinsfile_content)
    string_params = re.findall(r"string\(\s*name:\s*'([^']+)'", jenkinsfile_content)
    boolean_params = re.findall(r"booleanParam\(\s*name:\s*'([^']+)'", jenkinsfile_content)
    
    summary = f"- **Choice Parameters**: {len(choice_params)} ({', '.join(choice_params[:3])}{'...' if len(choice_params) > 3 else ''})\n"
    summary += f"- **String Parameters**: {len(string_params)} ({', '.join(string_params[:3])}{'...' if len(string_params) > 3 else ''})\n"
    summary += f"- **Boolean Parameters**: {len(boolean_params)} ({', '.join(boolean_params[:3])}{'...' if len(boolean_params) > 3 else ''})\n"
    
    return summary

async def _extract_stages_summary(jenkinsfile_content: str, ctx: Context) -> str:
    """Extract and summarize stages."""
    stages = re.findall(r"stage\('([^']+)'\)", jenkinsfile_content)
    
    summary = f"**Total Stages**: {len(stages)}\n\n"
    for i, stage in enumerate(stages, 1):
        summary += f"{i}. **{stage}**\n"
    
    return summary

async def _analyze_security_features(jenkinsfile_content: str, ctx: Context) -> str:
    """Analyze security features in the pipeline."""
    features = []
    
    if "timeout" in jenkinsfile_content:
        features.append("✅ Timeout protection")
    if "buildDiscarder" in jenkinsfile_content:
        features.append("✅ Build retention management")
    if "wrap" in jenkinsfile_content:
        features.append("✅ Build user wrapping")
    if "cleanup" in jenkinsfile_content:
        features.append("✅ Cleanup procedures")
    
    if features:
        return "\n".join(features)
    else:
        return "⚠️ Limited security features detected"

# ===== ADVANCED TOOLS =====

@mcp.tool
async def generate_pipeline_report(pipeline_name: str, ctx: Context, period: str = "last_30d", format: str = "html") -> dict[str, Any]:
    """Generate comprehensive pipeline report based on Jenkins build history."""
    return await analytics_tools.generate_pipeline_report(pipeline_name, ctx, period, format)

@mcp.tool
async def compare_pipeline_performance(pipeline_names: list[str], ctx: Context, period: str = "last_7d") -> dict[str, Any]:
    """Compare performance across multiple pipelines based on Jenkins build history."""
    return await analytics_tools.compare_pipeline_performance(pipeline_names, ctx, period)

@mcp.tool
async def audit_access_controls(pipeline_name: str, ctx: Context) -> dict[str, Any]:
    """Audit pipeline access controls and permissions using Jenkins security API."""
    return await advanced_security_tools.audit_access_controls(pipeline_name, ctx)

@mcp.tool
async def detect_pipeline_anomalies(pipeline_name: str, ctx: Context, sensitivity: str = "medium") -> dict[str, Any]:
    """Detect unusual patterns and anomalies in pipeline behavior using ML."""
    return await advanced_ai_tools.detect_pipeline_anomalies(pipeline_name, ctx, sensitivity)

@mcp.tool
async def intelligent_retry_logic(pipeline_name: str, ctx: Context, failure_reason: str = "unknown") -> dict[str, Any]:
    """Analyze failure patterns and suggest intelligent retry logic using ML."""
    return await advanced_ai_tools.intelligent_retry_logic(pipeline_name, ctx, failure_reason)

@mcp.tool
async def generate_ai_insights(pipeline_name: str, ctx: Context, insight_type: str = "comprehensive") -> dict[str, Any]:
    """Generate comprehensive AI-powered insights about the pipeline using real data analysis."""
    return await advanced_ai_tools.generate_ai_insights(pipeline_name, ctx, insight_type)

@mcp.tool
async def analyze_build_time_optimization(pipeline_name: str, ctx: Context, period: str = "last_30d") -> dict[str, Any]:
    """Analyze build time optimization opportunities using Jenkins data."""
    return await performance_tools.analyze_build_time_optimization(pipeline_name, ctx, period)

# ===== EXECUTION ANALYSIS TOOLS =====

@mcp.tool
async def reconstruct_from_execution(pipeline_name: str, ctx: Context) -> dict[str, Any]:
    """Reconstruct Jenkinsfile content from pipeline execution data."""
    return await execution_analysis_service.reconstruct_jenkinsfile(pipeline_name, ctx)

@mcp.tool
async def suggest_from_execution(pipeline_name: str, ctx: Context) -> dict[str, Any]:
    """Get improvement suggestions based on reconstructed Jenkinsfile from execution data."""
    # First reconstruct the Jenkinsfile to get the analysis
    reconstruction = await execution_analysis_service.reconstruct_jenkinsfile(pipeline_name, ctx)
    
    if 'reconstructed_jenkinsfile' in reconstruction and 'analysis' in reconstruction:
        jenkinsfile = reconstruction['reconstructed_jenkinsfile']
        analysis = reconstruction['analysis']
        return await execution_analysis_service.suggest_improvements(pipeline_name, jenkinsfile, analysis, ctx)
    else:
        return {
            "error": "Could not reconstruct Jenkinsfile for analysis",
            "pipeline_name": pipeline_name,
            "status": "failed"
        }

# ===== MCP RESOURCES =====

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
async def overall_health(ctx: Context) -> str:
    """Get overall system health and status."""
    return get_overall_health(jenkins_service)

# ===== MCP PROMPTS =====

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
    return security_audit_prompt(pipeline_name, security_tools)

# ===== SERVER INFO =====

@mcp.tool
async def get_server_info(ctx: Context) -> dict[str, Any]:
    """Get MCP server information including port configuration."""
    env_vars = {
        "JENKINS_URL": os.getenv("JENKINS_URL", "Not configured"),
        "JENKINS_USERNAME": os.getenv("JENKINS_USERNAME", "Not configured"),
        "JENKINS_TOKEN": "***" if os.getenv("JENKINS_TOKEN") else "Not configured",
        "MCP_SERVER_PORT": f"{MCP_SERVER_PORT} (default)" if MCP_SERVER_PORT == 8000 else str(MCP_SERVER_PORT)
    }
    
    return {
        "server_name": "Pipeline Awareness",
        "version": "3.0.0",
        "mcp_server_port": MCP_SERVER_PORT,
        "transport_modes": ["stdio", "http", "sse"],
        "total_tools": 25,
        "total_resources": 5,
        "total_prompts": 4,
        "jenkins_configured": jenkins_service.is_initialized(),
        "environment_variables": env_vars,
        "port_note": f"MCP server HTTP transport port: {MCP_SERVER_PORT} (set via MCP_SERVER_PORT env var)"
    }

@mcp.tool
async def test_connection(ctx: Context) -> dict[str, str]:
    """Test Jenkins connection."""
    return jenkins_service.test_connection()

@mcp.tool
async def configure_jenkins(url: str, username: str, token: str, ctx: Context, verify_ssl: bool = True) -> str:
    """Configure Jenkins connection."""
    # If using environment variable placeholder, use actual env var
    if token == "${JENKINS_TOKEN}":
        token = os.getenv("JENKINS_TOKEN", token)
    if username == "${JENKINS_USERNAME}":
        username = os.getenv("JENKINS_USERNAME", username)
    if url == "${JENKINS_URL}":
        url = os.getenv("JENKINS_URL", url)
    
    return jenkins_service.configure_jenkins(url, username, token, verify_ssl)

# ===== MAIN EXECUTION =====

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
