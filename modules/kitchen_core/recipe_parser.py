"""
Recipe Parser
==============
Parse recipes from various sources into structured models.

Supports:
- Google Docs (Lariat Recipe Book)
- CSV templates
- Prep lists
- Plain text recipes
"""

import re
import csv
import uuid
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from io import StringIO
from .models import Recipe, RecipeIngredient, RecipeType, Unit
from .unit_converter import UnitConverter


class RecipeParser:
    """
    Parse recipes from various text formats.
    """

    # Common ingredient patterns
    INGREDIENT_PATTERNS = [
        # "2 cups flour"
        r'^([\d./]+)\s+(cup|cups|tbsp|tsp|oz|lb|g|kg|gallon|quart|pint|each|ea)\s+(.+)$',
        # "flour, 2 cups"
        r'^(.+),\s*([\d./]+)\s+(cup|cups|tbsp|tsp|oz|lb|g|kg|gallon|quart|pint|each|ea)$',
        # "2 chicken breasts"
        r'^([\d./]+)\s+(.+)$',
    ]

    # Fraction mappings
    FRACTIONS = {
        '1/2': Decimal('0.5'),
        '1/3': Decimal('0.333'),
        '1/4': Decimal('0.25'),
        '2/3': Decimal('0.667'),
        '3/4': Decimal('0.75'),
        '1/8': Decimal('0.125'),
        '3/8': Decimal('0.375'),
        '5/8': Decimal('0.625'),
        '7/8': Decimal('0.875'),
    }

    def __init__(self):
        self.errors = []
        self.warnings = []

    def parse_text(self, text: str, source: str = "text") -> List[Recipe]:
        """
        Parse plain text containing one or more recipes.

        Args:
            text: Recipe text
            source: Source identifier

        Returns:
            List of parsed recipes
        """
        self.errors = []
        self.warnings = []
        recipes = []

        # Split into sections by recipe headers
        sections = self._split_into_recipes(text)

        for section in sections:
            recipe = self._parse_recipe_section(section, source)
            if recipe:
                recipes.append(recipe)

        return recipes

    def parse_csv(self, csv_content: str, source: str = "csv") -> List[Recipe]:
        """
        Parse recipes from CSV format.

        Expected columns:
        - recipe_name
        - ingredient_name
        - quantity
        - unit
        - prep_notes (optional)
        - yield_qty (optional)
        - portions (optional)

        Args:
            csv_content: CSV text content
            source: Source identifier

        Returns:
            List of parsed recipes
        """
        self.errors = []
        self.warnings = []
        recipes = {}

        reader = csv.DictReader(StringIO(csv_content))

        for row in reader:
            recipe_name = row.get('recipe_name', '').strip()
            if not recipe_name:
                continue

            # Get or create recipe
            if recipe_name not in recipes:
                recipes[recipe_name] = Recipe(
                    id=str(uuid.uuid4()),
                    name=recipe_name,
                    recipe_type=RecipeType.MENU_ITEM,
                    source=source
                )

                # Set yield/portions if provided
                if row.get('yield_qty'):
                    try:
                        recipes[recipe_name].yield_quantity = Decimal(row['yield_qty'])
                    except Exception:
                        pass
                if row.get('portions'):
                    try:
                        recipes[recipe_name].portions = int(row['portions'])
                    except Exception:
                        pass

            # Parse ingredient
            ingredient = self._parse_csv_ingredient(row)
            if ingredient:
                recipes[recipe_name].ingredients.append(ingredient)

        return list(recipes.values())

    def parse_prep_list(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse a prep list into structured items.

        Args:
            text: Prep list text

        Returns:
            List of prep items with quantities
        """
        items = []
        lines = text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Try to parse quantity and item
            item = self._parse_prep_line(line)
            if item:
                items.append(item)

        return items

    def parse_ingredient_line(
        self,
        line: str
    ) -> Optional[Tuple[Decimal, Unit, str, str]]:
        """
        Parse a single ingredient line.

        Returns:
            Tuple of (quantity, unit, ingredient_name, prep_notes) or None
        """
        line = line.strip()
        if not line:
            return None

        # Try each pattern
        for pattern in self.INGREDIENT_PATTERNS:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                groups = match.groups()

                if len(groups) >= 3:
                    qty_str = groups[0]
                    unit_str = groups[1]
                    name = groups[2]
                else:
                    qty_str = groups[0]
                    unit_str = 'each'
                    name = groups[1]

                # Parse quantity
                qty = self._parse_quantity(qty_str)

                # Parse unit
                unit = UnitConverter.parse_unit(unit_str)
                if not unit:
                    unit = Unit.EACH

                # Extract prep notes from name
                name, prep_notes = self._extract_prep_notes(name)

                return (qty, unit, name.strip(), prep_notes)

        # Fallback: just treat as ingredient name with qty=1
        return (Decimal('1'), Unit.EACH, line, None)

    def _split_into_recipes(self, text: str) -> List[str]:
        """Split text into recipe sections"""
        # Look for recipe headers (lines that might be recipe names)
        sections = []
        current = []

        lines = text.split('\n')

        for line in lines:
            # Detect recipe headers (capitalized, short lines, possibly with colons)
            if self._is_recipe_header(line):
                if current:
                    sections.append('\n'.join(current))
                current = [line]
            else:
                current.append(line)

        if current:
            sections.append('\n'.join(current))

        return sections if sections else [text]

    def _is_recipe_header(self, line: str) -> bool:
        """Detect if line is likely a recipe name/header"""
        line = line.strip()

        if not line:
            return False

        # All caps or Title Case, relatively short
        if len(line) < 50:
            if line.isupper() or line.istitle():
                # Doesn't look like an ingredient (no numbers at start)
                if not re.match(r'^\d', line):
                    return True

        # Ends with colon
        if line.endswith(':'):
            return True

        return False

    def _parse_recipe_section(self, section: str, source: str) -> Optional[Recipe]:
        """Parse a single recipe section"""
        lines = section.strip().split('\n')

        if not lines:
            return None

        # First non-empty line is the recipe name
        name = None
        ingredient_lines = []
        instructions = []
        in_instructions = False

        for line in lines:
            line = line.strip()

            if not line:
                continue

            if name is None:
                name = line.rstrip(':')
                continue

            # Check for instructions section
            if line.lower().startswith(('instructions:', 'directions:', 'method:', 'steps:')):
                in_instructions = True
                continue

            if in_instructions:
                instructions.append(line)
            else:
                # Check if this looks like an ingredient
                if self._looks_like_ingredient(line):
                    ingredient_lines.append(line)
                else:
                    # Might be instructions without header
                    instructions.append(line)

        if not name:
            return None

        # Create recipe
        recipe = Recipe(
            id=str(uuid.uuid4()),
            name=name,
            recipe_type=self._detect_recipe_type(name),
            source=source,
            instructions='\n'.join(instructions) if instructions else None
        )

        # Parse ingredients
        for line in ingredient_lines:
            parsed = self.parse_ingredient_line(line)
            if parsed:
                qty, unit, ing_name, prep = parsed
                recipe.ingredients.append(RecipeIngredient(
                    id=str(uuid.uuid4()),
                    recipe_id=recipe.id,
                    ingredient_id=self._generate_ingredient_id(ing_name),
                    quantity=qty,
                    unit=unit,
                    prep_notes=prep
                ))

        return recipe

    def _looks_like_ingredient(self, line: str) -> bool:
        """Check if line looks like an ingredient"""
        # Starts with number or fraction
        if re.match(r'^[\d/]', line):
            return True

        # Contains common unit words
        units = ['cup', 'tbsp', 'tsp', 'oz', 'lb', 'gallon', 'quart', 'pint', 'each']
        line_lower = line.lower()
        for unit in units:
            if unit in line_lower:
                return True

        return False

    def _parse_csv_ingredient(self, row: Dict[str, str]) -> Optional[RecipeIngredient]:
        """Parse ingredient from CSV row"""
        ing_name = row.get('ingredient_name', '').strip()
        qty_str = row.get('quantity', '1').strip()
        unit_str = row.get('unit', 'each').strip()
        prep_notes = row.get('prep_notes', '').strip()

        if not ing_name:
            return None

        qty = self._parse_quantity(qty_str)
        unit = UnitConverter.parse_unit(unit_str) or Unit.EACH

        return RecipeIngredient(
            id=str(uuid.uuid4()),
            recipe_id='',  # Will be set by caller
            ingredient_id=self._generate_ingredient_id(ing_name),
            quantity=qty,
            unit=unit,
            prep_notes=prep_notes if prep_notes else None
        )

    def _parse_prep_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a prep list line"""
        # Patterns: "10 lb potatoes", "Dice onions - 5 lb"
        patterns = [
            r'^([\d./]+)\s*(lb|oz|each|ea|qt|gal|#)?\s+(.+)$',
            r'^(.+)\s*[-:]\s*([\d./]+)\s*(lb|oz|each|ea|qt|gal|#)?$',
        ]

        for pattern in patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    if groups[0].replace('.', '').replace('/', '').isdigit():
                        qty = self._parse_quantity(groups[0])
                        unit = groups[1] or 'each'
                        item = groups[2]
                    else:
                        item = groups[0]
                        qty = self._parse_quantity(groups[1])
                        unit = groups[2] or 'each'

                    return {
                        'item': item.strip(),
                        'quantity': float(qty),
                        'unit': unit.lower().replace('#', 'lb')
                    }

        # Fallback: just the item name
        return {'item': line, 'quantity': 1, 'unit': 'each'}

    def _parse_quantity(self, qty_str: str) -> Decimal:
        """Parse quantity string to Decimal"""
        qty_str = qty_str.strip()

        # Check for fraction
        if qty_str in self.FRACTIONS:
            return self.FRACTIONS[qty_str]

        # Check for mixed number like "1 1/2"
        parts = qty_str.split()
        if len(parts) == 2 and parts[1] in self.FRACTIONS:
            return Decimal(parts[0]) + self.FRACTIONS[parts[1]]

        # Check for fraction like "1/2"
        if '/' in qty_str:
            try:
                num, den = qty_str.split('/')
                return Decimal(num) / Decimal(den)
            except Exception:
                pass

        # Direct conversion
        try:
            return Decimal(qty_str)
        except Exception:
            return Decimal('1')

    def _extract_prep_notes(self, name: str) -> Tuple[str, Optional[str]]:
        """Extract prep notes from ingredient name"""
        # Look for parenthetical notes
        match = re.match(r'^(.+)\s*\((.+)\)\s*$', name)
        if match:
            return match.group(1).strip(), match.group(2).strip()

        # Look for comma-separated notes
        if ',' in name:
            parts = name.split(',', 1)
            return parts[0].strip(), parts[1].strip()

        return name, None

    def _detect_recipe_type(self, name: str) -> RecipeType:
        """Detect recipe type from name"""
        name_lower = name.lower()

        component_keywords = [
            'sauce', 'dressing', 'jam', 'reduction', 'stock', 'broth',
            'marinade', 'rub', 'spice blend', 'mix', 'crumbs', 'garnish'
        ]

        for keyword in component_keywords:
            if keyword in name_lower:
                return RecipeType.COMPONENT

        return RecipeType.MENU_ITEM

    def _generate_ingredient_id(self, name: str) -> str:
        """Generate a consistent ID for an ingredient name"""
        # Normalize name
        normalized = name.lower().strip()
        normalized = re.sub(r'[^a-z0-9\s]', '', normalized)
        normalized = re.sub(r'\s+', '_', normalized)
        return normalized


class GoogleDocParser(RecipeParser):
    """
    Parse recipes from Google Docs format.
    Extends base parser with Google Docs-specific handling.
    """

    def parse_google_doc(self, doc_content: str) -> List[Recipe]:
        """
        Parse Google Doc content (exported as plain text).

        Args:
            doc_content: Text content from Google Doc

        Returns:
            List of parsed recipes
        """
        # Clean up Google Docs formatting
        content = self._clean_google_doc(doc_content)

        return self.parse_text(content, source="Lariat Recipe Book")

    def _clean_google_doc(self, content: str) -> str:
        """Clean up Google Docs formatting artifacts"""
        # Remove Google Docs header/footer
        lines = content.split('\n')
        cleaned = []

        for line in lines:
            # Skip page numbers
            if re.match(r'^\d+$', line.strip()):
                continue

            # Skip empty lines at document boundaries
            cleaned.append(line)

        return '\n'.join(cleaned)
