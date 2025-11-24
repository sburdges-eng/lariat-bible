/**
 * MenuItems Page
 * Manage menu items with profitability analysis
 */

import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import Table from '../components/Table';

export function MenuItems() {
  const [menuItems, setMenuItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulated data for now
    setMenuItems([
      {
        id: '1',
        name: 'Chicken Sandwich',
        category: 'Entrees',
        menu_price: 14.99,
        food_cost: 4.20,
        food_cost_pct: 0.28,
        gross_profit: 10.79,
        monthly_sales: 245,
      },
      {
        id: '2',
        name: 'House Salad',
        category: 'Starters',
        menu_price: 8.99,
        food_cost: 2.70,
        food_cost_pct: 0.30,
        gross_profit: 6.29,
        monthly_sales: 189,
      },
    ]);
    setLoading(false);
  }, []);

  const columns = [
    {
      key: 'name',
      header: 'Menu Item',
      render: (val) => <span className="font-medium">{val}</span>,
    },
    { key: 'category', header: 'Category' },
    {
      key: 'menu_price',
      header: 'Menu Price',
      render: (val) => `$${val.toFixed(2)}`,
    },
    {
      key: 'food_cost',
      header: 'Food Cost',
      render: (val) => `$${val.toFixed(2)}`,
    },
    {
      key: 'food_cost_pct',
      header: 'COGS %',
      render: (val) => (
        <span className={val > 0.32 ? 'text-red-600' : 'text-green-600'}>
          {(val * 100).toFixed(1)}%
        </span>
      ),
    },
    {
      key: 'gross_profit',
      header: 'Gross Profit',
      render: (val) => <span className="text-green-600">${val.toFixed(2)}</span>,
    },
    { key: 'monthly_sales', header: 'Monthly Sales' },
    {
      key: 'id',
      header: 'Monthly Profit',
      render: (val, row) => (
        <span className="font-medium text-green-600">
          ${(row.gross_profit * row.monthly_sales).toFixed(2)}
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
          <h1 className="text-2xl font-bold text-gray-900">Menu Items</h1>
          <p className="text-gray-600">
            Track profitability and pricing for menu items
          </p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          + Add Menu Item
        </button>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <Table
          data={menuItems}
          columns={columns}
          sortable
          emptyMessage="No menu items found."
        />
      </div>
    </div>
  );
}

export default MenuItems;
