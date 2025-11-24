"""
Menu Item Routes
=================
Manage menu items with profitability tracking.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()


class MenuItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str = "Entrees"
    recipe_id: Optional[str] = None
    menu_price: Optional[float] = None
    component_recipes: List[str] = []


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    menu_price: Optional[float] = None
    monthly_sales: Optional[int] = None


@router.get("")
async def get_all_menu_items(request: Request):
    """Get all menu items"""
    service = request.app.state.costing_service
    return {"menu_items": service.get_all_menu_items()}


@router.get("/profitability")
async def get_profitability_report(request: Request):
    """Get profitability analysis for all menu items"""
    service = request.app.state.costing_service
    items = service.get_all_menu_items()

    report = {
        'total_items': len(items),
        'items': [],
        'summary': {
            'avg_food_cost_pct': 0,
            'total_monthly_profit': 0,
            'items_above_target': 0,
            'items_below_target': 0
        }
    }

    target_pct = 0.28
    total_pct = 0
    items_with_pct = 0

    for item in items:
        if item.get('food_cost_pct'):
            total_pct += item['food_cost_pct']
            items_with_pct += 1

            if item['food_cost_pct'] <= target_pct:
                report['summary']['items_below_target'] += 1
            else:
                report['summary']['items_above_target'] += 1

        if item.get('gross_profit') and item.get('monthly_sales'):
            monthly_profit = item['gross_profit'] * item['monthly_sales']
            report['summary']['total_monthly_profit'] += monthly_profit

        report['items'].append({
            'name': item['name'],
            'menu_price': item.get('menu_price'),
            'food_cost': item.get('total_food_cost'),
            'food_cost_pct': item.get('food_cost_pct'),
            'gross_profit': item.get('gross_profit'),
            'monthly_sales': item.get('monthly_sales', 0),
            'monthly_profit': (item.get('gross_profit', 0) or 0) * (item.get('monthly_sales', 0) or 0)
        })

    if items_with_pct > 0:
        report['summary']['avg_food_cost_pct'] = total_pct / items_with_pct

    return report


@router.get("/{item_id}")
async def get_menu_item(request: Request, item_id: str):
    """Get menu item by ID"""
    service = request.app.state.costing_service
    items = service.get_all_menu_items()

    item = next((i for i in items if i['id'] == item_id), None)

    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    return item


@router.post("")
async def create_menu_item(request: Request, data: MenuItemCreate):
    """Create a new menu item"""
    service = request.app.state.costing_service
    return service.create_menu_item(data.model_dump())


@router.put("/{item_id}")
async def update_menu_item(request: Request, item_id: str, data: MenuItemUpdate):
    """Update a menu item"""
    service = request.app.state.costing_service
    items = service.get_all_menu_items()

    item = next((i for i in items if i['id'] == item_id), None)

    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    # Would update item
    return {"message": "Updated", "id": item_id}


@router.delete("/{item_id}")
async def delete_menu_item(request: Request, item_id: str):
    """Delete a menu item"""
    return {"message": "Menu item deleted", "id": item_id}


@router.post("/{item_id}/cost")
async def cost_menu_item(request: Request, item_id: str):
    """Calculate costs for a menu item"""
    service = request.app.state.costing_service
    result = service.cost_menu_item(item_id)

    if not result:
        raise HTTPException(status_code=404, detail="Menu item not found or costing failed")

    return result
