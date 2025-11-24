const { app, BrowserWindow, Menu, shell, dialog, Tray, nativeImage } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');

// Keep references to prevent garbage collection
let mainWindow;
let pythonProcess;
let tray;
let isQuitting = false;

const isDev = !app.isPackaged;

// Paths
const getAssetPath = (asset) => {
  if (isDev) {
    return path.join(__dirname, 'assets', asset);
  }
  return path.join(process.resourcesPath, 'assets', asset);
};

const getPythonPath = () => {
  if (isDev) {
    return path.join(__dirname, '..');
  }
  return path.join(process.resourcesPath);
};

// Start Python FastAPI backend
function startPythonBackend() {
  return new Promise((resolve, reject) => {
    const pythonPath = getPythonPath();

    // Try different Python commands
    const pythonCommands = ['python3', 'python', 'py'];
    let started = false;

    const tryPython = (index) => {
      if (index >= pythonCommands.length) {
        reject(new Error('Python not found. Please install Python 3.8+'));
        return;
      }

      const cmd = pythonCommands[index];
      console.log(`Trying ${cmd}...`);

      pythonProcess = spawn(cmd, ['-m', 'uvicorn', 'api.main:app', '--port', '8000'], {
        cwd: pythonPath,
        env: { ...process.env, PYTHONPATH: pythonPath }
      });

      pythonProcess.stdout.on('data', (data) => {
        console.log(`Python: ${data}`);
        if (data.toString().includes('Uvicorn running') || data.toString().includes('Application startup')) {
          started = true;
          resolve();
        }
      });

      pythonProcess.stderr.on('data', (data) => {
        console.log(`Python stderr: ${data}`);
        if (data.toString().includes('Uvicorn running') || data.toString().includes('Application startup')) {
          started = true;
          resolve();
        }
      });

      pythonProcess.on('error', () => {
        if (!started) {
          tryPython(index + 1);
        }
      });

      // Timeout and check if server is running
      setTimeout(() => {
        if (!started) {
          checkServerRunning().then(() => {
            started = true;
            resolve();
          }).catch(() => {
            // Keep waiting or try next
          });
        }
      }, 3000);
    };

    tryPython(0);

    // Final timeout
    setTimeout(() => {
      if (!started) {
        checkServerRunning().then(resolve).catch(() => {
          resolve(); // Continue anyway, user might start backend manually
        });
      }
    }, 10000);
  });
}

// Check if backend server is running
function checkServerRunning() {
  return new Promise((resolve, reject) => {
    http.get('http://localhost:8000/health', (res) => {
      resolve();
    }).on('error', reject);
  });
}

// Stop Python backend
function stopPythonBackend() {
  if (pythonProcess) {
    pythonProcess.kill();
    pythonProcess = null;
  }
}

// Create the main application window
function createWindow() {
  // Get icon based on platform
  let icon;
  if (process.platform === 'win32') {
    icon = getAssetPath('icon.ico');
  } else if (process.platform === 'darwin') {
    icon = getAssetPath('icon.icns');
  } else {
    icon = getAssetPath('icon.png');
  }

  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    icon: icon,
    title: 'The Lariat Bible',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    backgroundColor: '#1a1a2e',
    show: false
  });

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Load the app
  if (isDev) {
    // In development, connect to Vite dev server
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    // In production, load built files
    mainWindow.loadFile(path.join(__dirname, 'app', 'index.html'));
  }

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // Minimize to tray instead of closing
  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow.hide();
      return false;
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Create application menu
  createMenu();
}

// Create system tray
function createTray() {
  const iconPath = getAssetPath('icon.png');
  const icon = nativeImage.createFromPath(iconPath);
  tray = new Tray(icon.resize({ width: 16, height: 16 }));

  const contextMenu = Menu.buildFromTemplate([
    { label: 'Open The Lariat Bible', click: () => mainWindow.show() },
    { type: 'separator' },
    { label: 'Recipe Costing', click: () => { mainWindow.show(); mainWindow.webContents.send('navigate', '/recipes'); }},
    { label: 'Ingredients', click: () => { mainWindow.show(); mainWindow.webContents.send('navigate', '/ingredients'); }},
    { label: 'Vendor Import', click: () => { mainWindow.show(); mainWindow.webContents.send('navigate', '/vendors'); }},
    { type: 'separator' },
    { label: 'Quit', click: () => { isQuitting = true; app.quit(); }}
  ]);

  tray.setToolTip('The Lariat Bible');
  tray.setContextMenu(contextMenu);

  tray.on('double-click', () => {
    mainWindow.show();
  });
}

// Create application menu
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Import Vendor Prices',
          accelerator: 'CmdOrCtrl+I',
          click: () => mainWindow.webContents.send('navigate', '/vendors')
        },
        {
          label: 'Export Costing Report',
          accelerator: 'CmdOrCtrl+E',
          click: () => mainWindow.webContents.send('export', 'costing-book')
        },
        { type: 'separator' },
        { role: 'quit' }
      ]
    },
    {
      label: 'View',
      submenu: [
        {
          label: 'Dashboard',
          click: () => mainWindow.webContents.send('navigate', '/')
        },
        {
          label: 'Recipes',
          click: () => mainWindow.webContents.send('navigate', '/recipes')
        },
        {
          label: 'Ingredients',
          click: () => mainWindow.webContents.send('navigate', '/ingredients')
        },
        {
          label: 'Menu Items',
          click: () => mainWindow.webContents.send('navigate', '/menu-items')
        },
        { type: 'separator' },
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Tools',
      submenu: [
        {
          label: 'Cost All Recipes',
          click: () => mainWindow.webContents.send('action', 'cost-all')
        },
        {
          label: 'Auto-Link Ingredients',
          click: () => mainWindow.webContents.send('action', 'auto-link')
        },
        { type: 'separator' },
        {
          label: 'Settings',
          accelerator: 'CmdOrCtrl+,',
          click: () => mainWindow.webContents.send('navigate', '/settings')
        }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About The Lariat Bible',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About The Lariat Bible',
              message: 'The Lariat Bible v1.0.0',
              detail: 'Restaurant Recipe Costing System\n\nBuilt for The Lariat, Fort Collins, CO\n\nManage recipes, track ingredient costs, and optimize your food cost percentage.'
            });
          }
        }
      ]
    }
  ];

  // macOS specific menu adjustments
  if (process.platform === 'darwin') {
    template.unshift({
      label: app.name,
      submenu: [
        { role: 'about' },
        { type: 'separator' },
        { role: 'services' },
        { type: 'separator' },
        { role: 'hide' },
        { role: 'hideOthers' },
        { role: 'unhide' },
        { type: 'separator' },
        { role: 'quit' }
      ]
    });
  }

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// App lifecycle
app.whenReady().then(async () => {
  // Show splash or loading state
  console.log('Starting The Lariat Bible...');

  // Start Python backend
  try {
    await startPythonBackend();
    console.log('Backend started');
  } catch (err) {
    console.error('Backend failed to start:', err.message);
    // Continue anyway - backend might already be running
  }

  createWindow();
  createTray();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    } else {
      mainWindow.show();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  isQuitting = true;
  stopPythonBackend();
});

app.on('quit', () => {
  stopPythonBackend();
});
