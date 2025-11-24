"""
The Lariat Bible - FastAPI Backend
===================================
REST API for restaurant management system.

Provides endpoints for:
- Vendor file upload and matching
- Ingredient library management
- Recipe costing
- Menu item profitability
- External data integration
- Export functionality
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from api.routes import vendors, ingredients, recipes, menu_items, external_data, exports

# Import services for startup
from api.services.costing_service import CostingService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown"""
    # Startup: Initialize services
    app.state.costing_service = CostingService()
    print("Lariat Bible API - Services initialized")
    yield
    # Shutdown: Cleanup
    print("Lariat Bible API - Shutting down")


# Create FastAPI app
app = FastAPI(
    title="The Lariat Bible API",
    description="Restaurant management system for recipe costing, vendor comparison, and menu optimization",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(vendors.router, prefix="/api/vendors", tags=["Vendors"])
app.include_router(ingredients.router, prefix="/api/ingredients", tags=["Ingredients"])
app.include_router(recipes.router, prefix="/api/recipes", tags=["Recipes"])
app.include_router(menu_items.router, prefix="/api/menu-items", tags=["Menu Items"])
app.include_router(external_data.router, prefix="/api/external-data", tags=["External Data"])
app.include_router(exports.router, prefix="/api/exports", tags=["Exports"])


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Welcome to The Lariat Bible API",
        "status": "operational",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "vendors": "/api/vendors",
            "ingredients": "/api/ingredients",
            "recipes": "/api/recipes",
            "menu_items": "/api/menu-items",
            "external_data": "/api/external-data",
            "exports": "/api/exports"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Lariat Bible API",
        "restaurant": os.getenv("RESTAURANT_NAME", "The Lariat")
    }


@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    # This would be populated from actual data in production
    return {
        "ingredients": {"total": 0, "linked": 0},
        "recipes": {"total": 0, "costed": 0},
        "menu_items": {"total": 0},
        "potential_savings": 52000
    }


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", 8000))

    print(f"\n The Lariat Bible API")
    print(f" Starting server at http://{host}:{port}")
    print(f" API Docs: http://{host}:{port}/docs")
    print(f"\n Ctrl+C to stop\n")

    uvicorn.run(app, host=host, port=port, reload=True)
