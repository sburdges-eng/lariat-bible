/**
 * Recipes Page
 * Manage recipes with costing
 */

import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import Table from '../components/Table';
import RecipeEditor from '../components/RecipeEditor';
import { recipesApi } from '../api/recipes';
import { ingredientsApi } from '../api/ingredients';

export function Recipes() {
  const [recipes, setRecipes] = useState([]);
  const [ingredients, setIngredients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingRecipe, setEditingRecipe] = useState(null);
  const [showEditor, setShowEditor] = useState(false);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [recipesData, ingredientsData] = await Promise.all([
        recipesApi.getAll(),
        ingredientsApi.getAll(),
      ]);
      setRecipes(recipesData.recipes || recipesData || []);
      setIngredients(ingredientsData.ingredients || ingredientsData || []);
    } catch (error) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleCostRecipe = async (id) => {
    try {
      const result = await recipesApi.cost(id);
      toast.success(`Costed: $${result.cost_per_portion?.toFixed(2)}/portion`);
      loadData();
    } catch (error) {
      toast.error('Costing failed');
    }
  };

  const handleCostAll = async () => {
    try {
      const result = await recipesApi.costAll();
      toast.success(`Costed ${Object.keys(result).length} recipes`);
      loadData();
    } catch (error) {
      toast.error('Batch costing failed');
    }
  };

  const handleSaveRecipe = async (recipeData) => {
    try {
      if (editingRecipe?.id) {
        await recipesApi.update(editingRecipe.id, recipeData);
        toast.success('Recipe updated');
      } else {
        await recipesApi.create(recipeData);
        toast.success('Recipe created');
      }
      setShowEditor(false);
      setEditingRecipe(null);
      loadData();
    } catch (error) {
      toast.error('Save failed');
    }
  };

  const handleExportSummary = async () => {
    try {
      const blob = await recipesApi.exportSummary();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'recipe_costing_summary.csv';
      a.click();
      window.URL.revokeObjectURL(url);
      toast.success('Summary exported');
    } catch (error) {
      toast.error('Export failed');
    }
  };

  const filteredRecipes = recipes.filter((r) => {
    if (filter === 'costed' && !r.total_cost) return false;
    if (filter === 'uncosted' && r.total_cost) return false;
    return true;
  });

  const columns = [
    {
      key: 'name',
      header: 'Recipe',
      render: (val) => <span className="font-medium">{val}</span>,
    },
    { key: 'category', header: 'Category' },
    { key: 'recipe_type', header: 'Type' },
    { key: 'portions', header: 'Portions' },
    {
      key: 'total_cost',
      header: 'Total Cost',
      render: (val) => val ? `$${parseFloat(val).toFixed(2)}` : '-',
    },
    {
      key: 'cost_per_portion',
      header: 'Cost/Portion',
      render: (val) => val ? `$${parseFloat(val).toFixed(2)}` : '-',
    },
    {
      key: 'suggested_price',
      header: 'Suggested Price',
      render: (val) => val ? `$${parseFloat(val).toFixed(2)}` : '-',
    },
    {
      key: 'id',
      header: 'Actions',
      sortable: false,
      render: (val, row) => (
        <div className="flex gap-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setEditingRecipe(row);
              setShowEditor(true);
            }}
            className="text-blue-600 hover:text-blue-800 text-sm"
          >
            Edit
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleCostRecipe(val);
            }}
            className="text-yellow-600 hover:text-yellow-800 text-sm"
          >
            Cost
          </button>
        </div>
      ),
    },
  ];

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (showEditor) {
    return (
      <RecipeEditor
        recipe={editingRecipe}
        ingredients={ingredients}
        onSave={handleSaveRecipe}
        onCost={handleCostRecipe}
        onClose={() => {
          setShowEditor(false);
          setEditingRecipe(null);
        }}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Recipe Costing</h1>
          <p className="text-gray-600">
            {recipes.length} recipes | {recipes.filter(r => r.total_cost).length} costed
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleExportSummary}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Export Summary
          </button>
          <button
            onClick={handleCostAll}
            className="px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600"
          >
            Cost All Recipes
          </button>
          <button
            onClick={() => {
              setEditingRecipe(null);
              setShowEditor(true);
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            + New Recipe
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-sm text-gray-500">Total Recipes</div>
          <div className="text-2xl font-bold">{recipes.length}</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-sm text-gray-500">Avg Cost/Portion</div>
          <div className="text-2xl font-bold">
            ${(recipes.filter(r => r.cost_per_portion).reduce((sum, r) => sum + parseFloat(r.cost_per_portion), 0) / Math.max(recipes.filter(r => r.cost_per_portion).length, 1)).toFixed(2)}
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-sm text-gray-500">Menu Items</div>
          <div className="text-2xl font-bold">
            {recipes.filter(r => r.recipe_type === 'menu_item').length}
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-sm text-gray-500">Components</div>
          <div className="text-2xl font-bold">
            {recipes.filter(r => r.recipe_type === 'component').length}
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg"
        >
          <option value="all">All Recipes</option>
          <option value="costed">Costed Only</option>
          <option value="uncosted">Uncosted Only</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <Table
          data={filteredRecipes}
          columns={columns}
          sortable
          onRowClick={(row) => {
            setEditingRecipe(row);
            setShowEditor(true);
          }}
          emptyMessage="No recipes found. Create your first recipe."
        />
      </div>
    </div>
  );
}

export default Recipes;
