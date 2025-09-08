# Configuration Guide

## Authentication Options

### Standard Jenkins Authentication
```bash
# Environment variables
JENKINS_URL=https://your-jenkins-instance.com
JENKINS_USERNAME=your-username
JENKINS_TOKEN=your-api-token
JENKINS_VERIFY_SSL=true
```

### Azure Active Directory Authentication
```bash
# Environment variables for Azure AD
JENKINS_URL=https://your-jenkins-instance.com
JENKINS_USERNAME=your-object-id
JENKINS_TOKEN=your-api-token
JENKINS_VERIFY_SSL=true
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `JENKINS_URL` | Jenkins server URL | Required |
| `JENKINS_USERNAME` | Username or Object ID | Required |
| `JENKINS_TOKEN` | API token | Required |
| `JENKINS_VERIFY_SSL` | Verify SSL certificates | `true` |
| `MCP_SERVER_PORT` | **MCP server HTTP transport port** | `8000` |
| `AI_PROVIDER` | AI provider (openai, anthropic) | `openai` |
| `AI_API_KEY` | AI API key | Optional |
| `AI_MODEL` | AI model name | `gpt-4` |

## Port Configuration

The MCP server supports configurable ports for HTTP transport to avoid conflicts:

### **Default Configuration**
```bash
# Default port 8000
fastmcp run server.py --transport http
```

### **Custom Port Configuration**
```bash
# Set custom port via environment variable
MCP_SERVER_PORT=9000 fastmcp run server.py --transport http

# Or use FastMCP's built-in port option
fastmcp run server.py --transport http --port 9000
```

### **Port Conflict Resolution**
If port 8000 is already in use, you can easily change it:

```bash
# Check what's using port 8000
lsof -i :8000

# Use a different port
MCP_SERVER_PORT=9000 fastmcp run server.py --transport http
```

### **MCP Configuration with Custom Port**

**For Cursor:**
Update your `~/.cursor/mcp.json` to use a custom port:

**For VSCode:**
Update your `~/.vscode/mcp.json` to use a custom port:

```json
{
  "mcpServers": {
    "pipeline-awareness": {
      "command": "fastmcp",
      "args": ["run", "/path/to/server.py", "--transport", "http", "--port", "9000"],
      "env": {
        "JENKINS_URL": "https://your-jenkins.com",
        "JENKINS_USERNAME": "your-username",
        "JENKINS_TOKEN": "your-token",
        "MCP_SERVER_PORT": "9000"
      }
    }
  }
}
```

> **Note**: The `MCP_SERVER_PORT` is for the MCP server's HTTP transport, not for Jenkins. Jenkins uses its own port (usually 8080 or 443 for HTTPS).

## Command Line Options

```bash
fastmcp run server.py --help

Options:
  --transport string
        Transport type (stdio, http, sse)
  --port int
        Port for HTTP/SSE transport (default: 8000)
  --verbose
        Enable verbose logging
  --help
        Show help information
```

## Advanced Configuration

### Custom AI Provider
```bash
# Set AI provider
export AI_PROVIDER=anthropic
export AI_API_KEY=your-anthropic-key
export AI_MODEL=claude-3-sonnet
```

### SSL Configuration
```bash
# Disable SSL verification (not recommended for production)
export JENKINS_VERIFY_SSL=false

# Custom CA bundle
export JENKINS_CA_BUNDLE=/path/to/ca-bundle.pem
```

### Logging Configuration
```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG

# Custom log file
export LOG_FILE=/path/to/jenkins-intelligence.log
```
