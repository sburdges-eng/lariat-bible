/**
 * The Lariat Bible - Interactive Components
 * Real-time calculators, sortable tables, and interactive features
 */

// ==================== Interactive Vendor Comparison Table ====================

class VendorComparisonTable {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.vendors = [];
        this.sortColumn = 'name';
        this.sortDirection = 'asc';
        this.filterText = '';
        this.init();
    }

    init() {
        if (!this.container) return;

        // Load sample data (replace with API call)
        this.vendors = [
            {
                name: 'Shamrock Foods',
                category: 'Broadline',
                priceScore: 85,
                qualityScore: 90,
                deliveryScore: 88,
                avgPrice: '$1,250',
                monthlySavings: 4333,
                status: 'active'
            },
            {
                name: 'SYSCO',
                category: 'Broadline',
                priceScore: 72,
                qualityScore: 85,
                deliveryScore: 90,
                avgPrice: '$1,610',
                monthlySavings: 0,
                status: 'active'
            },
            {
                name: 'US Foods',
                category: 'Broadline',
                priceScore: 68,
                qualityScore: 82,
                deliveryScore: 85,
                avgPrice: '$1,750',
                monthlySavings: -140,
                status: 'pending'
            },
            {
                name: 'Restaurant Depot',
                category: 'Cash & Carry',
                priceScore: 92,
                qualityScore: 75,
                deliveryScore: 60,
                avgPrice: '$980',
                monthlySavings: 630,
                status: 'active'
            }
        ];

        this.render();
        this.attachEvents();
    }

    render() {
        // Apply filter
        let filteredVendors = this.vendors;
        if (this.filterText) {
            filteredVendors = this.vendors.filter(v =>
                v.name.toLowerCase().includes(this.filterText.toLowerCase()) ||
                v.category.toLowerCase().includes(this.filterText.toLowerCase())
            );
        }

        // Apply sort
        filteredVendors.sort((a, b) => {
            let aVal = a[this.sortColumn];
            let bVal = b[this.sortColumn];

            // Handle numbers vs strings
            if (typeof aVal === 'number') {
                return this.sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
            } else {
                return this.sortDirection === 'asc' ?
                    aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
            }
        });

        // Generate HTML
        const html = `
            <div class="vendor-table-controls">
                <input
                    type="text"
                    class="vendor-filter-input"
                    placeholder="Filter vendors..."
                    value="${this.filterText}"
                >
                <button class="btn btn-secondary" id="refreshVendors">
                    <i class="fas fa-sync"></i> Refresh
                </button>
            </div>
            <div class="table-responsive">
                <table class="vendor-table">
                    <thead>
                        <tr>
                            <th data-sort="name">
                                Vendor <i class="fas fa-sort"></i>
                            </th>
                            <th data-sort="category">
                                Category <i class="fas fa-sort"></i>
                            </th>
                            <th data-sort="priceScore">
                                Price Score <i class="fas fa-sort"></i>
                            </th>
                            <th data-sort="qualityScore">
                                Quality <i class="fas fa-sort"></i>
                            </th>
                            <th data-sort="deliveryScore">
                                Delivery <i class="fas fa-sort"></i>
                            </th>
                            <th data-sort="avgPrice">
                                Avg Order <i class="fas fa-sort"></i>
                            </th>
                            <th data-sort="monthlySavings">
                                Monthly Savings <i class="fas fa-sort"></i>
                            </th>
                            <th data-sort="status">
                                Status <i class="fas fa-sort"></i>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        ${filteredVendors.map(v => this.renderRow(v)).join('')}
                    </tbody>
                </table>
            </div>
        `;

        this.container.innerHTML = html;
    }

    renderRow(vendor) {
        const statusClass = vendor.status === 'active' ? 'status-active' :
                           vendor.status === 'pending' ? 'status-pending' : 'status-inactive';

        const savingsClass = vendor.monthlySavings > 0 ? 'savings-positive' :
                            vendor.monthlySavings < 0 ? 'savings-negative' : 'savings-neutral';

        return `
            <tr class="vendor-row" data-vendor="${vendor.name}">
                <td><strong>${vendor.name}</strong></td>
                <td>${vendor.category}</td>
                <td>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${vendor.priceScore}%"></div>
                        <span class="score-text">${vendor.priceScore}</span>
                    </div>
                </td>
                <td>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${vendor.qualityScore}%"></div>
                        <span class="score-text">${vendor.qualityScore}</span>
                    </div>
                </td>
                <td>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${vendor.deliveryScore}%"></div>
                        <span class="score-text">${vendor.deliveryScore}</span>
                    </div>
                </td>
                <td>${vendor.avgPrice}</td>
                <td class="${savingsClass}">
                    ${vendor.monthlySavings > 0 ? '+' : ''}$${Math.abs(vendor.monthlySavings).toLocaleString()}
                </td>
                <td><span class="status-badge ${statusClass}">${vendor.status}</span></td>
            </tr>
        `;
    }

    attachEvents() {
        // Sort headers
        const headers = this.container.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.addEventListener('click', () => {
                const column = header.dataset.sort;
                if (this.sortColumn === column) {
                    this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
                } else {
                    this.sortColumn = column;
                    this.sortDirection = 'asc';
                }
                this.render();
                this.attachEvents();
            });
        });

        // Filter input
        const filterInput = this.container.querySelector('.vendor-filter-input');
        if (filterInput) {
            filterInput.addEventListener('input', (e) => {
                this.filterText = e.target.value;
                this.render();
                this.attachEvents();
            });
        }

        // Refresh button
        const refreshBtn = document.getElementById('refreshVendors');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refresh());
        }

        // Row clicks
        const rows = this.container.querySelectorAll('.vendor-row');
        rows.forEach(row => {
            row.addEventListener('click', () => {
                const vendorName = row.dataset.vendor;
                this.showVendorDetails(vendorName);
            });
        });
    }

    async refresh() {
        // TODO: Fetch from API
        console.log('Refreshing vendor data...');
        window.LariatBible.showToast('Vendor data refreshed', 'success');
    }

    showVendorDetails(vendorName) {
        console.log('Show details for:', vendorName);
        window.LariatBible.showToast(`Showing details for ${vendorName}`, 'info');
    }
}

