/**
 * The Lariat Bible - Interactive Charts and Visualizations
 * Uses Chart.js for beautiful, responsive data visualization
 */

// Chart instances (store globally to update later)
let revenueChart = null;
let savingsChart = null;
let vendorChart = null;
let categoryChart = null;

// Chart color palette
const COLORS = {
    primary: '#2563eb',
    success: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
    info: '#06b6d4',
    purple: '#a855f7',
    pink: '#ec4899',
    gray: '#6b7280'
};

// ==================== Revenue Trend Chart ====================

/**
 * Create revenue trend chart
 * @param {string} canvasId - Canvas element ID
 */
function createRevenueChart(canvasId) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    // Sample data - will be replaced with real API data
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
    const restaurantRevenue = [18000, 19500, 20000, 21000, 20500, 20000];
    const cateringRevenue = [25000, 26500, 28000, 29000, 28500, 28000];

    revenueChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [
                {
                    label: 'Restaurant Revenue',
                    data: restaurantRevenue,
                    borderColor: COLORS.primary,
                    backgroundColor: COLORS.primary + '20',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Catering Revenue',
                    data: cateringRevenue,
                    borderColor: COLORS.success,
                    backgroundColor: COLORS.success + '20',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Monthly Revenue Trends',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': $' +
                                   context.parsed.y.toLocaleString();
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });

    return revenueChart;
}

// ==================== Savings Potential Chart ====================

/**
 * Create savings potential chart
 * @param {string} canvasId - Canvas element ID
 */
function createSavingsChart(canvasId) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const categories = ['Food Costs', 'Labor', 'Utilities', 'Supplies', 'Maintenance'];
    const current = [15000, 8000, 2000, 1500, 1000];
    const potential = [12000, 7500, 1800, 1200, 900];

    savingsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: categories,
            datasets: [
                {
                    label: 'Current Costs',
                    data: current,
                    backgroundColor: COLORS.warning + '80',
                    borderColor: COLORS.warning,
                    borderWidth: 1
                },
                {
                    label: 'With Optimization',
                    data: potential,
                    backgroundColor: COLORS.success + '80',
                    borderColor: COLORS.success,
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                },
                title: {
                    display: true,
                    text: 'Cost Savings Potential',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': $' +
                                   context.parsed.y.toLocaleString();
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });

    return savingsChart;
}

// ==================== Vendor Performance Chart ====================

/**
 * Create vendor performance comparison chart
 * @param {string} canvasId - Canvas element ID
 */
function createVendorChart(canvasId) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    vendorChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Price', 'Quality', 'Delivery', 'Service', 'Selection'],
            datasets: [
                {
                    label: 'Shamrock Foods',
                    data: [85, 90, 88, 92, 87],
                    borderColor: COLORS.success,
                    backgroundColor: COLORS.success + '40',
                    pointBackgroundColor: COLORS.success,
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: COLORS.success
                },
                {
                    label: 'SYSCO',
                    data: [72, 85, 90, 88, 92],
                    borderColor: COLORS.primary,
                    backgroundColor: COLORS.primary + '40',
                    pointBackgroundColor: COLORS.primary,
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: COLORS.primary
                },
                {
                    label: 'US Foods',
                    data: [68, 82, 85, 80, 88],
                    borderColor: COLORS.warning,
                    backgroundColor: COLORS.warning + '40',
                    pointBackgroundColor: COLORS.warning,
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: COLORS.warning
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                },
                title: {
                    display: true,
                    text: 'Vendor Performance Comparison',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20
                    }
                }
            }
        }
    });

    return vendorChart;
}

// ==================== Category Breakdown Chart ====================

/**
 * Create category breakdown pie chart
 * @param {string} canvasId - Canvas element ID
 */
