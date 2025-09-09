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
