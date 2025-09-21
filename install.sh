#!/bin/bash

# MCP Jenkins Intelligence Server - Installation Script
# This script downloads the latest binary from GitHub Releases

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO="heniv96/mcp-jenkins-intelligence"
BINARY_NAME="mcp-jenkins-server"
INSTALL_DIR="${HOME}/.local/bin"
CONFIG_DIR="${HOME}/.config"

echo -e "${BLUE}🚀 MCP Jenkins Intelligence Server - Installer${NC}"
echo "=================================================="

# Check if curl is available
if ! command -v curl &> /dev/null; then
    echo -e "${RED}❌ Error: curl is required but not installed.${NC}"
    exit 1
fi

# Check if jq is available for JSON parsing
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}⚠️  Warning: jq is not installed. Using latest release.${NC}"
    LATEST_TAG="latest"
else
    # Get the latest release tag
    LATEST_TAG=$(curl -s "https://api.github.com/repos/${REPO}/releases/latest" | jq -r .tag_name)
fi

echo -e "${BLUE}📦 Downloading ${BINARY_NAME} v${LATEST_TAG}...${NC}"

# Create install directory if it doesn't exist
mkdir -p "${INSTALL_DIR}"

# Download the binary
DOWNLOAD_URL="https://github.com/${REPO}/releases/download/${LATEST_TAG}/${BINARY_NAME}"
curl -L -o "${INSTALL_DIR}/${BINARY_NAME}" "${DOWNLOAD_URL}"

# Make it executable
chmod +x "${INSTALL_DIR}/${BINARY_NAME}"

echo -e "${GREEN}✅ Binary downloaded and installed to ${INSTALL_DIR}/${BINARY_NAME}${NC}"

# Check if the binary is in PATH
if [[ ":$PATH:" != *":${INSTALL_DIR}:"* ]]; then
    echo -e "${YELLOW}⚠️  Warning: ${INSTALL_DIR} is not in your PATH.${NC}"
    echo -e "${YELLOW}   Add this line to your ~/.bashrc or ~/.zshrc:${NC}"
    echo -e "${BLUE}   export PATH=\"\${PATH}:${INSTALL_DIR}\"${NC}"
fi

# Create example MCP configuration
echo -e "${BLUE}📝 Creating example MCP configuration...${NC}"
mkdir -p "${CONFIG_DIR}"

cat > "${CONFIG_DIR}/mcp-jenkins-example.json" << EOF
{
  "mcpServers": {
    "mcp-jenkins-intelligence": {
      "command": "${INSTALL_DIR}/${BINARY_NAME}",
      "args": [],
      "env": {
        "JENKINS_URL": "https://your-jenkins-url",
        "JENKINS_USERNAME": "your-username",
        "JENKINS_TOKEN": "your-token"
      }
    }
  }
}
EOF

echo -e "${GREEN}✅ Example configuration created at ${CONFIG_DIR}/mcp-jenkins-example.json${NC}"

echo ""
echo -e "${GREEN}🎉 Installation complete!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Update your MCP client configuration (Cursor/VSCode) with the path:"
echo "   ${INSTALL_DIR}/${BINARY_NAME}"
echo ""
echo "2. Set your Jenkins credentials in the environment variables:"
echo "   JENKINS_URL, JENKINS_USERNAME, JENKINS_TOKEN"
echo ""
echo "3. Restart your MCP client"
echo ""
echo -e "${BLUE}For more information, visit:${NC}"
echo "https://github.com/${REPO}"
