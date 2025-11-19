// Dashboard JavaScript - The Lariat Bible
// Interactive charts and data visualization

// ========================================
// Chart Configuration
// ========================================

const chartColors = {
    primary: '#667eea',
    secondary: '#764ba2',
    success: '#43e97b',
    danger: '#f5576c',
    warning: '#fa709a',
    info: '#4facfe',
};

const chartDefaults = {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: 2,
    plugins: {
        legend: {
            display: true,
            position: 'bottom',
        },
    },
    animation: {
        duration: 1000,
        easing: 'easeInOutQuart',
    },
};

// ========================================
// Initialize Dashboard
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    loadDashboardData();
});

function initializeDashboard() {
    createSavingsTrendChart();
    createVendorComparisonChart();
    createCategoryBreakdownChart();
    createRevenueCostChart();
    createPriceTrendChart();
    loadTopSavingsOpportunities();
}

// ========================================
// Savings Trend Chart
// ========================================

function createSavingsTrendChart() {
    const ctx = document.getElementById('savingsTrendChart');
    if (!ctx) return;

    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const currentMonth = new Date().getMonth();
    const labels = months.slice(Math.max(0, currentMonth - 5), currentMonth + 1);

    // Simulated savings data - replace with real API call
    const savingsData = [3200, 3500, 3800, 4100, 4200, 4333];

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Monthly Savings ($)',
                data: savingsData,
                borderColor: chartColors.success,
                backgroundColor: 'rgba(67, 233, 123, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointHoverRadius: 7,
                pointBackgroundColor: chartColors.success,
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
            }]
        },
        options: {
            ...chartDefaults,
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
            plugins: {
                ...chartDefaults.plugins,
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Savings: $' + context.parsed.y.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// ========================================
// Vendor Comparison Chart
// ========================================

function createVendorComparisonChart() {
    const ctx = document.getElementById('vendorComparisonChart');
    if (!ctx) return;

    const categories = ['Spices', 'Produce', 'Meat', 'Dairy', 'Dry Goods'];
    const shamrockPrices = [85, 120, 180, 95, 110];
    const syscoPrices = [120, 145, 195, 110, 125];

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: categories,
            datasets: [
                {
                    label: 'Shamrock Foods',
                    data: shamrockPrices,
                    backgroundColor: chartColors.success,
                    borderColor: chartColors.success,
                    borderWidth: 2,
                },
                {
                    label: 'SYSCO',
                    data: syscoPrices,
                    backgroundColor: chartColors.danger,
                    borderColor: chartColors.danger,
                    borderWidth: 2,
                }
            ]
        },
        options: {
            ...chartDefaults,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                }
            },
            plugins: {
                ...chartDefaults.plugins,
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': $' + context.parsed.y;
                        }
                    }
                }
            }
        }
    });
}

// ========================================
// Category Breakdown Chart
// ========================================

