"""
Prep Sheet Generator Module
Generates kitchen prep sheets from BEO data
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

from modules.core.models import BanquetEvent, IngredientQuantity

logger = logging.getLogger(__name__)


class PrepSheetGenerator:
    """Generate kitchen prep sheets from BEO events"""

    def __init__(self):
        self.header_text = "THE LARIAT - KITCHEN PREP SHEET"

    def generate_text_prep_sheet(
        self,
        event: BanquetEvent,
        ingredients: Optional[List[IngredientQuantity]] = None
    ) -> str:
        """
        Generate a text-format prep sheet

        Args:
            event: The banquet event
            ingredients: Optional calculated ingredients (uses event's if not provided)

        Returns:
            Formatted prep sheet as string
        """
        ingredients = ingredients or event.ingredients_needed

        lines = []
        lines.append("=" * 60)
        lines.append(self.header_text)
        lines.append("=" * 60)

        # Event details
        lines.append(f"\nEvent ID: {event.event_id}")
        lines.append(f"Client: {event.client_name}")
        lines.append(f"Date: {event.event_date.strftime('%A, %B %d, %Y')}")
        lines.append(f"Guest Count: {event.guest_count}")

        if event.notes:
            lines.append(f"Notes: {event.notes}")

        # Menu items
        lines.append("\n" + "-" * 40)
        lines.append("MENU ITEMS")
        lines.append("-" * 40)

        for item in event.menu_items:
            lines.append(f"  • {item.name} (x{item.quantity})")

        # Ingredients needed
        lines.append("\n" + "-" * 40)
        lines.append("INGREDIENTS TO PREP")
        lines.append("-" * 40)

        # Group by category or type
        ingredient_groups: Dict[str, List[IngredientQuantity]] = {
            'PROTEINS': [],
            'PRODUCE': [],
            'DAIRY': [],
            'SPICES': [],
            'OTHER': []
        }

        for ing in ingredients:
            name_upper = ing.ingredient_name.upper()

            if any(p in name_upper for p in ['CHICKEN', 'BEEF', 'PORK', 'FISH', 'SHRIMP']):
                ingredient_groups['PROTEINS'].append(ing)
            elif any(p in name_upper for p in ['LETTUCE', 'TOMATO', 'ONION', 'POTATO', 'CUCUMBER', 'GREENS']):
                ingredient_groups['PRODUCE'].append(ing)
            elif any(p in name_upper for p in ['BUTTER', 'CREAM', 'CHEESE', 'MILK']):
                ingredient_groups['DAIRY'].append(ing)
            elif any(p in name_upper for p in ['SALT', 'PEPPER', 'GARLIC', 'OREGANO', 'BASIL', 'POWDER']):
                ingredient_groups['SPICES'].append(ing)
            else:
                ingredient_groups['OTHER'].append(ing)

        for category, items in ingredient_groups.items():
            if items:
                lines.append(f"\n  {category}:")
                for ing in items:
                    qty_str = f"{ing.quantity:.2f}".rstrip('0').rstrip('.')
                    lines.append(f"    [ ] {ing.ingredient_name}: {qty_str} {ing.unit}")

        # Footer
        lines.append("\n" + "-" * 40)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("=" * 60)

        return "\n".join(lines)

    def generate_html_prep_sheet(
        self,
        event: BanquetEvent,
        ingredients: Optional[List[IngredientQuantity]] = None
    ) -> str:
        """
        Generate an HTML-format prep sheet

        Args:
            event: The banquet event
            ingredients: Optional calculated ingredients

        Returns:
            HTML prep sheet as string
        """
        ingredients = ingredients or event.ingredients_needed

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Prep Sheet - {event.event_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ text-align: center; color: #333; }}
        .header {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .section {{ margin: 20px 0; }}
        .section h2 {{ color: #555; border-bottom: 2px solid #ddd; padding-bottom: 5px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f0f0f0; }}
        .checkbox {{ width: 20px; }}
        .menu-item {{ margin: 5px 0; }}
        .footer {{ margin-top: 30px; text-align: center; color: #888; font-size: 12px; }}
    </style>
</head>
<body>
    <h1>🤠 {self.header_text}</h1>

    <div class="header">
        <strong>Event ID:</strong> {event.event_id}<br>
        <strong>Client:</strong> {event.client_name}<br>
        <strong>Date:</strong> {event.event_date.strftime('%A, %B %d, %Y')}<br>
        <strong>Guest Count:</strong> {event.guest_count}
        {"<br><strong>Notes:</strong> " + event.notes if event.notes else ""}
    </div>

    <div class="section">
        <h2>Menu Items</h2>
"""

        for item in event.menu_items:
            html += f'        <div class="menu-item">• {item.name} (x{item.quantity})</div>\n'

        html += """    </div>

    <div class="section">
        <h2>Ingredients to Prep</h2>
        <table>
            <tr>
                <th class="checkbox">✓</th>
                <th>Ingredient</th>
                <th>Quantity</th>
                <th>Unit</th>
            </tr>
"""

        for ing in ingredients:
            qty_str = f"{ing.quantity:.2f}".rstrip('0').rstrip('.')
            html += f"""            <tr>
                <td class="checkbox">☐</td>
                <td>{ing.ingredient_name}</td>
                <td>{qty_str}</td>
                <td>{ing.unit}</td>
            </tr>
"""

        html += f"""        </table>
    </div>

    <div class="footer">
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    </div>
</body>
</html>"""

        return html

    def save_text_prep_sheet(
        self,
        event: BanquetEvent,
        output_path: str,
        ingredients: Optional[List[IngredientQuantity]] = None
    ):
        """Save text prep sheet to file"""
        content = self.generate_text_prep_sheet(event, ingredients)
        Path(output_path).write_text(content, encoding='utf-8')
        logger.info(f"Text prep sheet saved to {output_path}")

    def save_html_prep_sheet(
        self,
        event: BanquetEvent,
        output_path: str,
        ingredients: Optional[List[IngredientQuantity]] = None
    ):
        """Save HTML prep sheet to file"""
        content = self.generate_html_prep_sheet(event, ingredients)
        Path(output_path).write_text(content, encoding='utf-8')
        logger.info(f"HTML prep sheet saved to {output_path}")
