"""
Unified Recipe Book Generator
Creates a standardized recipe book format with total yields, instructions,
and ingredient details in a universal format.
"""

import pandas as pd
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json


@dataclass
class RecipeIngredientEntry:
    """Individual ingredient entry for a recipe."""
    name: str
    quantity: float
    unit: str
    prep_notes: str = ""  # "diced", "julienned", etc.
    vendor_item_code: Optional[str] = None
    estimated_cost: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'quantity': self.quantity,
            'unit': self.unit,
            'prep_notes': self.prep_notes,
            'vendor_item_code': self.vendor_item_code,
            'estimated_cost': self.estimated_cost
        }
    
    def formatted_string(self) -> str:
        """Return formatted ingredient string."""
        prep = f", {self.prep_notes}" if self.prep_notes else ""
        return f"{self.quantity} {self.unit} {self.name}{prep}"


@dataclass
class UnifiedRecipe:
    """Unified recipe format with standard structure."""
    
    # Basic Information
    recipe_id: str
    name: str
    category: str  # Appetizer, Entree, Side, Sauce, Dessert, etc.
    subcategory: str = ""  # Beef, Chicken, Seafood, Vegetarian, etc.
    description: str = ""
    
    # Yields
    yield_quantity: float = 0.0
    yield_unit: str = "portions"  # portions, oz, cups, quarts, etc.
    portion_size: str = ""  # "8 oz", "1 plate", etc.
    
    # Timing
    prep_time_minutes: int = 0
    cook_time_minutes: int = 0
    rest_time_minutes: int = 0
    
    # Ingredients
    ingredients: List[RecipeIngredientEntry] = field(default_factory=list)
    
    # Instructions
    prep_instructions: List[str] = field(default_factory=list)
    cooking_instructions: List[str] = field(default_factory=list)
    plating_instructions: List[str] = field(default_factory=list)
    
    # Storage & Shelf Life
    storage_instructions: str = ""
    shelf_life_days: int = 0
    reheating_instructions: str = ""
    
    # Special Notes
    chef_notes: str = ""
    dietary_info: List[str] = field(default_factory=list)  # Gluten-Free, Vegan, etc.
    allergens: List[str] = field(default_factory=list)
    
    # Costing
    total_cost: float = 0.0
    cost_per_portion: float = 0.0
    
    # Metadata
    created_by: str = ""
    created_date: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    version: str = "1.0"
    
    @property
    def total_time_minutes(self) -> int:
        """Calculate total time."""
        return self.prep_time_minutes + self.cook_time_minutes + self.rest_time_minutes
    
    def calculate_cost(self) -> float:
        """Calculate total recipe cost from ingredients."""
        self.total_cost = sum(ing.estimated_cost for ing in self.ingredients)
        if self.yield_quantity > 0:
            self.cost_per_portion = self.total_cost / self.yield_quantity
        return self.total_cost
    
    def add_ingredient(self, name: str, quantity: float, unit: str, 
                       prep_notes: str = "", cost: float = 0.0) -> None:
        """Add an ingredient to the recipe."""
        self.ingredients.append(RecipeIngredientEntry(
            name=name,
            quantity=quantity,
            unit=unit,
            prep_notes=prep_notes,
            estimated_cost=cost
        ))
        self.last_modified = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert recipe to dictionary."""
        return {
            'recipe_id': self.recipe_id,
            'name': self.name,
            'category': self.category,
            'subcategory': self.subcategory,
            'description': self.description,
            'yield': {
                'quantity': self.yield_quantity,
                'unit': self.yield_unit,
                'portion_size': self.portion_size
            },
            'timing': {
                'prep_time_minutes': self.prep_time_minutes,
                'cook_time_minutes': self.cook_time_minutes,
                'rest_time_minutes': self.rest_time_minutes,
                'total_time_minutes': self.total_time_minutes
            },
            'ingredients': [ing.to_dict() for ing in self.ingredients],
            'instructions': {
                'prep': self.prep_instructions,
                'cooking': self.cooking_instructions,
                'plating': self.plating_instructions
            },
            'storage': {
                'instructions': self.storage_instructions,
                'shelf_life_days': self.shelf_life_days,
                'reheating': self.reheating_instructions
            },
            'notes': {
                'chef_notes': self.chef_notes,
                'dietary_info': self.dietary_info,
                'allergens': self.allergens
            },
            'costing': {
                'total_cost': self.total_cost,
                'cost_per_portion': self.cost_per_portion
            },
            'metadata': {
                'created_by': self.created_by,
                'created_date': self.created_date.isoformat() if self.created_date else None,
                'last_modified': self.last_modified.isoformat() if self.last_modified else None,
                'version': self.version
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UnifiedRecipe':
        """Create recipe from dictionary."""
        recipe = cls(
            recipe_id=data.get('recipe_id', ''),
            name=data.get('name', ''),
            category=data.get('category', ''),
            subcategory=data.get('subcategory', ''),
            description=data.get('description', '')
        )
        
        # Yield info
        yield_info = data.get('yield', {})
        recipe.yield_quantity = yield_info.get('quantity', 0)
        recipe.yield_unit = yield_info.get('unit', 'portions')
        recipe.portion_size = yield_info.get('portion_size', '')
        
        # Timing
        timing = data.get('timing', {})
        recipe.prep_time_minutes = timing.get('prep_time_minutes', 0)
        recipe.cook_time_minutes = timing.get('cook_time_minutes', 0)
        recipe.rest_time_minutes = timing.get('rest_time_minutes', 0)
        
        # Ingredients
        for ing_data in data.get('ingredients', []):
            recipe.ingredients.append(RecipeIngredientEntry(
                name=ing_data.get('name', ''),
                quantity=ing_data.get('quantity', 0),
                unit=ing_data.get('unit', ''),
                prep_notes=ing_data.get('prep_notes', ''),
                vendor_item_code=ing_data.get('vendor_item_code'),
                estimated_cost=ing_data.get('estimated_cost', 0)
            ))
        
        # Instructions
        instructions = data.get('instructions', {})
        recipe.prep_instructions = instructions.get('prep', [])
        recipe.cooking_instructions = instructions.get('cooking', [])
        recipe.plating_instructions = instructions.get('plating', [])
        
        # Storage
        storage = data.get('storage', {})
        recipe.storage_instructions = storage.get('instructions', '')
        recipe.shelf_life_days = storage.get('shelf_life_days', 0)
        recipe.reheating_instructions = storage.get('reheating', '')
        
        # Notes
        notes = data.get('notes', {})
        recipe.chef_notes = notes.get('chef_notes', '')
        recipe.dietary_info = notes.get('dietary_info', [])
        recipe.allergens = notes.get('allergens', [])
        
        # Costing
        costing = data.get('costing', {})
        recipe.total_cost = costing.get('total_cost', 0)
        recipe.cost_per_portion = costing.get('cost_per_portion', 0)
        
        # Metadata
        metadata = data.get('metadata', {})
        recipe.created_by = metadata.get('created_by', '')
        recipe.version = metadata.get('version', '1.0')
        
        if metadata.get('created_date'):
            recipe.created_date = datetime.fromisoformat(metadata['created_date'])
        if metadata.get('last_modified'):
            recipe.last_modified = datetime.fromisoformat(metadata['last_modified'])
        
        return recipe


class UnifiedRecipeBook:
    """
    Unified recipe book manager.
    Handles loading, saving, and exporting recipes in a standardized format.
    """
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.recipes: Dict[str, UnifiedRecipe] = {}
    
    def add_recipe(self, recipe: UnifiedRecipe) -> str:
        """Add a recipe to the book."""
        self.recipes[recipe.recipe_id] = recipe
        return recipe.recipe_id
    
    def get_recipe(self, recipe_id: str) -> Optional[UnifiedRecipe]:
        """Get a recipe by ID."""
        return self.recipes.get(recipe_id)
    
    def list_recipes(self, category: str = None) -> List[UnifiedRecipe]:
        """List all recipes, optionally filtered by category."""
        recipes = list(self.recipes.values())
        if category:
            recipes = [r for r in recipes if r.category.lower() == category.lower()]
        return recipes
    
    def import_from_csv(self, file_path: str) -> int:
        """
        Import recipes from CSV file.
        
        Expected columns:
        - recipe_id, name, category, subcategory, description
        - yield_quantity, yield_unit, portion_size
        - prep_time, cook_time
        - ingredients (JSON string or comma-separated)
        - instructions (JSON string or numbered list)
        """
        df = pd.read_csv(file_path)
        count = 0
        
        for _, row in df.iterrows():
            recipe = UnifiedRecipe(
                recipe_id=str(row.get('recipe_id', f'RECIPE_{count}')),
                name=str(row.get('name', 'Untitled')),
                category=str(row.get('category', 'Other')),
                subcategory=str(row.get('subcategory', '')),
                description=str(row.get('description', ''))
            )
            
            recipe.yield_quantity = float(row.get('yield_quantity', 0))
            recipe.yield_unit = str(row.get('yield_unit', 'portions'))
            recipe.portion_size = str(row.get('portion_size', ''))
            recipe.prep_time_minutes = int(row.get('prep_time', 0))
            recipe.cook_time_minutes = int(row.get('cook_time', 0))
            
            # Parse ingredients if provided
            if 'ingredients' in row and pd.notna(row['ingredients']):
                try:
                    ingredients = json.loads(row['ingredients'])
                    for ing in ingredients:
                        recipe.add_ingredient(
                            name=ing.get('name', ''),
                            quantity=ing.get('quantity', 0),
                            unit=ing.get('unit', ''),
                            prep_notes=ing.get('prep_notes', ''),
                            cost=ing.get('cost', 0)
                        )
                except json.JSONDecodeError:
                    # Try comma-separated format
                    for ing_str in str(row['ingredients']).split(';'):
                        if ing_str.strip():
                            recipe.add_ingredient(ing_str.strip(), 1, 'unit')
            
            # Parse instructions
            if 'instructions' in row and pd.notna(row['instructions']):
                try:
                    instructions = json.loads(row['instructions'])
                    recipe.cooking_instructions = instructions
                except json.JSONDecodeError:
                    recipe.cooking_instructions = str(row['instructions']).split(';')
            
            self.add_recipe(recipe)
            count += 1
        
        return count
    
    def export_to_json(self, file_path: str = None) -> str:
        """Export all recipes to JSON file."""
        if file_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = self.data_dir / f"recipe_book_{timestamp}.json"
        else:
            file_path = Path(file_path)
        
        data = {
            'metadata': {
                'exported': datetime.now().isoformat(),
                'total_recipes': len(self.recipes),
                'version': '1.0'
            },
            'recipes': [r.to_dict() for r in self.recipes.values()]
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return str(file_path)
    
    def load_from_json(self, file_path: str) -> int:
        """Load recipes from JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        count = 0
        for recipe_data in data.get('recipes', []):
            recipe = UnifiedRecipe.from_dict(recipe_data)
            self.add_recipe(recipe)
            count += 1
        
        return count
    
    def export_to_excel(self, file_path: str = None) -> str:
        """
        Export recipe book to Excel with multiple sheets:
        - Recipe Index: Overview of all recipes
        - Full Recipes: Detailed recipe cards
        - Ingredients Master: All ingredients across recipes
        - Category Summary: Recipes by category
        """
        if file_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = self.data_dir / f"recipe_book_{timestamp}.xlsx"
        else:
            file_path = Path(file_path)
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Sheet 1: Recipe Index
            index_data = []
            for recipe in self.recipes.values():
                index_data.append({
                    'Recipe ID': recipe.recipe_id,
                    'Name': recipe.name,
                    'Category': recipe.category,
                    'Subcategory': recipe.subcategory,
                    'Yield': f"{recipe.yield_quantity} {recipe.yield_unit}",
                    'Portion Size': recipe.portion_size,
                    'Total Time (min)': recipe.total_time_minutes,
                    'Cost/Portion': f"${recipe.cost_per_portion:.2f}" if recipe.cost_per_portion else 'N/A',
                    'Dietary Info': ', '.join(recipe.dietary_info),
                    'Allergens': ', '.join(recipe.allergens)
                })
            
            if index_data:
                pd.DataFrame(index_data).to_excel(writer, sheet_name='Recipe Index', index=False)
            
            # Sheet 2: Full Recipes (detailed view)
            recipe_details = []
            for recipe in self.recipes.values():
                # Compile all info into readable format
                ingredients_str = '\n'.join([ing.formatted_string() for ing in recipe.ingredients])
                all_instructions = []
                
                if recipe.prep_instructions:
                    all_instructions.append("PREP:")
                    all_instructions.extend([f"  {i+1}. {inst}" for i, inst in enumerate(recipe.prep_instructions)])
                
                if recipe.cooking_instructions:
                    all_instructions.append("COOKING:")
                    all_instructions.extend([f"  {i+1}. {inst}" for i, inst in enumerate(recipe.cooking_instructions)])
                
                if recipe.plating_instructions:
                    all_instructions.append("PLATING:")
                    all_instructions.extend([f"  {i+1}. {inst}" for i, inst in enumerate(recipe.plating_instructions)])
                
                instructions_str = '\n'.join(all_instructions)
                
                recipe_details.append({
                    'Recipe Name': recipe.name,
                    'Category': recipe.category,
                    'Description': recipe.description,
                    'Yield': f"{recipe.yield_quantity} {recipe.yield_unit}",
                    'Portion Size': recipe.portion_size,
                    'Prep Time': f"{recipe.prep_time_minutes} min",
                    'Cook Time': f"{recipe.cook_time_minutes} min",
                    'Total Time': f"{recipe.total_time_minutes} min",
                    'Ingredients': ingredients_str,
                    'Instructions': instructions_str,
                    'Storage': recipe.storage_instructions,
                    'Shelf Life': f"{recipe.shelf_life_days} days" if recipe.shelf_life_days else 'N/A',
                    'Chef Notes': recipe.chef_notes,
                    'Total Cost': f"${recipe.total_cost:.2f}" if recipe.total_cost else 'N/A',
                    'Cost Per Portion': f"${recipe.cost_per_portion:.2f}" if recipe.cost_per_portion else 'N/A'
                })
            
            if recipe_details:
                pd.DataFrame(recipe_details).to_excel(writer, sheet_name='Full Recipes', index=False)
            
            # Sheet 3: Ingredients Master List
            all_ingredients = []
            for recipe in self.recipes.values():
                for ing in recipe.ingredients:
                    all_ingredients.append({
                        'Ingredient': ing.name,
                        'Recipe': recipe.name,
                        'Quantity': ing.quantity,
                        'Unit': ing.unit,
                        'Prep Notes': ing.prep_notes,
                        'Vendor Code': ing.vendor_item_code or 'N/A',
                        'Estimated Cost': f"${ing.estimated_cost:.2f}" if ing.estimated_cost else 'N/A'
                    })
            
            if all_ingredients:
                pd.DataFrame(all_ingredients).to_excel(writer, sheet_name='Ingredients Master', index=False)
            
            # Sheet 4: Category Summary
            categories = {}
            for recipe in self.recipes.values():
                if recipe.category not in categories:
                    categories[recipe.category] = {
                        'count': 0,
                        'recipes': [],
                        'avg_time': 0,
                        'avg_cost': 0
                    }
                categories[recipe.category]['count'] += 1
                categories[recipe.category]['recipes'].append(recipe.name)
                categories[recipe.category]['avg_time'] += recipe.total_time_minutes
                categories[recipe.category]['avg_cost'] += recipe.cost_per_portion
            
            category_summary = []
            for cat, data in categories.items():
                category_summary.append({
                    'Category': cat,
                    'Recipe Count': data['count'],
                    'Recipes': ', '.join(data['recipes'][:5]) + ('...' if len(data['recipes']) > 5 else ''),
                    'Avg Total Time (min)': data['avg_time'] / data['count'] if data['count'] > 0 else 0,
                    'Avg Cost/Portion': f"${data['avg_cost'] / data['count']:.2f}" if data['count'] > 0 else 'N/A'
                })
            
            if category_summary:
                pd.DataFrame(category_summary).to_excel(writer, sheet_name='Category Summary', index=False)
        
        return str(file_path)
    
    def get_summary(self) -> Dict:
        """Get summary statistics for the recipe book."""
        if not self.recipes:
            return {'total_recipes': 0}
        
        categories = {}
        total_ingredients = 0
        total_cost = 0
        
        for recipe in self.recipes.values():
            cat = recipe.category
            categories[cat] = categories.get(cat, 0) + 1
            total_ingredients += len(recipe.ingredients)
            total_cost += recipe.total_cost
        
        return {
            'total_recipes': len(self.recipes),
            'categories': categories,
            'total_unique_ingredients': total_ingredients,
            'total_recipe_cost': total_cost,
            'average_cost_per_recipe': total_cost / len(self.recipes) if self.recipes else 0
        }