// ==================== Real-Time Recipe Cost Calculator ====================

class RecipeCostCalculator {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.ingredients = [];
        this.init();
    }

    init() {
        if (!this.container) return;
        this.render();
    }

    render() {
        const totalCost = this.calculateTotal();
        const perServing = this.servings > 0 ? totalCost / this.servings : 0;

        const html = `
            <div class="recipe-calculator">
                <div class="calculator-header">
                    <h3>Recipe Cost Calculator</h3>
                    <div class="serving-input">
                        <label>Servings:</label>
                        <input type="number" id="servingCount" value="4" min="1" max="1000">
                    </div>
                </div>

                <div class="ingredients-list">
                    <div class="ingredient-header">
                        <span>Ingredient</span>
                        <span>Quantity</span>
                        <span>Unit</span>
                        <span>Cost</span>
                        <span></span>
                    </div>
                    ${this.ingredients.map((ing, idx) => this.renderIngredient(ing, idx)).join('')}
                    <button class="btn-add-ingredient" id="addIngredient">
                        <i class="fas fa-plus"></i> Add Ingredient
                    </button>
                </div>

                <div class="cost-summary">
                    <div class="summary-row">
                        <span>Total Cost:</span>
                        <strong>${this.formatCurrency(totalCost)}</strong>
                    </div>
                    <div class="summary-row">
                        <span>Cost Per Serving:</span>
                        <strong>${this.formatCurrency(perServing)}</strong>
                    </div>
                    <div class="summary-row highlight">
                        <span>Target Food Cost (30%):</span>
                        <strong>${this.formatCurrency(perServing / 0.30)}</strong>
                    </div>
                </div>
            </div>
        `;

        this.container.innerHTML = html;
        this.attachEvents();
    }

    renderIngredient(ingredient, index) {
        return `
            <div class="ingredient-row">
                <input type="text" class="ing-name" value="${ingredient.name}" data-idx="${index}">
                <input type="number" class="ing-qty" value="${ingredient.quantity}" min="0" step="0.01" data-idx="${index}">
                <select class="ing-unit" data-idx="${index}">
                    <option ${ingredient.unit === 'cup' ? 'selected' : ''}>cup</option>
                    <option ${ingredient.unit === 'lb' ? 'selected' : ''}>lb</option>
                    <option ${ingredient.unit === 'oz' ? 'selected' : ''}>oz</option>
                    <option ${ingredient.unit === 'tbsp' ? 'selected' : ''}>tbsp</option>
                    <option ${ingredient.unit === 'tsp' ? 'selected' : ''}>tsp</option>
                    <option ${ingredient.unit === 'each' ? 'selected' : ''}>each</option>
                </select>
                <input type="number" class="ing-cost" value="${ingredient.cost}" min="0" step="0.01" data-idx="${index}">
                <button class="btn-remove" data-idx="${index}">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    }

    attachEvents() {
        // Add ingredient button
        const addBtn = document.getElementById('addIngredient');
        if (addBtn) {
            addBtn.addEventListener('click', () => {
                this.ingredients.push({
                    name: 'New Ingredient',
                    quantity: 1,
                    unit: 'cup',
                    cost: 0
                });
                this.render();
            });
        }

        // Remove buttons
        const removeButtons = this.container.querySelectorAll('.btn-remove');
        removeButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const idx = parseInt(btn.dataset.idx);
                this.ingredients.splice(idx, 1);
                this.render();
            });
        });

        // Input changes - real-time update
        const inputs = this.container.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('input', () => this.updateFromInputs());
        });
    }

    updateFromInputs() {
        // Update servings
        const servingInput = document.getElementById('servingCount');
        if (servingInput) {
            this.servings = parseInt(servingInput.value) || 4;
        }

        // Update ingredients
        const nameInputs = this.container.querySelectorAll('.ing-name');
        const qtyInputs = this.container.querySelectorAll('.ing-qty');
        const unitInputs = this.container.querySelectorAll('.ing-unit');
        const costInputs = this.container.querySelectorAll('.ing-cost');

        nameInputs.forEach((input, idx) => {
            if (this.ingredients[idx]) {
                this.ingredients[idx].name = input.value;
                this.ingredients[idx].quantity = parseFloat(qtyInputs[idx].value) || 0;
                this.ingredients[idx].unit = unitInputs[idx].value;
                this.ingredients[idx].cost = parseFloat(costInputs[idx].value) || 0;
            }
        });

        // Re-render summary only
        const totalCost = this.calculateTotal();
        const perServing = this.servings > 0 ? totalCost / this.servings : 0;

        const summary = this.container.querySelector('.cost-summary');
        if (summary) {
            summary.innerHTML = `
                <div class="summary-row">
                    <span>Total Cost:</span>
                    <strong>${this.formatCurrency(totalCost)}</strong>
                </div>
                <div class="summary-row">
                    <span>Cost Per Serving:</span>
                    <strong>${this.formatCurrency(perServing)}</strong>
                </div>
                <div class="summary-row highlight">
                    <span>Suggested Menu Price (30% food cost):</span>
                    <strong>${this.formatCurrency(perServing / 0.30)}</strong>
                </div>
            `;
        }
    }

    calculateTotal() {
        return this.ingredients.reduce((sum, ing) => sum + (ing.cost || 0), 0);
    }

    formatCurrency(amount) {
        return '$' + amount.toFixed(2);
    }

    servings = 4;

    loadSampleRecipe() {
        this.ingredients = [
            { name: 'Chicken Breast', quantity: 2, unit: 'lb', cost: 8.50 },
            { name: 'Olive Oil', quantity: 2, unit: 'tbsp', cost: 0.35 },
            { name: 'Garlic', quantity: 4, unit: 'each', cost: 0.40 },
            { name: 'Bell Peppers', quantity: 3, unit: 'each', cost: 3.00 },
            { name: 'Onion', quantity: 1, unit: 'each', cost: 0.75 }
        ];
        this.render();
    }
}

// ==================== Export Feature ====================

function exportTableToCSV(tableId, filename) {
    const table = document.querySelector(`#${tableId} table`);
    if (!table) return;

    let csv = [];
    const rows = table.querySelectorAll('tr');

    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const rowData = Array.from(cols).map(col => {
            let data = col.textContent.trim();
            // Handle commas in data
            if (data.includes(',')) {
                data = `"${data}"`;
            }
            return data;
        });
        csv.push(rowData.join(','));
    });

    // Download
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    window.URL.revokeObjectURL(url);

    window.LariatBible.showToast('Data exported successfully', 'success');
}

