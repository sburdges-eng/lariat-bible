// Vendor Analysis JavaScript
// Interactive vendor comparison and analysis

document.addEventListener('DOMContentLoaded', function() {
    initializeVendorAnalysis();
    loadComparisonData();
});

function initializeVendorAnalysis() {
    createCategorySavingsChart();
    createPriceDistributionChart();
}

async function loadComparisonData() {
    try {
        const response = await LariatBible.apiGet('/api/vendor-comparison/detailed');
        updateComparisonTable(response.comparison);
        updateSummaryMetrics(response.summary);
    } catch (error) {
        console.error('Error loading comparison data:', error);
    }
}

function updateComparison() {
    const primary = document.getElementById('primaryVendor').value;
    const compare = document.getElementById('compareVendor').value;
    console.log(`Comparing ${primary} with ${compare}`);
    loadComparisonData();
}

function refreshData() {
    LariatBible.showLoading();
    loadComparisonData();
    setTimeout(() => {
        LariatBible.hideLoading();
        LariatBible.showNotification('Data refreshed', 'success');
    }, 1000);
}

function exportFullComparison() {
    LariatBible.downloadFile('/api/export/price-comparison', `vendor_comparison_${Date.now()}.xlsx`);
}

function createCategorySavingsChart() {
    const ctx = document.getElementById('categorySavingsChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Spices', 'Produce', 'Meat', 'Dairy', 'Dry Goods'],
            datasets: [{
                label: 'Monthly Savings ($)',
                data: [850, 620, 1100, 450, 680],
                backgroundColor: '#43e97b',
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => '$' + value
                    }
                }
            }
        }
    });
}

function createPriceDistributionChart() {
    const ctx = document.getElementById('priceDistributionChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['0-10%', '10-20%', '20-30%', '30%+'],
            datasets: [{
                data: [15, 35, 28, 22],
                backgroundColor: ['#f5576c', '#fa709a', '#feca57', '#43e97b'],
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'right' }
            }
        }
    });
}

function updateComparisonTable(data) {
    const container = document.getElementById('comparisonTable');
    if (!container) return;

    const columns = [
        { field: 'product', label: 'Product', align: 'left' },
        { field: 'vendor_a', label: 'Vendor A', align: 'left' },
        { field: 'price_a', label: 'Price A', align: 'right', formatter: v => LariatBible.formatCurrency(v) },
        { field: 'vendor_b', label: 'Vendor B', align: 'left' },
        { field: 'price_b', label: 'Price B', align: 'right', formatter: v => LariatBible.formatCurrency(v) },
        { field: 'difference', label: 'Savings', align: 'right', formatter: v => LariatBible.formatCurrency(v) },
        { field: 'savings_percent', label: 'Savings %', align: 'right', formatter: v => LariatBible.formatPercent(v) },
    ];

    LariatBible.createDataTable('comparisonTable', data, columns);
}

function updateSummaryMetrics(summary) {
    if (document.getElementById('productsCompared')) {
        document.getElementById('productsCompared').textContent = summary.total_items;
    }
    if (document.getElementById('annualSavings')) {
        document.getElementById('annualSavings').textContent = LariatBible.formatCurrency(summary.total_savings * 12);
    }
}

function filterProducts() {
    const searchValue = document.getElementById('searchProducts').value;
    const category = document.getElementById('categoryFilter').value;
    console.log('Filtering:', searchValue, category);
}

function exportTableToExcel() {
    exportFullComparison();
}

function updatePriceTrends() {
    const category = document.getElementById('trendCategory').value;
    console.log('Updating trends for:', category);
}
