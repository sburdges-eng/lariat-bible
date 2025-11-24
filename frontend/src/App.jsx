/**
 * The Lariat Bible - Main App Component
 */

import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, NavLink, useNavigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import toast from 'react-hot-toast';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import VendorImport from './pages/VendorImport';
import Ingredients from './pages/Ingredients';
import Recipes from './pages/Recipes';
import MenuItems from './pages/MenuItems';
import Settings from './pages/Settings';

const queryClient = new QueryClient();

// Check if running in Electron
const isElectron = () => {
  return typeof window !== 'undefined' && window.electronAPI;
};

function Navigation() {
  const navItems = [
    { path: '/', label: 'Vendor Import', icon: '📦' },
    { path: '/ingredients', label: 'Ingredients', icon: '🥕' },
    { path: '/recipes', label: 'Recipes', icon: '📖' },
    { path: '/menu', label: 'Menu Items', icon: '🍽️' },
    { path: '/settings', label: 'Settings', icon: '⚙️' },
  ];

  return (
    <nav className="bg-amber-800 text-white">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🤠</span>
            <span className="font-bold text-xl">The Lariat Bible</span>
          </div>
          <div className="flex gap-1">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `px-4 py-2 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-amber-700 text-white'
                      : 'hover:bg-amber-700/50'
                  }`
                }
              >
                <span className="mr-2">{item.icon}</span>
                {item.label}
              </NavLink>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
}

function Dashboard() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Welcome to The Lariat Bible</h1>
      <p className="text-gray-600">
        Your complete restaurant management system for recipe costing, vendor comparison, and menu optimization.
      </p>

      <div className="grid md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-3xl mb-2">💰</div>
          <h3 className="font-medium text-lg">Vendor Comparison</h3>
          <p className="text-gray-500 text-sm mt-1">
            Compare SYSCO vs Shamrock pricing to find savings
          </p>
          <div className="text-2xl font-bold text-green-600 mt-4">
            $52,000
          </div>
          <div className="text-sm text-gray-500">Potential annual savings</div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-3xl mb-2">📊</div>
          <h3 className="font-medium text-lg">Recipe Costing</h3>
          <p className="text-gray-500 text-sm mt-1">
            Full cost breakdown for every recipe
          </p>
          <div className="text-2xl font-bold mt-4">28%</div>
          <div className="text-sm text-gray-500">Target food cost</div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-3xl mb-2">🌐</div>
          <h3 className="font-medium text-lg">External Data</h3>
          <p className="text-gray-500 text-sm mt-1">
            Access nutrition, prices, and local suppliers
          </p>
          <div className="text-2xl font-bold mt-4">8</div>
          <div className="text-sm text-gray-500">FREE data sources</div>
        </div>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
        <h3 className="font-medium text-amber-900 mb-2">Quick Start</h3>
        <ol className="list-decimal list-inside space-y-2 text-amber-800">
          <li>Upload your SYSCO and Shamrock price lists in <strong>Vendor Import</strong></li>
          <li>Run matching to identify savings opportunities</li>
          <li>Build your ingredient library in <strong>Ingredients</strong></li>
          <li>Create and cost your recipes in <strong>Recipes</strong></li>
          <li>Track profitability in <strong>Menu Items</strong></li>
        </ol>
      </div>
    </div>
  );
}

// Component to handle Electron IPC navigation
function ElectronBridge() {
  const navigate = useNavigate();

  useEffect(() => {
    if (!isElectron()) return;

    // Handle navigation from Electron menu
    window.electronAPI.onNavigate((path) => {
      const pathMap = {
        '/': '/',
        '/vendors': '/',
        '/ingredients': '/ingredients',
        '/recipes': '/recipes',
        '/menu-items': '/menu',
        '/settings': '/settings'
      };
      navigate(pathMap[path] || path);
    });

    // Handle actions from Electron menu
    window.electronAPI.onAction(async (action) => {
      switch (action) {
        case 'cost-all':
          toast.loading('Costing all recipes...');
          try {
            const res = await fetch('http://localhost:8000/api/recipes/cost-all', { method: 'POST' });
            const data = await res.json();
            toast.dismiss();
            toast.success(`Costed ${data.costed || 0} recipes`);
          } catch (err) {
            toast.dismiss();
            toast.error('Failed to cost recipes');
          }
          break;
        case 'auto-link':
          toast.loading('Auto-linking ingredients...');
          try {
            const res = await fetch('http://localhost:8000/api/ingredients/auto-link', { method: 'POST' });
            const data = await res.json();
            toast.dismiss();
            toast.success(`Linked ${data.linked || 0} ingredients`);
          } catch (err) {
            toast.dismiss();
            toast.error('Failed to auto-link');
          }
          break;
      }
    });

    // Handle export from Electron menu
    window.electronAPI.onExport((type) => {
      const exportUrls = {
        'costing-book': '/api/exports/costing-book',
        'recipes': '/api/exports/recipes',
        'ingredients': '/api/exports/ingredients',
        'summary': '/api/exports/summary'
      };
      const url = exportUrls[type];
      if (url) {
        window.open(`http://localhost:8000${url}`, '_blank');
      }
    });
  }, [navigate]);

  return null;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ElectronBridge />
        <div className="min-h-screen bg-gray-100">
          <Navigation />
          <main className="max-w-7xl mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<VendorImport />} />
              <Route path="/ingredients" element={<Ingredients />} />
              <Route path="/recipes" element={<Recipes />} />
              <Route path="/menu" element={<MenuItems />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
        </div>
        <Toaster position="top-right" />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
