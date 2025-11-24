/**
 * VendorImport Page
 * Upload and compare vendor files (SYSCO vs Shamrock)
 */

import { useState } from 'react';
import { toast } from 'react-hot-toast';
import FileUpload from '../components/FileUpload';
import MatchResults from '../components/MatchResults';
import Table from '../components/Table';
import { vendorApi } from '../api/vendors';

export function VendorImport() {
  const [syscoData, setSyscoData] = useState(null);
  const [shamrockData, setShamrockData] = useState(null);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleUpload = async (file, vendor) => {
    try {
      const result = await vendorApi.uploadFile(file, vendor);

      if (vendor === 'SYSCO') {
        setSyscoData(result);
        toast.success(`Loaded ${result.items?.length || 0} SYSCO items`);
      } else {
        setShamrockData(result);
        toast.success(`Loaded ${result.items?.length || 0} Shamrock items`);
      }
    } catch (error) {
      toast.error(`Upload failed: ${error.message}`);
    }
  };

  const runMatching = async () => {
    if (!syscoData || !shamrockData) {
      toast.error('Please upload both vendor files first');
      return;
    }

    setLoading(true);
    try {
      const result = await vendorApi.runMatching();
      setMatches(result.matches || []);
      toast.success(`Found ${result.matches?.length || 0} matches`);
    } catch (error) {
      toast.error(`Matching failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const exportResults = async () => {
    try {
      const blob = await vendorApi.exportMatches();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'vendor_match_results.csv';
      a.click();
      window.URL.revokeObjectURL(url);
      toast.success('Results exported');
    } catch (error) {
      toast.error(`Export failed: ${error.message}`);
    }
  };

  const previewColumns = [
    { key: 'item_code', header: 'Item Code' },
    { key: 'description', header: 'Description' },
    { key: 'pack_size', header: 'Pack Size' },
    { key: 'price', header: 'Price', render: (val) => `$${val?.toFixed(2) || '-'}` },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Vendor Import & Comparison</h1>
        <p className="text-gray-600">
          Upload vendor price lists to compare and find savings
        </p>
      </div>

      {/* Upload Section */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <h3 className="font-medium text-gray-900">SYSCO File</h3>
          <FileUpload onUpload={handleUpload} vendor="SYSCO" />
          {syscoData && (
            <div className="text-sm text-green-600">
              Loaded {syscoData.items?.length || 0} items
            </div>
          )}
        </div>

        <div className="space-y-4">
          <h3 className="font-medium text-gray-900">Shamrock Foods File</h3>
          <FileUpload onUpload={handleUpload} vendor="Shamrock" />
          {shamrockData && (
            <div className="text-sm text-green-600">
              Loaded {shamrockData.items?.length || 0} items
            </div>
          )}
        </div>
      </div>

      {/* Preview Section */}
      {(syscoData || shamrockData) && (
        <div className="grid md:grid-cols-2 gap-6">
          {syscoData && (
            <div>
              <h3 className="font-medium text-gray-900 mb-2">SYSCO Preview</h3>
              <div className="border rounded-lg overflow-hidden max-h-64 overflow-y-auto">
                <Table
                  data={(syscoData.items || []).slice(0, 10)}
                  columns={previewColumns}
                  sortable={false}
                />
              </div>
            </div>
          )}
          {shamrockData && (
            <div>
              <h3 className="font-medium text-gray-900 mb-2">Shamrock Preview</h3>
              <div className="border rounded-lg overflow-hidden max-h-64 overflow-y-auto">
                <Table
                  data={(shamrockData.items || []).slice(0, 10)}
                  columns={previewColumns}
                  sortable={false}
                />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Matching Section */}
      <div className="border-t pt-6">
        <div className="flex justify-center mb-6">
          <button
            onClick={runMatching}
            disabled={!syscoData || !shamrockData || loading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {loading ? (
              <>
                <span className="animate-spin">...</span>
                Running Matching...
              </>
            ) : (
              'Run Matching'
            )}
          </button>
        </div>

        {matches.length > 0 && (
          <MatchResults matches={matches} onExport={exportResults} />
        )}
      </div>
    </div>
  );
}

export default VendorImport;
