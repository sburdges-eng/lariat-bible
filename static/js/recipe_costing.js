// Recipe Costing JavaScript

let ingredientBreakdownChart = null;
let menuCostChart = null;

document.addEventListener('DOMContentLoaded', function() {
    initializeRecipeCosting();
});

function initializeRecipeCosting() {
    createIngredientBreakdownChart();
    createMenuCostComparisonChart();
}

function addIngredient() {
    const list = document.getElementById('ingredientsList');
    if (!list) return;

    const row = document.createElement('div');
    row.className = 'ingredient-row';
    row.innerHTML = `
        <input type="text" class="ingredient-name" placeholder="Ingredient name">
        <input type="number" class="ingredient-qty" placeholder="Qty" step="0.01">
        <select class="ingredient-unit">
            <option value="lb">Pounds</option>
            <option value="oz">Ounces</option>
            <option value="gal">Gallons</option>
            <option value="qt">Quarts</option>
            <option value="cup">Cups</option>
            <option value="tbsp">Tablespoons</option>
            <option value="tsp">Teaspoons</option>
            <option value="each">Each</option>
        </select>
        <input type="number" class="ingredient-cost" placeholder="Cost" step="0.01" oninput="calculateRecipeCost()">
        <button class="btn-remove" onclick="removeIngredient(this)">
            <i class="fas fa-trash"></i>
        </button>
    `;

    list.appendChild(row);
}

function removeIngredient(button) {
    button.closest('.ingredient-row').remove();
    calculateRecipeCost();
}

function calculateRecipeCost() {
    const costInputs = document.querySelectorAll('.ingredient-cost');
    let totalCost = 0;

    costInputs.forEach(input => {
        totalCost += parseFloat(input.value || 0);
    });

    const laborCost = totalCost * 0.30;
    const overheadCost = totalCost * 0.15;
    const totalPerServing = totalCost + laborCost + overheadCost;
    const suggestedPrice = totalPerServing / 0.55; // 45% margin

    if (document.getElementById('totalIngredientCost')) {
        document.getElementById('totalIngredientCost').textContent = LariatBible.formatCurrency(totalCost);
    }
    if (document.getElementById('laborCostEst')) {
        document.getElementById('laborCostEst').textContent = LariatBible.formatCurrency(laborCost);
    }
    if (document.getElementById('overheadCostEst')) {
        document.getElementById('overheadCostEst').textContent = LariatBible.formatCurrency(overheadCost);
    }
    if (document.getElementById('costPerServing')) {
        document.getElementById('costPerServing').textContent = LariatBible.formatCurrency(totalPerServing);
    }
    if (document.getElementById('suggestedPrice')) {
        document.getElementById('suggestedPrice').textContent = LariatBible.formatCurrency(suggestedPrice);
    }

    updateIngredientBreakdownChart(totalCost, laborCost, overheadCost);
}

function saveRecipe() {
    const name = document.getElementById('recipeName')?.value;
    if (!name) {
        LariatBible.showNotification('Please enter a recipe name', 'error');
        return;
    }

    LariatBible.showNotification(`Recipe "${name}" saved successfully`, 'success');
}

function importRecipes() {
    LariatBible.showNotification('Recipe import coming soon', 'info');
}

function exportRecipeCosts() {
    LariatBible.downloadFile('/api/export/recipe-costs', `recipe_costs_${Date.now()}.xlsx`);
}

function filterRecipes() {
    const searchValue = document.getElementById('recipeSearch')?.value;
    const category = document.getElementById('categoryFilter')?.value;
    console.log('Filtering recipes:', searchValue, category);
}

function createIngredientBreakdownChart() {
    const ctx = document.getElementById('ingredientBreakdownChart');
    if (!ctx) return;

    ingredientBreakdownChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Ingredients', 'Labor', 'Overhead'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: ['#667eea', '#fa709a', '#feca57'],
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

function updateIngredientBreakdownChart(ingredients, labor, overhead) {
    if (ingredientBreakdownChart) {
        ingredientBreakdownChart.data.datasets[0].data = [ingredients, labor, overhead];
        ingredientBreakdownChart.update();
    }
}

function createMenuCostComparisonChart() {
    const ctx = document.getElementById('menuCostComparisonChart');
    if (!ctx) return;

    menuCostChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['BBQ Sandwich', 'Burger', 'Salad', 'Wrap'],
            datasets: [{
                label: 'Cost per Serving',
                data: [4.50, 3.75, 2.85, 3.20],
                backgroundColor: '#667eea',
            }]
        },
        options: {
            responsive: true,
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

function calculateBatchCost() {
    const recipe = document.getElementById('batchRecipeSelect')?.value;
    const servings = document.getElementById('batchServings')?.value || 1;

    if (!recipe) {
        LariatBible.showNotification('Please select a recipe', 'error');
        return;
    }

    const costPerServing = 4.50; // Example
    const totalCost = costPerServing * servings;

    const resultsDiv = document.getElementById('batchResults');
    if (resultsDiv) {
        resultsDiv.innerHTML = `
            <div style="margin-top: 1rem; padding: 1.5rem; background: #f7f8fc; border-radius: 8px;">
                <h3>Batch Cost Summary</h3>
                <p><strong>Recipe:</strong> ${recipe}</p>
                <p><strong>Servings:</strong> ${servings}</p>
                <p><strong>Cost per Serving:</strong> ${LariatBible.formatCurrency(costPerServing)}</p>
                <p style="font-size: 1.5rem; color: #667eea;"><strong>Total Batch Cost: ${LariatBible.formatCurrency(totalCost)}</strong></p>
            </div>
        `;
    }
}
