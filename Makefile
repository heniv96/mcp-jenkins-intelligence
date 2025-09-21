# MCP Jenkins Intelligence - Makefile
# Build automation for MCP Jenkins Intelligence Server

# Variables
PYTHON := python3
PIP := pip3
PYINSTALLER := pyinstaller
PACKAGE_NAME := mcp-jenkins-intelligence
VERSION := 1.0.0
BINARY_NAME := mcp-jenkins-server
DIST_DIR := dist
BUILD_DIR := build
SPEC_FILE := $(PACKAGE_NAME).spec

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Default target
.PHONY: all
all: clean install build

# Help target
.PHONY: help
help:
	@echo "$(BLUE)MCP Jenkins Intelligence - Available Targets$(NC)"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  install     - Install dependencies"
	@echo "  clean       - Clean build artifacts"
	@echo "  format      - Format code with black and ruff"
	@echo "  lint        - Run linting checks"
	@echo ""
	@echo "$(GREEN)Building:$(NC)"
	@echo "  build       - Build binary executable"
	@echo "  build-dev   - Build development binary"
	@echo "  package     - Create distribution package"
	@echo ""
	@echo "$(GREEN)Running:$(NC)"
	@echo "  run         - Run the server in development mode"
	@echo "  run-binary  - Run the built binary"
	@echo ""
	@echo "$(GREEN)Utilities:$(NC)"
	@echo "  deps        - Show dependency tree"
	@echo "  check       - Run all checks (lint only)"
	@echo "  release     - Prepare for release"

# Install dependencies
.PHONY: install
install:
	@echo "$(BLUE)Installing dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

# Clean build artifacts
.PHONY: clean
clean:
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf $(BUILD_DIR)
	rm -rf $(DIST_DIR)
	rm -f *.spec
	rm -rf __pycache__
	rm -rf .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)✓ Build artifacts cleaned$(NC)"

# Format code
.PHONY: format
format:
	@echo "$(BLUE)Formatting code...$(NC)"
	black .
	ruff --fix .
	@echo "$(GREEN)✓ Code formatted$(NC)"

# Run linting
.PHONY: lint
lint:
	@echo "$(BLUE)Running linting checks...$(NC)"
	ruff check .
	mypy .
	@echo "$(GREEN)✓ Linting passed$(NC)"

# Build binary executable for current platform
.PHONY: build
build: clean install
	@echo "$(BLUE)Building binary executable for current platform...$(NC)"
	$(PYINSTALLER) --onefile \
		--name $(BINARY_NAME) \
		--add-data "prompts:prompts" \
		--add-data "resources:resources" \
		--add-data "models:models" \
		--add-data "utils:utils" \
		--add-data "services:services" \
		--add-data "config:config" \
		--hidden-import="fastmcp" \
		--hidden-import="jenkins" \
		--hidden-import="pydantic" \
		--hidden-import="requests" \
		--hidden-import="numpy" \
		--hidden-import="sklearn" \
		--hidden-import="sklearn.ensemble" \
		--hidden-import="sklearn.ensemble.IsolationForest" \
		--hidden-import="sklearn.cluster" \
		--hidden-import="sklearn.metrics" \
		--hidden-import="sklearn.linear_model" \
		--hidden-import="sklearn.neighbors" \
		--hidden-import="sklearn.tree" \
		--hidden-import="pandas" \
		--hidden-import="plotly" \
		--hidden-import="openai" \
		--hidden-import="anthropic" \
		--hidden-import="anyio" \
		--hidden-import="click" \
		--hidden-import="tenacity" \
		--hidden-import="croniter" \
		--hidden-import="uvicorn" \
		--hidden-import="starlette" \
		--hidden-import="fastapi" \
		--hidden-import="httpx" \
		--hidden-import="jinja2" \
		--hidden-import="rich" \
		--hidden-import="tabulate" \
		--hidden-import="python-dateutil" \
		--hidden-import="scipy" \
		--hidden-import="importlib_metadata" \
		--collect-all="fastmcp" \
		--collect-all="importlib_metadata" \
		server.py
	@echo "$(BLUE)Cleaning up build artifacts...$(NC)"
	rm -rf $(BUILD_DIR)
	rm -f $(SPEC_FILE)
	@echo "$(GREEN)✓ Binary built successfully$(NC)"
	@echo "$(YELLOW)Binary location: $(DIST_DIR)/$(BINARY_NAME)$(NC)"

