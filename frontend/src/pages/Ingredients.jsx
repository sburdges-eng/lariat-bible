/**
 * Ingredients Page
 * Manage canonical ingredient library
 */

import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import Table from '../components/Table';
import { ingredientsApi } from '../api/ingredients';

export function Ingredients() {
  const [ingredients, setIngredients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [editingId, setEditingId] = useState(null);

  useEffect(() => {
    loadIngredients();
  }, []);

  const loadIngredients = async () => {
    setLoading(true);
    try {
      const data = await ingredientsApi.getAll();
      setIngredients(data.ingredients || data || []);
    } catch (error) {
      toast.error('Failed to load ingredients');
    } finally {
      setLoading(false);
    }
  };

  const handleAutoLink = async () => {
    try {
      const result = await ingredientsApi.autoLink();
      toast.success(`Linked ${result.linked} ingredients`);
      loadIngredients();
    } catch (error) {
      toast.error('Auto-link failed');
    }
  };

  const filteredIngredients = ingredients.filter((ing) => {
    if (filter === 'linked' && !ing.preferred_vendor) return false;
    if (filter === 'unlinked' && ing.preferred_vendor) return false;
    if (search && !ing.name.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const columns = [
    {
      key: 'name',
      header: 'Ingredient',
      render: (val) => <span className="font-medium">{val}</span>,
    },
    { key: 'category', header: 'Category' },
    { key: 'default_unit', header: 'Unit' },
    {
      key: 'current_cost_per_unit',
      header: 'Cost/Unit',
      render: (val) => val ? `$${parseFloat(val).toFixed(4)}` : '-',
    },
    { key: 'preferred_vendor', header: 'Vendor' },
    {
      key: 'waste_factor',
      header: 'Waste %',
      render: (val) => val ? `${(val * 100).toFixed(0)}%` : '0%',
    },
    {
      key: 'id',
      header: 'Status',
      sortable: false,
      render: (val, row) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          row.preferred_vendor
            ? 'bg-green-100 text-green-800'
            : 'bg-yellow-100 text-yellow-800'
        }`}>
          {row.preferred_vendor ? 'Linked' : 'Unlinked'}
        </span>
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

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Ingredient Library</h1>
          <p className="text-gray-600">
            {ingredients.length} ingredients | {ingredients.filter(i => i.preferred_vendor).length} linked
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleAutoLink}
            className="px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600"
          >
            Auto-Link to Vendors
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            + Add Ingredient
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <input
          type="text"
          placeholder="Search ingredients..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg flex-1 max-w-xs"
        />
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg"
        >
          <option value="all">All Ingredients</option>
          <option value="linked">Linked Only</option>
          <option value="unlinked">Unlinked Only</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <Table
          data={filteredIngredients}
          columns={columns}
          sortable
          onRowClick={(row) => setEditingId(row.id)}
          emptyMessage="No ingredients found. Add ingredients to build your library."
        />
      </div>
    </div>
  );
}

export default Ingredients;