// ==================== Notification System ====================

class NotificationCenter {
    constructor() {
        this.notifications = [];
        this.init();
    }

    init() {
        // Create notification container if it doesn't exist
        if (!document.getElementById('notificationContainer')) {
            const container = document.createElement('div');
            container.id = 'notificationContainer';
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
    }

    show(message, type = 'info', duration = 3000) {
        const id = Date.now();
        const notification = {
            id,
            message,
            type
        };

        this.notifications.push(notification);
        this.render();

        // Auto-remove after duration
        if (duration > 0) {
            setTimeout(() => this.remove(id), duration);
        }
    }

    remove(id) {
        this.notifications = this.notifications.filter(n => n.id !== id);
        this.render();
    }

    render() {
        const container = document.getElementById('notificationContainer');
        if (!container) return;

        container.innerHTML = this.notifications.map(n => `
            <div class="notification notification-${n.type}" data-id="${n.id}">
                <i class="fas fa-${this.getIcon(n.type)}"></i>
                <span>${n.message}</span>
                <button class="notification-close" onclick="notifications.remove(${n.id})">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');
    }

    getIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
}

// Initialize notification system
const notifications = new NotificationCenter();

// Override showToast to use notification system
window.LariatBible.showToast = (message, type) => {
    notifications.show(message, type);
};

// ==================== Initialize ====================

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize vendor comparison table
    if (document.getElementById('vendorComparisonTable')) {
        window.vendorTable = new VendorComparisonTable('vendorComparisonTable');
    }

    // Initialize recipe calculator
    if (document.getElementById('recipeCalculator')) {
        window.recipeCalc = new RecipeCostCalculator('recipeCalculator');
        window.recipeCalc.loadSampleRecipe();
    }
});

// Export for global use
window.LariatInteractive = {
    VendorComparisonTable,
    RecipeCostCalculator,
    exportTableToCSV,
    notifications
};

console.log('✨ Interactive components loaded');
