/**
 * MatchResults Component
 * Display vendor matching results with savings analysis
 */

import { useMemo } from 'react';
import clsx from 'clsx';
import Table from './Table';

export function MatchResults({ matches = [], onExport }) {
  const summary = useMemo(() => {
    const totalItems = matches.length;
    const highConfidence = matches.filter((m) => m.confidence === 'high').length;
    const totalSavings = matches.reduce((sum, m) => sum + (m.savings || 0), 0);
    const avgSavings = totalItems > 0 ? totalSavings / totalItems : 0;

    return {
      totalItems,
      highConfidence,
      totalSavings,
      avgSavings,
    };
  }, [matches]);

  const columns = [
    {
      key: 'item',
      header: 'Item',
      render: (val) => <span className="font-medium">{val}</span>,
    },
    {
      key: 'shamrock_price',
      header: 'Shamrock',
      render: (val) => val ? `$${val.toFixed(2)}` : '-',
    },
    {
      key: 'sysco_price',
      header: 'SYSCO',
      render: (val) => val ? `$${val.toFixed(2)}` : '-',
    },
    {
      key: 'savings',
      header: 'Savings',
      render: (val) => (
        <span className={clsx(
          'font-medium',
          val > 0 ? 'text-green-600' : val < 0 ? 'text-red-600' : 'text-gray-500'
        )}>
          {val > 0 ? '+' : ''}{val ? `$${val.toFixed(2)}` : '-'}
        </span>
      ),
    },
    {
      key: 'savings_pct',
      header: 'Savings %',
      render: (val, row) => {
        if (!row.sysco_price || row.sysco_price === 0) return '-';
        const pct = ((row.sysco_price - row.shamrock_price) / row.sysco_price * 100);
        return (
          <span className={clsx(
            'font-medium',
            pct > 0 ? 'text-green-600' : pct < 0 ? 'text-red-600' : 'text-gray-500'
          )}>
            {pct > 0 ? '+' : ''}{pct.toFixed(1)}%
          </span>
        );
      },
    },
    {
      key: 'confidence',
      header: 'Confidence',
      render: (val) => (
        <span className={clsx(
          'px-2 py-1 rounded-full text-xs font-medium',
          val === 'high' && 'bg-green-100 text-green-800',
          val === 'medium' && 'bg-yellow-100 text-yellow-800',
          val === 'low' && 'bg-red-100 text-red-800'
        )}>
          {val}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-sm text-gray-500">Total Items</div>
          <div className="text-2xl font-bold">{summary.totalItems}</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-sm text-gray-500">High Confidence</div>
          <div className="text-2xl font-bold text-green-600">{summary.highConfidence}</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-sm text-gray-500">Total Savings</div>
          <div className="text-2xl font-bold text-green-600">
            ${summary.totalSavings.toFixed(2)}
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-sm text-gray-500">Avg Savings/Item</div>
          <div className="text-2xl font-bold">
            ${summary.avgSavings.toFixed(2)}
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-end">
        <button
          onClick={onExport}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Export Results CSV
        </button>
      </div>

      {/* Results Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <Table
          data={matches}
          columns={columns}
          sortable
          emptyMessage="No matches found. Upload vendor files and run matching."
        />
      </div>
    </div>
  );
}

export default MatchResults;
