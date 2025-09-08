"""MCP Prompts for pipeline analysis."""

from services.jenkins_service import JenkinsService
from utils import parse_timestamp


def analyze_pipeline_prompt(pipeline_name: str, core_tools, monitoring_tools) -> str:
    """Generate a prompt for analyzing a specific pipeline."""
    try:
        pipeline = core_tools.get_pipeline_details(pipeline_name, None)
        builds = core_tools.get_pipeline_builds(pipeline_name, None, limit=20)

        prompt = f"""
Analyze the Jenkins pipeline '{pipeline_name}' comprehensively:

Pipeline Details:
- Name: {pipeline.name}
- Display Name: {pipeline.display_name}
- URL: {pipeline.url}
- Description: {pipeline.description}
- Enabled: {pipeline.is_enabled}
- Health Score: {pipeline.health_score}

Recent Builds ({len(builds)} builds):
{chr(10).join([f"- Build #{b.number}: {b.status} ({b.timestamp.strftime('%Y-%m-%d %H:%M') if b.timestamp else 'Unknown time'})" for b in builds[:10]])}

Please provide:
1. Overall health assessment
2. Performance analysis
3. Failure patterns
4. Recommendations for improvement
5. Security considerations
6. Best practices compliance
"""

        return prompt

    except Exception as e:
        return f"Error generating analysis prompt: {str(e)}"


def failure_analysis_prompt(pipeline_name: str, build_number: int, jenkins_service: JenkinsService) -> str:
    """Generate a prompt for analyzing a specific pipeline failure."""
    try:
        build_info = jenkins_service.get_build_info(pipeline_name, build_number)
        console_output = jenkins_service.get_build_console_output(pipeline_name, build_number)

        prompt = f"""
Analyze the failure of Jenkins pipeline '{pipeline_name}' build #{build_number}:

Build Information:
- Status: {build_info.get('result', 'UNKNOWN')}
- Duration: {build_info.get('duration', 'Unknown')}ms
- Timestamp: {parse_timestamp(build_info.get('timestamp'))}
- URL: {build_info.get('url', 'Unknown')}

Console Output (last 50 lines):
{console_output.split(chr(10))[-50:] if console_output else 'No console output available'}

Please provide:
1. Root cause analysis
2. Error classification
3. Immediate fixes
4. Long-term improvements
5. Prevention strategies
"""

        return prompt

    except Exception as e:
        return f"Error generating failure analysis prompt: {str(e)}"


def optimization_prompt(pipeline_name: str, core_tools, monitoring_tools) -> str:
    """Generate a prompt for pipeline optimization analysis."""
    try:
        pipeline = core_tools.get_pipeline_details(pipeline_name, None)
        metrics = monitoring_tools.get_pipeline_metrics(pipeline_name, None, "last_7d")

        prompt = f"""
Analyze the Jenkins pipeline '{pipeline_name}' for optimization opportunities:

Pipeline Information:
- Name: {pipeline.name}
- Health Score: {pipeline.health_score}
- Enabled: {pipeline.is_enabled}

Performance Metrics (Last 7 Days):
- Success Rate: {metrics.get('success_rate', 0)}%
- Average Duration: {metrics.get('avg_duration_seconds', 0)} seconds
- Builds per Day: {metrics.get('builds_per_day', 0)}
- Total Builds: {metrics.get('total_builds', 0)}

Please provide:
1. Performance bottlenecks identification
2. Resource utilization analysis
3. Build frequency optimization
4. Error handling improvements
5. Security enhancements
6. Best practices recommendations
7. Specific actionable steps
"""

        return prompt

    except Exception as e:
        return f"Error generating optimization prompt: {str(e)}"


def security_audit_prompt(pipeline_name: str, jenkins_service: JenkinsService) -> str:
    """Generate a prompt for security audit analysis."""
    try:
        config = jenkins_service.get_job_config(pipeline_name)

        prompt = f"""
Perform a comprehensive security audit of Jenkins pipeline '{pipeline_name}':

Pipeline Configuration (excerpt):
{config[:1000]}...

Security Analysis Areas:
1. Credential Management
   - Hardcoded secrets detection
   - Credential storage practices
   - Access control mechanisms

2. Network Security
   - HTTPS/TLS usage
   - Insecure connections
   - External service communications

3. Code Security
   - Script injection vulnerabilities
   - Input validation
   - Error handling security

4. Access Control
   - User permissions
   - Role-based access
   - Authentication mechanisms

5. Compliance
   - Security standards adherence
   - Audit logging
   - Data protection

Please provide:
- Security vulnerabilities found
- Risk assessment (High/Medium/Low)
- Specific remediation steps
- Compliance recommendations
- Security best practices
"""

        return prompt

    except Exception as e:
        return f"Error generating security audit prompt: {str(e)}"
