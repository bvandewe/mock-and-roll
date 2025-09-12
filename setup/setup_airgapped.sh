#!/bin/bash
"""
Air-gapped environment setup script for Mock-and-Roll.

This script prepares the Mock-and-Roll server for air-gapped environments
by downloading necessary Swagger UI assets and configuring local serving.
"""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATIC_DIR="$PROJECT_ROOT/src/static/swagger-ui"

echo -e "${GREEN}Mock-and-Roll Air-gapped Setup${NC}"
echo "======================================"

# Check if static directory exists
if [[ ! -d "$STATIC_DIR" ]]; then
    echo -e "${YELLOW}Creating static directory...${NC}"
    mkdir -p "$STATIC_DIR"
fi

# Download Swagger UI assets
echo -e "${YELLOW}Downloading Swagger UI assets...${NC}"
cd "$STATIC_DIR"

# Download the assets
SWAGGER_VERSION="5.9.0"
echo "Downloading swagger-ui-bundle.js..."
curl -L -o swagger-ui-bundle.js "https://unpkg.com/swagger-ui-dist@$SWAGGER_VERSION/swagger-ui-bundle.js"

echo "Downloading swagger-ui.css..."
curl -L -o swagger-ui.css "https://unpkg.com/swagger-ui-dist@$SWAGGER_VERSION/swagger-ui.css"

echo "Downloading swagger-ui-standalone-preset.js..."
curl -L -o swagger-ui-standalone-preset.js "https://unpkg.com/swagger-ui-dist@$SWAGGER_VERSION/swagger-ui-standalone-preset.js"

# Verify downloads
echo -e "${YELLOW}Verifying downloads...${NC}"
MISSING_FILES=()

if [[ ! -f "swagger-ui-bundle.js" ]]; then
    MISSING_FILES+=("swagger-ui-bundle.js")
fi

if [[ ! -f "swagger-ui.css" ]]; then
    MISSING_FILES+=("swagger-ui.css")
fi

if [[ ! -f "swagger-ui-standalone-preset.js" ]]; then
    MISSING_FILES+=("swagger-ui-standalone-preset.js")
fi

if [[ ${#MISSING_FILES[@]} -eq 0 ]]; then
    echo -e "${GREEN}✓ All Swagger UI assets downloaded successfully!${NC}"
    echo ""
    echo "Files downloaded to: $STATIC_DIR"
    echo "  - swagger-ui-bundle.js ($(du -h swagger-ui-bundle.js | cut -f1))"
    echo "  - swagger-ui.css ($(du -h swagger-ui.css | cut -f1))"
    echo "  - swagger-ui-standalone-preset.js ($(du -h swagger-ui-standalone-preset.js | cut -f1))"
else
    echo -e "${RED}✗ Missing files: ${MISSING_FILES[*]}${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "To enable air-gapped mode for your configuration:"
echo "1. Add the following to your api.json configuration:"
echo '   "swagger_ui": {'
echo '     "airgapped_mode": true,'
echo '     "doc_expansion": "none",'
echo '     "display_request_duration": true'
echo '   }'
echo ""
echo "2. Start your server with the configured profile:"
echo "   ./mockctl start --config your-config-name"
echo ""
echo "3. Access Swagger UI at http://localhost:PORT/docs"
echo "   (assets will be served locally, no internet required)"
echo ""
echo -e "${YELLOW}Example airgapped configuration is available at:${NC}"
echo "   configs/airgapped/"
echo ""
echo "Test with: ./mockctl start --config airgapped"