# Build for macOS ARM64 (Apple Silicon)
.PHONY: build-macos-arm64
build-macos-arm64: clean install
	@echo "$(BLUE)Building binary for macOS ARM64...$(NC)"
	$(PYINSTALLER) --onefile \
		--name $(BINARY_NAME)-macos-arm64 \
		--add-data "prompts:prompts" \
		--add-data "resources:resources" \
		--add-data "models:models" \
		--add-data "utils:utils" \
		--add-data "services:services" \
		--add-data "config:config" \
		--hidden-import="fastmcp" \
		--hidden-import="jenkins" \
		--hidden-import="pydantic" \
		--hidden-import="requests" \
		--hidden-import="numpy" \
		--hidden-import="sklearn" \
		--hidden-import="sklearn.ensemble" \
		--hidden-import="sklearn.ensemble.IsolationForest" \
		--hidden-import="sklearn.cluster" \
		--hidden-import="sklearn.metrics" \
		--hidden-import="sklearn.linear_model" \
		--hidden-import="sklearn.neighbors" \
		--hidden-import="sklearn.tree" \
		--hidden-import="pandas" \
		--hidden-import="plotly" \
		--hidden-import="openai" \
		--hidden-import="anthropic" \
		--hidden-import="anyio" \
		--hidden-import="click" \
		--hidden-import="tenacity" \
		--hidden-import="croniter" \
		--hidden-import="uvicorn" \
		--hidden-import="starlette" \
		--hidden-import="fastapi" \
		--hidden-import="httpx" \
		--hidden-import="jinja2" \
		--hidden-import="rich" \
		--hidden-import="tabulate" \
		--hidden-import="python-dateutil" \
		--hidden-import="scipy" \
		--hidden-import="importlib_metadata" \
		--collect-all="fastmcp" \
		--collect-all="importlib_metadata" \
		server.py
	@echo "$(BLUE)Cleaning up build artifacts...$(NC)"
	rm -rf $(BUILD_DIR)
	rm -f $(SPEC_FILE)
	@echo "$(GREEN)✓ macOS ARM64 binary built successfully$(NC)"
	@echo "$(YELLOW)Binary location: $(DIST_DIR)/$(BINARY_NAME)-macos-arm64$(NC)"

# Build for Linux AMD64
.PHONY: build-linux-amd64
build-linux-amd64: clean install
	@echo "$(BLUE)Building binary for Linux AMD64...$(NC)"
	$(PYINSTALLER) --onefile \
		--name $(BINARY_NAME)-linux-amd64 \
		--add-data "prompts:prompts" \
		--add-data "resources:resources" \
		--add-data "models:models" \
		--add-data "utils:utils" \
		--add-data "services:services" \
		--add-data "config:config" \
		--hidden-import="fastmcp" \
		--hidden-import="jenkins" \
		--hidden-import="pydantic" \
		--hidden-import="requests" \
		--hidden-import="numpy" \
		--hidden-import="sklearn" \
		--hidden-import="sklearn.ensemble" \
		--hidden-import="sklearn.ensemble.IsolationForest" \
		--hidden-import="sklearn.cluster" \
		--hidden-import="sklearn.metrics" \
		--hidden-import="sklearn.linear_model" \
		--hidden-import="sklearn.neighbors" \
		--hidden-import="sklearn.tree" \
		--hidden-import="pandas" \
		--hidden-import="plotly" \
		--hidden-import="openai" \
		--hidden-import="anthropic" \
		--hidden-import="anyio" \
		--hidden-import="click" \
		--hidden-import="tenacity" \
		--hidden-import="croniter" \
		--hidden-import="uvicorn" \
		--hidden-import="starlette" \
		--hidden-import="fastapi" \
		--hidden-import="httpx" \
		--hidden-import="jinja2" \
		--hidden-import="rich" \
		--hidden-import="tabulate" \
		--hidden-import="python-dateutil" \
		--hidden-import="scipy" \
		--hidden-import="importlib_metadata" \
		--collect-all="fastmcp" \
		--collect-all="importlib_metadata" \
		server.py
	@echo "$(BLUE)Cleaning up build artifacts...$(NC)"
	rm -rf $(BUILD_DIR)
	rm -f $(SPEC_FILE)
	@echo "$(GREEN)✓ Linux AMD64 binary built successfully$(NC)"
	@echo "$(YELLOW)Binary location: $(DIST_DIR)/$(BINARY_NAME)-linux-amd64$(NC)"

