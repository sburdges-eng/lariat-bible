#!/bin/bash
# Build script for The Lariat Bible Desktop App

set -e

echo "=========================================="
echo "Building The Lariat Bible Desktop App"
echo "=========================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESKTOP_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="$(dirname "$DESKTOP_DIR")"

cd "$PROJECT_DIR"

# Step 1: Install Python dependencies
echo ""
echo "[1/5] Installing Python dependencies..."
pip install -r requirements.txt --quiet

# Step 2: Build React frontend
echo ""
echo "[2/5] Building React frontend..."
cd frontend
npm install --silent
npm run build
cd ..

# Step 3: Copy frontend build to desktop app
echo ""
echo "[3/5] Copying frontend build..."
rm -rf desktop/app
cp -r frontend/dist desktop/app

# Step 4: Install Electron dependencies
echo ""
echo "[4/5] Installing Electron dependencies..."
cd desktop
npm install --silent

# Step 5: Build desktop app
echo ""
echo "[5/5] Building desktop installer..."
npm run dist

echo ""
echo "=========================================="
echo "Build complete!"
echo "=========================================="
echo ""
echo "Installers are in: desktop/dist/"
ls -la dist/ 2>/dev/null || echo "(No dist folder yet - run on target platform)"
