// Profit Calculator JavaScript

let costChart = null;
let marginChart = null;

document.addEventListener('DOMContentLoaded', function() {
    initializeProfitCalculator();
});

function initializeProfitCalculator() {
    createCostBreakdownChart();
    createMarginComparisonChart();
}

function calculateMargins() {
    const foodCost = parseFloat(document.getElementById('foodCost')?.value || 0);
    const laborCost = parseFloat(document.getElementById('laborCost')?.value || 0);
    const overheadCost = parseFloat(document.getElementById('overheadCost')?.value || 0);
    const sellingPrice = parseFloat(document.getElementById('sellingPrice')?.value || 0);

    const totalCost = foodCost + laborCost + overheadCost;
    const netProfit = sellingPrice - totalCost;
    const profitMargin = sellingPrice > 0 ? (netProfit / sellingPrice) * 100 : 0;
    const foodCostPercent = sellingPrice > 0 ? (foodCost / sellingPrice) * 100 : 0;
    const laborCostPercent = sellingPrice > 0 ? (laborCost / sellingPrice) * 100 : 0;
    const targetPrice = totalCost / 0.55; // 45% margin

    // Update display
    if (document.getElementById('totalCost')) {
        document.getElementById('totalCost').textContent = LariatBible.formatCurrency(totalCost);
    }
    if (document.getElementById('profitMargin')) {
        document.getElementById('profitMargin').textContent = profitMargin.toFixed(1) + '%';
    }
    if (document.getElementById('netProfit')) {
        document.getElementById('netProfit').textContent = LariatBible.formatCurrency(netProfit);
    }
    if (document.getElementById('foodCostPercent')) {
        document.getElementById('foodCostPercent').textContent = foodCostPercent.toFixed(1) + '%';
    }
    if (document.getElementById('laborCostPercent')) {
        document.getElementById('laborCostPercent').textContent = laborCostPercent.toFixed(1) + '%';
    }
    if (document.getElementById('targetPrice')) {
        document.getElementById('targetPrice').textContent = LariatBible.formatCurrency(targetPrice);
    }

    // Update charts
    updateCostBreakdownChart(foodCost, laborCost, overheadCost);
    updateMarginComparisonChart(profitMargin);

    // Update scenarios
    updateScenarios(foodCost, laborCost, overheadCost, sellingPrice);
}

function createCostBreakdownChart() {
    const ctx = document.getElementById('costBreakdownChart');
    if (!ctx) return;

    costChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Food Cost', 'Labor Cost', 'Overhead'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: ['#f5576c', '#fa709a', '#feca57'],
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

function updateCostBreakdownChart(food, labor, overhead) {
    if (costChart) {
        costChart.data.datasets[0].data = [food, labor, overhead];
        costChart.update();
    }
}

function createMarginComparisonChart() {
    const ctx = document.getElementById('marginComparisonChart');
    if (!ctx) return;

    marginChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Current', 'Target (45%)'],
            datasets: [{
                label: 'Profit Margin (%)',
                data: [0, 45],
                backgroundColor: ['#4facfe', '#43e97b'],
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: value => value + '%'
                    }
                }
            }
        }
    });
}

function updateMarginComparisonChart(currentMargin) {
    if (marginChart) {
        marginChart.data.datasets[0].data = [currentMargin, 45];
        marginChart.update();
    }
}

function updateScenarios(food, labor, overhead, price) {
    // Scenario 1: Reduce food cost by 10%
    const newFood1 = food * 0.9;
    const newTotal1 = newFood1 + labor + overhead;
    const newMargin1 = price > 0 ? ((price - newTotal1) / price) * 100 : 0;
    const newProfit1 = price - newTotal1;

    if (document.getElementById('scenario1Margin')) {
        document.getElementById('scenario1Margin').textContent = newMargin1.toFixed(1) + '%';
    }
    if (document.getElementById('scenario1Profit')) {
        document.getElementById('scenario1Profit').textContent = '+' + LariatBible.formatCurrency(newProfit1 - (price - (food + labor + overhead)));
    }

    // Scenario 2: Increase price by 5%
    const newPrice2 = price * 1.05;
    const total2 = food + labor + overhead;
    const newMargin2 = newPrice2 > 0 ? ((newPrice2 - total2) / newPrice2) * 100 : 0;
    const newProfit2 = newPrice2 - total2;

    if (document.getElementById('scenario2Margin')) {
        document.getElementById('scenario2Margin').textContent = newMargin2.toFixed(1) + '%';
    }
    if (document.getElementById('scenario2Profit')) {
        document.getElementById('scenario2Profit').textContent = '+' + LariatBible.formatCurrency(newProfit2 - (price - total2));
    }

    // Scenario 3: Switch to Shamrock (29.5% savings on food)
    const newFood3 = food * 0.705;
    const newTotal3 = newFood3 + labor + overhead;
    const newMargin3 = price > 0 ? ((price - newTotal3) / price) * 100 : 0;
    const newProfit3 = price - newTotal3;

    if (document.getElementById('scenario3Margin')) {
        document.getElementById('scenario3Margin').textContent = newMargin3.toFixed(1) + '%';
    }
    if (document.getElementById('scenario3Profit')) {
        document.getElementById('scenario3Profit').textContent = '+' + LariatBible.formatCurrency(newProfit3 - (price - (food + labor + overhead)));
    }
}

function applyScenario(scenarioNum) {
    const foodCost = parseFloat(document.getElementById('foodCost')?.value || 0);
    const sellingPrice = parseFloat(document.getElementById('sellingPrice')?.value || 0);

    if (scenarioNum === 1) {
        document.getElementById('foodCost').value = (foodCost * 0.9).toFixed(2);
    } else if (scenarioNum === 2) {
        document.getElementById('sellingPrice').value = (sellingPrice * 1.05).toFixed(2);
    } else if (scenarioNum === 3) {
        document.getElementById('foodCost').value = (foodCost * 0.705).toFixed(2);
    }

    calculateMargins();
    LariatBible.showNotification(`Scenario ${scenarioNum} applied`, 'success');
}

function importMenuItems() {
    LariatBible.showNotification('Menu import coming soon', 'info');
}

function exportMarginAnalysis() {
    LariatBible.downloadFile('/api/export/price-comparison', `margin_analysis_${Date.now()}.xlsx`);
}
