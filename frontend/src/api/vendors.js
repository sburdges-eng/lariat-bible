/**
 * Vendor API
 * Upload and compare vendor files (SYSCO, Shamrock)
 */

import client from './client';

export const vendorApi = {
  /**
   * Upload vendor file for parsing
   */
  uploadFile: async (file, vendor) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('vendor', vendor);

    return client.post('/api/vendors/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  /**
   * Get preview of uploaded vendor data
   */
  getPreview: async (vendor) => {
    return client.get(`/api/vendors/preview/${vendor}`);
  },

  /**
   * Run matching between vendors
   */
  runMatching: async () => {
    return client.post('/api/vendors/match');
  },

  /**
   * Get match results
   */
  getMatchResults: async () => {
    return client.get('/api/vendors/matches');
  },

  /**
   * Export match results to CSV
   */
  exportMatches: async () => {
    return client.get('/api/vendors/export', { responseType: 'blob' });
  },

  /**
   * Get vendor comparison summary
   */
  getComparison: async () => {
    return client.get('/api/vendor-comparison');
  },
};

export default vendorApi;
