"""
Recipe Routes
==============
Manage recipes with costing.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import io

router = APIRouter()


class RecipeIngredientData(BaseModel):
    ingredient_id: str
    quantity: float
    unit: str = "oz"
    prep_notes: Optional[str] = None


class RecipeCreate(BaseModel):
    name: str
    recipe_type: str = "menu_item"
    category: Optional[str] = None
    portions: int = 1
    yield_quantity: float = 1
    yield_unit: str = "portion"
    target_food_cost_pct: float = 0.28
    instructions: Optional[str] = None
    ingredients: List[RecipeIngredientData] = []


class RecipeUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    portions: Optional[int] = None
    target_food_cost_pct: Optional[float] = None
    instructions: Optional[str] = None


class ParseRequest(BaseModel):
    text: str
    source: str = "text"


@router.get("")
async def get_all_recipes(request: Request):
    """Get all recipes"""
    service = request.app.state.costing_service
    return {"recipes": service.get_all_recipes()}


@router.get("/portion-pricing")
async def get_portion_pricing(request: Request):
    """Get portion pricing analysis for all recipes"""
    service = request.app.state.costing_service
    recipes = service.get_all_recipes()

    pricing = []
    for recipe in recipes:
        if recipe.get('cost_per_portion'):
            cost = recipe['cost_per_portion']
            pricing.append({
                'name': recipe['name'],
                'cost_per_portion': cost,
                'price_25': round(cost / 0.25, 2),
                'price_28': round(cost / 0.28, 2),
                'price_30': round(cost / 0.30, 2),
                'price_32': round(cost / 0.32, 2),
                'price_35': round(cost / 0.35, 2)
            })

    return {"pricing": pricing}


@router.get("/{recipe_id}")
async def get_recipe(request: Request, recipe_id: str):
    """Get recipe by ID with full details"""
    service = request.app.state.costing_service
    recipe = service.get_recipe(recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return recipe


@router.post("")
async def create_recipe(request: Request, data: RecipeCreate):
    """Create a new recipe"""
    service = request.app.state.costing_service
    return service.create_recipe(data.model_dump())


@router.put("/{recipe_id}")
async def update_recipe(request: Request, recipe_id: str, data: RecipeUpdate):
    """Update a recipe"""
    service = request.app.state.costing_service
    result = service.update_recipe(recipe_id, data.model_dump(exclude_none=True))

    if not result:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return result


@router.delete("/{recipe_id}")
async def delete_recipe(request: Request, recipe_id: str):
    """Delete a recipe"""
    service = request.app.state.costing_service
    recipe = service.get_recipe(recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Would actually delete from engine
    return {"message": "Recipe deleted", "id": recipe_id}


@router.post("/{recipe_id}/cost")
async def cost_recipe(request: Request, recipe_id: str):
    """Calculate costs for a recipe"""
    service = request.app.state.costing_service
    result = service.cost_recipe(recipe_id)

    if not result:
        raise HTTPException(status_code=404, detail="Recipe not found or costing failed")

    return result


@router.post("/cost-all")
async def cost_all_recipes(request: Request):
    """Cost all recipes"""
    service = request.app.state.costing_service
    return service.cost_all_recipes()


@router.get("/{recipe_id}/cost-history")
async def get_cost_history(request: Request, recipe_id: str):
    """Get cost history for a recipe"""
    service = request.app.state.costing_service
    return {"history": service.get_cost_history(recipe_id)}


@router.post("/parse")
async def parse_recipes(request: Request, data: ParseRequest):
    """Parse recipes from text"""
    service = request.app.state.costing_service
    recipes = service.parse_recipes(data.text, data.source)
    return {"recipes": recipes, "count": len(recipes)}


@router.post("/parse-google-doc")
async def parse_google_doc(request: Request, data: ParseRequest):
    """Parse recipes from Google Doc content"""
    service = request.app.state.costing_service
    recipes = service.parse_recipes(data.text, "Lariat Recipe Book")
    return {"recipes": recipes, "count": len(recipes)}


@router.get("/{recipe_id}/export/csv")
async def export_recipe_csv(request: Request, recipe_id: str):
    """Export recipe to CSV"""
    service = request.app.state.costing_service
    recipe = service.get_recipe(recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Generate CSV
    from modules.kitchen_core import CostingExporter, Recipe
    exporter = CostingExporter()

    # Would need to convert dict back to Recipe object
    # For now, return simple CSV
    csv = f"Recipe: {recipe['name']}\n"
    csv += f"Total Cost: ${recipe.get('total_cost', 0):.2f}\n"
    csv += f"Cost/Portion: ${recipe.get('cost_per_portion', 0):.2f}\n\n"
    csv += "Ingredient,Quantity,Unit,Cost\n"

    for ing in recipe.get('ingredients', []):
        csv += f"{ing['ingredient_name']},{ing['quantity']},{ing['unit']},${ing.get('extended_cost', 0):.2f}\n"

    return StreamingResponse(
        io.StringIO(csv),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={recipe['name'].replace(' ', '_')}.csv"}
    )


@router.get("/export/summary")
async def export_summary(request: Request):
    """Export all recipes summary to CSV"""
    service = request.app.state.costing_service
    recipes = service.get_all_recipes()

    csv = "Recipe Costing Summary\n\n"
    csv += "Recipe,Category,Portions,Total Cost,Cost/Portion,Suggested Price\n"

    for r in recipes:
        csv += f"{r['name']},{r.get('category', '')},{r['portions']},"
        csv += f"${r.get('total_cost', 0):.2f},"
        csv += f"${r.get('cost_per_portion', 0):.2f},"
        csv += f"${r.get('suggested_price', 0):.2f}\n"

    return StreamingResponse(
        io.StringIO(csv),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=recipe_summary.csv"}
    )


@router.post("/{recipe_id}/ingredients")
async def add_ingredient_to_recipe(
    request: Request,
    recipe_id: str,
    data: RecipeIngredientData
):
    """Add ingredient to recipe"""
    service = request.app.state.costing_service
    recipe = service.get_recipe(recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Would add ingredient to recipe
    return {"message": "Ingredient added", "recipe_id": recipe_id}


@router.delete("/{recipe_id}/ingredients/{ingredient_id}")
async def remove_ingredient_from_recipe(
    request: Request,
    recipe_id: str,
    ingredient_id: str
):
    """Remove ingredient from recipe"""
    service = request.app.state.costing_service
    recipe = service.get_recipe(recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return {"message": "Ingredient removed", "recipe_id": recipe_id, "ingredient_id": ingredient_id}
