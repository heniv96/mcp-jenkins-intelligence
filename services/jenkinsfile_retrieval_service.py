"""Comprehensive Jenkinsfile retrieval service for all Jenkins pipeline types."""

import logging
import re
import time
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from fastmcp import Context

from services.jenkins_service import JenkinsService

logger = logging.getLogger(__name__)


class JenkinsfileRetrievalService:
    """Service for retrieving Jenkinsfiles from all types of Jenkins pipelines."""

    def __init__(self, jenkins_service: JenkinsService):
        self.jenkins = jenkins_service

    async def get_jenkinsfile(self, job_name: str, ctx: Context) -> Dict[str, Any]:
        """Get Jenkinsfile for a single pipeline using SCMFileSystem method."""
        try:
            await ctx.info(f"Getting Jenkinsfile for pipeline: {job_name}")
            
            # Try SCMFileSystem method first (best for Git-based pipelines)
            jenkinsfile_content = await self._get_jenkinsfile_via_scm(job_name, ctx)
            
            if jenkinsfile_content and not jenkinsfile_content.startswith("Error:"):
                return {
                    "job_name": job_name,
                    "content": jenkinsfile_content,
                    "method": "SCMFileSystem",
                    "source": "Git Repository",
                    "timestamp": datetime.now().isoformat(),
                    "success": True
                }
            
            # Fallback to config.xml for inline pipelines
            await ctx.info("SCMFileSystem failed, trying config.xml method...")
            config_content = await self._get_jenkinsfile_from_config(job_name, ctx)
            
            if config_content and not config_content.startswith("Error:"):
                return {
                    "job_name": job_name,
                    "content": config_content,
                    "method": "config.xml",
                    "source": "Inline Pipeline Script",
                    "timestamp": datetime.now().isoformat(),
                    "success": True
                }
            
            return {
                "job_name": job_name,
                "content": f"Error: Could not retrieve Jenkinsfile for {job_name}",
                "method": "None",
                "source": "Unknown",
                "timestamp": datetime.now().isoformat(),
                "success": False
            }
            
        except Exception as e:
            logger.error(f"Error getting Jenkinsfile for {job_name}: {e}")
            return {
                "job_name": job_name,
                "content": f"Error: {str(e)}",
                "method": "None",
                "source": "Unknown",
                "timestamp": datetime.now().isoformat(),
                "success": False
            }

    async def get_all_jenkinsfiles(self, ctx: Context) -> Dict[str, Any]:
        """Get Jenkinsfiles from all pipelines in Jenkins."""
        await ctx.info("🔍 Retrieving Jenkinsfiles from all Jenkins pipelines...")
        
        if not self.jenkins.is_initialized():
            await ctx.error("Jenkins not initialized. Please configure Jenkins connection first.")
            return {"error": "Jenkins not initialized"}

        try:
            # Get all jobs
            jobs = self.jenkins.get_jobs()
            await ctx.info(f"Found {len(jobs)} jobs in Jenkins")
            
            results = {
                "total_jobs": len(jobs),
                "pipeline_jobs": 0,
                "freestyle_jobs": 0,
                "multibranch_jobs": 0,
                "jenkinsfiles": [],
                "errors": []
            }

            for job in jobs:
                job_name = job['name']
                job_type = job.get('_class', '')
                
                try:
                    await ctx.info(f"Processing job: {job_name} (type: {job_type})")
                    
                    # Determine job type and get appropriate Jenkinsfile
                    if 'WorkflowJob' in job_type:
                        # Single pipeline job
                        results["pipeline_jobs"] += 1
                        jenkinsfile_data = await self._get_pipeline_jenkinsfile(job_name, ctx)
                        if jenkinsfile_data:
                            jenkinsfile_data["job_type"] = "Pipeline"
                            results["jenkinsfiles"].append(jenkinsfile_data)
                    
                    elif 'WorkflowMultiBranchProject' in job_type:
                        # Multibranch pipeline
                        results["multibranch_jobs"] += 1
                        branch_jenkinsfiles = await self._get_multibranch_jenkinsfiles(job_name, ctx)
                        for branch_data in branch_jenkinsfiles:
                            branch_data["job_type"] = "Multibranch Pipeline"
                            results["jenkinsfiles"].append(branch_data)
                    
                    elif 'FreeStyleProject' in job_type:
                        # Freestyle job - check if it has pipeline steps
                        results["freestyle_jobs"] += 1
                        freestyle_data = await self._get_freestyle_jenkinsfile(job_name, ctx)
                        if freestyle_data:
                            freestyle_data["job_type"] = "Freestyle"
                            results["jenkinsfiles"].append(freestyle_data)
                    
                    else:
                        # Other job types
                        other_data = await self._get_other_job_jenkinsfile(job_name, ctx)
                        if other_data:
                            other_data["job_type"] = "Other"
                            results["jenkinsfiles"].append(other_data)
                
                except Exception as e:
                    error_msg = f"Error processing job {job_name}: {str(e)}"
                    logger.warning(error_msg)
                    results["errors"].append(error_msg)
                    await ctx.warning(error_msg)

            await ctx.info(f"✅ Successfully processed {len(results['jenkinsfiles'])} Jenkinsfiles")
            return results

        except Exception as e:
            await ctx.error(f"Failed to get all Jenkinsfiles: {str(e)}")
            return {"error": str(e)}

    async def _get_pipeline_jenkinsfile(self, job_name: str, ctx: Context) -> Optional[Dict[str, Any]]:
        """Get Jenkinsfile from a single pipeline job."""
        try:
            # Method 1: Try SCMFileSystem (best method)
            jenkinsfile_content = await self._get_jenkinsfile_via_scm(job_name, ctx)
            if jenkinsfile_content and not jenkinsfile_content.startswith("Error:"):
                return {
                    "job_name": job_name,
                    "content": jenkinsfile_content,
                    "method": "SCMFileSystem",
                    "source": "Git Repository",
                    "timestamp": datetime.now().isoformat()
                }

            # Method 2: Try workspace file
            jenkinsfile_content = self.jenkins.get_workspace_file(job_name, "Jenkinsfile", False)
            if jenkinsfile_content and not jenkinsfile_content.startswith("File not found"):
                return {
                    "job_name": job_name,
                    "content": jenkinsfile_content,
                    "method": "Workspace",
                    "source": "Jenkins Workspace",
                    "timestamp": datetime.now().isoformat()
                }

            # Method 3: Try config.xml for inline scripts
            config = self.jenkins.get_job_config(job_name)
            if 'pipeline' in config.lower() and 'scriptpath' in config.lower():
                # External Jenkinsfile
                script_path_match = re.search(r'<scriptPath>(.*?)</scriptPath>', config)
                if script_path_match:
                    script_path = script_path_match.group(1)
                    return {
                        "job_name": job_name,
                        "content": f"# External Jenkinsfile: {script_path}\n# This Jenkinsfile is stored in Git repository\n# Pipeline Configuration:\n{config}",
                        "method": "Config",
                        "source": f"Git Repository ({script_path})",
                        "timestamp": datetime.now().isoformat()
                    }
            elif '<script>' in config and '</script>' in config:
                # Inline script
                script_match = re.search(r'<script>(.*?)</script>', config, re.DOTALL)
                if script_match:
                    return {
                        "job_name": job_name,
                        "content": script_match.group(1).strip(),
                        "method": "Config",
                        "source": "Inline Script",
                        "timestamp": datetime.now().isoformat()
                    }

            return None

        except Exception as e:
            logger.warning(f"Failed to get Jenkinsfile for pipeline {job_name}: {e}")
            return None

    async def _get_multibranch_jenkinsfiles(self, job_name: str, ctx: Context) -> List[Dict[str, Any]]:
        """Get Jenkinsfiles from all branches of a multibranch pipeline."""
        try:
            await ctx.info(f"Processing multibranch pipeline: {job_name}")
            
            # Use proven Groovy script to get all branches and their Jenkinsfiles
            groovy_script = f"""
import jenkins.model.*
import org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject
import org.jenkinsci.plugins.workflow.job.WorkflowJob
import jenkins.scm.api.SCMFileSystem

def mb = Jenkins.instance.getItemByFullName('{job_name}') as WorkflowMultiBranchProject
def results = []

if (mb) {{
    mb.getItems().each {{ WorkflowJob branchJob ->
        def scriptPath = branchJob.getDefinition().getScriptPath() ?: "Jenkinsfile"
        def scms = branchJob.getDefinition().getSCMs()
        
        if (scms && scms.size() > 0) {{
            def scm = scms[0]
            def fs = SCMFileSystem.of(branchJob, scm)
            
            if (fs != null && fs.getRoot().child(scriptPath).exists()) {{
                def content = fs.getRoot().child(scriptPath).contentAsString()
                results.add([
                    branch: branchJob.name,
                    fullName: branchJob.fullName,
                    content: content,
                    scriptPath: scriptPath
                ])
            }} else {{
                results.add([
                    branch: branchJob.name,
                    fullName: branchJob.fullName,
                    content: "# No Jenkinsfile found for branch: " + branchJob.name,
                    scriptPath: scriptPath,
                    error: "SCMFileSystem null or file not found"
                ])
            }}
        }} else {{
            results.add([
                branch: branchJob.name,
                fullName: branchJob.fullName,
                content: "# No SCMs found for branch: " + branchJob.name,
                scriptPath: scriptPath,
                error: "No SCMs found"
            ])
        }}
    }}
}}

println "=== MULTIBRANCH_RESULTS_START ==="
results.each {{ result ->
    println "BRANCH: " + result.branch
    println "FULLNAME: " + result.fullName
    println "SCRIPTPATH: " + result.scriptPath
    if (result.error) {{
        println "ERROR: " + result.error
    }}
    println "CONTENT_START:"
    println result.content
    println "CONTENT_END:"
    println "---"
}}
println "=== MULTIBRANCH_RESULTS_END ==="
"""

            result = self.jenkins.execute_groovy_script(groovy_script)
            
            # Parse the structured result
            branches = self._parse_multibranch_results(result)
            
            # Convert to the expected format
            jenkinsfiles = []
            for branch in branches:
                jenkinsfiles.append({
                    "job_name": f"{job_name}/{branch['branch']}",
                    "branch": branch['branch'],
                    "content": branch['content'],
                    "method": "SCMFileSystem_Proven",
                    "source": f"Git Repository ({branch.get('scriptPath', 'Jenkinsfile')})",
                    "timestamp": datetime.now().isoformat(),
                    "error": branch.get('error')
                })
            
            await ctx.info(f"Found {len(jenkinsfiles)} branches in multibranch pipeline")
            return jenkinsfiles

        except Exception as e:
            logger.warning(f"Failed to get multibranch Jenkinsfiles for {job_name}: {e}")
            return [{
                "job_name": f"{job_name}/error",
                "branch": "error",
                "content": f"# Error getting multibranch Jenkinsfiles: {str(e)}",
                "method": "SCMFileSystem_Proven",
                "source": "Git Repository",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }]

    async def _get_freestyle_jenkinsfile(self, job_name: str, ctx: Context) -> Optional[Dict[str, Any]]:
        """Get pipeline content from a freestyle job (if it has pipeline steps)."""
        try:
            config = self.jenkins.get_job_config(job_name)
            
            # Check if it has pipeline steps
            if 'pipeline' in config.lower() or 'workflow' in config.lower():
                # Extract any pipeline-related content
                pipeline_match = re.search(r'<pipeline>(.*?)</pipeline>', config, re.DOTALL)
                if pipeline_match:
                    return {
                        "job_name": job_name,
                        "content": pipeline_match.group(1).strip(),
                        "method": "Config",
                        "source": "Freestyle Pipeline Steps",
                        "timestamp": datetime.now().isoformat()
                    }
            
            # Check for shell scripts that might contain pipeline-like content
            shell_matches = re.findall(r'<command>(.*?)</command>', config, re.DOTALL)
            if shell_matches:
                pipeline_content = "\n".join(shell_matches)
                if any(keyword in pipeline_content.lower() for keyword in ['pipeline', 'stage', 'node', 'workflow']):
                    return {
                        "job_name": job_name,
                        "content": f"# Freestyle Job with Pipeline-like Content\n# Shell Commands:\n{pipeline_content}",
                        "method": "Config",
                        "source": "Freestyle Shell Scripts",
                        "timestamp": datetime.now().isoformat()
                    }
            
            return None

        except Exception as e:
            logger.warning(f"Failed to get freestyle Jenkinsfile for {job_name}: {e}")
            return None

    async def _get_other_job_jenkinsfile(self, job_name: str, ctx: Context) -> Optional[Dict[str, Any]]:
        """Get pipeline content from other job types."""
        try:
            config = self.jenkins.get_job_config(job_name)
            
            # Look for any pipeline-related content in the config
            if any(keyword in config.lower() for keyword in ['pipeline', 'workflow', 'jenkinsfile']):
                return {
                    "job_name": job_name,
                    "content": f"# Job Configuration (contains pipeline references)\n{config}",
                    "method": "Config",
                    "source": "Job Configuration",
                    "timestamp": datetime.now().isoformat()
                }
            
            return None

        except Exception as e:
            logger.warning(f"Failed to get other job Jenkinsfile for {job_name}: {e}")
            return None

    async def _get_jenkinsfile_from_config(self, job_name: str, ctx: Context) -> str:
        """Get Jenkinsfile from config.xml for inline pipelines."""
        try:
            await ctx.info(f"Getting Jenkinsfile from config.xml for {job_name}")
            
            # Get job config
            config_xml = self.jenkins_service.get_job_config(job_name)
            
            # Parse XML to extract pipeline script
            import xml.etree.ElementTree as ET
            root = ET.fromstring(config_xml)
            
            # Look for pipeline script in different locations
            script_elements = root.findall(".//script")
            if script_elements:
                return script_elements[0].text or ""
            
            # Look for definition/script
            definition = root.find(".//definition")
            if definition is not None:
                script_elem = definition.find("script")
                if script_elem is not None:
                    return script_elem.text or ""
            
            return "Error: No pipeline script found in config.xml"
            
        except Exception as e:
            logger.error(f"Error getting Jenkinsfile from config for {job_name}: {e}")
            return f"Error: {str(e)}"

    async def _get_jenkinsfile_via_scm(self, job_name: str, ctx: Context) -> str:
        """Get Jenkinsfile using SCMFileSystem - PROVEN METHOD."""
        try:
            # Use the proven Groovy script that works with the actual Jenkins instance
            groovy_script = f"""
import jenkins.model.*
import org.jenkinsci.plugins.workflow.job.WorkflowJob
import jenkins.scm.api.SCMFileSystem

def job = Jenkins.instance.getItemByFullName('{job_name}') as WorkflowJob
def scriptPath = job.getDefinition().getScriptPath() ?: "Jenkinsfile"
def scms = job.getDefinition().getSCMs()
if (scms && scms.size() > 0) {{
    def scm = scms[0]
    def fs = SCMFileSystem.of(job, scm)
    if (fs != null && fs.getRoot().child(scriptPath).exists()) {{
        println "=== JENKINSFILE_CONTENT_START ==="
        println fs.getRoot().child(scriptPath).contentAsString()
        println "=== JENKINSFILE_CONTENT_END ==="
    }} else {{
        println "=== ERROR: SCMFileSystem null or file not found ==="
        println "ScriptPath: ${{scriptPath}}"
        println "SCM: ${{scm}}"
        println "SCMFileSystem null: ${{fs == null}}"
    }}
}} else {{
    println "=== ERROR: No SCMs found ==="
    println "ScriptPath: ${{scriptPath}}"
}}
"""

            result = self.jenkins.execute_groovy_script(groovy_script)
            
            # Parse the result to extract Jenkinsfile content
            if "=== JENKINSFILE_CONTENT_START ===" in result and "=== JENKINSFILE_CONTENT_END ===" in result:
                start_marker = "=== JENKINSFILE_CONTENT_START ==="
                end_marker = "=== JENKINSFILE_CONTENT_END ==="
                
                start_idx = result.find(start_marker) + len(start_marker)
                end_idx = result.find(end_marker)
                
                if start_idx > len(start_marker) - 1 and end_idx > start_idx:
                    return result[start_idx:end_idx].strip()
            
            return f"Error: Failed to retrieve Jenkinsfile - {result}"

        except Exception as e:
            logger.warning(f"SCMFileSystem method failed for {job_name}: {e}")
            return f"Error: SCMFileSystem failed - {str(e)}"

    def _parse_multibranch_results(self, result: str) -> List[Dict[str, Any]]:
        """Parse multibranch results from Groovy script output."""
        try:
            if "=== MULTIBRANCH_RESULTS_START ===" not in result or "=== MULTIBRANCH_RESULTS_END ===" not in result:
                return []
            
            # Extract content between markers
            start_marker = "=== MULTIBRANCH_RESULTS_START ==="
            end_marker = "=== MULTIBRANCH_RESULTS_END ==="
            
            start_idx = result.find(start_marker) + len(start_marker)
            end_idx = result.find(end_marker)
            
            if start_idx <= len(start_marker) - 1 or end_idx <= start_idx:
                return []
            
            content = result[start_idx:end_idx].strip()
            
            # Parse each branch result
            branches = []
            current_branch = {}
            current_content = []
            in_content = False
            
            for line in content.split('\n'):
                line = line.strip()
                
                if line.startswith("BRANCH:"):
                    if current_branch:
                        current_branch["content"] = "\n".join(current_content).strip()
                        branches.append(current_branch)
                    current_branch = {"branch": line.replace("BRANCH:", "").strip()}
                    current_content = []
                    in_content = False
                elif line.startswith("FULLNAME:"):
                    current_branch["fullName"] = line.replace("FULLNAME:", "").strip()
                elif line.startswith("SCRIPTPATH:"):
                    current_branch["scriptPath"] = line.replace("SCRIPTPATH:", "").strip()
                elif line.startswith("ERROR:"):
                    current_branch["error"] = line.replace("ERROR:", "").strip()
                elif line == "CONTENT_START:":
                    in_content = True
                elif line == "CONTENT_END:":
                    in_content = False
                elif line == "---":
                    if current_branch:
                        current_branch["content"] = "\n".join(current_content).strip()
                        branches.append(current_branch)
                        current_branch = {}
                        current_content = []
                elif in_content and current_branch:
                    current_content.append(line)
            
            # Add the last branch if exists
            if current_branch:
                current_branch["content"] = "\n".join(current_content).strip()
                branches.append(current_branch)
            
            return branches
            
        except Exception as e:
            logger.warning(f"Failed to parse multibranch results: {e}")
            return []

    async def get_jenkinsfile_for_specific_build(self, job_name: str, build_number: int, ctx: Context) -> Dict[str, Any]:
        """Get the exact Jenkinsfile used by a specific build."""
        await ctx.info(f"Getting Jenkinsfile for {job_name} build #{build_number}")
        
        if not self.jenkins.is_initialized():
            await ctx.error("Jenkins not initialized. Please configure Jenkins connection first.")
            return {"error": "Jenkins not initialized"}

        try:
            # Use Groovy script to get Jenkinsfile from specific build
            groovy_script = f"""
            import jenkins.model.*
            import org.jenkinsci.plugins.workflow.job.*
            import jenkins.scm.api.*
            import jenkins.scm.api.mixin.*

            def job = Jenkins.instance.getItemByFullName('{job_name}') as WorkflowJob
            def run = job.getBuildByNumber({build_number}) as Run
            
            if (run) {{
                def rev = run.getAction(SCMRevisionAction)?.getRevision()
                if (rev != null) {{
                    def scriptPath = job.getDefinition().getScriptPath() ?: "Jenkinsfile"
                    def fs = SCMFileSystem.of(job, rev)
                    
                    if (fs != null && fs.getRoot().child(scriptPath).exists()) {{
                        return [
                            content: fs.getRoot().child(scriptPath).contentAsString(),
                            revision: rev.toString(),
                            scriptPath: scriptPath,
                            success: true
                        ]
                    }} else {{
                        return [
                            error: "SCMFileSystem.of(job, rev) returned null or file not found",
                            success: false
                        ]
                    }}
                }} else {{
                    return [
                        error: "No SCMRevision on that run (was it inline? or no SCM?)",
                        success: false
                    ]
                }}
            }} else {{
                return [
                    error: "Build not found",
                    success: false
                ]
            }}
            """

            result = self.jenkins.execute_groovy_script(groovy_script)
            
            # Parse the result
            import json
            try:
                if isinstance(result, str):
                    build_data = json.loads(result)
                else:
                    build_data = result
                
                if build_data.get('success', False):
                    return {
                        "job_name": job_name,
                        "build_number": build_number,
                        "content": build_data['content'],
                        "revision": build_data.get('revision'),
                        "script_path": build_data.get('scriptPath'),
                        "method": "SCMFileSystem (Specific Build)",
                        "source": f"Git Repository (Build #{build_number})",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "job_name": job_name,
                        "build_number": build_number,
                        "error": build_data.get('error', 'Unknown error'),
                        "method": "SCMFileSystem (Specific Build)",
                        "source": f"Git Repository (Build #{build_number})",
                        "timestamp": datetime.now().isoformat()
                    }
                    
            except (json.JSONDecodeError, TypeError) as e:
                return {
                    "job_name": job_name,
                    "build_number": build_number,
                    "error": f"Failed to parse result: {str(e)}",
                    "raw_result": str(result),
                    "method": "SCMFileSystem (Specific Build)",
                    "source": f"Git Repository (Build #{build_number})",
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            await ctx.error(f"Failed to get Jenkinsfile for build: {str(e)}")
            return {
                "job_name": job_name,
                "build_number": build_number,
                "error": str(e),
                "method": "SCMFileSystem (Specific Build)",
                "source": f"Git Repository (Build #{build_number})",
                "timestamp": datetime.now().isoformat()
            }

    async def get_pipeline_types_summary(self, ctx: Context) -> Dict[str, Any]:
        """Get a summary of all pipeline types and their Jenkinsfile availability."""
        await ctx.info("📊 Analyzing pipeline types and Jenkinsfile availability...")
        
        if not self.jenkins.is_initialized():
            await ctx.error("Jenkins not initialized. Please configure Jenkins connection first.")
            return {"error": "Jenkins not initialized"}

        try:
            jobs = self.jenkins.get_jobs()
            
            summary = {
                "total_jobs": len(jobs),
                "pipeline_types": {
                    "Pipeline": {"count": 0, "with_jenkinsfile": 0},
                    "Multibranch Pipeline": {"count": 0, "with_jenkinsfile": 0},
                    "Freestyle": {"count": 0, "with_jenkinsfile": 0},
                    "Other": {"count": 0, "with_jenkinsfile": 0}
                },
                "jenkinsfile_sources": {
                    "Git Repository": 0,
                    "Inline Script": 0,
                    "Workspace": 0,
                    "Not Available": 0
                },
                "errors": []
            }

            for job in jobs:
                job_name = job['name']
                job_type = job.get('_class', '')
                
                try:
                    if 'WorkflowJob' in job_type:
                        summary["pipeline_types"]["Pipeline"]["count"] += 1
                        jenkinsfile_data = await self._get_pipeline_jenkinsfile(job_name, ctx)
                        if jenkinsfile_data:
                            summary["pipeline_types"]["Pipeline"]["with_jenkinsfile"] += 1
                            source = jenkinsfile_data.get("source", "Unknown")
                            if "Git" in source:
                                summary["jenkinsfile_sources"]["Git Repository"] += 1
                            elif "Inline" in source:
                                summary["jenkinsfile_sources"]["Inline Script"] += 1
                            elif "Workspace" in source:
                                summary["jenkinsfile_sources"]["Workspace"] += 1
                        else:
                            summary["jenkinsfile_sources"]["Not Available"] += 1
                    
                    elif 'WorkflowMultiBranchProject' in job_type:
                        summary["pipeline_types"]["Multibranch Pipeline"]["count"] += 1
                        branch_jenkinsfiles = await self._get_multibranch_jenkinsfiles(job_name, ctx)
                        if branch_jenkinsfiles and any(not bf.get('error') for bf in branch_jenkinsfiles):
                            summary["pipeline_types"]["Multibranch Pipeline"]["with_jenkinsfile"] += 1
                            summary["jenkinsfile_sources"]["Git Repository"] += len([bf for bf in branch_jenkinsfiles if not bf.get('error')])
                        else:
                            summary["jenkinsfile_sources"]["Not Available"] += 1
                    
                    elif 'FreeStyleProject' in job_type:
                        summary["pipeline_types"]["Freestyle"]["count"] += 1
                        freestyle_data = await self._get_freestyle_jenkinsfile(job_name, ctx)
                        if freestyle_data:
                            summary["pipeline_types"]["Freestyle"]["with_jenkinsfile"] += 1
                            summary["jenkinsfile_sources"]["Inline Script"] += 1
                        else:
                            summary["jenkinsfile_sources"]["Not Available"] += 1
                    
                    else:
                        summary["pipeline_types"]["Other"]["count"] += 1
                        other_data = await self._get_other_job_jenkinsfile(job_name, ctx)
                        if other_data:
                            summary["pipeline_types"]["Other"]["with_jenkinsfile"] += 1
                            summary["jenkinsfile_sources"]["Inline Script"] += 1
                        else:
                            summary["jenkinsfile_sources"]["Not Available"] += 1
                
                except Exception as e:
                    error_msg = f"Error analyzing job {job_name}: {str(e)}"
                    summary["errors"].append(error_msg)
                    logger.warning(error_msg)

            await ctx.info("✅ Pipeline types analysis completed")
            return summary

        except Exception as e:
            await ctx.error(f"Failed to analyze pipeline types: {str(e)}")
            return {"error": str(e)}