# Build all platforms
.PHONY: build-all
build-all: build-macos-arm64 build-linux-amd64
	@echo "$(GREEN)✓ All platform binaries built successfully$(NC)"
	@echo "$(YELLOW)Binaries location: $(DIST_DIR)/$(NC)"
	@ls -la $(DIST_DIR)/

# Build development binary (with debug info)
.PHONY: build-dev
build-dev: clean install
	@echo "$(BLUE)Building development binary...$(NC)"
	$(PYINSTALLER) --onefile --debug=all \
		--name $(BINARY_NAME)-dev \
		--add-data "prompts:prompts" \
		--add-data "resources:resources" \
		--add-data "models:models" \
		--add-data "utils:utils" \
		--add-data "services:services" \
		--add-data "config:config" \
		--hidden-import="sklearn" \
		--hidden-import="sklearn.ensemble" \
		--hidden-import="sklearn.ensemble.IsolationForest" \
		--hidden-import="sklearn.cluster" \
		--hidden-import="sklearn.metrics" \
		--hidden-import="sklearn.linear_model" \
		--hidden-import="sklearn.neighbors" \
		--hidden-import="sklearn.tree" \
		--hidden-import="importlib_metadata" \
		--collect-all="fastmcp" \
		--collect-all="importlib_metadata" \
		server.py
	@echo "$(BLUE)Cleaning up build artifacts...$(NC)"
	rm -rf $(BUILD_DIR)
	rm -f $(SPEC_FILE)
	@echo "$(GREEN)✓ Development binary built$(NC)"

# Create distribution package
.PHONY: package
package: build
	@echo "$(BLUE)Creating distribution package...$(NC)"
	mkdir -p $(DIST_DIR)/package
	cp $(DIST_DIR)/$(BINARY_NAME) $(DIST_DIR)/package/
	cp README.md $(DIST_DIR)/package/
	cp LICENSE $(DIST_DIR)/package/
	cp requirements.txt $(DIST_DIR)/package/
	cp -r manuals $(DIST_DIR)/package/
	cd $(DIST_DIR) && tar -czf $(PACKAGE_NAME)-$(VERSION).tar.gz package/
	@echo "$(GREEN)✓ Package created: $(DIST_DIR)/$(PACKAGE_NAME)-$(VERSION).tar.gz$(NC)"

# Run server in development mode
.PHONY: run
run:
	@echo "$(BLUE)Running server in development mode...$(NC)"
	$(PYTHON) server.py

# Run built binary
.PHONY: run-binary
run-binary:
	@echo "$(BLUE)Running built binary...$(NC)"
	./$(DIST_DIR)/$(BINARY_NAME)

# Show dependency tree
.PHONY: deps
deps:
	@echo "$(BLUE)Dependency tree:$(NC)"
	$(PIP) show --tree $(PACKAGE_NAME) || $(PIP) list

