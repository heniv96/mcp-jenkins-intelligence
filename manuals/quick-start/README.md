# Quick Start Guide

## Prerequisites

- Python 3.8 or later
- Jenkins instance with API access
- VSCode or Cursor AI with MCP support
- macOS, Linux, or Windows operating system

## Installation

**Quick Setup:**
1. **Clone and install**
   ```bash
   git clone https://github.com/heniv96/mcp-jenkins-intelligence.git
   cd mcp-jenkins-intelligence
   pip install -r requirements.txt
   pip install -e .
   ```

2. **Configure Jenkins Authentication**

   **Option A: Standard Jenkins**
   ```bash
   # Create .env file
   echo "JENKINS_URL=https://your-jenkins-instance.com" >> .env
   echo "JENKINS_USERNAME=your-username" >> .env
   echo "JENKINS_TOKEN=your-api-token" >> .env
   ```

   **Option B: Azure AD Integration**
   ```bash
   # Create .env file for Azure AD
   echo "JENKINS_URL=https://your-jenkins-instance.com" >> .env
   echo "JENKINS_USERNAME=your-object-id" >> .env
   echo "JENKINS_TOKEN=your-api-token" >> .env
   ```

3. **Configure VSCode/Cursor AI**

   **For Cursor:**
   Add to your `~/.cursor/mcp.json`:
   ```json
   {
     "mcpServers": {
       "pipeline-awareness": {
         "command": "fastmcp",
         "args": ["run", "/path/to/mcp-jenkins-intelligence/server.py", "--transport", "stdio"],
         "env": {
           "JENKINS_URL": "https://your-jenkins-instance.com",
           "JENKINS_USERNAME": "your-username",
           "JENKINS_TOKEN": "your-api-token"
         }
       }
     }
   }
   ```

   **For VSCode:**
   Add to your `~/.vscode/mcp.json`:
   ```json
   {
     "mcpServers": {
       "pipeline-awareness": {
         "command": "fastmcp",
         "args": ["run", "/path/to/mcp-jenkins-intelligence/server.py", "--transport", "stdio"],
         "env": {
           "JENKINS_URL": "https://your-jenkins-instance.com",
           "JENKINS_USERNAME": "your-username",
           "JENKINS_TOKEN": "your-api-token"
         }
       }
     }
   }
   ```

4. **Restart VSCode/Cursor AI** and start using natural language commands!

## Basic Usage

```bash
# List all pipelines
"Show me all my Jenkins pipelines"

# Get pipeline details
"Get details for the frontend-deployment pipeline"

# Analyze pipeline health
"Analyze the health of my production pipeline"

# Troubleshoot failures
"Why did the backend-deployment pipeline fail in build #123?"

# AI-powered insights
"What are the most common failure patterns in my pipelines?"
```

## Next Steps

- See [Configuration Guide](../configuration/README.md) for advanced setup
- See [Troubleshooting Guide](../troubleshooting/README.md) for common issues
- Explore the [Natural Language Examples](../../README.md#-natural-language-examples) for more usage patterns
