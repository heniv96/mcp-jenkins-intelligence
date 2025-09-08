# MCP Jenkins Intelligence

[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.0-purple.svg)](https://github.com/jlowin/fastmcp)
[![Jenkins](https://img.shields.io/badge/Jenkins-API-orange.svg)](https://jenkins.io/)
[![MCP](https://img.shields.io/badge/MCP-Protocol-green.svg)](https://modelcontextprotocol.io/)
[![Stars](https://img.shields.io/github/stars/heniv96/mcp-jenkins-intelligence?style=social)](https://github.com/heniv96/mcp-jenkins-intelligence/stargazers)
[![Issues](https://img.shields.io/github/issues/heniv96/mcp-jenkins-intelligence)](https://github.com/heniv96/mcp-jenkins-intelligence/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/heniv96/mcp-jenkins-intelligence/pulls)

> **The Jenkins Intelligence Platform**  
> Transform your Jenkins operations with AI-powered natural language interfaces and comprehensive pipeline analysis.

## Overview

MCP Jenkins Intelligence is a comprehensive Model Context Protocol (MCP) solution designed for professional DevOps teams. It provides natural language interfaces for complex Jenkins pipeline operations, enabling teams to monitor, analyze, and optimize their CI/CD workflows through AI-powered conversations in VSCode and Cursor.

## ✨ Key Features

### **Intelligent Pipeline Analysis**
- **Real-time Monitoring**: Live pipeline status, health metrics, and performance analytics
- **AI-Powered Insights**: Natural language queries for complex pipeline analysis
- **Failure Analysis**: Deep dive into pipeline failures with intelligent root cause analysis
- **Performance Optimization**: Automated suggestions for improving build times and success rates
- **Advanced Analytics**: Comprehensive reporting and performance comparisons
- **Anomaly Detection**: AI-powered detection of unusual pipeline behavior patterns

### **Advanced AI Capabilities**
- **Natural Language Processing**: Conversational interface for complex DevOps operations
- **Smart Diagnostics**: AI-driven pipeline health analysis and troubleshooting guidance
- **Context-Aware Prompts**: Intelligent prompt suggestions for different analysis scenarios
- **Automated Reporting**: Proactive identification of issues and optimization opportunities

### **Enterprise Security & Compliance**
- **Multi-Authentication Support**: Standard Jenkins and Azure AD integration
- **Secure Communication**: TLS encryption for all Jenkins API communications
- **Audit Logging**: Comprehensive audit trails for all pipeline operations
- **Minimal Privilege**: Secure by design with least privilege access patterns
- **Enterprise-Grade Data Protection**: 19+ protection patterns for complete data anonymization
- **Complete Anonymization**: Pipeline names, cluster names, folder names, app names, branch names, organization names, repository names, and code file names are all protected
- **Hash-based Security**: Sensitive data is replaced with secure hashes before AI communication
- **Local Execution**: All data processing happens locally - no data leaves your environment
- **Recursive Protection**: Works on nested data structures and complex objects
- **Access Control Auditing**: Comprehensive permission and access control analysis

### **Advanced Analytics & Reporting**
- **Comprehensive Reports**: Generate detailed reports with metrics and insights
- **Performance Comparisons**: Compare pipeline performance across teams and environments
- **Trend Analysis**: Long-term performance and reliability trend analysis

### **Advanced AI Features**
- **Anomaly Detection**: AI-powered detection of unusual pipeline behavior patterns
- **Comprehensive Insights**: AI-generated insights and recommendations

### **Performance Optimization**
- **Build Time Analysis**: Detailed analysis and optimization suggestions for build times

### **Deployment & Distribution**
- **Multiple Deployment Options**: Development setup or production deployment
- **Cross-Platform Support**: Works on macOS, Linux, and Windows
- **Easy Configuration**: Simple setup with environment variables or MCP config

## 🏗️ Architecture

### MCP Protocol Integration

The following diagram shows how MCP Jenkins Intelligence integrates with VSCode and Cursor AI through the Model Context Protocol:

```
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐
│ VSCode/     │───▶│ MCP Protocol │───▶│ Jenkins         │
│ Cursor AI   │    └──────────────┘    │ Intelligence    │
└─────────────┘                        │    Server       │
                                       └─────────┬───────┘
                                                 │
                    ┌────────────────────────────┼────────────────────────────┐
                    │                            │                            │
            ┌───────▼───────┐            ┌───────▼───────┐            ┌───────▼───────┐
            │ Jenkins       │            │ AI Analysis   │            │ Pipeline      │
            │ API           │            │ Engine        │            │ Resources     │
            └───────┬───────┘            └───────┬───────┘            └───────┬───────┘
                    │                            │                            │  
                    ┌────────────────────────────┼────────────────────────────┐
                    │                            │                            │
                 ┌───────▼───────┐            ┌───────▼───────┐            ┌───────▼───────┐
                 │ Core Tools    │            │ Analysis      │            │ MCP Resources │
                 │ (30 tools)    │            │ Tools         │            │ & Prompts     │
                 │               │            │               │            │               │
                 │ • List        │            │ • Health      │            │ • Status      │
                 │ • Details     │            │   Analysis    │            │   Resource    │
                 │ • Builds      │            │ • Failure     │            │ • Summary     │
                 │ • Configure   │            │   Analysis    │            │   Resource    │
                 │ • Test        │            │ • AI Queries  │            │ • Dashboard   │
                 │ • Questions   │            │ • Metrics     │            │   Resource    │
                 │ • Trigger     │            │ • Dependencies│            │ • Logs        │
                 │ • Stop        │            │ • Trends      │            │   Resource    │
                 │ • Enable/Dis  │            │ • Security    │            │ • Health      │
                 │ • Config      │            │ • Export      │            │   Resource    │
                 │ • Predict     │            │ • Optimize    │            │ • Analysis    │
                 │ • Suggest     │            │               │            │   Prompts     │
                 └───────────────┘            └───────────────┘            └───────────────┘
```

### Modular Architecture

The internal architecture follows a clean, modular design with separation of concerns:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MCP Layer                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  FastMCP Server  ──▶  Tool Registry  ──▶  Request Router                    │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────────────────────┐
│                           Modular Services                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Models    │  │  Services   │  │  Resources  │  │   Prompts   │        │
│  │             │  │             │  │             │  │             │        │
│  │ • Pipeline  │  │ • Jenkins   │  │ • Status    │  │ • Analysis  │        │
│  │ • Build     │  │ • Core      │  │ • Summary   │  │ • Failure   │        │
│  │ • Health    │  │ • Control   │  │ • Dashboard │  │ • Optimize  │        │
│  │ • Failure   │  │ • Monitor   │  │ • Logs      │  │ • Security  │        │
│  │ • Query     │  │ • AI        │  │ • Health    │  │             │        │
│  │             │  │ • Security  │  │             │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────────────────────┐
│                         Tool Categories                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  Core Tools (9)     │  Control Tools (4)   │  Monitoring (4)  │  AI Tools (5)│
│  ─────────────      │  ─────────────       │  ─────────────   │  ─────────  │
│  • list_pipelines   │  • trigger_build     │  • get_metrics   │ • Predict   │
│  • get_details      │  • stop_build        │  • dependencies  │   Failure   │
│  • get_builds       │  • enable_disable    │  • monitor_queue │ • Suggest   │
│  • ask_questions    │  • get_config        │  • analyze_trends│   Optimize  │
│  • configure_jenkins│                      │                  │ • Anomaly   │
│  • test_connection  │                      │                  │   Detection │
│  • analyze_health   │                      │                  │ • AI        │
│  • analyze_failure  │                      │                  │   Insights  │
│  • get_server_info  │                      │                  │ • Retry     │
│                     │                      │                  │   Logic     │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────────────────┐
│                    Additional Tool Categories                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  Security (2)    │  Jenkinsfile (3)  │  Analytics (2)  │  Performance (1) │
│  ───────────     │  ─────────────    │  ───────────    │  ─────────────   │
│  • scan_security │  • get_jenkinsfile│  • generate_    │  • analyze_      │
│                  │  • reconstruct    │    report       │    build_time    │
│                  │  • suggest_       │  • compare_     │                  │
│                  │    improvements   │    performance  │                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────────────────┐
│                    MCP Resources & Prompts                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  Resources (5)        │  Prompts (4)                                        │
│  ─────────────        │  ───────────                                        │
│  • pipeline://status  │  • analyze_pipeline_prompt                          │
│  • pipeline://{name}/ │  • failure_analysis_prompt                          │
│    summary            │  • optimization_prompt                              │
│  • pipeline://dashboard│  • security_audit_prompt                           │
│  • pipeline://{name}/ │                                                     │
│    logs               │                                                     │
│  • pipeline://health  │                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
mcp-jenkins-intelligence/
├── server.py                 # Clean main server (559 lines)
├── models/
│   ├── __init__.py
│   └── pipeline.py          # Pydantic models
├── services/
│   ├── __init__.py
│   ├── jenkins_service.py   # Jenkins API wrapper
│   ├── core_tools.py        # Core pipeline tools
│   ├── control_tools.py     # Pipeline control tools
│   ├── monitoring_tools.py  # Monitoring & analytics
│   ├── ai_tools.py          # AI intelligence tools
│   ├── security_tools.py    # Security & compliance
│   ├── advanced_ai_tools.py # Advanced AI features
│   ├── advanced_security_tools.py # Advanced security tools
│   ├── analytics_tools.py   # Analytics & reporting
│   ├── jenkinsfile_service.py # Jenkinsfile management
│   └── performance_tools.py # Performance optimization
├── resources/
│   ├── __init__.py
│   └── pipeline_resources.py # MCP resources
├── prompts/
│   ├── __init__.py
│   └── pipeline_prompts.py  # MCP prompts
├── config/
│   └── settings.py          # Configuration management
├── utils/
│   ├── __init__.py
│   └── helpers.py           # Helper functions
├── manuals/
│   └── examples/
│       └── mcp-config-standalone.json # Example configuration
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Project configuration
├── LICENSE                 # MIT License
└── README.md              # This file
```

### Architecture Benefits

#### **🏗️ Modular Design**
- **Single Responsibility**: Each module has one clear purpose
- **Easy Navigation**: Find specific functionality quickly
- **Reduced Complexity**: Each file is focused and manageable
- **Team Collaboration**: Multiple developers can work on different modules

#### **📈 Scalability**
- **Easy Extension**: Add new tools by creating new service classes
- **Modular Testing**: Test individual components in isolation
- **Performance**: Lazy loading and efficient resource management

#### **🔧 Maintainability**
- **Clean Code**: Well-organized, documented, and type-safe
- **No Linting Errors**: Follows Python best practices
- **Version Control**: Easier to track changes and manage conflicts
- **Debugging**: Easier to isolate and fix issues

#### **📊 Code Quality Metrics**
- **Main Server**: 559 lines with clean modular architecture
- **Total Codebase**: 4,768 lines across all Python files
- **Maintainability Index**: Significantly improved with modular design
- **Cyclomatic Complexity**: Reduced per module through separation of concerns

## 🛠️ Available Tools

### **Core Pipeline Management Tools (9 Total)**

| Category | Tools | Description |
|----------|-------|-------------|
| **Core Pipeline Operations (5)** | `list_pipelines`, `get_pipeline_details`, `get_pipeline_builds`, `analyze_pipeline_health`, `analyze_pipeline_failure` | Direct Jenkins API operations, monitoring, and analysis |
| **AI-Powered Analysis (1)** | `ask_pipeline_question` | Natural language queries and intelligent insights |
| **Configuration Management (3)** | `configure_jenkins`, `test_connection`, `get_server_info` | Jenkins connection setup, validation, and server information |

### **Pipeline Control Tools (4 Total) - ⚠️ Safety Confirmation Required**

| Tool | Description | Safety Features |
|------|-------------|-----------------|
| `trigger_pipeline_build` | Trigger a new build with optional parameters | ⚠️ Requires `confirm=True` - explains impact before execution |
| `stop_pipeline_build` | Stop a running pipeline build | ⚠️ Requires `confirm=True` - warns about potential consequences |
| `enable_disable_pipeline` | Enable or disable a pipeline | ⚠️ Requires `confirm=True` - explains what will be affected |
| `get_pipeline_config` | Get pipeline configuration (Jenkinsfile/XML) | ✅ Safe - read-only operation |

**⚠️ Safety Note**: Only the Pipeline Control Tools require safety confirmations. All other tools are read-only or analysis-only operations that cannot modify Jenkins state.

### **Monitoring & Analysis Tools (4 Total)**

| Tool | Description |
|------|-------------|
| `get_pipeline_metrics` | Get detailed metrics (success rate, duration, frequency) |
| `get_pipeline_dependencies` | Get upstream/downstream pipeline dependencies |
| `monitor_pipeline_queue` | Monitor Jenkins build queue and pending builds |
| `analyze_build_trends` | Analyze trends across multiple pipelines |

### **AI Intelligence Tools (5 Total)**

| Tool | Description |
|------|-------------|
| `predict_pipeline_failure` | AI prediction of failure risk based on patterns |
| `suggest_pipeline_optimization` | AI suggestions for performance optimization |
| `detect_pipeline_anomalies` | Detect unusual patterns and anomalies in pipeline behavior using ML |
| `intelligent_retry_logic` | Analyze failure patterns and suggest intelligent retry logic using ML |
| `generate_ai_insights` | Generate comprehensive AI-powered insights about the pipeline using real data analysis |

### **Security Tools (2 Total)**

| Tool | Description |
|------|-------------|
| `scan_pipeline_security` | Security vulnerability scan and best practices check |
| `audit_access_controls` | Audit pipeline access controls and permissions using Jenkins security API |

### **Jenkinsfile Tools (3 Total)**

| Tool | Description |
|------|-------------|
| `get_jenkinsfile` | Get Jenkinsfile (automatically reconstructs if stored in Git) |
| `reconstruct_jenkinsfile` | Reconstruct Jenkinsfile content from pipeline execution data |
| `suggest_pipeline_improvements` | Get improvement suggestions based on reconstructed Jenkinsfile |

### **Advanced Analytics & Reporting Tools (2 Total)**

| Tool | Description |
|------|-------------|
| `generate_pipeline_report` | Generate comprehensive pipeline report based on Jenkins build history |
| `compare_pipeline_performance` | Compare performance across multiple pipelines based on Jenkins build history |

### **Performance Optimization Tools (1 Total)**

| Tool | Description |
|------|-------------|
| `analyze_build_time_optimization` | Analyze build time optimization opportunities using Jenkins data |

#### **🔍 Automatic Jenkinsfile Reconstruction**

The MCP server now automatically detects when a Jenkinsfile is stored in a Git repository (not directly accessible through Jenkins API) and seamlessly reconstructs it:

- **Smart Detection**: Automatically identifies Git-based pipelines
- **Seamless Experience**: When you ask "Show me the Jenkinsfile", it automatically reconstructs it
- **No Manual Steps**: No need to manually call reconstruction tools
- **Rich Metadata**: Includes pipeline analysis and reconstruction details


#### **💡 Smart Improvement Suggestions**

Based on reconstructed Jenkinsfile content, the system provides intelligent suggestions:

- **Performance Optimizations**: Parallel execution, timeout controls, retry logic
- **Security Enhancements**: Credential handling, access controls
- **Reliability Improvements**: Error handling, conditional execution
- **Best Practices**: Jenkins pipeline best practices and patterns

### **MCP Resources (5 Total)**

| Resource | Description |
|----------|-------------|
| `pipeline://status` | Get overall system status and health summary |
| `pipeline://{pipeline_name}/summary` | Get comprehensive pipeline summary with recent builds |
| `pipeline://dashboard` | Get comprehensive dashboard view of all pipelines |
| `pipeline://{pipeline_name}/logs/{build_number}` | Get build logs for a specific pipeline build |
| `pipeline://health` | Get overall system health and alerts |

### **MCP Prompts (4 Total)**

| Prompt | Description |
|--------|-------------|
| `analyze_pipeline_prompt` | Generate prompts for comprehensive pipeline analysis |
| `failure_analysis_prompt` | Generate prompts for failure analysis |
| `optimization_prompt` | Generate prompts for pipeline optimization analysis |
| `security_audit_prompt` | Generate prompts for security audit analysis |

## ⚠️ Safety Features

### **Pipeline Control Safety**
All pipeline control operations require explicit confirmation to prevent accidental changes:

- **`trigger_pipeline_build`**: Shows detailed impact explanation before execution
- **`stop_pipeline_build`**: Warns about potential system inconsistencies
- **`enable_disable_pipeline`**: Explains what will be affected by the change

### **Safety Confirmation Example**
```bash
# First call - shows safety warning
trigger_pipeline_build(pipeline_name="production-deploy", parameters={"env": "prod"})

# Response:
# ⚠️  SAFETY CHECK REQUIRED ⚠️
# 
# You are about to trigger a new build for pipeline 'production-deploy' with parameters: {'env': 'prod'}.
# 
# This will:
# - Start a new build immediately
# - Consume Jenkins resources
# - May trigger downstream pipelines
# - Could affect production systems
# 
# To proceed, call this tool again with confirm=True

# Second call - executes the action
trigger_pipeline_build(pipeline_name="production-deploy", parameters={"env": "prod"}, confirm=True)
```

## 🚀 Quick Start

For detailed installation and setup instructions, see the [Quick Start Guide](manuals/quick-start/README.md).

**TL;DR:**
```bash
git clone https://github.com/heniv96/mcp-jenkins-intelligence.git
cd mcp-jenkins-intelligence
pip install -r requirements.txt
pip install -e .
# Configure Jenkins credentials and MCP settings
# See manuals/quick-start/README.md for details
```

## 📋 Natural Language Examples

### **Pipeline Monitoring**
```
"Show me all my Jenkins pipelines and their current status"
"List all failed pipelines from the last week"
"Get the health status of my production deployment pipeline"
"Show me recent builds for the frontend pipeline"
```

### **Performance Analysis**
```
"What's the average build time for the backend pipeline?"
"Which pipelines are taking the longest to complete?"
"Show me the success rate of my CI/CD pipelines"
"Compare the performance of dev vs prod pipelines"
```

### **Failure Analysis**
```
"Why did the deployment pipeline fail yesterday?"
"Analyze the failure in the frontend pipeline build #456"
"What are the most common failure patterns in my pipelines?"
"Help me troubleshoot the stuck build in the database pipeline"
```

### **AI-Powered Insights**
```
"Suggest improvements for my CI/CD pipeline"
"Generate a performance report for the last month"
"What security issues exist in my pipeline configurations?"
"Which pipelines need immediate attention?"
"Predict which pipelines are likely to fail"
"Optimize my production deployment pipeline"
```

### **Pipeline Control & Management**
```
"Trigger a new build for the frontend pipeline"
"Stop the running build #123 for the backend pipeline"
"Disable the test pipeline temporarily"
"Get the configuration for the production pipeline"
"Show me the dependencies for the deployment pipeline"
```

### **Advanced Analytics & Monitoring**
```
"Get detailed metrics for my production pipeline"
"Analyze build trends across all my pipelines"
"Monitor the Jenkins build queue"
"Export pipeline data in CSV format"
"Scan the security of my deployment pipeline"
```

### **Dashboard & Health Monitoring**
```
"Show me the pipeline dashboard"
"Get the overall system health"
"Check the logs for build #456 of the API pipeline"
"Generate a comprehensive pipeline report"
```

## 🔧 Configuration

For detailed configuration options, see the [Configuration Guide](manuals/configuration/README.md).

**Quick Reference:**
- **Authentication**: Standard Jenkins or Azure AD
- **Environment Variables**: `JENKINS_URL`, `JENKINS_USERNAME`, `JENKINS_TOKEN`
- **Port Configuration**: Customizable MCP server port
- **Command Line Options**: `--transport`, `--port`, `--verbose`

## 🔧 Troubleshooting

For detailed troubleshooting steps, see the [Troubleshooting Guide](manuals/troubleshooting/README.md).

**Common Issues:**
- **401 Unauthorized**: Check credentials and Object ID (Azure AD)
- **Connection Issues**: Verify network connectivity and SSL settings
- **Tool Not Found**: Ensure all dependencies are installed

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Development Commands

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest

# Format code
black .

# Run linter
flake8 .

# Type checking
mypy .
```

### Code Style

- Follow PEP 8 Python formatting
- Use meaningful variable and function names
- Add type hints for all functions
- Include docstrings for public functions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) for the MCP specification
- [FastMCP](https://github.com/jlowin/fastmcp) for the excellent MCP framework
- [Jenkins](https://jenkins.io/) for the amazing CI/CD platform
- [Python](https://python.org/) for the excellent programming language
- The open-source community for inspiration and support

## 📚 Documentation

### Quick Links
- **Getting Started**: See installation section above for detailed setup
- **Configuration**: Authentication options and environment variables
- **Troubleshooting**: Common issues and solutions
- **API Reference**: Complete tool documentation

## 📞 Support

- **Documentation**: [Wiki](https://github.com/heniv96/mcp-jenkins-intelligence/wiki)
- **Issues**: [GitHub Issues](https://github.com/heniv96/mcp-jenkins-intelligence/issues)
- **Discussions**: [GitHub Discussions](https://github.com/heniv96/mcp-jenkins-intelligence/discussions)

---

**Made with ❤️ for the DevOps community**