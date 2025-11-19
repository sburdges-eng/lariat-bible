/**
 * Main Application Logic
 * Handles UI interactions and data display
 */

class LariatApp {
    constructor() {
        this.currentTab = 'dashboard';
        this.data = {
            vendors: [],
            recipes: [],
            menu: [],
            equipment: []
        };

        this.init();
    }

    /**
     * Initialize the application
     */
    init() {
        this.setupTabNavigation();
        this.loadDashboardData();
        this.checkDatabaseStatus();

        // Refresh data every 30 seconds
        setInterval(() => this.refreshData(), 30000);
    }

    /**
     * Setup tab navigation
     */
    setupTabNavigation() {
        const tabButtons = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tabName = button.dataset.tab;

                // Remove active class from all buttons and contents
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));

                // Add active class to clicked button and corresponding content
                button.classList.add('active');
                document.getElementById(`${tabName}-tab`).classList.add('active');

                // Load data for the selected tab
                this.loadTabData(tabName);
            });
        });
    }

    /**
     * Load dashboard data
     */
    async loadDashboardData() {
        try {
            // Load all data in parallel
            const [vendors, recipes, menu, equipment] = await Promise.all([
                api.getVendors(),
                api.getRecipes(),
                api.getMenuItems(),
                api.getEquipment()
            ]);

            this.data.vendors = vendors.vendors || [];
            this.data.recipes = recipes.recipes || [];
            this.data.menu = menu.items || [];
            this.data.equipment = equipment.equipment || [];

            this.updateDashboardMetrics();
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.updateDashboardMetrics(); // Use mock data
        }
    }

    /**
     * Update dashboard metrics
     */
    updateDashboardMetrics() {
        const recipeCount = document.getElementById('recipe-count');
        const menuCount = document.getElementById('menu-count');

        if (recipeCount) {
            recipeCount.textContent = this.data.recipes.length || 3;
        }

        if (menuCount) {
            menuCount.textContent = this.data.menu.length || 2;
        }
    }

    /**
     * Check database status
     */
    async checkDatabaseStatus() {
        const dbStatus = document.getElementById('db-status');
        if (!dbStatus) return;

        try {
            const isOnline = await api.checkConnection();

            if (isOnline) {
                dbStatus.textContent = '🟢 Connected';
                dbStatus.style.color = 'var(--success-color)';
            } else {
                dbStatus.textContent = '🟡 Standalone Mode';
                dbStatus.style.color = 'var(--warning-color)';
            }
        } catch (error) {
            dbStatus.textContent = '🟡 Standalone Mode';
            dbStatus.style.color = 'var(--warning-color)';
        }
    }

    /**
     * Load data for specific tab
     */
    async loadTabData(tabName) {
        switch (tabName) {
            case 'vendors':
                this.loadVendorsTab();
                break;
            case 'recipes':
                this.loadRecipesTab();
                break;
            case 'menu':
                this.loadMenuTab();
                break;
            case 'equipment':
                this.loadEquipmentTab();
                break;
            case 'wifi':
                // WiFi tab is handled by WiFiManager
                break;
            default:
                break;
        }
    }

    /**
     * Load vendors tab
     */
    async loadVendorsTab() {
        const container = document.getElementById('vendor-comparison');
        if (!container) return;

        container.innerHTML = '<p class="loading">Loading vendor data</p>';

        try {
            const data = await api.getVendors();
            this.data.vendors = data.vendors || [];

            if (this.data.vendors.length === 0) {
                container.innerHTML = '<p>No vendor data available</p>';
                return;
            }

            container.innerHTML = this.renderVendorComparison(this.data.vendors);
        } catch (error) {
            container.innerHTML = '<p>Error loading vendor data</p>';
        }
    }

    /**
     * Render vendor comparison
     */
    renderVendorComparison(vendors) {
        return `
            <div class="vendor-grid">
                ${vendors.map(vendor => `
                    <div class="vendor-card card">
                        <h4>${vendor.name}</h4>
                        <div class="vendor-stats">
                            <div class="stat-row">
                                <span>Products:</span>
                                <strong>${vendor.products || 0}</strong>
                            </div>
                            <div class="stat-row">
                                <span>Total Cost:</span>
                                <strong>$${(vendor.total_cost || 0).toLocaleString()}</strong>
                            </div>
                            <div class="stat-row">
                                <span>Avg Savings:</span>
                                <strong class="success-text">${vendor.avg_savings || '0%'}</strong>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
            <style>
                .vendor-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                }
                .vendor-card h4 {
                    color: var(--primary-color);
                    margin-bottom: 15px;
                    font-size: 1.3rem;
                }
                .vendor-stats {
                    display: grid;
                    gap: 10px;
                }
                .stat-row {
                    display: flex;
                    justify-content: space-between;
                    padding: 10px;
                    background: var(--light-bg);
                    border-radius: 6px;
                }
                .success-text {
                    color: var(--success-color);
                }
            </style>
        `;
    }

    /**
     * Load recipes tab
     */
    async loadRecipesTab() {
        const container = document.getElementById('recipe-list');
        if (!container) return;

        container.innerHTML = '<p class="loading">Loading recipes</p>';

        try {
            const data = await api.getRecipes();
            this.data.recipes = data.recipes || [];

            if (this.data.recipes.length === 0) {
                container.innerHTML = '<p>No recipes found. Click "Add Recipe" to create one.</p>';
                return;
            }

            container.innerHTML = this.renderRecipeList(this.data.recipes);
        } catch (error) {
            container.innerHTML = '<p>Error loading recipes</p>';
        }

        // Setup add recipe button
        const addBtn = document.getElementById('add-recipe-btn');
        if (addBtn) {
            addBtn.onclick = () => this.showAddRecipeForm();
        }

        // Setup search
        const searchInput = document.getElementById('recipe-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterRecipes(e.target.value);
            });
        }
    }

    /**
     * Render recipe list
     */
    renderRecipeList(recipes) {
        return `
            <div class="recipe-grid">
                ${recipes.map(recipe => `
                    <div class="recipe-card card">
                        <h4>${recipe.name}</h4>
                        <div class="recipe-details">
                            <span class="badge">${recipe.category || 'Uncategorized'}</span>
                            <div class="recipe-stats">
                                <span>🥘 ${recipe.ingredients || 0} ingredients</span>
                                <span>💰 $${(recipe.cost || 0).toFixed(2)} cost</span>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
            <style>
                .recipe-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                    gap: 15px;
                }
                .recipe-card h4 {
                    color: var(--primary-color);
                    margin-bottom: 10px;
                }
                .recipe-details {
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }
                .badge {
                    display: inline-block;
                    padding: 4px 12px;
                    background: var(--accent-color);
                    color: white;
                    border-radius: 12px;
                    font-size: 0.85rem;
                    width: fit-content;
                }
                .recipe-stats {
                    display: flex;
                    flex-direction: column;
                    gap: 5px;
                    color: var(--text-light);
                    font-size: 0.9rem;
                }
            </style>
        `;
    }

    /**
     * Filter recipes by search term
     */
    filterRecipes(searchTerm) {
        const filtered = this.data.recipes.filter(recipe =>
            recipe.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            (recipe.category && recipe.category.toLowerCase().includes(searchTerm.toLowerCase()))
        );

        const container = document.getElementById('recipe-list');
        if (container) {
            container.innerHTML = this.renderRecipeList(filtered);
        }
    }

    /**
     * Load menu tab
     */
    async loadMenuTab() {
        const container = document.getElementById('menu-list');
        if (!container) return;

        container.innerHTML = '<p class="loading">Loading menu items</p>';

        try {
            const data = await api.getMenuItems();
            this.data.menu = data.items || [];

            if (this.data.menu.length === 0) {
                container.innerHTML = '<p>No menu items found. Click "Add Menu Item" to create one.</p>';
                return;
            }

            container.innerHTML = this.renderMenuList(this.data.menu);
        } catch (error) {
            container.innerHTML = '<p>Error loading menu items</p>';
        }

        // Setup add menu item button
        const addBtn = document.getElementById('add-menu-item-btn');
        if (addBtn) {
            addBtn.onclick = () => this.showAddMenuItemForm();
        }
    }

    /**
     * Render menu list
     */
    renderMenuList(items) {
        return `
            <div class="menu-grid">
                ${items.map(item => `
                    <div class="menu-card card">
                        <h4>${item.name}</h4>
                        <div class="menu-pricing">
                            <div class="price-row">
                                <span>Menu Price:</span>
                                <strong>$${(item.price || 0).toFixed(2)}</strong>
                            </div>
                            <div class="price-row">
                                <span>Cost:</span>
                                <span>$${(item.cost || 0).toFixed(2)}</span>
                            </div>
                            <div class="price-row margin-row">
                                <span>Margin:</span>
                                <strong class="success-text">${item.margin || '0%'}</strong>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
            <style>
                .menu-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                    gap: 15px;
                }
                .menu-card h4 {
                    color: var(--primary-color);
                    margin-bottom: 15px;
                }
                .menu-pricing {
                    display: grid;
                    gap: 8px;
                }
                .price-row {
                    display: flex;
                    justify-content: space-between;
                    padding: 8px;
                    background: var(--light-bg);
                    border-radius: 6px;
                }
                .margin-row {
                    border-left: 4px solid var(--success-color);
                }
            </style>
        `;
    }

    /**
     * Load equipment tab
     */
    async loadEquipmentTab() {
        const container = document.getElementById('equipment-list');
        if (!container) return;

        container.innerHTML = '<p class="loading">Loading equipment</p>';

        try {
            const data = await api.getEquipment();
            this.data.equipment = data.equipment || [];

            if (this.data.equipment.length === 0) {
                container.innerHTML = '<p>No equipment found. Click "Add Equipment" to create an entry.</p>';
                return;
            }

            container.innerHTML = this.renderEquipmentList(this.data.equipment);
        } catch (error) {
            container.innerHTML = '<p>Error loading equipment</p>';
        }

        // Setup add equipment button
        const addBtn = document.getElementById('add-equipment-btn');
        if (addBtn) {
            addBtn.onclick = () => this.showAddEquipmentForm();
        }
    }

    /**
     * Render equipment list
     */
    renderEquipmentList(equipment) {
        return `
            <div class="equipment-grid">
                ${equipment.map(item => `
                    <div class="equipment-card card">
                        <h4>${item.name}</h4>
                        <div class="equipment-details">
                            <div class="detail-row">
                                <span>Purchased:</span>
                                <span>${new Date(item.purchase_date).toLocaleDateString()}</span>
                            </div>
                            <div class="detail-row">
                                <span>Cost:</span>
                                <strong>$${(item.cost || 0).toLocaleString()}</strong>
                            </div>
                            <div class="detail-row">
                                <span>Status:</span>
                                <span class="status-badge ${item.status}">${item.status || 'Unknown'}</span>
                            </div>
                            <div class="detail-row">
                                <span>Next Maintenance:</span>
                                <span>${new Date(item.next_maintenance).toLocaleDateString()}</span>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
            <style>
                .equipment-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
                    gap: 15px;
                }
                .equipment-card h4 {
                    color: var(--primary-color);
                    margin-bottom: 15px;
                }
                .equipment-details {
                    display: grid;
                    gap: 10px;
                }
                .detail-row {
                    display: flex;
                    justify-content: space-between;
                    padding: 10px;
                    background: var(--light-bg);
                    border-radius: 6px;
                    font-size: 0.95rem;
                }
                .status-badge.operational {
                    color: var(--success-color);
                    font-weight: 500;
                }
            </style>
        `;
    }

    /**
     * Show add recipe form (placeholder)
     */
    showAddRecipeForm() {
        alert('Add Recipe functionality coming soon!\n\nThis will allow you to:\n- Create new recipes\n- Add ingredients\n- Calculate costs\n- Link to menu items');
    }

    /**
     * Show add menu item form (placeholder)
     */
    showAddMenuItemForm() {
        alert('Add Menu Item functionality coming soon!\n\nThis will allow you to:\n- Create menu items\n- Link to recipes\n- Set pricing\n- Calculate margins');
    }

    /**
     * Show add equipment form (placeholder)
     */
    showAddEquipmentForm() {
        alert('Add Equipment functionality coming soon!\n\nThis will allow you to:\n- Add new equipment\n- Track maintenance\n- Monitor depreciation\n- Set reminders');
    }

    /**
     * Refresh all data
     */
    async refreshData() {
        console.log('Refreshing data...');
        await this.loadDashboardData();

        // Refresh current tab
        this.loadTabData(this.currentTab);
    }
}

// Initialize app when DOM is ready
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new LariatApp();
});