# Example usage
if __name__ == "__main__":
    book = UnifiedRecipeBook()
    
    # Create sample recipe
    recipe = UnifiedRecipe(
        recipe_id="LARIAT001",
        name="House Blackened Chicken",
        category="Entree",
        subcategory="Chicken",
        description="Signature blackened chicken breast with Cajun spices",
        yield_quantity=10,
        yield_unit="portions",
        portion_size="6 oz chicken breast",
        prep_time_minutes=15,
        cook_time_minutes=20
    )
    
    # Add ingredients
    recipe.add_ingredient("Chicken Breast, Boneless/Skinless", 3.75, "lb", cost=8.50)
    recipe.add_ingredient("Blackening Spice", 2, "tbsp", cost=0.50)
    recipe.add_ingredient("Olive Oil", 2, "tbsp", cost=0.25)
    recipe.add_ingredient("Butter", 2, "tbsp", cost=0.30)
    
    # Add instructions
    recipe.prep_instructions = [
        "Portion chicken breasts to 6 oz portions",
        "Pat chicken dry with paper towels",
        "Season both sides generously with blackening spice"
    ]
    
    recipe.cooking_instructions = [
        "Heat cast iron skillet over high heat until smoking",
        "Add olive oil and swirl to coat",
        "Add chicken, presentation side down",
        "Cook 4-5 minutes until blackened",
        "Flip and cook additional 4-5 minutes",
        "Add butter and baste",
        "Rest for 2 minutes before serving"
    ]
    
    recipe.plating_instructions = [
        "Slice chicken on bias",
        "Fan across plate",
        "Drizzle with pan butter"
    ]
    
    recipe.storage_instructions = "Refrigerate in airtight container"
    recipe.shelf_life_days = 3
    recipe.dietary_info = ["High Protein", "Gluten-Free"]
    recipe.allergens = ["Dairy"]
    recipe.chef_notes = "Ensure cast iron is properly seasoned. Good ventilation required - will smoke!"
    
    # Calculate cost
    recipe.calculate_cost()
    
    # Add to book
    book.add_recipe(recipe)
    
    # Export
    json_path = book.export_to_json()
    print(f"JSON exported to: {json_path}")
    
    excel_path = book.export_to_excel()
    print(f"Excel exported to: {excel_path}")
    
    # Summary
    print(f"\nBook Summary: {book.get_summary()}")
