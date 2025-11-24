const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods to renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  // Navigation from menu
  onNavigate: (callback) => {
    ipcRenderer.on('navigate', (event, path) => callback(path));
  },

  // Actions from menu
  onAction: (callback) => {
    ipcRenderer.on('action', (event, action) => callback(action));
  },

  // Export triggers from menu
  onExport: (callback) => {
    ipcRenderer.on('export', (event, type) => callback(type));
  },

  // Get app version
  getVersion: () => {
    return '1.0.0';
  },

  // Platform info
  platform: process.platform
});