# Run all checks
.PHONY: check
check: lint
	@echo "$(GREEN)✓ All checks passed$(NC)"

# Prepare for release
.PHONY: release
release: clean check build package
	@echo "$(GREEN)✓ Release preparation complete$(NC)"
	@echo "$(YELLOW)Release artifacts:$(NC)"
	@echo "  - Binary: $(DIST_DIR)/$(BINARY_NAME)"
	@echo "  - Package: $(DIST_DIR)/$(PACKAGE_NAME)-$(VERSION).tar.gz"

# Create GitHub release
.PHONY: github-release
github-release: build-all
	@echo "$(BLUE)Creating GitHub release...$(NC)"
	@if [ -z "$(VERSION)" ]; then echo "$(RED)Error: VERSION is required. Use: make github-release VERSION=v1.0.0$(NC)"; exit 1; fi
	@echo "$(BLUE)Creating release notes...$(NC)"
	@echo "## 🚀 MCP Jenkins Intelligence Server $(VERSION)" > /tmp/release_notes.md
	@echo "" >> /tmp/release_notes.md
	@echo "### ✨ Features" >> /tmp/release_notes.md
	@echo "- **Self-contained binary executables** - no Python installation required" >> /tmp/release_notes.md
	@echo "- **Multi-platform support** - macOS ARM64 and Linux AMD64" >> /tmp/release_notes.md
	@echo "- **33 MCP tools** for comprehensive Jenkins pipeline analysis" >> /tmp/release_notes.md
	@echo "- **Auto-configuration** using environment variables" >> /tmp/release_notes.md
	@echo "- **AI-powered insights** and failure analysis" >> /tmp/release_notes.md
	@echo "- **Jenkinsfile retrieval** with 100% accuracy" >> /tmp/release_notes.md
	@echo "- **Security scanning** and vulnerability detection" >> /tmp/release_notes.md
	@echo "- **Performance optimization** suggestions" >> /tmp/release_notes.md
	@echo "" >> /tmp/release_notes.md
	@echo "### 🛠️ Installation" >> /tmp/release_notes.md
	@echo "1. Download the appropriate binary for your platform from this release" >> /tmp/release_notes.md
	@echo "2. Make it executable: \`chmod +x mcp-jenkins-server-<platform>\`" >> /tmp/release_notes.md
	@echo "3. Configure your MCP client (Cursor/VSCode) to use the binary" >> /tmp/release_notes.md
	@echo "" >> /tmp/release_notes.md
	@echo "### 📦 Available Binaries" >> /tmp/release_notes.md
	@echo "- **\`mcp-jenkins-server-macos-arm64\`** - macOS Apple Silicon (M1/M2/M3)" >> /tmp/release_notes.md
	@echo "- **\`mcp-jenkins-server-linux-amd64\`** - Linux AMD64 (Ubuntu, Debian, CentOS, etc.)" >> /tmp/release_notes.md
	@echo "" >> /tmp/release_notes.md
	@echo "### 📋 MCP Configuration" >> /tmp/release_notes.md
	@echo "\`\`\`json" >> /tmp/release_notes.md
	@echo "{" >> /tmp/release_notes.md
	@echo "  \"mcpServers\": {" >> /tmp/release_notes.md
	@echo "    \"mcp-jenkins-intelligence\": {" >> /tmp/release_notes.md
	@echo "      \"command\": \"/path/to/mcp-jenkins-server-<platform>\"," >> /tmp/release_notes.md
	@echo "      \"args\": []," >> /tmp/release_notes.md
	@echo "      \"env\": {" >> /tmp/release_notes.md
	@echo "        \"JENKINS_URL\": \"https://your-jenkins-url\"," >> /tmp/release_notes.md
	@echo "        \"JENKINS_USERNAME\": \"your-username\"," >> /tmp/release_notes.md
	@echo "        \"JENKINS_TOKEN\": \"your-token\"" >> /tmp/release_notes.md
	@echo "      }" >> /tmp/release_notes.md
	@echo "    }" >> /tmp/release_notes.md
	@echo "  }" >> /tmp/release_notes.md
	@echo "}" >> /tmp/release_notes.md
	@echo "\`\`\`" >> /tmp/release_notes.md
	@echo "" >> /tmp/release_notes.md
	@echo "### 🔧 Available Tools" >> /tmp/release_notes.md
	@echo "- **Core Tools**: List pipelines, get details, analyze health" >> /tmp/release_notes.md
	@echo "- **Monitoring Tools**: Metrics, dependencies, queue monitoring" >> /tmp/release_notes.md
	@echo "- **AI Tools**: Failure prediction, optimization suggestions" >> /tmp/release_notes.md
	@echo "- **Security Tools**: Vulnerability scanning" >> /tmp/release_notes.md
	@echo "- **Jenkinsfile Tools**: Retrieve and analyze Jenkinsfiles" >> /tmp/release_notes.md
	@echo "- **Advanced Tools**: Reports, comparisons, anomaly detection" >> /tmp/release_notes.md
	@echo "" >> /tmp/release_notes.md
	@echo "### 🏗️ Build Information" >> /tmp/release_notes.md
	@echo "- **Platforms**: macOS ARM64, Linux AMD64" >> /tmp/release_notes.md
	@echo "- **Python**: 3.13.7" >> /tmp/release_notes.md
	@echo "- **Dependencies**: All included in binaries" >> /tmp/release_notes.md
	@echo "- **Size**: ~73MB per binary" >> /tmp/release_notes.md
	@echo "" >> /tmp/release_notes.md
	@echo "### 📖 Documentation" >> /tmp/release_notes.md
	@echo "See the README.md for detailed usage instructions and examples." >> /tmp/release_notes.md
	@gh release create $(VERSION) dist/$(BINARY_NAME)-macos-arm64 dist/$(BINARY_NAME)-linux-amd64 \
		--title "MCP Jenkins Intelligence Server $(VERSION)" \
		--notes-file /tmp/release_notes.md
	@rm -f /tmp/release_notes.md
	@echo "$(GREEN)✓ GitHub release $(VERSION) created with multi-platform binaries$(NC)"

