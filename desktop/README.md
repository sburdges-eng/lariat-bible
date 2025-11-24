# The Lariat Bible - Desktop App

Installable desktop application for The Lariat restaurant management system.

## Prerequisites

- **Node.js** 18+ (for building the app)
- **Python** 3.8+ (for the backend)
- **npm** or **yarn**

## Quick Start (Development)

### 1. Install Dependencies

```bash
# Install Python dependencies (from project root)
cd ..
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install

# Install desktop app dependencies
cd ../desktop
npm install
```

### 2. Run in Development Mode

Start the backend and frontend in separate terminals:

**Terminal 1 - Backend:**
```bash
cd ..
uvicorn api.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd ../frontend
npm run dev
```

**Terminal 3 - Electron:**
```bash
npm start
```

## Building the Installer

### Automated Build

**macOS/Linux:**
```bash
chmod +x scripts/build.sh
./scripts/build.sh
```

**Windows:**
```cmd
scripts\build.bat
```

### Manual Build Steps

1. Build the React frontend:
   ```bash
   cd ../frontend
   npm run build
   ```

2. Copy build to desktop app:
   ```bash
   cp -r dist ../desktop/app
   ```

3. Build the installer:
   ```bash
   cd ../desktop
   npm run dist
   ```

The installer will be in `desktop/dist/`.

## Platform-Specific Builds

```bash
# Windows
npm run build:win

# macOS
npm run build:mac

# Linux
npm run build:linux
```

## App Icon

The Lariat logo is in `assets/logo.svg`. To generate platform icons:

1. Install sharp: `npm install sharp`
2. Run: `node scripts/generate-icons.js`
3. For Windows `.ico` and macOS `.icns`, use additional tools or online converters

## Features

- **Native Menu Bar** - Access all features from the menu
- **System Tray** - Quick access when minimized
- **Offline Capable** - Works without internet (external data requires connection)
- **Auto-starts Backend** - Python FastAPI server starts automatically

## Troubleshooting

### Backend doesn't start
- Ensure Python 3.8+ is installed and in PATH
- Install dependencies: `pip install -r requirements.txt`
- Check if port 8000 is available

### App shows blank screen
- Wait for backend to start (can take a few seconds)
- Check developer console (View > Toggle Developer Tools)

### Icons not showing
- Run icon generation script
- Ensure `assets/icon.png` exists
