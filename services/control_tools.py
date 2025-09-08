"""Pipeline control tools with safety confirmations."""

from typing import Any

from fastmcp import Context

from services.jenkins_service import JenkinsService


class ControlTools:
    """Pipeline control tools with safety confirmations."""

    def __init__(self, jenkins_service: JenkinsService):
        self.jenkins = jenkins_service

    async def trigger_pipeline_build(self, pipeline_name: str, ctx: Context, parameters: dict[str, Any] = None, confirm: bool = False) -> str:
        """Trigger a new build for a pipeline with optional parameters."""
        if not confirm:
            param_info = f" with parameters: {parameters}" if parameters else ""
            return f"⚠️  SAFETY CHECK REQUIRED ⚠️\n\nYou are about to trigger a new build for pipeline '{pipeline_name}'{param_info}.\n\nThis will:\n- Start a new build immediately\n- Consume Jenkins resources\n- May trigger downstream pipelines\n- Could affect production systems\n\nTo proceed, call this tool again with confirm=True"

        await ctx.info(f"Triggering build for pipeline: {pipeline_name}")

        if not self.jenkins.is_initialized():
            await ctx.error("Jenkins not initialized. Please configure Jenkins connection first.")
            raise ValueError("Jenkins not initialized. Please configure Jenkins connection first.")

        try:
            await ctx.info("Starting pipeline build...")
            if parameters:
                self.jenkins.build_job(pipeline_name, parameters)
                await ctx.info(f"Build triggered with parameters: {parameters}")
            else:
                self.jenkins.build_job(pipeline_name)
                await ctx.info("Build triggered without parameters")

            return f"✅ Successfully triggered build for pipeline '{pipeline_name}'"

        except Exception as e:
            await ctx.error(f"Error triggering build for {pipeline_name}: {str(e)}")
            raise

    async def stop_pipeline_build(self, pipeline_name: str, build_number: int, ctx: Context, confirm: bool = False) -> str:
        """Stop a running pipeline build."""
        if not confirm:
            return f"⚠️  SAFETY CHECK REQUIRED ⚠️\n\nYou are about to STOP build #{build_number} of pipeline '{pipeline_name}'.\n\nThis will:\n- Immediately halt the running build\n- Mark the build as ABORTED\n- Stop any running processes\n- May leave systems in inconsistent state\n\nTo proceed, call this tool again with confirm=True"

        await ctx.info(f"Stopping build #{build_number} for pipeline: {pipeline_name}")

        if not self.jenkins.is_initialized():
            await ctx.error("Jenkins not initialized. Please configure Jenkins connection first.")
            raise ValueError("Jenkins not initialized. Please configure Jenkins connection first.")

        try:
            await ctx.info("Stopping pipeline build...")
            self.jenkins.stop_build(pipeline_name, build_number)
            await ctx.info(f"Build #{build_number} stopped successfully")

            return f"✅ Successfully stopped build #{build_number} for pipeline '{pipeline_name}'"

        except Exception as e:
            await ctx.error(f"Error stopping build {build_number} for {pipeline_name}: {str(e)}")
            raise

    async def enable_disable_pipeline(self, pipeline_name: str, enabled: bool, ctx: Context, confirm: bool = False) -> str:
        """Enable or disable a pipeline."""
        action = "enable" if enabled else "disable"

        if not confirm:
            return f"⚠️  SAFETY CHECK REQUIRED ⚠️\n\nYou are about to {action.upper()} pipeline '{pipeline_name}'.\n\nThis will:\n- {'Allow' if enabled else 'Prevent'} new builds from starting\n- {'Resume' if enabled else 'Stop'} scheduled builds\n- {'Enable' if enabled else 'Disable'} webhook triggers\n- {'Allow' if enabled else 'Block'} manual triggers\n\nTo proceed, call this tool again with confirm=True"

        await ctx.info(f"{action.capitalize()}ing pipeline: {pipeline_name}")

        if not self.jenkins.is_initialized():
            await ctx.error("Jenkins not initialized. Please configure Jenkins connection first.")
            raise ValueError("Jenkins not initialized. Please configure Jenkins connection first.")

        try:
            await ctx.info(f"{action.capitalize()}ing pipeline...")
            self.jenkins.disable_job(pipeline_name) if not enabled else self.jenkins.enable_job(pipeline_name)
            await ctx.info(f"Pipeline {action}d successfully")

            return f"✅ Successfully {action}d pipeline '{pipeline_name}'"

        except Exception as e:
            await ctx.error(f"Error {action}ing pipeline {pipeline_name}: {str(e)}")
            raise

    async def get_pipeline_config(self, pipeline_name: str, ctx: Context) -> str:
        """Get the configuration (Jenkinsfile/XML) of a pipeline."""
        await ctx.info(f"Getting configuration for pipeline: {pipeline_name}")

        if not self.jenkins.is_initialized():
            await ctx.error("Jenkins not initialized. Please configure Jenkins connection first.")
            raise ValueError("Jenkins not initialized. Please configure Jenkins connection first.")

        try:
            await ctx.info("Fetching pipeline configuration...")
            config = self.jenkins.get_job_config(pipeline_name)

            # Check if this is a Pipeline job and if the config contains actual Jenkinsfile content
            if 'pipeline' in config.lower() and 'scriptpath' in config.lower():
                # This is a Pipeline job, check if we can get the actual Jenkinsfile content
                await ctx.info("Pipeline job detected. Checking for Jenkinsfile content...")

                # Try to extract Jenkinsfile path from config
                import re
                script_path_match = re.search(r'<scriptPath>(.*?)</scriptPath>', config)
                if script_path_match:
                    script_path = script_path_match.group(1)
                    await ctx.info(f"Jenkinsfile path found: {script_path}")

                    # Check if this is a Git-based pipeline (common case where Jenkinsfile is not in config)
                    if 'jenkinsfile' in script_path.lower() or 'jenkinsfile' in script_path.lower():
                        await ctx.warning("Jenkinsfile is stored in Git repository, not in Jenkins config.")
                        await ctx.info("Attempting to reconstruct Jenkinsfile from execution data...")

                        # Import JenkinsfileService for reconstruction
                        from services.jenkinsfile_service import JenkinsfileService
                        jenkinsfile_service = JenkinsfileService(self.jenkins)

                        try:
                            reconstruction = await jenkinsfile_service.reconstruct_jenkinsfile(pipeline_name, ctx)

                            if 'reconstructed_jenkinsfile' in reconstruction:
                                await ctx.info("✅ Successfully reconstructed Jenkinsfile from execution data!")

                                # Return the reconstructed Jenkinsfile with metadata
                                jenkinsfile = reconstruction['reconstructed_jenkinsfile']
                                analysis = reconstruction.get('analysis', {})

                                result = f"""# Reconstructed Jenkinsfile for {pipeline_name}
# Build Analyzed: {reconstruction.get('build_analyzed', 'Unknown')}
# Reconstruction Method: {reconstruction.get('reconstruction_method', 'Unknown')}
# Total Stages: {analysis.get('total_stages', 'Unknown')}
# Total Duration: {analysis.get('total_duration_formatted', 'Unknown')}
# Technologies: {', '.join(analysis.get('technologies_used', []))}

{jenkinsfile}

# Original Jenkins Configuration (for reference):
{config}"""

                                return result
                            else:
                                await ctx.warning("Could not reconstruct Jenkinsfile. Returning original config.")
                        except Exception as recon_error:
                            await ctx.warning(f"Jenkinsfile reconstruction failed: {recon_error}")
                            await ctx.info("Returning original configuration...")

            await ctx.info("Configuration retrieved successfully")
            return config

        except Exception as e:
            await ctx.error(f"Error getting configuration for {pipeline_name}: {str(e)}")
            raise