# Install binary system-wide (requires sudo)
.PHONY: install-binary
install-binary: build
	@echo "$(BLUE)Installing binary system-wide...$(NC)"
	sudo cp $(DIST_DIR)/$(BINARY_NAME) /usr/local/bin/
	sudo chmod +x /usr/local/bin/$(BINARY_NAME)
	@echo "$(GREEN)✓ Binary installed to /usr/local/bin/$(BINARY_NAME)$(NC)"

# Uninstall binary
.PHONY: uninstall-binary
uninstall-binary:
	@echo "$(BLUE)Uninstalling binary...$(NC)"
	sudo rm -f /usr/local/bin/$(BINARY_NAME)
	@echo "$(GREEN)✓ Binary uninstalled$(NC)"

# Show binary info
.PHONY: info
info:
	@echo "$(BLUE)Binary Information:$(NC)"
	@echo "  Name: $(BINARY_NAME)"
	@echo "  Version: $(VERSION)"
	@echo "  Location: $(DIST_DIR)/$(BINARY_NAME)"
	@if [ -f "$(DIST_DIR)/$(BINARY_NAME)" ]; then \
		echo "  Size: $$(du -h $(DIST_DIR)/$(BINARY_NAME) | cut -f1)"; \
		echo "  Status: $(GREEN)✓ Built$(NC)"; \
	else \
		echo "  Status: $(RED)✗ Not built$(NC)"; \
	fi

# Quick start (install and build)
.PHONY: quickstart
quickstart: install build
	@echo "$(GREEN)✓ Quick start complete!$(NC)"
	@echo "$(YELLOW)Run with: ./$(DIST_DIR)/$(BINARY_NAME)$(NC)"