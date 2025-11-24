/**
 * Recipes API
 * Manage recipes and costing
 */

import client from './client';

export const recipesApi = {
  /**
   * Get all recipes
   */
  getAll: async () => {
    return client.get('/api/recipes');
  },

  /**
   * Get single recipe with ingredients
   */
  getById: async (id) => {
    return client.get(`/api/recipes/${id}`);
  },

  /**
   * Create new recipe
   */
  create: async (recipe) => {
    return client.post('/api/recipes', recipe);
  },

  /**
   * Update recipe
   */
  update: async (id, recipe) => {
    return client.put(`/api/recipes/${id}`, recipe);
  },

  /**
   * Delete recipe
   */
  delete: async (id) => {
    return client.delete(`/api/recipes/${id}`);
  },

  /**
   * Parse recipe from text
   */
  parse: async (text, source = 'text') => {
    return client.post('/api/recipes/parse', { text, source });
  },

  /**
   * Parse recipe from Google Doc
   */
  parseGoogleDoc: async (content) => {
    return client.post('/api/recipes/parse-google-doc', { content });
  },

  /**
   * Cost a single recipe
   */
  cost: async (id) => {
    return client.post(`/api/recipes/${id}/cost`);
  },

  /**
   * Cost all recipes
   */
  costAll: async () => {
    return client.post('/api/recipes/cost-all');
  },

  /**
   * Get recipe cost history
   */
  getCostHistory: async (id) => {
    return client.get(`/api/recipes/${id}/cost-history`);
  },

  /**
   * Export recipe to CSV
   */
  exportCsv: async (id) => {
    return client.get(`/api/recipes/${id}/export/csv`, { responseType: 'blob' });
  },

  /**
   * Export all recipes summary
   */
  exportSummary: async () => {
    return client.get('/api/recipes/export/summary', { responseType: 'blob' });
  },

  /**
   * Get portion pricing analysis
   */
  getPortionPricing: async () => {
    return client.get('/api/recipes/portion-pricing');
  },

  /**
   * Add ingredient to recipe
   */
  addIngredient: async (recipeId, ingredient) => {
    return client.post(`/api/recipes/${recipeId}/ingredients`, ingredient);
  },

  /**
   * Update ingredient in recipe
   */
  updateIngredient: async (recipeId, ingredientId, data) => {
    return client.put(`/api/recipes/${recipeId}/ingredients/${ingredientId}`, data);
  },

  /**
   * Remove ingredient from recipe
   */
  removeIngredient: async (recipeId, ingredientId) => {
    return client.delete(`/api/recipes/${recipeId}/ingredients/${ingredientId}`);
  },

  /**
   * Search recipes from external sources
   */
  searchExternal: async (query, cuisine = null, diet = null) => {
    return client.get('/api/external-data/recipes/search', {
      params: { q: query, cuisine, diet },
    });
  },
};

export default recipesApi;
