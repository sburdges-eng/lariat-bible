/**
 * RecipeEditor Component
 * Edit recipe with ingredients and costing
 */

import { useState, useEffect, useMemo } from 'react';
import clsx from 'clsx';

export function RecipeEditor({
  recipe = null,
  ingredients = [],
  onSave,
  onCost,
  onClose,
}) {
  const [formData, setFormData] = useState({
    name: '',
    category: '',
    portions: 1,
    yield_quantity: 1,
    yield_unit: 'portion',
    target_food_cost_pct: 28,
    instructions: '',
    ingredients: [],
  });

  useEffect(() => {
    if (recipe) {
      setFormData({
        name: recipe.name || '',
        category: recipe.category || '',
        portions: recipe.portions || 1,
        yield_quantity: recipe.yield_quantity || 1,
        yield_unit: recipe.yield_unit || 'portion',
        target_food_cost_pct: (recipe.target_food_cost_pct || 0.28) * 100,
        instructions: recipe.instructions || '',
        ingredients: recipe.ingredients || [],
      });
    }
  }, [recipe]);

  const totals = useMemo(() => {
    const totalCost = formData.ingredients.reduce(
      (sum, ing) => sum + (ing.extended_cost || 0),
      0
    );
    const costPerPortion = formData.portions > 0 ? totalCost / formData.portions : 0;
    const targetPct = formData.target_food_cost_pct / 100;
    const suggestedPrice = targetPct > 0 ? costPerPortion / targetPct : 0;

    return { totalCost, costPerPortion, suggestedPrice };
  }, [formData.ingredients, formData.portions, formData.target_food_cost_pct]);

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleIngredientChange = (index, field, value) => {
    setFormData((prev) => {
      const newIngredients = [...prev.ingredients];
      newIngredients[index] = { ...newIngredients[index], [field]: value };

      // Recalculate extended cost
      if (field === 'quantity' || field === 'unit_cost') {
        const qty = parseFloat(newIngredients[index].quantity) || 0;
        const cost = parseFloat(newIngredients[index].unit_cost) || 0;
        newIngredients[index].extended_cost = qty * cost;
      }

      return { ...prev, ingredients: newIngredients };
    });
  };

  const addIngredient = () => {
    setFormData((prev) => ({
      ...prev,
      ingredients: [
        ...prev.ingredients,
        { id: Date.now(), ingredient_id: '', quantity: 0, unit: 'oz', unit_cost: 0, extended_cost: 0 },
      ],
    }));
  };

  const removeIngredient = (index) => {
    setFormData((prev) => ({
      ...prev,
      ingredients: prev.ingredients.filter((_, i) => i !== index),
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave?.({
      ...formData,
      target_food_cost_pct: formData.target_food_cost_pct / 100,
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold">
          {recipe ? 'Edit Recipe' : 'New Recipe'}
        </h2>
        {onClose && (
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            X
          </button>
        )}
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Info */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Recipe Name
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category
            </label>
            <select
              value={formData.category}
              onChange={(e) => handleChange('category', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select category</option>
              <option value="Appetizers">Appetizers</option>
              <option value="Entrees">Entrees</option>
              <option value="Sides">Sides</option>
              <option value="Desserts">Desserts</option>
              <option value="Sauces">Sauces/Dressings</option>
              <option value="Prep">Prep Items</option>
            </select>
          </div>
        </div>

        {/* Yield/Portions */}
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Yield Quantity
            </label>
            <input
              type="number"
              value={formData.yield_quantity}
              onChange={(e) => handleChange('yield_quantity', parseFloat(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              min="0"
              step="0.1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Yield Unit
            </label>
            <input
              type="text"
              value={formData.yield_unit}
              onChange={(e) => handleChange('yield_unit', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="portions, servings, etc."
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Portions
            </label>
            <input
              type="number"
              value={formData.portions}
              onChange={(e) => handleChange('portions', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              min="1"
            />
          </div>
        </div>

        {/* Ingredients Table */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <label className="block text-sm font-medium text-gray-700">
              Ingredients
            </label>
            <button
              type="button"
              onClick={addIngredient}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              + Add Ingredient
            </button>
          </div>

          <div className="border rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Ingredient</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase w-20">Qty</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase w-20">Unit</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase w-24">Cost/Unit</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase w-24">Total</th>
                  <th className="px-3 py-2 w-10"></th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {formData.ingredients.map((ing, idx) => (
                  <tr key={ing.id || idx}>
                    <td className="px-3 py-2">
                      <select
                        value={ing.ingredient_id}
                        onChange={(e) => handleIngredientChange(idx, 'ingredient_id', e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      >
                        <option value="">Select ingredient</option>
                        {ingredients.map((i) => (
                          <option key={i.id} value={i.id}>{i.name}</option>
                        ))}
                      </select>
                    </td>
                    <td className="px-3 py-2">
                      <input
                        type="number"
                        value={ing.quantity}
                        onChange={(e) => handleIngredientChange(idx, 'quantity', parseFloat(e.target.value))}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                        min="0"
                        step="0.01"
                      />
                    </td>
                    <td className="px-3 py-2">
                      <select
                        value={ing.unit}
                        onChange={(e) => handleIngredientChange(idx, 'unit', e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      >
                        <option value="oz">oz</option>
                        <option value="lb">lb</option>
                        <option value="cup">cup</option>
                        <option value="tbsp">tbsp</option>
                        <option value="tsp">tsp</option>
                        <option value="each">each</option>
                        <option value="gallon">gallon</option>
                      </select>
                    </td>
                    <td className="px-3 py-2">
                      <input
                        type="number"
                        value={ing.unit_cost}
                        onChange={(e) => handleIngredientChange(idx, 'unit_cost', parseFloat(e.target.value))}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                        min="0"
                        step="0.01"
                      />
                    </td>
                    <td className="px-3 py-2 text-sm font-medium">
                      ${(ing.extended_cost || 0).toFixed(2)}
                    </td>
                    <td className="px-3 py-2">
                      <button
                        type="button"
                        onClick={() => removeIngredient(idx)}
                        className="text-red-500 hover:text-red-700"
                      >
                        X
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Costing Summary */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="grid grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-sm text-gray-500">Total Cost</div>
              <div className="text-xl font-bold">${totals.totalCost.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Cost/Portion</div>
              <div className="text-xl font-bold">${totals.costPerPortion.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Target COGS</div>
              <input
                type="number"
                value={formData.target_food_cost_pct}
                onChange={(e) => handleChange('target_food_cost_pct', parseFloat(e.target.value))}
                className="w-20 px-2 py-1 border border-gray-300 rounded text-center"
                min="1"
                max="100"
              />
              <span className="ml-1">%</span>
            </div>
            <div>
              <div className="text-sm text-gray-500">Suggested Price</div>
              <div className="text-xl font-bold text-green-600">
                ${totals.suggestedPrice.toFixed(2)}
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3">
          {onClose && (
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
          )}
          {onCost && (
            <button
              type="button"
              onClick={() => onCost?.(recipe?.id)}
              className="px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600"
            >
              Recalculate Costs
            </button>
          )}
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Save Recipe
          </button>
        </div>
      </form>
    </div>
  );
}

export default RecipeEditor;