function createCategoryBreakdownChart() {
    const ctx = document.getElementById('categoryBreakdownChart');
    if (!ctx) return;

    const categories = ['Spices', 'Produce', 'Meat & Protein', 'Dairy', 'Dry Goods', 'Beverages'];
    const costs = [850, 1200, 1800, 950, 1100, 600];
    const colors = [
        chartColors.primary,
        chartColors.success,
        chartColors.danger,
        chartColors.info,
        chartColors.warning,
        chartColors.secondary,
    ];

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: categories,
            datasets: [{
                data: costs,
                backgroundColor: colors,
                borderColor: '#fff',
                borderWidth: 3,
            }]
        },
        options: {
            ...chartDefaults,
            aspectRatio: 1.5,
            plugins: {
                ...chartDefaults.plugins,
                legend: {
                    position: 'right',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return label + ': $' + value.toLocaleString() + ' (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });
}

// ========================================
// Revenue vs Cost Chart
// ========================================

function createRevenueCostChart() {
    const ctx = document.getElementById('revenueCostChart');
    if (!ctx) return;

    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
    const revenue = [45000, 46500, 47200, 48000, 47800, 48000];
    const costs = [42000, 42800, 43100, 43600, 43200, 43400];

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [
                {
                    label: 'Revenue',
                    data: revenue,
                    borderColor: chartColors.success,
                    backgroundColor: 'rgba(67, 233, 123, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                },
                {
                    label: 'Costs',
                    data: costs,
                    borderColor: chartColors.danger,
                    backgroundColor: 'rgba(245, 87, 108, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                }
            ]
        },
        options: {
            ...chartDefaults,
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return '$' + (value / 1000) + 'k';
                        }
                    }
                }
            },
            plugins: {
                ...chartDefaults.plugins,
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': $' + context.parsed.y.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// ========================================
// Interactive Price Trend Chart (Plotly)
// ========================================

function createPriceTrendChart() {
    const container = document.getElementById('priceTrendChart');
    if (!container) return;

    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    // Sample data - replace with real API call
    const shamrockTrace = {
        x: months,
        y: [2.50, 2.45, 2.40, 2.38, 2.35, 2.33, 2.30, 2.28, 2.25, 2.23, 2.20, 2.18],
        name: 'Shamrock Foods',
        type: 'scatter',
        mode: 'lines+markers',
        line: { color: chartColors.success, width: 3 },
        marker: { size: 8 },
    };

    const syscoTrace = {
        x: months,
        y: [3.50, 3.48, 3.45, 3.42, 3.40, 3.38, 3.35, 3.33, 3.30, 3.28, 3.25, 3.23],
        name: 'SYSCO',
        type: 'scatter',
        mode: 'lines+markers',
        line: { color: chartColors.danger, width: 3 },
        marker: { size: 8 },
    };

    const layout = {
        title: 'Price Trend per Pound',
        xaxis: { title: 'Month' },
        yaxis: { title: 'Price ($)', tickprefix: '$' },
        hovermode: 'x unified',
        showlegend: true,
        legend: { x: 0, y: 1.2, orientation: 'h' },
    };

    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
    };

    Plotly.newPlot(container, [shamrockTrace, syscoTrace], layout, config);
}

// ========================================
// Top Savings Opportunities Table
// ========================================

function loadTopSavingsOpportunities() {
    const container = document.getElementById('savingsTable');
    if (!container) return;

    // Sample data - replace with real API call
    const opportunities = [
        { product: 'Black Pepper (Fine)', currentPrice: 3.25, bestPrice: 2.18, savings: 1.07, savingsPercent: 32.9 },
        { product: 'Onion Powder', currentPrice: 2.85, bestPrice: 2.05, savings: 0.80, savingsPercent: 28.1 },
        { product: 'Garlic Powder', currentPrice: 2.95, bestPrice: 2.15, savings: 0.80, savingsPercent: 27.1 },
        { product: 'Paprika', currentPrice: 3.50, bestPrice: 2.65, savings: 0.85, savingsPercent: 24.3 },
        { product: 'Cumin', currentPrice: 3.15, bestPrice: 2.45, savings: 0.70, savingsPercent: 22.2 },
        { product: 'Oregano', currentPrice: 3.40, bestPrice: 2.70, savings: 0.70, savingsPercent: 20.6 },
        { product: 'Chili Powder', currentPrice: 2.75, bestPrice: 2.20, savings: 0.55, savingsPercent: 20.0 },
        { product: 'Cinnamon', currentPrice: 3.80, bestPrice: 3.05, savings: 0.75, savingsPercent: 19.7 },
        { product: 'Basil', currentPrice: 4.20, bestPrice: 3.40, savings: 0.80, savingsPercent: 19.0 },
        { product: 'Cayenne Pepper', currentPrice: 3.60, bestPrice: 2.95, savings: 0.65, savingsPercent: 18.1 },
    ];

    let html = `
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                    <th style="padding: 1rem; text-align: left;">Rank</th>
                    <th style="padding: 1rem; text-align: left;">Product</th>
                    <th style="padding: 1rem; text-align: right;">Current Price</th>
                    <th style="padding: 1rem; text-align: right;">Best Price</th>
                    <th style="padding: 1rem; text-align: right;">Savings</th>
                    <th style="padding: 1rem; text-align: right;">Savings %</th>
                </tr>
            </thead>
            <tbody>
    `;

    opportunities.forEach((item, index) => {
        const rowStyle = index % 2 === 0 ? 'background: #f7f8fc;' : 'background: white;';
        html += `
            <tr style="${rowStyle}">
                <td style="padding: 1rem; font-weight: 700; color: #667eea;">#${index + 1}</td>
                <td style="padding: 1rem; font-weight: 600;">${item.product}</td>
                <td style="padding: 1rem; text-align: right; color: #f5576c;">$${item.currentPrice.toFixed(2)}</td>
                <td style="padding: 1rem; text-align: right; color: #43e97b;">$${item.bestPrice.toFixed(2)}</td>
                <td style="padding: 1rem; text-align: right; font-weight: 700; color: #43e97b;">$${item.savings.toFixed(2)}</td>
                <td style="padding: 1rem; text-align: right; font-weight: 700; color: #43e97b;">${item.savingsPercent.toFixed(1)}%</td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;

    container.innerHTML = html;
}

// ========================================
// Data Loading and Updates
// ========================================

async function loadDashboardData() {
    try {
        const response = await fetch('/api/vendor-comparison');
        const data = await response.json();

        // Update metrics
        document.getElementById('annualSavings').textContent = '$' + data.annual_savings.toLocaleString();

        // Update other metrics as needed
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

function updateDashboard() {
    const dateRange = document.getElementById('dateRange').value;
    console.log('Updating dashboard for date range:', dateRange);
    // Implement date range filtering
    loadDashboardData();
}

// ========================================
// Export Functions
// ========================================

function exportChart(chartId) {
    const chart = Chart.getChart(chartId);
    if (chart) {
        const url = chart.toBase64Image();
        const link = document.createElement('a');
        link.download = `${chartId}-${Date.now()}.png`;
        link.href = url;
        link.click();
    }
}

function exportPriceTrend() {
    console.log('Exporting price trend to Excel...');
    // Implement Excel export using backend API
    fetch('/api/export/price-trend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `price-trend-${Date.now()}.xlsx`;
        a.click();
    })
    .catch(error => console.error('Export error:', error));
}

function exportSavingsOpportunities() {
    console.log('Exporting savings opportunities to Excel...');
    // Implement Excel export
    fetch('/api/export/savings-opportunities', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `savings-opportunities-${Date.now()}.xlsx`;
        a.click();
    })
    .catch(error => console.error('Export error:', error));
}

function updatePriceTrendChart() {
    const category = document.getElementById('productSelector').value;
    console.log('Updating price trend for category:', category);
    // Implement category filtering
}
