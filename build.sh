#!/bin/bash
# Build script for MCP Jenkins Intelligence

set -e

echo "🚀 MCP Jenkins Intelligence - Build Script"
echo "=========================================="

# Check if Python 3.11+ is available
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.11+ is required, but found $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Check if make is available
if ! command -v make &> /dev/null; then
    echo "❌ Error: make is not installed"
    exit 1
fi

echo "✅ Make is available"

# Run the build process
echo ""
echo "🔧 Running build process..."
make quickstart

echo ""
echo "🎉 Build completed successfully!"
echo ""
echo "📦 Binary location: dist/mcp-jenkins-server"
echo "📊 Package location: dist/mcp-jenkins-intelligence-1.0.0.tar.gz"
echo ""
echo "🚀 To run the binary:"
echo "   ./dist/mcp-jenkins-server"
echo ""
echo "📋 To install system-wide:"
echo "   make install-binary"
