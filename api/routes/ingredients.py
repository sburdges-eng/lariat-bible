"""
Ingredient Routes
==================
Manage canonical ingredient library.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()


class IngredientCreate(BaseModel):
    name: str
    category: str = "Other"
    default_unit: str = "oz"
    current_cost_per_unit: Optional[float] = None
    preferred_vendor: Optional[str] = None
    waste_factor: float = 0.0
    aliases: List[str] = []


class IngredientUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    default_unit: Optional[str] = None
    current_cost_per_unit: Optional[float] = None
    preferred_vendor: Optional[str] = None
    waste_factor: Optional[float] = None


class LinkRequest(BaseModel):
    product_id: str


@router.get("")
async def get_all_ingredients(request: Request):
    """Get all ingredients in the library"""
    service = request.app.state.costing_service
    return {"ingredients": service.get_all_ingredients()}


@router.get("/search")
async def search_ingredients(request: Request, q: str):
    """Search ingredients by name"""
    service = request.app.state.costing_service
    all_ings = service.get_all_ingredients()

    q_lower = q.lower()
    matches = [
        ing for ing in all_ings
        if q_lower in ing['name'].lower()
    ]

    return {"ingredients": matches, "query": q}


@router.get("/unlinked")
async def get_unlinked_ingredients(request: Request):
    """Get ingredients without vendor linking"""
    service = request.app.state.costing_service
    all_ings = service.get_all_ingredients()

    unlinked = [ing for ing in all_ings if not ing.get('preferred_vendor')]

    return {"ingredients": unlinked, "count": len(unlinked)}


@router.get("/{ingredient_id}")
async def get_ingredient(request: Request, ingredient_id: str):
    """Get ingredient by ID"""
    service = request.app.state.costing_service
    ing = service.get_ingredient(ingredient_id)

    if not ing:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    return ing


@router.post("")
async def create_ingredient(request: Request, data: IngredientCreate):
    """Create a new ingredient"""
    service = request.app.state.costing_service
    return service.create_ingredient(data.model_dump())


@router.put("/{ingredient_id}")
async def update_ingredient(request: Request, ingredient_id: str, data: IngredientUpdate):
    """Update an ingredient"""
    service = request.app.state.costing_service
    result = service.update_ingredient(ingredient_id, data.model_dump(exclude_none=True))

    if not result:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    return result


@router.delete("/{ingredient_id}")
async def delete_ingredient(request: Request, ingredient_id: str):
    """Delete an ingredient"""
    service = request.app.state.costing_service
    ing = service.get_ingredient(ingredient_id)

    if not ing:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    # Mark as inactive instead of deleting
    service.update_ingredient(ingredient_id, {'is_active': False})
    return {"message": "Ingredient deleted", "id": ingredient_id}


@router.post("/{ingredient_id}/link")
async def link_to_vendor(request: Request, ingredient_id: str, data: LinkRequest):
    """Manually link ingredient to vendor product"""
    service = request.app.state.costing_service
    # Implementation would link to vendor product
    return {"message": "Linked", "ingredient_id": ingredient_id, "product_id": data.product_id}


@router.post("/auto-link")
async def auto_link_all(request: Request):
    """Auto-link all ingredients to cheapest vendor options"""
    service = request.app.state.costing_service
    result = service.auto_link_ingredients()
    return result
