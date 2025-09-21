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

# Build binary executable
.PHONY: build
build: clean install
	@echo "$(BLUE)Building binary executable...$(NC)"
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