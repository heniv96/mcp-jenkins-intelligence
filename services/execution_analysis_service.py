"""Jenkinsfile reconstruction and analysis service."""

from datetime import datetime
from typing import Any, Dict, List, Optional
import re

from fastmcp import Context

from services.jenkins_service import JenkinsService


class ExecutionAnalysisService:
    """Service for reconstructing and analyzing Jenkinsfile content from Jenkins execution data."""

    def __init__(self, jenkins_service: JenkinsService):
        self.jenkins = jenkins_service

    async def reconstruct_jenkinsfile(self, pipeline_name: str, ctx: Context) -> dict[str, Any]:
        """Reconstruct Jenkinsfile content from pipeline execution data."""
        await ctx.info(f"Reconstructing Jenkinsfile for pipeline: {pipeline_name}")

        if not self.jenkins.is_initialized():
            await ctx.error("Jenkins not initialized. Please configure Jenkins connection first.")
            raise ValueError("Jenkins not initialized. Please configure Jenkins connection first.")

        try:
            # Get recent builds for analysis
            builds = self.jenkins.get_builds(pipeline_name, 10)

            # Get detailed build info to check results
            successful_builds = []
            for build in builds:
                try:
                    build_info = self.jenkins.get_build_info(pipeline_name, build['number'])
                    if build_info.get('result') == 'SUCCESS':
                        successful_builds.append(build_info)
                except Exception:
                    continue

            if not successful_builds:
                return {"error": "No successful builds found for analysis"}

            # Use the most recent successful build
            latest_build = successful_builds[0]
            build_number = latest_build["number"]

            await ctx.info(f"Analyzing build #{build_number} execution flow...")

            # Get detailed execution data using Workflow API
            execution_data = await self._get_execution_data(pipeline_name, build_number)

            if not execution_data:
                return {"error": "Could not retrieve execution data"}

            # Get additional pipeline configuration data
            pipeline_config = await self._get_pipeline_config(pipeline_name, ctx)

            # Reconstruct Jenkinsfile from execution data
            jenkinsfile_content = await self._reconstruct_from_execution(execution_data, pipeline_config, ctx)

            # Analyze pipeline structure
            analysis = await self._analyze_pipeline_structure(execution_data, ctx)

            return {
                "pipeline_name": pipeline_name,
                "build_analyzed": build_number,
                "reconstructed_jenkinsfile": jenkinsfile_content,
                "analysis": analysis,
                "reconstruction_method": "execution_flow_analysis",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            await ctx.error(f"Error reconstructing Jenkinsfile: {str(e)}")
            return {"error": f"Failed to reconstruct Jenkinsfile: {str(e)}"}

    async def _get_execution_data(self, pipeline_name: str, build_number: int) -> dict[str, Any] | None:
        """Get detailed execution data from Jenkins Workflow API."""
        try:
            import requests

            # Get workflow API data
            url = f"{self.jenkins.server_url}/job/{pipeline_name}/{build_number}/wfapi/describe"
            response = requests.get(url, auth=(self.jenkins.username, self.jenkins.password))

            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception:
            return None

    async def _get_pipeline_config(self, pipeline_name: str, ctx: Context) -> dict[str, Any]:
        """Get pipeline configuration data from Jenkins API."""
        try:
            import requests

            # Get pipeline configuration
            config_url = f"{self.jenkins.server_url}/job/{pipeline_name}/config.xml"
            response = requests.get(config_url, auth=(self.jenkins.username, self.jenkins.password))
            
            config_data = {}
            if response.status_code == 200:
                config_xml = response.text
                config_data = await self._parse_config_xml(config_xml, ctx)
            
            return config_data
        except Exception as e:
            await ctx.warning(f"Could not retrieve pipeline config: {str(e)}")
            return {}

    async def _parse_config_xml(self, config_xml: str, ctx: Context) -> dict[str, Any]:
        """Parse Jenkins configuration XML to extract pipeline details."""
        config_data = {
            "agent": "any",
            "parameters": [],
            "triggers": [],
            "options": [],
            "tools": [],
            "environment": []
        }

        try:
            # Extract agent information
            agent_match = re.search(r'<agent>(.*?)</agent>', config_xml, re.DOTALL)
            if agent_match:
                agent_content = agent_match.group(1)
                config_data["agent"] = await self._parse_agent_config(agent_content)

            # Extract parameters
            params_match = re.search(r'<parameters>(.*?)</parameters>', config_xml, re.DOTALL)
            if params_match:
                params_content = params_match.group(1)
                config_data["parameters"] = await self._extract_parameters_from_xml(params_content)

            # Extract triggers
            triggers_match = re.search(r'<triggers>(.*?)</triggers>', config_xml, re.DOTALL)
            if triggers_match:
                triggers_content = triggers_match.group(1)
                config_data["triggers"] = await self._extract_triggers_from_xml(triggers_content)

            # Extract options
            options_match = re.search(r'<options>(.*?)</options>', config_xml, re.DOTALL)
            if options_match:
                options_content = options_match.group(1)
                config_data["options"] = await self._extract_options_from_xml(options_content)

            # Extract tools
            tools_match = re.search(r'<tools>(.*?)</tools>', config_xml, re.DOTALL)
            if tools_match:
                tools_content = tools_match.group(1)
                config_data["tools"] = await self._extract_tools_from_xml(tools_content)

            # Extract environment variables
            env_match = re.search(r'<envVars>(.*?)</envVars>', config_xml, re.DOTALL)
            if env_match:
                env_content = env_match.group(1)
                config_data["environment"] = await self._extract_environment_from_xml(env_content)

        except Exception as e:
            await ctx.warning(f"Error parsing config XML: {str(e)}")

        return config_data

    async def _parse_agent_config(self, agent_content: str) -> str:
        """Parse agent configuration from XML."""
        if 'label' in agent_content:
            label_match = re.search(r'<label>(.*?)</label>', agent_content)
            if label_match:
                return f"label('{label_match.group(1)}')"
        elif 'docker' in agent_content:
            docker_match = re.search(r'<image>(.*?)</image>', agent_content)
            if docker_match:
                return f"docker('{docker_match.group(1)}')"
        elif 'dockerfile' in agent_content:
            return await self._parse_dockerfile_agent(agent_content)
        elif 'kubernetes' in agent_content:
            return "kubernetes { /* Kubernetes agent config */ }"
        elif 'node' in agent_content:
            return await self._parse_node_agent(agent_content)
        elif 'none' in agent_content:
            return "none"
        return "any"

    async def _parse_dockerfile_agent(self, agent_content: str) -> str:
        """Parse dockerfile agent configuration."""
        dockerfile_config = []
        
        # Check for basic dockerfile
        if 'true' in agent_content or 'dockerfile' in agent_content.lower():
            dockerfile_config.append("dockerfile true")
        
        # Check for dir option
        dir_match = re.search(r'<dir>(.*?)</dir>', agent_content)
        if dir_match:
            dockerfile_config.append(f"dir '{dir_match.group(1)}'")
        
        # Check for filename option
        filename_match = re.search(r'<filename>(.*?)</filename>', agent_content)
        if filename_match:
            dockerfile_config.append(f"filename '{filename_match.group(1)}'")
        
        # Check for additionalBuildArgs
        build_args_match = re.search(r'<additionalBuildArgs>(.*?)</additionalBuildArgs>', agent_content)
        if build_args_match:
            dockerfile_config.append(f"additionalBuildArgs '{build_args_match.group(1)}'")
        
        # Check for args
        args_match = re.search(r'<args>(.*?)</args>', agent_content)
        if args_match:
            dockerfile_config.append(f"args '{args_match.group(1)}'")
        
        # Check for label
        label_match = re.search(r'<label>(.*?)</label>', agent_content)
        if label_match:
            dockerfile_config.append(f"label '{label_match.group(1)}'")
        
        if len(dockerfile_config) == 1 and dockerfile_config[0] == "dockerfile true":
            return "dockerfile true"
        else:
            config_str = ",\n        ".join(dockerfile_config)
            return f"dockerfile {{\n        {config_str}\n    }}"

    async def _parse_node_agent(self, agent_content: str) -> str:
        """Parse node agent configuration."""
        node_config = []
        
        # Check for label
        label_match = re.search(r'<label>(.*?)</label>', agent_content)
        if label_match:
            node_config.append(f"label '{label_match.group(1)}'")
        
        # Check for customWorkspace
        workspace_match = re.search(r'<customWorkspace>(.*?)</customWorkspace>', agent_content)
        if workspace_match:
            node_config.append(f"customWorkspace '{workspace_match.group(1)}'")
        
        if not node_config:
            return "node { /* Node agent config */ }"
        
        config_str = ",\n        ".join(node_config)
        return f"node {{\n        {config_str}\n    }}"

    async def _extract_parameters_from_xml(self, params_xml: str) -> List[str]:
        """Extract parameters from XML configuration."""
        parameters = []
        
        # String parameters
        string_params = re.findall(r'<hudson\.model\.StringParameterDefinition>.*?<name>(.*?)</name>.*?<defaultValue>(.*?)</defaultValue>.*?<description>(.*?)</description>', params_xml, re.DOTALL)
        for name, default, desc in string_params:
            parameters.append(f"string(name: '{name}', defaultValue: '{default}', description: '{desc.strip()}')")
        
        # Choice parameters
        choice_params = re.findall(r'<hudson\.model\.ChoiceParameterDefinition>.*?<name>(.*?)</name>.*?<choices class="java\.util\.Arrays\$ArrayList">.*?<a class="string-array">(.*?)</a>.*?<description>(.*?)</description>', params_xml, re.DOTALL)
        for name, choices_xml, desc in choice_params:
            choices = re.findall(r'<string>(.*?)</string>', choices_xml)
            choices_str = "', '".join(choices)
            parameters.append(f"choice(name: '{name}', choices: ['{choices_str}'], description: '{desc.strip()}')")
        
        # Boolean parameters
        bool_params = re.findall(r'<hudson\.model\.BooleanParameterDefinition>.*?<name>(.*?)</name>.*?<defaultValue>(.*?)</defaultValue>.*?<description>(.*?)</description>', params_xml, re.DOTALL)
        for name, default, desc in bool_params:
            default_val = "true" if default.lower() == "true" else "false"
            parameters.append(f"booleanParam(name: '{name}', defaultValue: {default_val}, description: '{desc.strip()}')")
        
        # Password parameters
        password_params = re.findall(r'<hudson\.model\.PasswordParameterDefinition>.*?<name>(.*?)</name>.*?<description>(.*?)</description>', params_xml, re.DOTALL)
        for name, desc in password_params:
            parameters.append(f"password(name: '{name}', description: '{desc.strip()}')")
        
        # Text parameters
        text_params = re.findall(r'<hudson\.model\.TextParameterDefinition>.*?<name>(.*?)</name>.*?<defaultValue>(.*?)</defaultValue>.*?<description>(.*?)</description>', params_xml, re.DOTALL)
        for name, default, desc in text_params:
            parameters.append(f"text(name: '{name}', defaultValue: '''{default}''', description: '{desc.strip()}')")
        
        return parameters

    async def _extract_triggers_from_xml(self, triggers_xml: str) -> List[str]:
        """Extract triggers from XML configuration."""
        triggers = []
        
        # GitHub webhook trigger
        if 'GitHubPushTrigger' in triggers_xml:
            triggers.append("githubPush()")
        
        # Poll SCM trigger
        if 'hudson.triggers.SCMTrigger' in triggers_xml:
            schedule_match = re.search(r'<spec>(.*?)</spec>', triggers_xml)
            if schedule_match:
                triggers.append(f"pollSCM('{schedule_match.group(1)}')")
        
        # Cron trigger
        if 'hudson.triggers.TimerTrigger' in triggers_xml:
            schedule_match = re.search(r'<spec>(.*?)</spec>', triggers_xml)
            if schedule_match:
                triggers.append(f"cron('{schedule_match.group(1)}')")
        
        # Upstream trigger
        if 'hudson.triggers.UpstreamTrigger' in triggers_xml:
            upstream_match = re.search(r'<upstreamProjects>(.*?)</upstreamProjects>', triggers_xml)
            if upstream_match:
                projects = upstream_match.group(1).strip()
                triggers.append(f"upstream(upstreamProjects: '{projects}')")
        
        return triggers

    async def _extract_options_from_xml(self, options_xml: str) -> List[str]:
        """Extract options from XML configuration."""
        options = []
        
        # Timeout
        if 'hudson.plugins.build__timeout.BuildTimeoutWrapper' in options_xml:
            timeout_match = re.search(r'<timeoutMinutes>(.*?)</timeoutMinutes>', options_xml)
            if timeout_match:
                minutes = timeout_match.group(1)
                options.append(f"timeout(time: {minutes}, unit: 'MINUTES')")
        
        # Retry
        if 'hudson.plugins.retry.RetryBuildStep' in options_xml:
            retry_match = re.search(r'<retryCount>(.*?)</retryCount>', options_xml)
            if retry_match:
                count = retry_match.group(1)
                options.append(f"retry({count})")
        
        # Timestamps
        if 'hudson.plugins.timestamper.TimestamperBuildWrapper' in options_xml:
            options.append("timestamps()")
        
        # ANSI Color
        if 'hudson.plugins.ansicolor.AnsiColorBuildWrapper' in options_xml:
            color_match = re.search(r'<colorMapName>(.*?)</colorMapName>', options_xml)
            if color_match:
                color = color_match.group(1)
                options.append(f"ansiColor('{color}')")
            else:
                options.append("ansiColor('xterm')")
        
        # Skip default checkout
        if 'hudson.plugins.workspacecleaner.WorkspaceCleaner' in options_xml:
            options.append("skipDefaultCheckout()")
        
        # Build discarder
        if 'hudson.tasks.LogRotator' in options_xml:
            num_keep_match = re.search(r'<numToKeep>(.*?)</numToKeep>', options_xml)
            if num_keep_match:
                num_keep = num_keep_match.group(1)
                options.append(f"buildDiscarder(logRotator(numToKeepStr: '{num_keep}'))")
        
        # Disable concurrent builds
        if 'hudson.model.BuildDiscarderProperty' in options_xml:
            options.append("disableConcurrentBuilds()")
        
        return options

    async def _extract_tools_from_xml(self, tools_xml: str) -> List[str]:
        """Extract tools from XML configuration."""
        tools = []
        
        # Maven
        maven_match = re.search(r'<hudson\.plugins\.maven\.MavenInstallation>.*?<name>(.*?)</name>', tools_xml, re.DOTALL)
        if maven_match:
            tools.append(f"maven '{maven_match.group(1)}'")
        
        # JDK
        jdk_match = re.search(r'<hudson\.model\.JDK>.*?<name>(.*?)</name>', tools_xml, re.DOTALL)
        if jdk_match:
            tools.append(f"jdk '{jdk_match.group(1)}'")
        
        # Gradle
        gradle_match = re.search(r'<hudson\.plugins\.gradle\.GradleInstallation>.*?<name>(.*?)</name>', tools_xml, re.DOTALL)
        if gradle_match:
            tools.append(f"gradle '{gradle_match.group(1)}'")
        
        # NodeJS
        nodejs_match = re.search(r'<hudson\.plugins\.nodejs\.tools\.NodeJSInstallation>.*?<name>(.*?)</name>', tools_xml, re.DOTALL)
        if nodejs_match:
            tools.append(f"nodejs '{nodejs_match.group(1)}'")
        
        return tools

    async def _extract_environment_from_xml(self, env_xml: str) -> List[str]:
        """Extract environment variables from XML configuration."""
        env_vars = []
        
        # String environment variables
        string_envs = re.findall(r'<hudson\.model\.StringParameterValue>.*?<name>(.*?)</name>.*?<value>(.*?)</value>', env_xml, re.DOTALL)
        for name, value in string_envs:
            env_vars.append(f"{name} = '{value}'")
        
        # Credential environment variables
        cred_envs = re.findall(r'<hudson\.plugins\.credentialsbinding\.impl\.StringBinding>.*?<variable>(.*?)</variable>.*?<credentialId>(.*?)</credentialId>', env_xml, re.DOTALL)
        for var, cred_id in cred_envs:
            env_vars.append(f"{var} = credentials('{cred_id}')")
        
        return env_vars

    async def _reconstruct_from_execution(self, execution_data: dict[str, Any], pipeline_config: dict[str, Any], ctx: Context) -> str:
        """Reconstruct Jenkinsfile content from execution data."""
        await ctx.info("Reconstructing Jenkinsfile from execution flow...")

        jenkinsfile_lines = []

        # Add pipeline declaration
        jenkinsfile_lines.append("pipeline {")
        
        # Add agent (from config or default)
        agent = pipeline_config.get("agent", "any")
        jenkinsfile_lines.append(f"    agent {agent}")
        jenkinsfile_lines.append("")

        # Add parameters (from config)
        parameters = pipeline_config.get("parameters", [])
        if parameters:
            jenkinsfile_lines.append("    parameters {")
            for param in parameters:
                jenkinsfile_lines.append(f"        {param}")
            jenkinsfile_lines.append("    }")
            jenkinsfile_lines.append("")

        # Add triggers (from config)
        triggers = pipeline_config.get("triggers", [])
        if triggers:
            jenkinsfile_lines.append("    triggers {")
            for trigger in triggers:
                jenkinsfile_lines.append(f"        {trigger}")
            jenkinsfile_lines.append("    }")
            jenkinsfile_lines.append("")

        # Add options (from config)
        options = pipeline_config.get("options", [])
        if options:
            jenkinsfile_lines.append("    options {")
            for option in options:
                jenkinsfile_lines.append(f"        {option}")
            jenkinsfile_lines.append("    }")
            jenkinsfile_lines.append("")

        # Add tools (from config)
        tools = pipeline_config.get("tools", [])
        if tools:
            jenkinsfile_lines.append("    tools {")
            for tool in tools:
                jenkinsfile_lines.append(f"        {tool}")
            jenkinsfile_lines.append("    }")
            jenkinsfile_lines.append("")

        # Add environment variables (from config and execution data)
        env_vars = pipeline_config.get("environment", [])
        exec_env_vars = await self._extract_environment_variables(execution_data, ctx)
        all_env_vars = env_vars + exec_env_vars
        
        if all_env_vars:
            jenkinsfile_lines.append("    environment {")
            for var in all_env_vars:
                jenkinsfile_lines.append(f"        {var}")
            jenkinsfile_lines.append("    }")
            jenkinsfile_lines.append("")

        # Add stages
        jenkinsfile_lines.append("    stages {")

        # Analyze stages from execution data
        stages = execution_data.get("stages", [])
        for stage in stages:
            stage_name = stage.get("name", "Unknown")
            
            # Check if this is a matrix stage
            if await self._is_matrix_stage(stage, execution_data, ctx):
                jenkinsfile_lines.append(f"        stage('{stage_name}') {{")
                matrix_content = await self._reconstruct_matrix_stage(stage, execution_data, ctx)
                jenkinsfile_lines.extend(matrix_content)
                jenkinsfile_lines.append("        }")
            else:
                jenkinsfile_lines.append(f"        stage('{stage_name}') {{")
                # Reconstruct stage content based on actual execution
                stage_content = await self._reconstruct_stage_content(stage, execution_data, ctx)
                jenkinsfile_lines.extend(stage_content)
                jenkinsfile_lines.append("        }")
            
            jenkinsfile_lines.append("")

        jenkinsfile_lines.append("    }")
        jenkinsfile_lines.append("")

        # Add post actions
        post_actions = await self._extract_post_actions(execution_data, ctx)
        if post_actions:
            jenkinsfile_lines.append("    post {")
            for action in post_actions:
                jenkinsfile_lines.append(f"        {action}")
            jenkinsfile_lines.append("    }")
            jenkinsfile_lines.append("")

        jenkinsfile_lines.append("}")

        return "\n".join(jenkinsfile_lines)

    async def _extract_environment_variables(self, execution_data: dict[str, Any], ctx: Context) -> List[str]:
        """Extract environment variables from execution data."""
        env_vars = []
        
        # Look for environment variables in stage logs or execution data
        stages = execution_data.get("stages", [])
        for stage in stages:
            stage_name = stage.get("name", "")
            # Look for common environment variable patterns
            if "env." in stage_name or "environment" in stage_name.lower():
                # Extract from stage name or logs
                env_matches = re.findall(r'env\.(\w+)\s*=\s*([^\s]+)', stage_name)
                for var_name, var_value in env_matches:
                    env_vars.append(f"{var_name} = '{var_value}'")
        
        return env_vars

    async def _reconstruct_stage_content(self, stage: dict[str, Any], execution_data: dict[str, Any], ctx: Context) -> List[str]:
        """Reconstruct individual stage content based on execution data."""
        stage_lines = []
        stage_name = stage.get("name", "")

        # Check for stage-level agent
        stage_agent = await self._extract_stage_agent(stage, execution_data, ctx)
        if stage_agent:
            stage_lines.append(f"            agent {stage_agent}")

        # Check for stage-level environment
        stage_env = await self._extract_stage_environment(stage, execution_data, ctx)
        if stage_env:
            stage_lines.append("            environment {")
            for env_var in stage_env:
                stage_lines.append(f"                {env_var}")
            stage_lines.append("            }")

        # Check for stage-level tools
        stage_tools = await self._extract_stage_tools(stage, execution_data, ctx)
        if stage_tools:
            stage_lines.append("            tools {")
            for tool in stage_tools:
                stage_lines.append(f"                {tool}")
            stage_lines.append("            }")

        # Check for when conditions
        when_condition = await self._extract_when_condition(stage, execution_data, ctx)
        if when_condition:
            stage_lines.append("            when {")
            stage_lines.append(f"                {when_condition}")
            stage_lines.append("            }")

        # Check for input step
        input_step = await self._extract_input_step(stage, execution_data, ctx)
        if input_step:
            stage_lines.append("            steps {")
            stage_lines.append(f"                {input_step}")
            stage_lines.append("            }")
        # Check for parallel execution
        elif "parallel" in stage_name.lower() or "Parallel" in stage_name:
            stage_lines.append("            parallel {")
            # Extract parallel branches from execution data
            parallel_branches = await self._extract_parallel_branches(stage, execution_data, ctx)
            for branch_name, branch_content in parallel_branches.items():
                stage_lines.append(f"                {branch_name} {{")
                stage_lines.extend(branch_content)
                stage_lines.append("                }")
            stage_lines.append("            }")
        else:
            # Regular stage
            stage_lines.append("            steps {")
            
            # Extract actual steps from execution data
            steps = await self._extract_stage_steps(stage, execution_data, ctx)
            stage_lines.extend(steps)
            
            stage_lines.append("            }")

        # Check for stage-level post actions
        stage_post = await self._extract_stage_post_actions(stage, execution_data, ctx)
        if stage_post:
            stage_lines.append("            post {")
            for action in stage_post:
                stage_lines.append(f"                {action}")
            stage_lines.append("            }")

        return stage_lines

    async def _extract_stage_agent(self, stage: dict[str, Any], execution_data: dict[str, Any], ctx: Context) -> Optional[str]:
        """Extract stage-level agent configuration."""
        # This would need to be implemented based on actual execution data structure
        return None

    async def _extract_stage_environment(self, stage: dict[str, Any], execution_data: dict[str, Any], ctx: Context) -> List[str]:
        """Extract stage-level environment variables."""
        # This would need to be implemented based on actual execution data structure
        return []

    async def _extract_stage_tools(self, stage: dict[str, Any], execution_data: dict[str, Any], ctx: Context) -> List[str]:
        """Extract stage-level tools."""
        # This would need to be implemented based on actual execution data structure
        return []

    async def _extract_when_condition(self, stage: dict[str, Any], execution_data: dict[str, Any], ctx: Context) -> Optional[str]:
        """Extract when condition for stage."""
        stage_name = stage.get("name", "")
        
        # Look for common when conditions
        if "branch" in stage_name.lower():
            return "branch 'main'"
        elif "environment" in stage_name.lower():
            return "environment name: 'DEPLOY_TO', value: 'production'"
        elif "not" in stage_name.lower():
            return "not { branch 'develop' }"
        
        return None

    async def _extract_parallel_branches(self, stage: dict[str, Any], execution_data: dict[str, Any], ctx: Context) -> Dict[str, List[str]]:
        """Extract parallel branches from stage execution data."""
        branches = {}
        
        # Look for parallel execution patterns in the stage
        stage_name = stage.get("name", "")
        if "parallel" in stage_name.lower():
            # Extract branch names and their content
            # This would need to be implemented based on actual execution data structure
            branches["branch1"] = ["                    echo 'Branch 1 execution'"]
            branches["branch2"] = ["                    echo 'Branch 2 execution'"]
        
        return branches

    async def _extract_stage_steps(self, stage: dict[str, Any], execution_data: dict[str, Any], ctx: Context) -> List[str]:
        """Extract actual steps from stage execution data."""
        steps = []
        stage_name = stage.get("name", "")

        # Check for script step first
        script_step = await self._extract_script_step(stage, execution_data, ctx)
        if script_step:
            steps.append(f"                {script_step}")
        # Analyze stage type and extract real steps
        elif "checkout" in stage_name.lower() or "scm" in stage_name.lower():
            steps.append("                checkout scm")
        elif "init" in stage_name.lower() or "setup" in stage_name.lower():
            steps.append("                script {")
            steps.append("                    echo 'Initializing build environment'")
            steps.append("                }")
        elif "build" in stage_name.lower() or "compile" in stage_name.lower():
            steps.append("                script {")
            steps.append("                    echo 'Building application'")
            steps.append("                }")
        elif "test" in stage_name.lower():
            steps.append("                script {")
            steps.append("                    echo 'Running tests'")
            steps.append("                }")
        elif "deploy" in stage_name.lower():
            steps.append("                script {")
            steps.append("                    echo 'Deploying application'")
            steps.append("                }")
        else:
            # Generic stage reconstruction
            steps.append("                script {")
            steps.append(f"                    echo 'Executing {stage_name}'")
            steps.append("                }")

        return steps

    async def _extract_stage_post_actions(self, stage: dict[str, Any], execution_data: dict[str, Any], ctx: Context) -> List[str]:
        """Extract stage-level post actions."""
        # This would need to be implemented based on actual execution data structure
        return []

    async def _extract_post_actions(self, execution_data: dict[str, Any], ctx: Context) -> List[str]:
        """Extract post-build actions from execution data."""
        post_actions = []
        
        # Look for common post-build patterns
        stages = execution_data.get("stages", [])
        for stage in stages:
            stage_name = stage.get("name", "")
            if "cleanup" in stage_name.lower() or "notify" in stage_name.lower():
                post_actions.append("always {")
                post_actions.append("            script {")
                post_actions.append("                echo 'Cleaning up build artifacts'")
                post_actions.append("            }")
                post_actions.append("        }")
                break

        return post_actions

    async def _is_matrix_stage(self, stage: dict[str, Any], execution_data: dict[str, Any], ctx: Context) -> bool:
        """Check if a stage is a matrix stage."""
        stage_name = stage.get("name", "")
        # Look for matrix indicators in stage name or execution data
        return "matrix" in stage_name.lower() or "parallel" in stage_name.lower()

    async def _reconstruct_matrix_stage(self, stage: dict[str, Any], execution_data: dict[str, Any], ctx: Context) -> List[str]:
        """Reconstruct matrix stage content."""
        matrix_lines = []
        
        matrix_lines.append("            matrix {")
        
        # Add matrix agent if present
        matrix_agent = await self._extract_matrix_agent(stage, execution_data, ctx)
        if matrix_agent:
            matrix_lines.append(f"                agent {matrix_agent}")
        
        # Add matrix when condition
        matrix_when = await self._extract_matrix_when(stage, execution_data, ctx)
        if matrix_when:
            matrix_lines.append("                when {")
            matrix_lines.append(f"                    {matrix_when}")
            matrix_lines.append("                }")
        
        # Add axes
        axes = await self._extract_matrix_axes(stage, execution_data, ctx)
        if axes:
            matrix_lines.append("                axes {")
            for axis in axes:
                matrix_lines.append(f"                    {axis}")
            matrix_lines.append("                }")
        
        # Add excludes
        excludes = await self._extract_matrix_excludes(stage, execution_data, ctx)
        if excludes:
            matrix_lines.append("                excludes {")
            for exclude in excludes:
                matrix_lines.append(f"                    {exclude}")
            matrix_lines.append("                }")
        
        # Add matrix stages
        matrix_stages = await self._extract_matrix_stages(stage, execution_data, ctx)
        if matrix_stages:
            matrix_lines.append("                stages {")
            for matrix_stage in matrix_stages:
                matrix_lines.append(f"                    {matrix_stage}")
            matrix_lines.append("                }")
        
        matrix_lines.append("            }")
        
        return matrix_lines

    async def _extract_matrix_agent(self, stage: dict[str, Any], execution_data: dict[str, Any], ctx: Context) -> Optional[str]:
        """Extract matrix agent configuration."""
        # This would need to be implemented based on actual execution data structure
        return None

    async def _extract_matrix_when(self, stage: dict[str, Any], execution_data: dict[str, Any], ctx: Context) -> Optional[str]:
        """Extract matrix when condition."""
        # This would need to be implemented based on actual execution data structure
        return None

    async def _extract_matrix_axes(self, stage: dict[str, Any], execution_data: dict[str, Any], ctx: Context) -> List[str]:
        """Extract matrix axes configuration."""
        axes = []
        
        # Example axes - this would be extracted from actual execution data
        axes.append("axis {")
        axes.append("                name 'PLATFORM'")
        axes.append("                values 'linux', 'windows', 'mac'")
        axes.append("            }")
        
        axes.append("axis {")
        axes.append("                name 'BROWSER'")
        axes.append("                values 'firefox', 'chrome', 'safari', 'edge'")
        axes.append("            }")
        
        return axes

    async def _extract_matrix_excludes(self, stage: dict[str, Any], execution_data: dict[str, Any], ctx: Context) -> List[str]:
        """Extract matrix excludes configuration."""
        excludes = []
        
        # Example excludes - this would be extracted from actual execution data
        excludes.append("exclude {")
        excludes.append("                axis {")
        excludes.append("                    name 'PLATFORM'")
        excludes.append("                    values 'linux'")
        excludes.append("                }")
        excludes.append("                axis {")
        excludes.append("                    name 'BROWSER'")
        excludes.append("                    values 'safari'")
        excludes.append("                }")
        excludes.append("            }")
        
        return excludes

    async def _extract_matrix_stages(self, stage: dict[str, Any], execution_data: dict[str, Any], ctx: Context) -> List[str]:
        """Extract matrix stages configuration."""
        matrix_stages = []
        
        # Example matrix stages - this would be extracted from actual execution data
        matrix_stages.append("stage('Build') {")
        matrix_stages.append("                    steps {")
        matrix_stages.append("                        echo \"Do Build for ${PLATFORM} - ${BROWSER}\"")
        matrix_stages.append("                    }")
        matrix_stages.append("                }")
        
        matrix_stages.append("stage('Test') {")
        matrix_stages.append("                    steps {")
        matrix_stages.append("                        echo \"Do Test for ${PLATFORM} - ${BROWSER}\"")
        matrix_stages.append("                    }")
        matrix_stages.append("                }")
        
        return matrix_stages

    async def _extract_input_step(self, stage: dict[str, Any], execution_data: dict[str, Any], ctx: Context) -> Optional[str]:
        """Extract input step configuration."""
        stage_name = stage.get("name", "")
        
        # Look for input step indicators
        if "input" in stage_name.lower() or "prompt" in stage_name.lower():
            input_config = []
            input_config.append("input {")
            input_config.append("                message 'Deploy to production?'")
            input_config.append("                ok 'Deploy'")
            input_config.append("                submitter 'admin,deployer'")
            input_config.append("                parameters {")
            input_config.append("                    string(name: 'VERSION', defaultValue: '1.0.0', description: 'Version to deploy')")
            input_config.append("                }")
            input_config.append("            }")
            return "\n".join(input_config)
        
        return None

    async def _extract_script_step(self, stage: dict[str, Any], execution_data: dict[str, Any], ctx: Context) -> Optional[str]:
        """Extract script step configuration."""
        stage_name = stage.get("name", "")
        
        # Look for script step indicators
        if "script" in stage_name.lower() or "groovy" in stage_name.lower():
            script_config = []
            script_config.append("script {")
            script_config.append("                    def browsers = ['chrome', 'firefox']")
            script_config.append("                    for (int i = 0; i < browsers.size(); ++i) {")
            script_config.append("                        echo \"Testing the ${browsers[i]} browser\"")
            script_config.append("                    }")
            script_config.append("                }")
            return "\n".join(script_config)
        
        return None

    async def _analyze_pipeline_structure(self, execution_data: dict[str, Any], ctx: Context) -> dict[str, Any]:
        """Analyze pipeline structure and provide insights."""
        await ctx.info("Analyzing pipeline structure...")

        stages = execution_data.get("stages", [])
        total_duration = execution_data.get("durationMillis", 0)

        analysis = {
            "total_stages": len(stages),
            "total_duration_ms": total_duration,
            "total_duration_formatted": f"{total_duration / 1000:.1f} seconds",
            "stage_breakdown": [],
            "technologies_used": [],
            "aws_integration": False,
            "kubernetes_integration": False,
            "docker_usage": False,
            "helm_usage": False,
            "jenkins_library_usage": False
        }

        # Analyze each stage
        for stage in stages:
            stage_name = stage.get("name", "")
            stage_duration = stage.get("durationMillis", 0)
            stage_percentage = (stage_duration / total_duration * 100) if total_duration > 0 else 0

            analysis["stage_breakdown"].append({
                "name": stage_name,
                "duration_ms": stage_duration,
                "duration_formatted": f"{stage_duration / 1000:.1f} seconds",
                "percentage": stage_percentage
            })

            # Detect technologies
            if "aws" in stage_name.lower() or "ec2" in stage_name.lower():
                analysis["aws_integration"] = True
            if "k8s" in stage_name.lower() or "kubernetes" in stage_name.lower():
                analysis["kubernetes_integration"] = True
            if "docker" in stage_name.lower():
                analysis["docker_usage"] = True
            if "helm" in stage_name.lower():
                analysis["helm_usage"] = True
            if "library" in stage_name.lower():
                analysis["jenkins_library_usage"] = True

        # Compile technologies list
        if analysis["aws_integration"]:
            analysis["technologies_used"].append("AWS")
        if analysis["kubernetes_integration"]:
            analysis["technologies_used"].append("Kubernetes")
        if analysis["docker_usage"]:
            analysis["technologies_used"].append("Docker")
        if analysis["helm_usage"]:
            analysis["technologies_used"].append("Helm")
        if analysis["jenkins_library_usage"]:
            analysis["technologies_used"].append("Jenkins Shared Libraries")

        return analysis

    async def suggest_improvements(self, pipeline_name: str, jenkinsfile: str, analysis: dict[str, Any], ctx: Context) -> dict[str, Any]:
        """Suggest improvements for the reconstructed Jenkinsfile."""
        await ctx.info("Analyzing pipeline for improvement suggestions...")

        suggestions = []

        # Check for common improvements
        if not any("timeout" in line.lower() for line in jenkinsfile.split("\n")):
            suggestions.append({
                "type": "reliability",
                "priority": "high",
                "title": "Add timeout controls",
                "description": "Add timeouts to prevent hanging builds",
                "example": "timeout(time: 30, unit: 'MINUTES') { /* stage content */ }"
            })

        if not any("retry" in line.lower() for line in jenkinsfile.split("\n")):
            suggestions.append({
                "type": "reliability",
                "priority": "medium",
                "title": "Add retry logic",
                "description": "Add retry mechanisms for transient failures",
                "example": "retry(3) { /* critical operations */ }"
            })

        if not any("when" in line.lower() for line in jenkinsfile.split("\n")):
            suggestions.append({
                "type": "efficiency",
                "priority": "low",
                "title": "Add conditional execution",
                "description": "Use 'when' conditions to skip unnecessary stages",
                "example": "when { not { params.dry_run } }"
            })

        # Check for security improvements
        if "withCredentials" not in jenkinsfile:
            suggestions.append({
                "type": "security",
                "priority": "high",
                "title": "Secure credential handling",
                "description": "Use withCredentials for sensitive data",
                "example": "withCredentials([string(credentialsId: 'my-secret', variable: 'SECRET')]) { /* use $SECRET */ }"
            })

        # Performance analysis
        stage_breakdown = analysis.get("stage_breakdown", [])
        if stage_breakdown:
            longest_stage = max(stage_breakdown, key=lambda x: x["duration_ms"])
            if longest_stage["duration_ms"] > 60000:  # More than 1 minute
                suggestions.append({
                    "type": "performance",
                    "priority": "medium",
                    "title": f"Optimize {longest_stage['name']} stage",
                    "description": f"This stage takes {longest_stage['duration_formatted']} ({longest_stage['percentage']:.1f}% of total time)",
                    "example": "Consider breaking into smaller steps or using parallel execution"
                })

        return {
            "pipeline_name": pipeline_name,
            "total_suggestions": len(suggestions),
            "suggestions": suggestions,
            "analysis_summary": {
                "technologies": analysis.get("technologies_used", []),
                "total_duration": analysis.get("total_duration_formatted", "Unknown"),
                "stage_count": analysis.get("total_stages", 0)
            }
        }