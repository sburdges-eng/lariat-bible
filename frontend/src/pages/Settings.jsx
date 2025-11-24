/**
 * Settings Page
 * Configure API keys and preferences
 */

import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';

export function Settings() {
  const [settings, setSettings] = useState({
    target_food_cost_pct: 28,
    restaurant_name: 'The Lariat',
    default_waste_factor: 5,
  });

  const [apiStatus, setApiStatus] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkApiStatus();
  }, []);

  const checkApiStatus = async () => {
    try {
      const response = await fetch('/api/external-data/status');
      const data = await response.json();
      setApiStatus(data.sources || {});
    } catch (error) {
      console.error('Failed to check API status');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = () => {
    toast.success('Settings saved');
  };

  const externalDataSources = [
    { id: 'usda_fooddata', name: 'USDA FoodData Central', keyRequired: true },
    { id: 'open_food_facts', name: 'Open Food Facts', keyRequired: false },
    { id: 'spoonacular', name: 'Spoonacular', keyRequired: true },
    { id: 'edamam', name: 'Edamam', keyRequired: true },
    { id: 'usda_market_news', name: 'USDA Market News', keyRequired: false },
    { id: 'local_suppliers', name: 'LocalHarvest', keyRequired: false },
    { id: 'commodity_prices', name: 'Index Mundi', keyRequired: false },
    { id: 'barcode_lookup', name: 'Barcode Lookup', keyRequired: false },
  ];

  return (
    <div className="space-y-8 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600">Configure your Lariat Bible preferences</p>
      </div>

      {/* General Settings */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-medium mb-4">General Settings</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Restaurant Name
            </label>
            <input
              type="text"
              value={settings.restaurant_name}
              onChange={(e) => setSettings({ ...settings, restaurant_name: e.target.value })}
              className="w-full max-w-md px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Default Target Food Cost %
            </label>
            <div className="flex items-center gap-2">
              <input
                type="number"
                value={settings.target_food_cost_pct}
                onChange={(e) => setSettings({ ...settings, target_food_cost_pct: parseInt(e.target.value) })}
                className="w-20 px-3 py-2 border border-gray-300 rounded-lg"
                min="1"
                max="100"
              />
              <span>%</span>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Default Waste Factor %
            </label>
            <div className="flex items-center gap-2">
              <input
                type="number"
                value={settings.default_waste_factor}
                onChange={(e) => setSettings({ ...settings, default_waste_factor: parseInt(e.target.value) })}
                className="w-20 px-3 py-2 border border-gray-300 rounded-lg"
                min="0"
                max="50"
              />
              <span>%</span>
            </div>
          </div>
        </div>
      </div>

      {/* External Data Sources */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-medium mb-4">External Data Sources</h2>
        <p className="text-sm text-gray-600 mb-4">
          Status of FREE external data sources integrated into the system
        </p>

        <div className="space-y-3">
          {externalDataSources.map((source) => {
            const status = apiStatus[source.id];
            const isAvailable = status?.available;

            return (
              <div key={source.id} className="flex items-center justify-between py-2 border-b">
                <div>
                  <div className="font-medium">{source.name}</div>
                  <div className="text-sm text-gray-500">
                    {source.keyRequired ? 'API key required' : 'No key required'}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    isAvailable
                      ? 'bg-green-100 text-green-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {isAvailable ? 'Connected' : 'Not configured'}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-medium text-blue-900">Getting API Keys</h3>
          <p className="text-sm text-blue-800 mt-1">
            To enable all features, add your FREE API keys to the .env file:
          </p>
          <ul className="text-sm text-blue-700 mt-2 space-y-1">
            <li>USDA: https://fdc.nal.usda.gov/api-key-signup.html</li>
            <li>Spoonacular: https://spoonacular.com/food-api/console</li>
            <li>Edamam: https://developer.edamam.com</li>
          </ul>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Save Settings
        </button>
      </div>
    </div>
  );
}

export default Settings;