function createCategoryChart(canvasId) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Produce', 'Meat & Seafood', 'Dairy', 'Dry Goods', 'Beverages', 'Other'],
            datasets: [{
                data: [8500, 12000, 4500, 6000, 3000, 2000],
                backgroundColor: [
                    COLORS.success,
                    COLORS.danger,
                    COLORS.info,
                    COLORS.warning,
                    COLORS.purple,
                    COLORS.gray
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                },
                title: {
                    display: true,
                    text: 'Food Cost Breakdown',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return label + ': $' + value.toLocaleString() +
                                   ' (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });

    return categoryChart;
}

// ==================== Sparkline Charts ====================

/**
 * Create small sparkline chart for stat cards
 * @param {string} canvasId - Canvas element ID
 * @param {Array} data - Data points
 * @param {string} color - Chart color
 */
function createSparkline(canvasId, data, color = COLORS.primary) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map((_, i) => i),
            datasets: [{
                data: data,
                borderColor: color,
                backgroundColor: color + '20',
                borderWidth: 2,
                tension: 0.4,
                fill: true,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            },
            scales: {
                x: { display: false },
                y: { display: false }
            },
            elements: {
                line: { borderWidth: 2 }
            }
        }
    });
}

// ==================== Chart Update Functions ====================

/**
 * Update chart with new data
 * @param {Chart} chart - Chart instance
 * @param {Array} newData - New data array
 */
function updateChart(chart, newData) {
    if (!chart) return;

    chart.data.datasets[0].data = newData;
    chart.update('active');
}

/**
 * Update revenue chart with API data
 * @param {Object} apiData - Data from API
 */
async function updateRevenueChart(apiData) {
    if (!revenueChart) return;

    // Update with real data from API
    // This is a placeholder - implement based on your API structure
    revenueChart.data.datasets[0].data = apiData.restaurant || [];
    revenueChart.data.datasets[1].data = apiData.catering || [];
    revenueChart.update();
}

// ==================== Initialization ====================

/**
 * Initialize all charts
 */
function initializeCharts() {
    console.log('📊 Initializing interactive charts...');

    // Create main charts if containers exist
    if (document.getElementById('revenueChart')) {
        createRevenueChart('revenueChart');
    }

    if (document.getElementById('savingsChart')) {
        createSavingsChart('savingsChart');
    }

    if (document.getElementById('vendorChart')) {
        createVendorChart('vendorChart');
    }

    if (document.getElementById('categoryChart')) {
        createCategoryChart('categoryChart');
    }

    // Create sparklines for stat cards
    const sparklineData = [65, 68, 70, 72, 71, 75, 78, 80, 77, 82];

    if (document.getElementById('revenueSpark')) {
        createSparkline('revenueSpark', sparklineData, COLORS.success);
    }
    if (document.getElementById('savingsSpark')) {
        createSparkline('savingsSpark', [45, 50, 48, 52, 55, 58, 60, 62, 64, 65], COLORS.primary);
    }
    if (document.getElementById('eventsSpark')) {
        createSparkline('eventsSpark', [3, 4, 5, 4, 6, 7, 8, 7, 9, 7], COLORS.info);
    }

    console.log('✅ Charts initialized successfully');
}

// ==================== Auto-refresh ====================

/**
 * Set up auto-refresh for charts
 */
function setupChartAutoRefresh() {
    // Refresh charts every 5 minutes
    setInterval(async () => {
        console.log('🔄 Refreshing charts...');

        try {
            // Fetch fresh data
            const response = await fetch('/');
            const data = await response.json();

            // Update charts with new data
            if (data.metrics) {
                // Update based on your API structure
                console.log('Charts refreshed with latest data');
            }
        } catch (error) {
            console.error('Error refreshing charts:', error);
        }
    }, 5 * 60 * 1000);
}

// Export for use in other modules
window.LariatCharts = {
    initialize: initializeCharts,
    createRevenueChart,
    createSavingsChart,
    createVendorChart,
    createCategoryChart,
    createSparkline,
    updateChart,
    setupAutoRefresh: setupChartAutoRefresh
};

console.log('📊 Chart module loaded');
