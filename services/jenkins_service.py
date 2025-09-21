"""Jenkins service wrapper for API operations."""

import logging
from typing import Any

import jenkins

logger = logging.getLogger(__name__)


class JenkinsService:
    """Jenkins API service wrapper."""

    def __init__(self):
        self.client: jenkins.Jenkins | None = None
        self.username: str | None = None
        self.password: str | None = None
        self.server_url: str | None = None

    def initialize(self, url: str, username: str, token: str, verify_ssl: bool = True) -> None:
        """Initialize Jenkins client."""
        try:
            self.client = jenkins.Jenkins(url, username=username, password=token)
            self.username = username
            self.password = token
            self.server_url = url
            self.client.get_whoami()
            logger.info(f"Successfully connected to Jenkins at {url}")
        except Exception as e:
            logger.error(f"Failed to initialize Jenkins: {e}")
            raise

    def is_initialized(self) -> bool:
        """Check if Jenkins client is initialized."""
        return self.client is not None

    def test_connection(self) -> dict[str, str]:
        """Test Jenkins connection."""
        try:
            if not self.is_initialized():
                return {"result": "Jenkins not initialized"}
            
            # Test connection by getting server info
            info = self.client.get_info()
            return {"result": "Jenkins connection successful"}
        except Exception as e:
            return {"result": f"Jenkins connection failed: {str(e)}"}

    def configure_jenkins(self, url: str, username: str, token: str, verify_ssl: bool = True) -> str:
        """Configure Jenkins connection."""
        try:
            self.initialize(url, username, token, verify_ssl)
            return f"Successfully configured Jenkins connection to {url}"
        except Exception as e:
            return f"Failed to configure Jenkins: {str(e)}"

    def get_jobs(self) -> list[dict[str, Any]]:
        """Get all jobs from Jenkins."""
        if not self.client:
            raise ValueError("Jenkins not initialized")
        return self.client.get_jobs()

    def get_job_info(self, job_name: str) -> dict[str, Any]:
        """Get job information."""
        if not self.client:
            raise ValueError("Jenkins not initialized")
        return self.client.get_job_info(job_name)

    def get_builds(self, job_name: str, limit: int = 20) -> list[dict[str, Any]]:
        """Get builds for a job."""
        if not self.client:
            raise ValueError("Jenkins not initialized")
        job_info = self.client.get_job_info(job_name)
        builds = job_info.get('builds', [])
        return builds[:limit]

    def get_build_info(self, job_name: str, build_number: int) -> dict[str, Any]:
        """Get build information."""
        if not self.client:
            raise ValueError("Jenkins not initialized")
        try:
            build_info = self.client.get_build_info(job_name, build_number)
            logger.debug(f"Retrieved build info for {job_name}#{build_number}: {build_info.get('result', 'UNKNOWN')}")
            return build_info
        except Exception as e:
            logger.warning(f"Failed to get build info for {job_name}#{build_number}: {e}")
            raise

    def get_build_console_output(self, job_name: str, build_number: int) -> str:
        """Get build console output."""
        if not self.client:
            raise ValueError("Jenkins not initialized")
        return self.client.get_build_console_output(job_name, build_number)

    def get_job_config(self, job_name: str) -> str:
        """Get job configuration."""
        if not self.client:
            raise ValueError("Jenkins not initialized")
        return self.client.get_job_config(job_name)

    def build_job(self, job_name: str, parameters: dict[str, Any] | None = None) -> None:
        """Build a job."""
        if not self.client:
            raise ValueError("Jenkins not initialized")
        if parameters:
            self.client.build_job(job_name, parameters)
        else:
            self.client.build_job(job_name)

    def stop_build(self, job_name: str, build_number: int) -> None:
        """Stop a build."""
        if not self.client:
            raise ValueError("Jenkins not initialized")
        self.client.stop_build(job_name, build_number)

    def enable_job(self, job_name: str) -> None:
        """Enable a job."""
        if not self.client:
            raise ValueError("Jenkins not initialized")
        self.client.enable_job(job_name)

    def disable_job(self, job_name: str) -> None:
        """Disable a job."""
        if not self.client:
            raise ValueError("Jenkins not initialized")
        self.client.disable_job(job_name)

    def get_queue_info(self) -> list[dict[str, Any]]:
        """Get queue information."""
        if not self.client:
            raise ValueError("Jenkins not initialized")
        return self.client.get_queue_info()

    def get_whoami(self) -> dict[str, Any]:
        """Get current user information."""
        if not self.client:
            raise ValueError("Jenkins not initialized")
        return self.client.get_whoami()

    def get_system_info(self) -> dict[str, Any]:
        """Get Jenkins system information."""
        if not self.client:
            raise ValueError("Jenkins not initialized")
        try:
            return self.client.get_system_info()
        except Exception:
            # Fallback if get_system_info is not available
            return {
                "version": "Unknown",
                "mode": "Unknown",
                "url": self.client.server if hasattr(self.client, 'server') else "Unknown"
            }

    def get_build_status(self, job_name: str, build_number: int) -> str:
        """Get build status efficiently."""
        if not self.client:
            raise ValueError("Jenkins not initialized")
        try:
            build_info = self.client.get_build_info(job_name, build_number)
            result = build_info.get("result")
            
            # Handle different status representations
            if result is None or result == "null":
                if build_info.get("building", False):
                    return "RUNNING"
                else:
                    return "UNKNOWN"
            
            return result
        except Exception as e:
            logger.warning(f"Failed to get build status for {job_name}#{build_number}: {e}")
            return "UNKNOWN"

    def execute_groovy_script(self, script: str) -> str:
        """Execute a Groovy script in Jenkins Script Console."""
        if not self.client:
            raise ValueError("Jenkins not initialized")
        try:
            result = self.client.run_script(script)
            return result
        except Exception as e:
            logger.error(f"Failed to execute Groovy script: {e}")
            raise

    def get_workspace_file(self, job_name: str, file_path: str, ensure_workspace: bool = True) -> str:
        """Get file content from Jenkins workspace using multiple REST API methods."""
        if not self.client:
            raise ValueError("Jenkins not initialized")
        
        try:
            import requests
            import time
            
            # Use Jenkins credentials for authentication
            auth = (self.username, self.password)
            
            # Method 1: Try workspace file directly
            workspace_url = f"{self.server_url}/job/{job_name}/ws/{file_path}"
            response = requests.get(workspace_url, auth=auth, timeout=30)
            
            if response.status_code == 200:
                logger.info("Successfully retrieved file from workspace")
                return response.text
            
            # Method 2: Try last successful build artifacts
            logger.info("Workspace not available, trying last successful build artifacts...")
            artifact_url = f"{self.server_url}/job/{job_name}/lastSuccessfulBuild/artifact/{file_path}"
            response = requests.get(artifact_url, auth=auth, timeout=30)
            
            if response.status_code == 200:
                logger.info("Successfully retrieved file from last successful build artifacts")
                return response.text
            
            # Method 3: Try last build artifacts
            logger.info("Last successful build not available, trying last build artifacts...")
            artifact_url = f"{self.server_url}/job/{job_name}/lastBuild/artifact/{file_path}"
            response = requests.get(artifact_url, auth=auth, timeout=30)
            
            if response.status_code == 200:
                logger.info("Successfully retrieved file from last build artifacts")
                return response.text
            
            # Method 4: Try to trigger build and wait
            if ensure_workspace:
                logger.info(f"All artifact methods failed, attempting to trigger build for {job_name}")
                try:
                    # Try to trigger a build to create workspace
                    self.build_job(job_name)
                    # Wait for the build to start and create workspace
                    time.sleep(10)
                    # Try workspace again
                    response = requests.get(workspace_url, auth=auth, timeout=30)
                    if response.status_code == 200:
                        logger.info("Successfully retrieved file after triggering build")
                        return response.text
                except Exception as e:
                    logger.warning(f"Failed to trigger build: {e}")
            
            # Method 5: Fallback to Groovy script
            logger.warning("All REST API methods failed, trying Groovy script fallback")
            return self._get_workspace_file_groovy(job_name, file_path)
                
        except Exception as e:
            logger.warning(f"All methods failed: {e}, trying Groovy script")
            return self._get_workspace_file_groovy(job_name, file_path)
    
    def _get_workspace_file_groovy(self, job_name: str, file_path: str) -> str:
        """Fallback method using Groovy script to get workspace file."""
        groovy_script = f"""
        def jobName = '{job_name}'
        def job = Jenkins.instance.getItemByFullName(jobName)
        
        if (job) {{
            // Try multiple methods to get workspace
            def workspacePath = null
            
            // Method 1: Try job.getWorkspace()
            try {{
                def workspace = job.getWorkspace()
                if (workspace) {{
                    workspacePath = workspace.getRemote()
                }}
            }} catch (Exception e) {{
                // Method 2: Try getting from last build
                def lastBuild = job.getLastBuild()
                if (lastBuild) {{
                    try {{
                        def workspace = lastBuild.getWorkspace()
                        if (workspace) {{
                            workspacePath = workspace.getRemote()
                        }}
                    }} catch (Exception e2) {{
                        // Method 3: Try to get workspace path from job directory
                        def jobDir = job.getRootDir()
                        workspacePath = jobDir.getAbsolutePath() + "/workspace"
                    }}
                }}
            }}
            
            if (workspacePath) {{
                def filePath = new File(workspacePath, '{file_path}')
                
                if (filePath.exists()) {{
                    return filePath.text
                }} else {{
                    return "File not found: {file_path} in workspace: " + workspacePath
                }}
            }} else {{
                return "Workspace not found for job: {job_name}. This might be because the job has never been built or the workspace is not accessible."
            }}
        }} else {{
            return "Job not found: {job_name}"
        }}
        """
        
        try:
            result = self.execute_groovy_script(groovy_script)
            return result
        except Exception as e:
            logger.error(f"Failed to get workspace file {file_path} for job {job_name}: {e}")
            raise

