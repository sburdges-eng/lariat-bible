"""
Costing Engine
===============
Main engine for recipe costing operations.
Coordinates all costing components.
"""

import uuid
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from .models import (
    Ingredient, VendorProduct, Recipe, RecipeIngredient,
    MenuItem, CostSnapshot, CostingResult, IngredientMatch,
    MatchConfidence, RecipeType, Unit
)
from .unit_converter import UnitConverter
from .cost_calculator import CostCalculator
from .recipe_parser import RecipeParser, GoogleDocParser


class CostingEngine:
    """
    Main costing engine for The Lariat.

    Coordinates:
    - Ingredient library management
    - Vendor product linking
    - Recipe parsing and costing
    - Cost snapshots
    """

    def __init__(self):
        self.ingredients: Dict[str, Ingredient] = {}
        self.vendor_products: Dict[str, VendorProduct] = {}
        self.recipes: Dict[str, Recipe] = {}
        self.menu_items: Dict[str, MenuItem] = {}
        self.snapshots: List[CostSnapshot] = []

        self.calculator = CostCalculator(self.ingredients)
        self.parser = RecipeParser()
        self.google_parser = GoogleDocParser()

    # =========================================================================
    # Ingredient Management
    # =========================================================================

    def add_ingredient(self, ingredient: Ingredient) -> str:
        """Add ingredient to library"""
        self.ingredients[ingredient.id] = ingredient
        self.calculator.set_ingredients(self.ingredients)
        return ingredient.id

    def get_ingredient(self, ingredient_id: str) -> Optional[Ingredient]:
        """Get ingredient by ID"""
        return self.ingredients.get(ingredient_id)

    def find_ingredient_by_name(self, name: str) -> Optional[Ingredient]:
        """Find ingredient by name or alias"""
        name_lower = name.lower().strip()

        for ing in self.ingredients.values():
            if ing.name.lower() == name_lower:
                return ing
            if name_lower in [a.lower() for a in ing.aliases]:
                return ing

        return None

    def get_all_ingredients(self) -> List[Ingredient]:
        """Get all ingredients"""
        return list(self.ingredients.values())

    # =========================================================================
    # Vendor Product Management
    # =========================================================================

    def add_vendor_product(self, product: VendorProduct) -> str:
        """Add vendor product"""
        self.vendor_products[product.id] = product
        return product.id

    def import_vendor_products(
        self,
        products: List[Dict[str, Any]],
        vendor: str
    ) -> Tuple[int, List[str]]:
        """
        Import vendor products from parsed data.

        Args:
            products: List of product dicts
            vendor: Vendor name (SYSCO, Shamrock, etc.)

        Returns:
            Tuple of (count imported, list of errors)
        """
        imported = 0
        errors = []

        for prod_data in products:
            try:
                product = VendorProduct(
                    id=str(uuid.uuid4()),
                    vendor=vendor,
                    item_code=prod_data.get('item_code', ''),
                    description=prod_data.get('description', ''),
                    pack_size=prod_data.get('pack_size', ''),
                    unit=prod_data.get('unit', 'each'),
                    price=Decimal(str(prod_data.get('price', 0))),
                    category=prod_data.get('category'),
                    brand=prod_data.get('brand'),
                    upc=prod_data.get('upc')
                )

                # Calculate price per unit
                pack_qty, pack_unit = UnitConverter.parse_pack_size(product.pack_size)
                if pack_qty > 0:
                    product.price_per_unit = product.price / pack_qty

                self.vendor_products[product.id] = product
                imported += 1

            except Exception as e:
                errors.append(f"Error importing {prod_data.get('description', 'unknown')}: {e}")

        return imported, errors

    # =========================================================================
    # Ingredient-Vendor Matching
    # =========================================================================

    def auto_link_ingredients(self) -> Dict[str, Any]:
        """
        Automatically link ingredients to vendor products.

        Returns:
            Summary of linking results
        """
        results = {
            'linked': 0,
            'unlinked': 0,
            'needs_review': 0,
            'matches': []
        }

        for ingredient in self.ingredients.values():
            matches = self._find_vendor_matches(ingredient)

            if matches:
                best_match = matches[0]

                # Create match record
                match = IngredientMatch(
                    ingredient_id=ingredient.id,
                    vendor_product_id=best_match['product_id'],
                    vendor=best_match['vendor'],
                    confidence=best_match['confidence'],
                    match_score=best_match['score'],
                    is_preferred=True,
                    matched_by='auto'
                )

                ingredient.vendor_matches = [match]

                # Set pricing from best match
                product = self.vendor_products[best_match['product_id']]
                ingredient.current_cost_per_unit = product.price_per_unit
                ingredient.preferred_vendor = product.vendor
                ingredient.preferred_product_id = product.id

                if best_match['confidence'] == MatchConfidence.HIGH:
                    results['linked'] += 1
                else:
                    results['needs_review'] += 1

                results['matches'].append({
                    'ingredient': ingredient.name,
                    'product': product.description,
                    'vendor': product.vendor,
                    'confidence': best_match['confidence'].value,
                    'score': best_match['score']
                })
            else:
                results['unlinked'] += 1

        return results

    def _find_vendor_matches(
        self,
        ingredient: Ingredient
    ) -> List[Dict[str, Any]]:
        """Find matching vendor products for an ingredient"""
        matches = []
        search_terms = [ingredient.name.lower()] + [a.lower() for a in ingredient.aliases]

        for product in self.vendor_products.values():
            desc_lower = product.description.lower()

            for term in search_terms:
                score = self._calculate_match_score(term, desc_lower)

                if score > 0.5:
                    confidence = self._score_to_confidence(score)
                    matches.append({
                        'product_id': product.id,
                        'vendor': product.vendor,
                        'score': score,
                        'confidence': confidence
                    })
                    break

        # Sort by score descending
        matches.sort(key=lambda x: x['score'], reverse=True)

        return matches

    def _calculate_match_score(self, term: str, description: str) -> float:
        """Calculate fuzzy match score between term and description"""
        # Simple word-based matching
        term_words = set(term.split())
        desc_words = set(description.split())

        if not term_words:
            return 0.0

        # Check exact containment
        if term in description:
            return 0.95

        # Word overlap
        common = term_words & desc_words
        score = len(common) / len(term_words)

        return score

    def _score_to_confidence(self, score: float) -> MatchConfidence:
        """Convert match score to confidence level"""
        if score >= 0.9:
            return MatchConfidence.HIGH
        elif score >= 0.7:
            return MatchConfidence.MEDIUM
        else:
            return MatchConfidence.LOW

    def manually_link(
        self,
        ingredient_id: str,
        product_id: str,
        user: str = "manual"
    ) -> bool:
        """Manually link ingredient to vendor product"""
        ingredient = self.ingredients.get(ingredient_id)
        product = self.vendor_products.get(product_id)

        if not ingredient or not product:
            return False

        match = IngredientMatch(
            ingredient_id=ingredient_id,
            vendor_product_id=product_id,
            vendor=product.vendor,
            confidence=MatchConfidence.MANUAL,
            match_score=1.0,
            is_preferred=True,
            matched_by=user
        )

        # Clear existing preferred
        for m in ingredient.vendor_matches:
            m.is_preferred = False

        ingredient.vendor_matches.append(match)
        ingredient.current_cost_per_unit = product.price_per_unit
        ingredient.preferred_vendor = product.vendor
        ingredient.preferred_product_id = product_id

        return True

    # =========================================================================
    # Recipe Management
    # =========================================================================

    def add_recipe(self, recipe: Recipe) -> str:
        """Add recipe to library"""
        self.recipes[recipe.id] = recipe
        return recipe.id

    def get_recipe(self, recipe_id: str) -> Optional[Recipe]:
        """Get recipe by ID"""
        return self.recipes.get(recipe_id)

    def parse_recipes_from_text(self, text: str, source: str = "text") -> List[Recipe]:
        """Parse and add recipes from text"""
        recipes = self.parser.parse_text(text, source)
        for recipe in recipes:
            self.recipes[recipe.id] = recipe
        return recipes

    def parse_recipes_from_csv(self, csv_content: str, source: str = "csv") -> List[Recipe]:
        """Parse and add recipes from CSV"""
        recipes = self.parser.parse_csv(csv_content, source)
        for recipe in recipes:
            self.recipes[recipe.id] = recipe
        return recipes

    def parse_recipes_from_google_doc(self, doc_content: str) -> List[Recipe]:
        """Parse and add recipes from Google Doc"""
        recipes = self.google_parser.parse_google_doc(doc_content)
        for recipe in recipes:
            self.recipes[recipe.id] = recipe
        return recipes

    # =========================================================================
    # Costing
    # =========================================================================

    def cost_recipe(self, recipe_id: str) -> Optional[CostingResult]:
        """Cost a single recipe"""
        recipe = self.recipes.get(recipe_id)
        if not recipe:
            return None

        # Link ingredients
        self._link_recipe_ingredients(recipe)

        # Calculate costs
        result = self.calculator.cost_recipe(recipe)

        # Store snapshot
        if result.snapshot:
            self.snapshots.append(result.snapshot)

        return result

    def cost_all_recipes(self) -> Dict[str, CostingResult]:
        """Cost all recipes"""
        results = {}
        for recipe_id in self.recipes:
            result = self.cost_recipe(recipe_id)
            if result:
                results[recipe_id] = result
        return results

    def _link_recipe_ingredients(self, recipe: Recipe):
        """Link recipe ingredients to ingredient library"""
        for recipe_ing in recipe.ingredients:
            # Try to find by ID first
            ingredient = self.ingredients.get(recipe_ing.ingredient_id)

            # If not found, try by name
            if not ingredient:
                ingredient = self.find_ingredient_by_name(recipe_ing.ingredient_id)

            if ingredient:
                recipe_ing.ingredient = ingredient
                recipe_ing.ingredient_id = ingredient.id

    # =========================================================================
    # Menu Items
    # =========================================================================

    def add_menu_item(self, menu_item: MenuItem) -> str:
        """Add menu item"""
        self.menu_items[menu_item.id] = menu_item
        return menu_item.id

    def cost_menu_item(self, menu_item_id: str) -> Optional[Dict[str, Any]]:
        """Cost a menu item"""
        menu_item = self.menu_items.get(menu_item_id)
        if not menu_item:
            return None

        return self.calculator.cost_menu_item(menu_item, self.recipes)

    # =========================================================================
    # Snapshots & History
    # =========================================================================

    def get_snapshots_for_recipe(self, recipe_id: str) -> List[CostSnapshot]:
        """Get all snapshots for a recipe"""
        return [s for s in self.snapshots if s.recipe_id == recipe_id]

    def get_cost_history(self, recipe_id: str) -> List[Dict[str, Any]]:
        """Get cost history for a recipe"""
        snapshots = self.get_snapshots_for_recipe(recipe_id)
        snapshots.sort(key=lambda s: s.snapshot_date)

        history = []
        prev = None

        for snap in snapshots:
            entry = {
                'date': snap.snapshot_date.isoformat(),
                'cost': float(snap.cost),
                'cost_per_portion': float(snap.cost_per_portion) if snap.cost_per_portion else None,
            }

            if prev:
                entry['variance'] = float(snap.cost - prev.cost)
                entry['variance_pct'] = float((snap.cost - prev.cost) / prev.cost * 100) if prev.cost > 0 else 0

            history.append(entry)
            prev = snap

        return history

    # =========================================================================
    # Export
    # =========================================================================

    def get_costing_summary(self) -> Dict[str, Any]:
        """Get overall costing summary"""
        costed_recipes = [r for r in self.recipes.values() if r.total_cost is not None]

        total_recipes = len(self.recipes)
        costed_count = len(costed_recipes)

        return {
            'total_recipes': total_recipes,
            'costed_recipes': costed_count,
            'uncosted_recipes': total_recipes - costed_count,
            'total_ingredients': len(self.ingredients),
            'linked_ingredients': sum(1 for i in self.ingredients.values() if i.preferred_vendor),
            'vendor_products': {
                vendor: sum(1 for p in self.vendor_products.values() if p.vendor == vendor)
                for vendor in set(p.vendor for p in self.vendor_products.values())
            },
            'average_recipe_cost': float(sum(r.total_cost for r in costed_recipes) / costed_count) if costed_count > 0 else 0,
            'average_portion_cost': float(sum(r.cost_per_portion for r in costed_recipes) / costed_count) if costed_count > 0 else 0,
        }
