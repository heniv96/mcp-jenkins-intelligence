# Troubleshooting Guide

## Authentication Issues

### 401 Unauthorized Error
If you're getting 401 Unauthorized errors:

1. **Verify your credentials:**
   - For standard Jenkins: Use your Jenkins username and API token
   - For Azure AD: Use your Object ID (not email) and API token

2. **Check your Object ID (Azure AD):**
   - Log into Azure Portal
   - Go to Azure Active Directory → Users
   - Find your user → Object ID field
   - It should look like: `ghrrrf1c-655a9-33hh-b123-e6f5999e4ege`

3. **Generate a fresh API token:**
   - Log into Jenkins
   - Go to your profile → Configure
   - Generate a new API token
   - Update your configuration

4. **Test your credentials manually:**
   ```bash
   # Test with curl
   curl -u "your-username:your-token" https://your-jenkins.com/api/json
   
   # For Azure AD
   curl -u "your-object-id:your-token" https://your-jenkins.com/api/json
   ```

### "Jenkins not configured" Error
This means the MCP server needs to be configured internally:

1. **Use the configure_jenkins tool** in your AI assistant:
   - "Configure Jenkins with URL: https://your-jenkins.com, username: your-username, token: your-token"

2. **Or restart VSCode/Cursor** after updating your MCP configuration

## Common Configuration Mistakes

1. **Using email instead of Object ID (Azure AD):**
   - ❌ Wrong: `JENKINS_USERNAME=example@user-ad.com`
   - ✅ Correct: `JENKINS_USERNAME=12394912-ft43-9f91-f10d-example123`

2. **Using wrong token format:**
   - Make sure you're using the API token, not your password
   - API tokens are usually longer and contain letters/numbers

3. **Missing environment variables:**
   - Ensure all required environment variables are set
   - Check for typos in variable names

## Connection Issues

### Network Connectivity
```bash
# Test basic connectivity
ping your-jenkins-instance.com

# Test HTTPS connectivity
curl -I https://your-jenkins-instance.com

# Test with authentication
curl -u "username:token" https://your-jenkins-instance.com/api/json
```

### SSL Certificate Issues
```bash
# Check SSL certificate
openssl s_client -connect your-jenkins-instance.com:443 -servername your-jenkins-instance.com

# Disable SSL verification (temporary)
export JENKINS_VERIFY_SSL=false
```

## MCP Server Issues

### Server Not Starting
```bash
# Check if port is available
lsof -i :8000

# Use different port
MCP_SERVER_PORT=9000 fastmcp run server.py --transport http

# Check logs
fastmcp run server.py --transport stdio --verbose
```

### Tool Not Found Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (requires 3.8+)
- Verify MCP configuration syntax

## Performance Issues

### Slow Response Times
1. **Check Jenkins server performance:**
   ```bash
   # Test API response time
   time curl -u "username:token" https://your-jenkins.com/api/json
   ```

2. **Optimize query parameters:**
   - Use `limit` parameter to reduce data transfer
   - Filter by status when possible

3. **Check network latency:**
   ```bash
   # Test network speed
   curl -w "@curl-format.txt" -o /dev/null -s "https://your-jenkins.com/api/json"
   ```

### Memory Issues
- Reduce `limit` parameters in queries
- Close unused MCP connections
- Restart the MCP server periodically

## Debug Mode

### Enable Verbose Logging
```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# Or use command line flag
fastmcp run server.py --verbose
```

### Test Individual Tools
```bash
# Test connection
python -c "from services.jenkins_service import JenkinsService; js = JenkinsService(); js.initialize('https://your-jenkins.com', 'username', 'token'); print('Connected!')"
```

## Getting Help

### Log Files
- Check application logs for detailed error messages
- Look for stack traces in error output
- Enable debug logging for more information

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `401 Unauthorized` | Wrong credentials | Check username/token |
| `Connection refused` | Network issue | Check URL and connectivity |
| `SSL verification failed` | Certificate issue | Check SSL settings |
| `Tool not found` | Missing dependency | Install requirements |
| `Timeout` | Slow response | Check Jenkins performance |

### Support Resources
- Check the [Configuration Guide](../configuration/README.md) for setup details
- Review the [Quick Start Guide](../quick-start/README.md) for basic setup
- Open an issue on GitHub for bugs or feature requests
