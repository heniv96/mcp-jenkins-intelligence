"""Advanced Security & Compliance Tools for Jenkins Pipeline Intelligence."""

import hashlib
import logging
import re
from datetime import datetime
from typing import Any

from fastmcp import Context

logger = logging.getLogger(__name__)


class AdvancedSecurityTools:
    """Advanced security and compliance tools for Jenkins pipelines."""

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

    async def audit_access_controls(
        self,
        pipeline_name: str,
        ctx: Context
    ) -> dict[str, Any]:
        """Audit pipeline access controls and permissions using Jenkins security API (no LDAP/AD integration)."""
        await ctx.info(f"Auditing access controls for {pipeline_name} - Using Jenkins security API")

        try:
            # Get pipeline configuration
            config = self.jenkins.get_job_config(pipeline_name)

            # Get Jenkins system information for security context
            self.jenkins.get_system_info()

            # Analyze pipeline permissions
            permission_analysis = {
                "pipeline_name": pipeline_name,
                "audit_timestamp": datetime.now().isoformat(),
                "data_source": "Jenkins security API (no external LDAP/AD integration)",
                "permissions": {},
                "security_issues": [],
                "recommendations": []
            }

            # Check for explicit permissions in pipeline config
            if "properties" in config:
                properties = config["properties"]

                # Check for authorization matrix
                if "hudson.security.AuthorizationMatrixProperty" in str(properties):
                    permission_analysis["permissions"]["authorization_matrix"] = "configured"
                else:
                    permission_analysis["permissions"]["authorization_matrix"] = "not_configured"
                    permission_analysis["security_issues"].append({
                        "severity": "medium",
                        "issue": "No authorization matrix configured",
                        "description": "Pipeline does not have explicit permission controls"
                    })

                # Check for build permissions
                if "hudson.model.BuildAuthorizationToken" in str(properties):
                    permission_analysis["permissions"]["build_token"] = "configured"
                else:
                    permission_analysis["permissions"]["build_token"] = "not_configured"
                    permission_analysis["security_issues"].append({
                        "severity": "low",
                        "issue": "No build authorization token",
                        "description": "Pipeline can be triggered without authentication"
                    })

            # Check for SCM permissions
            if "scm" in config:
                scm_config = config["scm"]
                if "userRemoteConfigs" in scm_config:
                    permission_analysis["permissions"]["scm_access"] = "configured"
                else:
                    permission_analysis["permissions"]["scm_access"] = "not_configured"
                    permission_analysis["security_issues"].append({
                        "severity": "high",
                        "issue": "SCM access not properly configured",
                        "description": "Pipeline may have insecure SCM access"
                    })

            # Check for credential usage
            if "credentials" in config or "credentialsId" in config:
                permission_analysis["permissions"]["credentials"] = "configured"
            else:
                permission_analysis["permissions"]["credentials"] = "not_configured"
                permission_analysis["security_issues"].append({
                    "severity": "medium",
                    "issue": "No credential management configured",
                    "description": "Pipeline may use hardcoded credentials"
                })

            # Check for parameter security
            if "parametersDefinitionProperty" in config:
                params = config["parametersDefinitionProperty"]
                if "passwordParameterDefinition" in str(params):
                    permission_analysis["permissions"]["password_params"] = "configured"
                    permission_analysis["security_issues"].append({
                        "severity": "high",
                        "issue": "Password parameters detected",
                        "description": "Password parameters may be logged in build history"
                    })
                else:
                    permission_analysis["permissions"]["password_params"] = "not_configured"

            # Check for build triggers security
            if "triggers" in config:
                triggers = config["triggers"]
                if "hudson.triggers.SCMTrigger" in str(triggers):
                    permission_analysis["permissions"]["scm_trigger"] = "configured"
                    permission_analysis["security_issues"].append({
                        "severity": "medium",
                        "issue": "SCM trigger configured",
                        "description": "Pipeline triggers on SCM changes - ensure proper access controls"
                    })
                else:
                    permission_analysis["permissions"]["scm_trigger"] = "not_configured"

            # Check for build environment security
            if "buildEnvironment" in config:
                env_config = config["buildEnvironment"]
                if "maskPasswords" in env_config and env_config["maskPasswords"]:
                    permission_analysis["permissions"]["password_masking"] = "enabled"
                else:
                    permission_analysis["permissions"]["password_masking"] = "disabled"
                    permission_analysis["security_issues"].append({
                        "severity": "high",
                        "issue": "Password masking not enabled",
                        "description": "Passwords may be visible in build logs"
                    })

            # Generate security recommendations
            if permission_analysis["security_issues"]:
                high_severity = [issue for issue in permission_analysis["security_issues"] if issue["severity"] == "high"]
                medium_severity = [issue for issue in permission_analysis["security_issues"] if issue["severity"] == "medium"]
                low_severity = [issue for issue in permission_analysis["security_issues"] if issue["severity"] == "low"]

                if high_severity:
                    permission_analysis["recommendations"].append("URGENT: Address high-severity security issues immediately")
                if medium_severity:
                    permission_analysis["recommendations"].append("Review and address medium-severity security issues")
                if low_severity:
                    permission_analysis["recommendations"].append("Consider addressing low-severity security issues")

                permission_analysis["recommendations"].extend([
                    "Enable authorization matrix for fine-grained access control",
                    "Configure build authorization tokens for secure triggering",
                    "Enable password masking in build environment",
                    "Review and audit credential usage",
                    "Implement proper SCM access controls"
                ])
            else:
                permission_analysis["recommendations"].append("Pipeline access controls appear to be properly configured")

            # Calculate security score
            total_checks = 6  # Number of security checks performed
            passed_checks = sum(1 for perm in permission_analysis["permissions"].values() if perm == "configured" or perm == "enabled")
            security_score = (passed_checks / total_checks) * 100

            permission_analysis["security_score"] = round(security_score, 2)
            permission_analysis["total_issues"] = len(permission_analysis["security_issues"])

            await ctx.info(f"✅ Access control audit completed - Security score: {security_score:.1f}%")

            # Protect sensitive data before returning to AI
            protected_analysis = self._protect_sensitive_data_in_dict(permission_analysis)
            return protected_analysis

        except Exception as e:
            await ctx.error(f"Error auditing access controls: {str(e)}")
            raise
