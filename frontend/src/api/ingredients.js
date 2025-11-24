/**
 * Ingredients API
 * Manage canonical ingredient library
 */

import client from './client';

export const ingredientsApi = {
  /**
   * Get all ingredients
   */
  getAll: async () => {
    return client.get('/api/ingredients');
  },

  /**
   * Get single ingredient
   */
  getById: async (id) => {
    return client.get(`/api/ingredients/${id}`);
  },

  /**
   * Create new ingredient
   */
  create: async (ingredient) => {
    return client.post('/api/ingredients', ingredient);
  },

  /**
   * Update ingredient
   */
  update: async (id, ingredient) => {
    return client.put(`/api/ingredients/${id}`, ingredient);
  },

  /**
   * Delete ingredient
   */
  delete: async (id) => {
    return client.delete(`/api/ingredients/${id}`);
  },

  /**
   * Link ingredient to vendor product
   */
  linkToVendor: async (ingredientId, productId) => {
    return client.post(`/api/ingredients/${ingredientId}/link`, {
      product_id: productId,
    });
  },

  /**
   * Auto-link all ingredients to cheapest vendor options
   */
  autoLink: async () => {
    return client.post('/api/ingredients/auto-link');
  },

  /**
   * Search ingredients
   */
  search: async (query) => {
    return client.get('/api/ingredients/search', { params: { q: query } });
  },

  /**
   * Get unlinked ingredients
   */
  getUnlinked: async () => {
    return client.get('/api/ingredients/unlinked');
  },

  /**
   * Get external data for ingredient (nutrition, etc.)
   */
  getExternalData: async (ingredientName) => {
    return client.get('/api/external-data/ingredients/search', {
      params: { q: ingredientName },
    });
  },

  /**
   * Get nutrition info for ingredient
   */
  getNutrition: async (ingredientName, amount = 100, unit = 'g') => {
    return client.get('/api/external-data/ingredients/nutrition', {
      params: { ingredient: ingredientName, amount, unit },
    });
  },
};

export default ingredientsApi;
