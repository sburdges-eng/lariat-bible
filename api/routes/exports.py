"""
Export Routes
==============
Export data in various formats.
"""

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import io
from datetime import datetime

router = APIRouter()


@router.get("/summary")
async def export_full_summary(request: Request):
    """Export complete costing summary"""
    service = request.app.state.costing_service
    summary = service.get_costing_summary()

    csv = "The Lariat Bible - Costing Summary\n"
    csv += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

    csv += "OVERVIEW\n"
    csv += f"Total Recipes,{summary.get('total_recipes', 0)}\n"
    csv += f"Costed Recipes,{summary.get('costed_recipes', 0)}\n"
    csv += f"Total Ingredients,{summary.get('total_ingredients', 0)}\n"
    csv += f"Linked Ingredients,{summary.get('linked_ingredients', 0)}\n"
    csv += f"Average Recipe Cost,${summary.get('average_recipe_cost', 0):.2f}\n"
    csv += f"Average Portion Cost,${summary.get('average_portion_cost', 0):.2f}\n"

    return StreamingResponse(
        io.StringIO(csv),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=costing_summary.csv"}
    )


@router.get("/ingredients")
async def export_ingredients(request: Request):
    """Export ingredient master list"""
    service = request.app.state.costing_service
    ingredients = service.get_all_ingredients()

    csv = "Ingredient Master List\n\n"
    csv += "Name,Category,Unit,Cost/Unit,Vendor,Waste %,Linked\n"

    for ing in ingredients:
        csv += f"{ing['name']},"
        csv += f"{ing.get('category', '')},"
        csv += f"{ing.get('default_unit', '')},"
        csv += f"${ing.get('current_cost_per_unit', 0):.4f}," if ing.get('current_cost_per_unit') else "N/A,"
        csv += f"{ing.get('preferred_vendor', 'None')},"
        csv += f"{ing.get('waste_factor', 0) * 100:.0f}%,"
        csv += f"{'Yes' if ing.get('preferred_vendor') else 'No'}\n"

    return StreamingResponse(
        io.StringIO(csv),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ingredients.csv"}
    )


@router.get("/recipes")
async def export_all_recipes(request: Request):
    """Export all recipes with costing"""
    service = request.app.state.costing_service
    recipes = service.get_all_recipes()

    csv = "Recipe Costing Report\n\n"
    csv += "Name,Category,Type,Portions,Total Cost,Cost/Portion,Target COGS %,Suggested Price\n"

    for r in recipes:
        csv += f"{r['name']},"
        csv += f"{r.get('category', '')},"
        csv += f"{r.get('recipe_type', '')},"
        csv += f"{r.get('portions', 1)},"
        csv += f"${r.get('total_cost', 0):.2f}," if r.get('total_cost') else "N/A,"
        csv += f"${r.get('cost_per_portion', 0):.2f}," if r.get('cost_per_portion') else "N/A,"
        csv += f"{r.get('target_food_cost_pct', 0.28) * 100:.0f}%,"
        csv += f"${r.get('suggested_price', 0):.2f}\n" if r.get('suggested_price') else "N/A\n"

    return StreamingResponse(
        io.StringIO(csv),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=recipes.csv"}
    )


@router.get("/portion-pricing")
async def export_portion_pricing(request: Request):
    """Export portion pricing analysis"""
    service = request.app.state.costing_service
    recipes = service.get_all_recipes()

    csv = "Portion Pricing Analysis\n\n"
    csv += "Recipe,Cost/Portion,Price @ 25%,Price @ 28%,Price @ 30%,Price @ 32%,Price @ 35%\n"

    for r in recipes:
        cost = r.get('cost_per_portion')
        if cost:
            csv += f"{r['name']},"
            csv += f"${cost:.2f},"
            csv += f"${cost/0.25:.2f},"
            csv += f"${cost/0.28:.2f},"
            csv += f"${cost/0.30:.2f},"
            csv += f"${cost/0.32:.2f},"
            csv += f"${cost/0.35:.2f}\n"

    return StreamingResponse(
        io.StringIO(csv),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=portion_pricing.csv"}
    )


@router.get("/menu-items")
async def export_menu_items(request: Request):
    """Export menu items with profitability"""
    service = request.app.state.costing_service
    items = service.get_all_menu_items()

    csv = "Menu Item Profitability Report\n\n"
    csv += "Name,Category,Menu Price,Food Cost,COGS %,Gross Profit,Monthly Sales,Monthly Profit\n"

    for item in items:
        monthly_profit = (item.get('gross_profit', 0) or 0) * (item.get('monthly_sales', 0) or 0)

        csv += f"{item['name']},"
        csv += f"{item.get('category', '')},"
        csv += f"${item.get('menu_price', 0):.2f}," if item.get('menu_price') else "N/A,"
        csv += f"${item.get('total_food_cost', 0):.2f}," if item.get('total_food_cost') else "N/A,"
        csv += f"{item.get('food_cost_pct', 0) * 100:.1f}%," if item.get('food_cost_pct') else "N/A,"
        csv += f"${item.get('gross_profit', 0):.2f}," if item.get('gross_profit') else "N/A,"
        csv += f"{item.get('monthly_sales', 0)},"
        csv += f"${monthly_profit:.2f}\n"

    return StreamingResponse(
        io.StringIO(csv),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=menu_profitability.csv"}
    )


@router.get("/costing-book")
async def export_costing_book(request: Request):
    """Export complete costing book (JSON format)"""
    service = request.app.state.costing_service

    book = {
        'generated': datetime.now().isoformat(),
        'restaurant': 'The Lariat',
        'summary': service.get_costing_summary(),
        'ingredients': service.get_all_ingredients(),
        'recipes': service.get_all_recipes(),
        'menu_items': service.get_all_menu_items()
    }

    import json
    json_str = json.dumps(book, indent=2, default=str)

    return StreamingResponse(
        io.StringIO(json_str),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=costing_book.json"}
    )
