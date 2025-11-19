/**
 * API Communication Layer
 * Handles all communication with the Flask backend
 * Can work independently or with backend
 */

class LariatAPI {
    constructor(baseURL = '') {
        this.baseURL = baseURL || window.location.origin;
        this.isOnline = false;
        this.checkConnection();
    }

    /**
     * Check if backend API is available
     */
    async checkConnection() {
        try {
            const response = await fetch(`${this.baseURL}/health`, {
                method: 'GET',
                timeout: 5000
            });
            this.isOnline = response.ok;
            this.updateConnectionStatus();
            return this.isOnline;
        } catch (error) {
            console.warn('Backend API not available, running in standalone mode');
            this.isOnline = false;
            this.updateConnectionStatus();
            return false;
        }
    }

    /**
     * Update UI connection status
     */
    updateConnectionStatus() {
        const apiStatus = document.getElementById('api-status');
        if (apiStatus) {
            if (this.isOnline) {
                apiStatus.textContent = '🟢 Online';
                apiStatus.style.color = 'var(--success-color)';
            } else {
                apiStatus.textContent = '🔴 Offline (Standalone Mode)';
                apiStatus.style.color = 'var(--danger-color)';
            }
        }
    }

    /**
     * Generic API request handler
     */
    async request(endpoint, options = {}) {
        try {
            const url = `${this.baseURL}${endpoint}`;
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API Request Failed: ${endpoint}`, error);

            // Return mock data in standalone mode
            return this.getMockData(endpoint);
        }
    }

    /**
     * Get mock data for standalone mode
     */
    getMockData(endpoint) {
        const mockData = {
            '/api/vendors': {
                vendors: [
                    {
                        name: 'SYSCO',
                        products: 150,
                        total_cost: 12500,
                        avg_savings: '18%'
                    },
                    {
                        name: 'Shamrock Foods',
                        products: 145,
                        total_cost: 8900,
                        avg_savings: '29.5%'
                    }
                ],
                total_savings: 52000
            },
            '/api/recipes': {
                recipes: [
                    {
                        id: 1,
                        name: 'Western Burger',
                        ingredients: 12,
                        cost: 4.50,
                        category: 'Burgers'
                    },
                    {
                        id: 2,
                        name: 'BBQ Ribs',
                        ingredients: 8,
                        cost: 8.75,
                        category: 'Entrees'
                    },
                    {
                        id: 3,
                        name: 'House Salad',
                        ingredients: 10,
                        cost: 2.25,
                        category: 'Salads'
                    }
                ]
            },
            '/api/menu': {
                items: [
                    {
                        id: 1,
                        name: 'Western Burger',
                        price: 12.99,
                        cost: 4.50,
                        margin: '65%'
                    },
                    {
                        id: 2,
                        name: 'BBQ Ribs',
                        price: 18.99,
                        cost: 8.75,
                        margin: '54%'
                    }
                ]
            },
            '/api/equipment': {
                equipment: [
                    {
                        id: 1,
                        name: 'Industrial Oven',
                        purchase_date: '2022-03-15',
                        cost: 8500,
                        status: 'operational',
                        next_maintenance: '2025-12-01'
                    },
                    {
                        id: 2,
                        name: 'Walk-in Freezer',
                        purchase_date: '2021-06-20',
                        cost: 12000,
                        status: 'operational',
                        next_maintenance: '2025-11-25'
                    }
                ]
            }
        };

        return mockData[endpoint] || { error: 'No mock data available' };
    }

    /**
     * Vendor API methods
     */
    async getVendors() {
        return this.request('/api/vendors');
    }

    async getVendorComparison() {
        return this.request('/api/vendors/comparison');
    }

    /**
     * Recipe API methods
     */
    async getRecipes() {
        return this.request('/api/recipes');
    }

    async getRecipe(id) {
        return this.request(`/api/recipes/${id}`);
    }

    async createRecipe(recipeData) {
        return this.request('/api/recipes', {
            method: 'POST',
            body: JSON.stringify(recipeData)
        });
    }

    /**
     * Menu API methods
     */
    async getMenuItems() {
        return this.request('/api/menu');
    }

    async getMenuItem(id) {
        return this.request(`/api/menu/${id}`);
    }

    /**
     * Equipment API methods
     */
    async getEquipment() {
        return this.request('/api/equipment');
    }

    async getEquipmentItem(id) {
        return this.request(`/api/equipment/${id}`);
    }

    /**
     * WiFi API methods
     */
    async getWiFiConfig() {
        return this.request('/api/wifi/config');
    }

    async saveWiFiConfig(config) {
        return this.request('/api/wifi/config', {
            method: 'POST',
            body: JSON.stringify(config)
        });
    }

    async getConnectedDevices() {
        return this.request('/api/wifi/devices');
    }

    async getNetworkStats() {
        return this.request('/api/wifi/stats');
    }

    async scanNetworks() {
        return this.request('/api/wifi/scan');
    }

    async getCaptivePortalConfig() {
        return this.request('/api/wifi/portal');
    }

    async saveCaptivePortalConfig(config) {
        return this.request('/api/wifi/portal', {
            method: 'POST',
            body: JSON.stringify(config)
        });
    }
}

// Initialize API client
const api = new LariatAPI();

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LariatAPI;
}
