/**
 * WiFi Manager Module
 * Handles all WiFi-related functionality independently
 */

class WiFiManager {
    constructor() {
        this.currentNetwork = null;
        this.connectedDevices = [];
        this.networkStats = {
            devices: 0,
            bandwidth: 0,
            uptime: 99.8
        };
        this.captivePortalEnabled = false;

        this.init();
    }

    /**
     * Initialize WiFi Manager
     */
    init() {
        this.setupEventListeners();
        this.checkNetworkStatus();
        this.loadSavedConfig();

        // Update network status every 5 seconds
        setInterval(() => this.checkNetworkStatus(), 5000);

        // Update device list every 10 seconds
        setInterval(() => this.updateConnectedDevices(), 10000);
    }

    /**
     * Setup event listeners for WiFi controls
     */
    setupEventListeners() {
        // WiFi settings button
        const wifiSettingsBtn = document.getElementById('wifi-settings-btn');
        if (wifiSettingsBtn) {
            wifiSettingsBtn.addEventListener('click', () => this.openWiFiModal());
        }

        // Save WiFi configuration
        const saveWiFiBtn = document.getElementById('save-wifi-config');
        if (saveWiFiBtn) {
            saveWiFiBtn.addEventListener('click', () => this.saveWiFiConfig());
        }

        // Save portal configuration
        const savePortalBtn = document.getElementById('save-portal-config');
        if (savePortalBtn) {
            savePortalBtn.addEventListener('click', () => this.savePortalConfig());
        }

        // Captive portal toggle
        const portalToggle = document.getElementById('enable-captive-portal');
        if (portalToggle) {
            portalToggle.addEventListener('change', (e) => {
                this.captivePortalEnabled = e.target.checked;
                this.togglePortalFields(e.target.checked);
            });
        }

        // Network scan button
        const scanBtn = document.getElementById('scan-networks');
        if (scanBtn) {
            scanBtn.addEventListener('click', () => this.scanNetworks());
        }

        // Modal close button
        const closeBtn = document.querySelector('.modal .close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closeWiFiModal());
        }

        // Click outside modal to close
        const modal = document.getElementById('wifi-modal');
        if (modal) {
            window.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeWiFiModal();
                }
            });
        }
    }

    /**
     * Check network connection status
     */
    async checkNetworkStatus() {
        const isOnline = navigator.onLine;
        const wifiIcon = document.getElementById('wifi-icon');
        const wifiStatus = document.getElementById('wifi-status');
        const networkStatus = document.getElementById('network-status');

        if (isOnline) {
            // Check actual internet connectivity
            try {
                const response = await fetch('https://www.google.com/favicon.ico', {
                    mode: 'no-cors',
                    cache: 'no-cache'
                });

                if (wifiIcon) wifiIcon.textContent = '📶';
                if (wifiStatus) wifiStatus.textContent = 'Connected';
                if (networkStatus) {
                    networkStatus.textContent = '🟢 Online';
                    networkStatus.style.color = 'var(--success-color)';
                }
            } catch (error) {
                this.setDisconnectedStatus();
            }
        } else {
            this.setDisconnectedStatus();
        }

        // Try to get network info from API
        try {
            const stats = await api.getNetworkStats();
            if (stats && !stats.error) {
                this.updateNetworkStats(stats);
            }
        } catch (error) {
            // Use mock data in standalone mode
            this.updateNetworkStats(this.networkStats);
        }
    }

    /**
     * Set disconnected status
     */
    setDisconnectedStatus() {
        const wifiIcon = document.getElementById('wifi-icon');
        const wifiStatus = document.getElementById('wifi-status');
        const networkStatus = document.getElementById('network-status');

        if (wifiIcon) wifiIcon.textContent = '📵';
        if (wifiStatus) wifiStatus.textContent = 'Disconnected';
        if (networkStatus) {
            networkStatus.textContent = '🔴 Offline';
            networkStatus.style.color = 'var(--danger-color)';
        }
    }

    /**
     * Update network statistics display
     */
    updateNetworkStats(stats) {
        const totalDevices = document.getElementById('total-devices');
        const bandwidthUsage = document.getElementById('bandwidth-usage');
        const uptime = document.getElementById('uptime');

        if (totalDevices) totalDevices.textContent = stats.devices || this.connectedDevices.length;
        if (bandwidthUsage) bandwidthUsage.textContent = stats.bandwidth || '45 MB/s';
        if (uptime) uptime.textContent = stats.uptime ? `${stats.uptime}%` : '99.8%';
    }

    /**
     * Update connected devices list
     */
    async updateConnectedDevices() {
        try {
            const data = await api.getConnectedDevices();
            if (data && data.devices) {
                this.connectedDevices = data.devices;
                this.renderDeviceList();
            }
        } catch (error) {
            // Use mock data
            this.renderDeviceList();
        }
    }

    /**
     * Render device list
     */
    renderDeviceList() {
        const deviceList = document.getElementById('connected-devices');
        if (!deviceList) return;

        // If no devices from API, use defaults
        if (this.connectedDevices.length === 0) {
            return; // Keep the HTML defaults
        }

        deviceList.innerHTML = this.connectedDevices.map(device => `
            <div class="device-item">
                <span class="device-name">${device.name}</span>
                <span class="device-ip">${device.ip}</span>
                <span class="device-status ${device.online ? 'online' : 'offline'}">
                    ${device.online ? 'Online' : 'Offline'}
                </span>
            </div>
        `).join('');
    }

    /**
     * Save WiFi configuration
     */
    async saveWiFiConfig() {
        const ssid = document.getElementById('wifi-ssid').value;
        const password = document.getElementById('wifi-password').value;
        const type = document.getElementById('wifi-type').value;

        if (!ssid) {
            alert('Please enter a network name (SSID)');
            return;
        }

        const config = {
            ssid: ssid,
            password: password,
            type: type,
            timestamp: new Date().toISOString()
        };

        try {
            // Save to backend if available
            await api.saveWiFiConfig(config);

            // Save to localStorage for standalone mode
            localStorage.setItem('lariat_wifi_config', JSON.stringify(config));

            this.showNotification('WiFi configuration saved successfully!', 'success');
        } catch (error) {
            // Even if API fails, save locally
            localStorage.setItem('lariat_wifi_config', JSON.stringify(config));
            this.showNotification('WiFi configuration saved locally', 'warning');
        }
    }

    /**
     * Save captive portal configuration
     */
    async savePortalConfig() {
        const enabled = document.getElementById('enable-captive-portal').checked;
        const message = document.getElementById('portal-message').value;
        const redirect = document.getElementById('portal-redirect').value;

        const config = {
            enabled: enabled,
            message: message,
            redirect: redirect,
            timestamp: new Date().toISOString()
        };

        try {
            // Save to backend if available
            await api.saveCaptivePortalConfig(config);

            // Save to localStorage for standalone mode
            localStorage.setItem('lariat_portal_config', JSON.stringify(config));

            this.showNotification('Captive portal settings saved successfully!', 'success');
        } catch (error) {
            // Even if API fails, save locally
            localStorage.setItem('lariat_portal_config', JSON.stringify(config));
            this.showNotification('Captive portal settings saved locally', 'warning');
        }
    }

    /**
     * Load saved configuration from localStorage
     */
    loadSavedConfig() {
        // Load WiFi config
        const wifiConfig = localStorage.getItem('lariat_wifi_config');
        if (wifiConfig) {
            try {
                const config = JSON.parse(wifiConfig);
                const ssidInput = document.getElementById('wifi-ssid');
                const typeInput = document.getElementById('wifi-type');

                if (ssidInput) ssidInput.value = config.ssid || '';
                if (typeInput) typeInput.value = config.type || 'guest';
            } catch (error) {
                console.error('Error loading WiFi config:', error);
            }
        }

        // Load portal config
        const portalConfig = localStorage.getItem('lariat_portal_config');
        if (portalConfig) {
            try {
                const config = JSON.parse(portalConfig);
                const enabledInput = document.getElementById('enable-captive-portal');
                const messageInput = document.getElementById('portal-message');
                const redirectInput = document.getElementById('portal-redirect');

                if (enabledInput) {
                    enabledInput.checked = config.enabled || false;
                    this.togglePortalFields(config.enabled);
                }
                if (messageInput) messageInput.value = config.message || '';
                if (redirectInput) redirectInput.value = config.redirect || '';
            } catch (error) {
                console.error('Error loading portal config:', error);
            }
        }
    }

    /**
     * Toggle portal configuration fields
     */
    togglePortalFields(enabled) {
        const messageInput = document.getElementById('portal-message');
        const redirectInput = document.getElementById('portal-redirect');

        if (messageInput) messageInput.disabled = !enabled;
        if (redirectInput) redirectInput.disabled = !enabled;
    }

    /**
     * Scan for available networks
     */
    async scanNetworks() {
        const scanBtn = document.getElementById('scan-networks');
        const originalText = scanBtn.textContent;

        scanBtn.textContent = '🔄 Scanning...';
        scanBtn.disabled = true;

        try {
            const data = await api.scanNetworks();

            if (data && data.networks) {
                this.renderNetworkScan(data.networks);
            } else {
                // Show default networks
                this.showNotification('Showing saved networks', 'info');
            }
        } catch (error) {
            this.showNotification('Network scan failed, showing saved networks', 'warning');
        } finally {
            scanBtn.textContent = originalText;
            scanBtn.disabled = false;
        }
    }

    /**
     * Render scanned networks
     */
    renderNetworkScan(networks) {
        const scanContainer = document.getElementById('network-scan');
        if (!scanContainer) return;

        const networkHTML = networks.map(network => {
            const signalStrength = this.getSignalIcon(network.signal);
            return `
                <div class="network-item" data-ssid="${network.ssid}">
                    <span class="signal-strength">${signalStrength}</span>
                    <span class="network-name">${network.ssid}</span>
                    <span class="network-security">${network.secured ? '🔒' : '🔓'}</span>
                </div>
            `;
        }).join('');

        scanContainer.innerHTML = `<h4>Available Networks</h4>${networkHTML}`;

        // Add click handlers to network items
        scanContainer.querySelectorAll('.network-item').forEach(item => {
            item.addEventListener('click', () => {
                const ssid = item.dataset.ssid;
                document.getElementById('wifi-ssid').value = ssid;
                this.closeWiFiModal();
            });
        });
    }

    /**
     * Get signal strength icon
     */
    getSignalIcon(strength) {
        if (strength >= 75) return '📶📶📶📶';
        if (strength >= 50) return '📶📶📶';
        if (strength >= 25) return '📶📶';
        return '📶';
    }

    /**
     * Open WiFi settings modal
     */
    openWiFiModal() {
        const modal = document.getElementById('wifi-modal');
        if (modal) {
            modal.style.display = 'block';
        }
    }

    /**
     * Close WiFi settings modal
     */
    closeWiFiModal() {
        const modal = document.getElementById('wifi-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    /**
     * Show notification to user
     */
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            background: ${type === 'success' ? 'var(--success-color)' :
                         type === 'warning' ? 'var(--warning-color)' :
                         type === 'error' ? 'var(--danger-color)' :
                         'var(--primary-color)'};
            color: white;
            padding: 15px 25px;
            border-radius: 8px;
            box-shadow: var(--shadow);
            z-index: 1001;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    /**
     * Generate WiFi QR Code
     */
    generateQRCode() {
        const ssid = document.getElementById('wifi-ssid').value;
        const password = document.getElementById('wifi-password').value;

        if (!ssid) return;

        // WiFi QR code format: WIFI:T:WPA;S:SSID;P:PASSWORD;;
        const qrData = `WIFI:T:WPA;S:${ssid};P:${password};;`;

        // In a real implementation, you would use a QR code library
        // For now, we'll show the data
        console.log('QR Code Data:', qrData);
        this.showNotification('QR Code generated (check console)', 'info');
    }
}

// Initialize WiFi Manager
let wifiManager;
document.addEventListener('DOMContentLoaded', () => {
    wifiManager = new WiFiManager();
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
