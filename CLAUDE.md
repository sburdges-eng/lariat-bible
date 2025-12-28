# CLAUDE.md - The Lariat Bible Developer Guide

> Comprehensive guide for AI assistants working on The Lariat Bible restaurant management system

## Table of Contents
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Development Setup](#development-setup)
- [Module Documentation](#module-documentation)
- [Development Workflows](#development-workflows)
- [Code Conventions](#code-conventions)
- [Data Models](#data-models)
- [Testing Strategy](#testing-strategy)
- [Common Tasks](#common-tasks)
- [Important Context](#important-context)

---

## Project Overview

**The Lariat Bible** is a comprehensive restaurant management system built for The Lariat restaurant in Fort Collins, Colorado. It serves as the single source of truth for restaurant operations.

### Business Context
# CLAUDE.md - The Lariat Bible

> **AI Assistant Guide for The Lariat Restaurant Management System**
> Last Updated: 2025-11-18

## Project Overview

**The Lariat Bible** is a comprehensive restaurant management system for The Lariat restaurant in Fort Collins, Colorado. This system serves as the single source of truth for vendor pricing, inventory management, recipe standardization, catering operations, equipment maintenance, and financial reporting.

### Key Business Metrics
- **Monthly Catering Revenue**: $28,000
- **Monthly Restaurant Revenue**: $20,000
- **Target Catering Margin**: 45%
- **Target Restaurant Margin**: 4%
- **Annual Savings Potential**: $52,000 (switching from SYSCO to Shamrock Foods)

### Primary Goals
1. Vendor price comparison and optimization
2. Inventory management and tracking
3. Recipe standardization and costing
4. Catering operations management
5. Equipment maintenance scheduling
6. Financial reporting and business intelligence

### Tech Stack
- **Backend**: Python 3.8+, Flask
- **Database**: SQLAlchemy (currently SQLite, designed for PostgreSQL migration)
- **Data Processing**: Pandas, NumPy
- **OCR**: Pytesseract, OpenCV
- **PDF Processing**: PyPDF2, ReportLab
- **Testing**: Pytest
- **Code Quality**: Black (formatting), Flake8 (linting)

---

## Architecture

### Directory Structure
```
lariat-bible/
├── app.py                      # Flask web application entry point
├── setup.py                    # Initial setup and configuration
├── requirements.txt            # Python dependencies
│
├── modules/                    # Business logic modules
│   ├── core/
│   │   └── lariat_bible.py    # Main integration class
│   ├── vendor_analysis/
│   │   ├── __init__.py
│   │   ├── comparator.py      # Price comparison engine
│   │   ├── accurate_matcher.py # Product matching logic
│   │   └── corrected_comparison.py
│   ├── recipes/
│   │   └── recipe.py          # Recipe, Ingredient, RecipeIngredient models
│   ├── menu/
│   │   ├── __init__.py
│   │   └── menu_item.py       # MenuItem model
│   ├── order_guides/
│   │   └── order_guide_manager.py # Order guide comparison
│   ├── equipment/
│   │   └── equipment_manager.py   # Equipment tracking
│   └── email_parser/
│       └── email_parser.py    # Invoice email parsing
│
├── data/                      # Data storage (gitignored)
│   ├── invoices/             # Invoice images and PDFs
│   ├── exports/              # Generated reports
│   └── *.csv                 # Comparison data
│
├── static/                   # Web assets (planned)
├── templates/                # HTML templates (planned)
├── tests/                    # Test suites (to be developed)
├── logs/                     # Application logs (gitignored)
└── backups/                  # Data backups (gitignored)
```

### Core Architecture Pattern
The system uses a **modular, dataclass-based architecture**:
- Each module is self-contained with clear responsibilities
- Data models use Python dataclasses for type safety
- Central integration through `LariatBible` class
- Flask API provides REST endpoints for web interface

---

## Development Setup

### Initial Setup
```bash
# Clone repository
- **Potential Annual Savings** (Shamrock vs SYSCO): $52,000 (~29.5% savings)

### Project Purpose
The owner, Sean, needs a data-driven system to:
1. Compare vendor pricing and identify savings (primarily Shamrock Foods vs SYSCO)
2. Track and cost recipes accurately
3. Optimize menu pricing to hit target margins
4. Manage equipment maintenance schedules
5. Streamline catering operations
6. Generate business intelligence reports

---

## Repository Structure

```
lariat-bible/
├── app.py                      # Flask web application entry point
├── setup.py                    # Initial setup script
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration (gitignored)
├── data/                       # Data storage
│   ├── invoices/              # Vendor invoices (images/PDFs)
│   └── *.csv                  # Sample comparison data
├── modules/                    # Business logic modules
│   ├── core/                  # Core integration
│   │   └── lariat_bible.py   # Main LariatBible class (359 lines)
│   ├── vendor_analysis/       # Price comparison & OCR
│   │   ├── __init__.py
│   │   ├── comparator.py     # VendorComparator class
│   │   ├── accurate_matcher.py
│   │   └── corrected_comparison.py
│   ├── recipes/               # Recipe management
│   │   └── recipe.py         # Recipe, Ingredient classes
│   ├── menu/                  # Menu items
│   │   ├── __init__.py
│   │   └── menu_item.py      # MenuItem class
│   ├── order_guides/          # Vendor order guides
│   │   └── order_guide_manager.py
│   ├── equipment/             # Equipment tracking
│   │   └── equipment_manager.py
│   └── email_parser/          # Email invoice parsing
│       └── email_parser.py
├── documentation/              # Additional docs
│   ├── README.md
│   ├── PRODUCT_MATCHING_VERIFICATION.md
│   ├── GITHUB_SETUP.md
│   └── GITHUB_QUICK_SETUP.md
└── CLAUDE.md                  # This file
```

### Lines of Code
- **Total Python Code**: ~2,422 lines
- **Development Stage**: Early/Active Development
- Many modules are scaffolded but not fully implemented

---

## Technology Stack

### Core Technologies
- **Language**: Python 3.8+
- **Web Framework**: Flask 3.0.0
- **Database**: SQLAlchemy 2.0.23 (SQLite for development)
- **API**: Flask-CORS, RESTful endpoints

### Data Processing
- **pandas** 2.1.4 - Data analysis and vendor comparisons
- **numpy** 1.26.2 - Numerical operations
- **openpyxl** 3.1.2 - Excel file handling

### OCR & Image Processing
- **pytesseract** 0.3.10 - OCR for invoice processing
- **Pillow** 10.1.0 - Image manipulation
- **opencv-python** 4.8.1.78 - Image preprocessing
- **PyPDF2** 3.0.1 - PDF processing

### Development Tools
- **black** - Code formatting (run before commits)
- **flake8** - Linting
- **pytest** - Testing framework
- **pre-commit** - Git hooks

### Other Key Libraries
- **python-dotenv** - Environment configuration
- **pydantic** - Data validation
- **rich** - Terminal output formatting
- **schedule** - Task scheduling (maintenance reminders)

---

## Core Architecture

### Main Integration Point: `LariatBible` Class

The `modules/core/lariat_bible.py` file contains the central `LariatBible` class that coordinates all modules:

```python
from modules.core.lariat_bible import lariat_bible

# Singleton instance available for import
lariat_bible.add_ingredient(ingredient)
lariat_bible.create_recipe_with_costing(recipe)
lariat_bible.run_comprehensive_comparison()
```

### Key Classes and Their Relationships

1. **Ingredient** (recipes/recipe.py)
   - Stores pricing from multiple vendors
   - Calculates best price and preferred vendor
   - Tracks last update timestamps

2. **Recipe** (recipes/recipe.py)
   - Contains RecipeIngredient objects
   - Calculates total cost and cost per portion
   - Analyzes vendor impact

3. **MenuItem** (menu/menu_item.py)
   - Links to Recipe
   - Tracks menu price and food cost
   - Calculates margins and suggests pricing

4. **VendorComparator** (vendor_analysis/comparator.py)
   - Compares Shamrock Foods vs SYSCO
   - Identifies savings opportunities
   - Generates reports

5. **OrderGuideManager** (order_guides/order_guide_manager.py)
   - Manages vendor product catalogs
   - Performs bulk price comparisons
   - Exports comparison spreadsheets

6. **EquipmentManager** (equipment/equipment_manager.py)
   - Tracks equipment and maintenance
   - Schedules preventive maintenance
   - Manages vendor contacts

---

## Development Workflows

### Setting Up the Development Environment

```bash
# Clone and setup
git clone <repository-url>
cd lariat-bible

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run setup script
python setup.py

# Configure environment
# Edit .env file with your settings

# Start development server
python app.py
```

### Environment Configuration
The `.env` file contains critical configuration:
```env
# Database
DATABASE_URL=sqlite:///lariat.db

# Security
SECRET_KEY=change-this-to-a-random-secret-key

# Paths
INVOICE_STORAGE_PATH=./data/invoices
BACKUP_PATH=./backups

# Business Settings
RESTAURANT_NAME=The Lariat
LOCATION=Fort Collins, CO
DEFAULT_CATERING_MARGIN=0.45
DEFAULT_RESTAURANT_MARGIN=0.04

# Vendor Information
PRIMARY_VENDOR=Shamrock Foods
COMPARISON_VENDOR=SYSCO

# Web Interface
FLASK_ENV=development
FLASK_DEBUG=True
HOST=127.0.0.1
PORT=5000
```

---

## Module Documentation

### 1. Core Module (`modules/core/lariat_bible.py`)

**Purpose**: Main integration point for all system functionality

**Key Class**: `LariatBible`
- Coordinates all managers and modules
- Maintains restaurant metrics
- Provides high-level business operations

**Important Methods**:
- `add_ingredient(ingredient)` - Add/update ingredient with vendor pricing
- `create_recipe_with_costing(recipe)` - Create recipe and calculate costs
- `link_recipe_to_menu(recipe_id, menu_item_id)` - Connect recipes to menu items
- `run_comprehensive_comparison()` - Execute full vendor analysis
- `optimize_menu_pricing()` - Analyze and suggest price adjustments
- `generate_executive_summary()` - Create comprehensive report
- `export_all_data(export_dir)` - Export all data for backup

### 2. Vendor Analysis Module (`modules/vendor_analysis/`)

**Purpose**: Compare vendor prices and identify savings opportunities

**Key Files**:
- `comparator.py` - Main comparison engine
- `accurate_matcher.py` - Product matching between vendors
- `corrected_comparison.py` - Verified comparisons

**Critical Considerations**:
- **Product matching MUST be exact** (see `PRODUCT_MATCHING_VERIFICATION.md`)
- Different grinds of spices are NOT interchangeable
- Black pepper fine ≠ Black pepper coarse
- Garlic powder ≠ Garlic granulated

**Key Class**: `VendorComparator`
- `compare_vendors(vendor1, vendor2)` - Calculate savings
- `analyze_category(category, items)` - Category-level analysis
- `identify_top_savings(products, top_n)` - Find biggest opportunities
- `generate_report(output_path)` - Create formatted report
- `calculate_margin_impact(monthly_savings)` - Impact on margins

**NEW: Hybrid Vendor Matcher** (`hybrid_matcher.py`)

The most powerful tool for vendor comparison - combines automated fuzzy matching with critical specification validation.

**Key Class**: `HybridVendorMatcher`
- `match_all(shamrock_df, sysco_df)` - Match all products with validation
- `to_dataframe()` - Export matches to DataFrame
- `to_ingredients()` - Convert matches to Ingredient objects
- `get_savings_summary()` - Calculate total savings potential

**Features**:
- **Fuzzy Matching**: Automated text similarity (handles typos, variations)
- **Specification Validation**: REJECTS mismatches (Fine ≠ Coarse pepper)
- **Pack Size Intelligence**: Correctly interprets Shamrock vs SYSCO formats
- **Confidence Scoring**: HIGH/MEDIUM/LOW/REJECTED
- **Direct Integration**: Outputs to Ingredient dataclass

**Workflow**:
1. Load vendor data (Excel, CSV, or DataFrame)
2. Fuzzy match finds candidates (similarity scoring)
3. Specification validator checks for critical mismatches
4. Pack size parser calculates unit prices
5. Results ranked by confidence and savings
6. High-confidence matches → Ingredient objects

**Vendor Data**:
- Shamrock Foods: 29.5% average discount vs SYSCO
- Monthly savings potential: ~$4,333
- Annual savings potential: ~$52,000

### 3. Recipe Module (`modules/recipes/recipe.py`)

**Purpose**: Manage recipes, ingredients, and costing

**Data Models**:

**`Ingredient`** (Dataclass):
```python
- ingredient_id: str
- name: str
- category: str
- unit_of_measure: str
- case_size: str
- sysco_item_code, sysco_price, sysco_unit_price
- shamrock_item_code, shamrock_price, shamrock_unit_price
- preferred_vendor: str
- price_difference: float
- storage_location: str
- shelf_life_days: int
```

**`RecipeIngredient`** (Dataclass):
```python
- ingredient: Ingredient
- quantity: float
- unit: str
- prep_instruction: str
- cost: float (calculated property)
```

**`Recipe`** (Dataclass):
```python
- recipe_id: str
- name: str
- category: str
- yield_amount: float
- yield_unit: str
- portion_size: str
- ingredients: List[RecipeIngredient]
- prep_instructions: List[str]
- cooking_instructions: List[str]
- total_cost: float (calculated property)
- cost_per_portion: float (calculated property)
```

**Key Methods**:
- `Ingredient.calculate_best_price()` - Determine preferred vendor
- `Recipe.get_shopping_list(multiplier)` - Generate vendor-optimized list
- `Recipe.analyze_vendor_impact()` - Compare costs across vendors

### 4. Menu Module (`modules/menu/menu_item.py`)

**Purpose**: Manage menu items with pricing and recipe links

**`MenuItem`** (Dataclass):
```python
- item_id: str
- name: str
- category: str (Appetizer, Entree, Dessert, etc.)
- menu_price: float
- food_cost: float
- target_margin: float (default 0.30)
- recipe_id: str (optional link)
- available: bool
- seasonal: bool
- dietary_flags: List[str]
- allergens: List[str]
- popularity_score: int
- monthly_sales: int
```

**Calculated Properties**:
- `margin` - Actual profit margin
- `margin_variance` - Difference from target
- `suggested_price` - Price to achieve target margin

**Key Methods**:
- `update_food_cost(new_cost)` - Update cost and analyze pricing
- `to_dict()` / `from_dict()` - Serialization

### 5. Order Guide Manager (`modules/order_guides/order_guide_manager.py`)

**Purpose**: Manage and compare vendor order guides

**Key Operations**:
- Load SYSCO order guide
- Load Shamrock order guide
- Compare prices across vendors
- Generate purchase recommendations
- Export comparison reports

### 6. Equipment Manager (`modules/equipment/equipment_manager.py`)

**Purpose**: Track equipment, maintenance schedules, and history

**Key Features**:
- Equipment inventory
- Maintenance scheduling
- Service history logging
- Depreciation tracking
- Vendor contact management

### 7. Email Parser (`modules/email_parser/email_parser.py`)

**Purpose**: Parse vendor invoice emails for automated data extraction

**Capabilities**:
- Extract invoice data from emails
- OCR invoice images
- Match products to database
- Auto-update pricing
- Flag price changes

---

## Development Workflows

### Adding a New Ingredient
```python
from modules.recipes.recipe import Ingredient
from modules.core.lariat_bible import lariat_bible

ingredient = Ingredient(
    ingredient_id="ING001",
    name="Black Pepper Fine",
    category="Spice",
    unit_of_measure="lb",
    case_size="25 lb bag",
    sysco_item_code="1234567",
    sysco_price=50.00,
    sysco_unit_price=2.00,
    shamrock_item_code="SHA001",
    shamrock_price=35.00,
    shamrock_unit_price=1.40
)

result = lariat_bible.add_ingredient(ingredient)
# Returns preferred vendor and savings
```

### Creating a Recipe with Costing
```python
from modules.recipes.recipe import Recipe, RecipeIngredient

recipe = Recipe(
    recipe_id="RCP001",
    name="House BBQ Sauce",
    category="Sauce",
    yield_amount=128,
    yield_unit="oz",
    portion_size="2 oz",
    ingredients=[
        RecipeIngredient(
            ingredient=black_pepper_ingredient,
            quantity=0.25,
            unit="lb",
            prep_instruction="freshly ground"
        ),
        # ... more ingredients
    ]
)

result = lariat_bible.create_recipe_with_costing(recipe)
# Returns cost per portion, vendor analysis, suggested price
```

### Running Vendor Comparison (Legacy)
# Run setup
python setup.py

# Configure .env file
# Edit .env with your settings
```

### Running the Application

```bash
# Start Flask development server
python app.py

# Access at http://127.0.0.1:5000
# API endpoints:
# - GET /                       - Dashboard
# - GET /api/health            - Health check
# - GET /api/modules           - List modules
# - GET /api/vendor-comparison - Vendor savings
```

### Code Quality Standards

**Before committing:**
```bash
# Format code
black .

# Lint code
flake8 .

# Run tests
pytest
```

**Commit message format:**
```
<type>: <description>

Examples:
feat: Add invoice OCR processing
fix: Correct margin calculation in MenuItem
refactor: Simplify vendor comparison logic
docs: Update recipe costing documentation
test: Add tests for VendorComparator
```

---

## Key Conventions & Patterns

### 1. Vendor Names - CRITICAL
Always use consistent vendor names:
- **Shamrock Foods** (preferred vendor, ~29.5% cheaper)
- **SYSCO** (comparison vendor)

**Case sensitivity matters** in vendor comparisons!

### 2. Product Matching Rules

When comparing products between vendors:
- Match by EXACT product specification (not just name)
- Black Pepper Fine ≠ Black Pepper Coarse
- See `PRODUCT_MATCHING_VERIFICATION.md` for details
- Different grinds serve different culinary purposes

### 3. Pricing Calculations

**Margin formula:**
```python
margin = (menu_price - food_cost) / menu_price
```

**Target margins:**
- Catering: 45% (0.45)
- Restaurant: 4% (0.04)

**Suggested price:**
```python
suggested_price = food_cost / (1 - target_margin)
```

### 4. File Organization

**Data files:**
- Invoices: `data/invoices/`
- Exports: `data/exports/`
- Reports: `reports/`

**Naming conventions:**
- Use snake_case for Python files and variables
- Use descriptive names: `vendor_comparator` not `vc`
- Class names: PascalCase (e.g., `VendorComparator`)

### 5. Environment Variables

Required in `.env`:
```bash
DATABASE_URL=sqlite:///lariat.db
SECRET_KEY=<random-secret-key>
INVOICE_STORAGE_PATH=./data/invoices
RESTAURANT_NAME=The Lariat
PRIMARY_VENDOR=Shamrock Foods
COMPARISON_VENDOR=SYSCO
DEFAULT_CATERING_MARGIN=0.45
DEFAULT_RESTAURANT_MARGIN=0.04
```

---

## Module-Specific Guidelines

### Vendor Analysis Module

**Purpose**: Compare vendor prices, process invoices, identify savings

**Key files:**
- `comparator.py` - Main comparison logic
- `accurate_matcher.py` - Product matching algorithms
- Invoice processor (planned) - OCR for invoice data extraction

**When working on this module:**
- Always validate product matches are exact (grind, size, quality)
- Track price update timestamps
- Consider minimum order quantities
- Factor in delivery costs for true comparison

**Example usage:**
```python
from modules.vendor_analysis import VendorComparator

comparator = VendorComparator()
savings = comparator.compare_vendors('Shamrock Foods', 'SYSCO')
report = comparator.generate_report('reports/vendor_analysis.txt')
```

### Recipe Management Module

**Purpose**: Standardize recipes, calculate costs, analyze vendor impact

**Key classes:**
- `Ingredient` - Base ingredient with vendor pricing
- `RecipeIngredient` - Ingredient usage in recipe (quantity, unit)
- `Recipe` - Complete recipe with costing

**When working on this module:**
- Support recipe scaling (6 servings → 50 servings)
- Track cost history as ingredient prices change
- Consider prep time and labor costs (future)
- Handle fractional units properly (e.g., 0.25 tsp)

**Example usage:**
```python
from modules.recipes.recipe import Recipe, Ingredient, RecipeIngredient

# Create ingredient
flour = Ingredient(
    ingredient_id="ING001",
    name="All-Purpose Flour",
    sysco_price=18.99,
    shamrock_price=12.50,
    unit="LB"
)

# Create recipe
recipe = Recipe(
    recipe_id="REC001",
    name="Biscuits",
    category="Bakery",
    yield_amount=24,
    yield_unit="biscuits"
)
```

### Menu Management Module

**Purpose**: Link recipes to menu items, optimize pricing

**When working on this module:**
- Auto-update menu prices when recipe costs change
- Flag items below target margin
- Support different menu categories (catering vs restaurant)
- Calculate margin impact of price changes

### Equipment Management Module

**Purpose**: Track equipment, schedule maintenance

**When working on this module:**
- Use depreciation schedules
- Track repair history
- Alert on overdue maintenance
- Store vendor contact info

---

## Testing Strategy

### Test Organization
```
tests/
├── test_vendor_analysis.py
├── test_recipes.py
├── test_menu.py
└── test_integration.py
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific module
pytest tests/test_vendor_analysis.py

# Run with coverage
pytest --cov=modules --cov-report=html
```

### Test Data
- Use fixture data for consistent testing
- Don't commit real invoice data (sensitive)
- Mock vendor API calls if implemented

---

## Common Tasks for AI Assistants

### Adding a New Ingredient

```python
from modules.core.lariat_bible import lariat_bible
from modules.recipes.recipe import Ingredient

ingredient = Ingredient(
    ingredient_id="ING999",
    name="Paprika",
    category="Spices",
    sysco_price=15.99,
    sysco_case_size="6/1LB",
    shamrock_price=11.25,
    shamrock_case_size="25LB",
    unit="LB"
)

result = lariat_bible.add_ingredient(ingredient)
print(result)  # Shows preferred vendor and savings
```

### Creating a Recipe with Costing

```python
from modules.core.lariat_bible import lariat_bible
from modules.recipes.recipe import Recipe, RecipeIngredient

recipe = Recipe(
    recipe_id="REC999",
    name="BBQ Sauce",
    category="Sauce",
    yield_amount=1,
    yield_unit="gallon"
)

# Add ingredients
recipe.add_ingredient(RecipeIngredient(
    ingredient=existing_ingredient,
    quantity=2,
    unit="cups"
))

result = lariat_bible.create_recipe_with_costing(recipe)
print(result)  # Shows total cost, per-portion cost, vendor analysis
```

### Running Vendor Comparison

```python
from modules.core.lariat_bible import lariat_bible

# Import order guides
lariat_bible.import_order_guides(
    sysco_file="data/sysco_order_guide.xlsx",
    shamrock_file="data/shamrock_order_guide.xlsx"
)

# Run comprehensive comparison
results = lariat_bible.run_comprehensive_comparison()
# Exports to data/vendor_comparison.xlsx
```

### Running Hybrid Vendor Matching (RECOMMENDED)
```python
from modules.core.lariat_bible import lariat_bible

# Method 1: Direct from Excel file
results = lariat_bible.import_and_match_vendors(
    excel_file="data/vendor_data.xlsx",
    shamrock_sheet="Shamrock_Data",
    sysco_sheet="Sysco_Data"
)

print(f"Total matches: {results['total_matches']}")
print(f"Ingredients added: {results['ingredients_added']}")
print(f"Estimated monthly savings: ${results['savings_summary']['estimated_monthly_savings']:.2f}")

# Export results to Excel
lariat_bible.export_vendor_matches("data/hybrid_match_results.xlsx")

# Access the matched ingredients
for ingredient_id, ingredient in lariat_bible.ingredients.items():
    if ingredient.preferred_vendor == "Shamrock Foods":
        print(f"{ingredient.name}: Save ${ingredient.price_difference:.2f}/lb")
```

### Method 2: Using HybridVendorMatcher Directly
```python
from modules.vendor_analysis import HybridVendorMatcher
import pandas as pd

# Load vendor data
shamrock_df = pd.read_excel("vendor_data.xlsx", sheet_name="Shamrock_Data")
sysco_df = pd.read_excel("vendor_data.xlsx", sheet_name="Sysco_Data")

# Create matcher and run
matcher = HybridVendorMatcher()
matches = matcher.match_all(shamrock_df, sysco_df)

# Get results
df = matcher.to_dataframe()

# Filter high-confidence matches
high_conf = df[df['Confidence'] == 'HIGH']
print(f"High confidence matches: {len(high_conf)}")

# Check for specification rejections
rejected = df[df['Confidence'] == 'REJECTED']
print(f"Rejected due to spec mismatch: {len(rejected)}")

# Get savings summary
savings = matcher.get_savings_summary()
print(f"Estimated annual savings: ${savings['estimated_annual_savings']:,.2f}")
```

### Optimizing Menu Pricing
```python
from modules.core.lariat_bible import lariat_bible

# Get pricing optimization suggestions
optimization = lariat_bible.optimize_menu_pricing()

# Returns list of items needing price adjustment
for item in optimization:
    print(f"{item['item']}: ${item['current_price']} → ${item['suggested_price']}")
```

---

## Code Conventions

### Python Style
- **Formatting**: Black (line length 100)
- **Linting**: Flake8
- **Type Hints**: Use type hints for all function signatures
- **Docstrings**: Google-style docstrings for all public methods

### Naming Conventions
- **Classes**: PascalCase (e.g., `VendorComparator`, `MenuItem`)
- **Functions/Methods**: snake_case (e.g., `calculate_best_price`, `generate_report`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_MARGIN`, `SYSCO_DISCOUNT`)
- **Private methods**: Prefix with underscore (e.g., `_internal_method`)

### Import Order
1. Standard library imports
2. Third-party imports
3. Local application imports

```python
import json
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
from flask import Flask, jsonify

from modules.recipes.recipe import Recipe, Ingredient
```

### Dataclass Usage
- Use `@dataclass` for data models
- Include type hints for all fields
- Provide sensible defaults
- Implement `__post_init__` for initialization logic
- Use `@property` for calculated fields

### Error Handling
- Return dictionaries with `{'error': 'message'}` for recoverable errors
- Raise exceptions for critical errors
- Log all errors to logs directory
- Include context in error messages

---

## Data Models

### Vendor Data Structure
```python
{
    'vendor_name': str,
    'discount': float,  # As decimal (0.295 = 29.5%)
    'item_code': str,
    'description': str,
    'pack_size': str,
    'case_price': float,
    'unit_price': float,
    'category': str,
    'last_updated': datetime
}
```

### Recipe Costing Flow
```
Ingredient (with vendor prices)
    ↓
RecipeIngredient (quantity + ingredient)
    ↓
Recipe (collection of RecipeIngredients)
    ↓
MenuItem (links to Recipe)
    ↓
Menu Price Optimization
```

### Margin Calculations
- **Food Cost Percentage**: `food_cost / menu_price`
- **Margin**: `(menu_price - food_cost) / menu_price`
- **Suggested Price**: `food_cost / (1 - target_margin)`

---

## Testing Strategy

### Test Organization (Planned)
```
tests/
├── test_recipes.py          # Recipe and ingredient tests
├── test_menu.py             # Menu item tests
├── test_vendor_analysis.py  # Vendor comparison tests
├── test_integration.py      # End-to-end tests
└── fixtures/                # Test data
```

### Testing Approach
- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test module interactions
- **Data Validation**: Ensure price calculations are accurate
- **Fixtures**: Use realistic sample data from actual operations

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=modules --cov-report=html

# Run specific test file
pytest tests/test_recipes.py

# Run with verbose output
pytest -v
```

---

## Common Tasks

### Task 1: Update Vendor Pricing
1. Receive new order guide (email or file)
2. Parse using appropriate module
3. Update ingredient prices in database
4. Recalculate recipe costs
5. Generate margin impact report
6. Update menu prices if needed

### Task 2: Add New Recipe
1. Define ingredients with quantities
2. Ensure all ingredients have vendor pricing
3. Create Recipe object with instructions
4. Calculate total cost and cost per portion
5. Link to menu item (if applicable)
6. Export recipe card

### Task 3: Generate Vendor Comparison Report (Using Hybrid Matcher)
1. Prepare Excel file with two sheets:
   - `Shamrock_Data`: columns = sku, description, price, pack
   - `Sysco_Data`: columns = sku, description, price, pack
2. Run hybrid matching:
   ```python
   results = lariat_bible.import_and_match_vendors("vendor_data.xlsx")
   ```
3. Review results:
   - HIGH confidence → Auto-approve
   - MEDIUM/LOW → Manual review required
   - REJECTED → Specification mismatch (DO NOT USE)
4. Export detailed report:
   ```python
   lariat_bible.export_vendor_matches("comparison_results.xlsx")
   ```
5. Check savings summary:
   ```python
   print(results['savings_summary'])
   ```
6. Approved ingredients are automatically added to system

### Task 4: Optimize Menu Pricing
1. Ensure all menu items have linked recipes
2. Update ingredient costs from latest vendor data
3. Recalculate all recipe costs
4. Run pricing optimization
5. Review suggestions with business logic
6. Generate pricing change recommendations

---

## Important Context

### Critical Business Rules

#### Product Matching
- **NEVER assume similar products are identical**
- Black pepper fine ≠ Black pepper coarse (different mesh sizes, different uses)
- Garlic powder ≠ Garlic granulated (different textures, different applications)
- Always verify exact specifications before declaring a match
- See `PRODUCT_MATCHING_VERIFICATION.md` for detailed guidelines

#### Pricing Strategy
- **Catering target margin**: 45% (high-margin focus)
- **Restaurant target margin**: 4% (volume-based, competitive market)
- Price adjustments should maintain target margins
- Consider popularity_score when suggesting price changes

#### Vendor Selection
- **Shamrock Foods** is generally preferred (29.5% average savings)
- **SYSCO** may be better for specialty items
- Mixed vendor orders are acceptable for optimal pricing
- Consider delivery schedules and minimum orders

### Data Sensitivity
- Invoice data contains proprietary business information
- Pricing data is confidential
- All files in `data/invoices/` are gitignored
- Reports should not be committed to version control
- Use .env for sensitive configuration

### Performance Considerations
- OCR processing can be slow (use async where possible)
- Large order guide comparisons should be cached
- Export operations should run in background
- Database queries should be optimized (use indexes)

### Future Enhancements (Roadmap)
1. Database migration to PostgreSQL
2. Web dashboard with real-time updates
3. Mobile app for inventory management
4. Automated email parsing and price updates
5. Integration with POS system
6. Predictive ordering based on sales trends
7. Multi-location support
8. API for third-party integrations

---

## Flask API Endpoints

### Current Endpoints
- `GET /` - Dashboard overview
- `GET /api/health` - Health check
- `GET /api/modules` - List all modules and status
- `GET /api/vendor-comparison` - Vendor comparison data

### API Response Format
```json
{
    "status": "success|error",
    "data": {...},
    "message": "Optional message",
    "timestamp": "ISO 8601 datetime"
}
```

---

## Working with AI Assistants

### Best Practices for AI Development

1. **Always Read First**: Before modifying code, read the relevant files to understand current implementation

2. **Verify Business Logic**: Price calculations and vendor comparisons have real financial impact. Double-check all math.

3. **Respect Data Models**: Use the established dataclass structures. Don't create ad-hoc dictionaries when a model exists.

4. **Test with Real Data**: The `data/` directory contains actual comparison data. Use it for testing.

5. **Document Changes**: Update this file when adding new modules or changing architecture

6. **Follow Conventions**: Use Black for formatting, type hints for clarity, and docstrings for documentation

7. **Consider Business Context**: This is a real business. Suggestions should be practical and implementable.

8. **Handle Edge Cases**:
   - Missing vendor data
   - Products only available from one vendor
   - Zero quantities or prices
   - Seasonal availability

9. **Use Hybrid Matcher for Vendor Comparisons**:
   - ALWAYS use `HybridVendorMatcher` for new vendor comparisons
   - NEVER bypass specification validation (it prevents costly mistakes)
   - REVIEW all REJECTED matches (they failed for good reasons)
   - TRUST HIGH confidence matches
   - MANUALLY VERIFY MEDIUM/LOW confidence matches

### Common Pitfalls to Avoid

- ❌ Matching products by name similarity alone
- ❌ Assuming all prices are current
- ❌ Ignoring pack size differences
- ❌ Hard-coding business values (use constants or config)
- ❌ Committing sensitive data
- ❌ Breaking existing recipe-menu links
- ❌ Changing margins without business justification

### When in Doubt

1. Check `PRODUCT_MATCHING_VERIFICATION.md` for matching rules
2. Review existing similar implementations
3. Consult the README.md for project context
4. Ask for clarification on business rules
5. Test with sample data before production use

---

## Git Workflow

### Branch Strategy
- `main` - Production-ready code
- `claude/*` - AI development branches
- Feature branches for major changes

### Commit Messages
Follow conventional commits:
```
feat: Add vendor price comparison API endpoint
fix: Correct margin calculation for catering items
docs: Update CLAUDE.md with testing strategy
refactor: Extract price calculation to separate method
```

### Before Committing
1. Run Black: `black modules/`
2. Run Flake8: `flake8 modules/`
3. Run tests: `pytest`
4. Verify no sensitive data included
5. Update documentation if needed

---

## Maintenance & Support

### Log Files
- Application logs: `logs/app.log`
- Error logs: `logs/error.log`
- Debug logs: `logs/debug.log` (development only)

### Backup Strategy
- Daily exports to `backups/` directory
- Database backups before major changes
- Invoice data backed up to external storage

### Monitoring
- Check vendor price updates weekly
- Review margin reports monthly
- Validate recipe costs quarterly
- Update order guides as received

---

## Quick Reference

### Most Used Commands
```bash
# Start dev server
python app.py

# Run setup
python setup.py

# Format code
black modules/

# Lint code
flake8 modules/

# Run tests
pytest
```

### Key File Locations
- Main integration: `modules/core/lariat_bible.py`
- Vendor comparison: `modules/vendor_analysis/comparator.py`
- Recipe models: `modules/recipes/recipe.py`
- Menu models: `modules/menu/menu_item.py`
- Web app: `app.py`
- Config: `.env`

### Important Numbers
- Catering margin target: 45%
- Restaurant margin target: 4%
- Shamrock discount average: 29.5%
- Monthly savings potential: $4,333
- Annual savings potential: $52,000

---

## Version History

**Current Version**: 1.0.0-beta
**Last Updated**: November 19, 2025
**Maintained By**: Sean (Restaurant Owner)
**AI Documentation**: Claude (Anthropic)

---

## Contact & Support

For questions about:
- **Business Logic**: Contact Sean
- **Technical Issues**: Review this documentation
- **New Features**: Create detailed requirements
- **Bug Reports**: Include steps to reproduce

---

*This documentation is a living document. Update it as the system evolves.*
print(f"Items compared: {results['items_compared']}")
print(f"Monthly savings: ${results['recommendations']['estimated_monthly_savings']}")
```

### Optimizing Menu Pricing

```python
from modules.core.lariat_bible import lariat_bible

# Get pricing optimization suggestions
optimizations = lariat_bible.optimize_menu_pricing()

for item in optimizations[:5]:  # Top 5
    print(f"{item['item']}: ${item['current_price']} → ${item['suggested_price']}")
    print(f"  Current margin: {item['current_margin']:.1%}")
    print(f"  Target margin: {item['target_margin']:.1%}")
```

### Generating Reports

```python
from modules.core.lariat_bible import lariat_bible

# Executive summary
summary = lariat_bible.generate_executive_summary()
print(summary)

# Vendor comparison report
from modules.vendor_analysis import VendorComparator
comparator = VendorComparator()
report = comparator.generate_report('reports/vendor_report.txt')

# Export all data
exports = lariat_bible.export_all_data('data/exports')
print(f"Exported files: {exports}")
```

---

## Important Business Context

### The Vendor Savings Discovery

Sean discovered that **Shamrock Foods offers ~29.5% better pricing** than SYSCO on many items. This is a HUGE finding ($52,000 annual savings potential).

**Critical considerations:**
1. Not all products are available from both vendors
2. Product specifications must match exactly (e.g., pepper grind size)
3. Delivery minimums and frequencies differ
4. Quality may vary between vendors for some items
5. Existing vendor relationships and payment terms matter

### The Catering Focus

Catering is the profit driver (45% margin vs 4% restaurant margin):
- Monthly catering revenue: $28,000
- Monthly restaurant revenue: $20,000
- **Strategy**: Focus on growing catering, maintain restaurant as marketing

### Equipment Tracking Matters

The restaurant has significant equipment investments. Proper maintenance:
- Prevents costly emergency repairs
- Extends equipment lifespan
- Maintains food safety compliance
- Reduces downtime

---

## Known Issues & Future Work

### Current Limitations

1. **Invoice OCR** - Planned but not fully implemented
   - Manual data entry currently required
   - Need to handle various invoice formats

2. **Database** - Using SQLite for development
   - Plan migration to PostgreSQL for production
   - Need proper migrations (Alembic configured)

3. **Authentication** - Basic setup only
   - No multi-user support yet
   - No role-based access control

4. **Mobile Interface** - Not implemented
   - Current focus is web interface
   - Need responsive design for kitchen staff

5. **Inventory Tracking** - Partially implemented
   - No real-time stock updates
   - No integration with POS system

### Planned Features

**Phase 1** (Current):
- ✅ Project structure
- ⏳ Vendor analysis core features
- ⏳ Recipe database

**Phase 2**:
- Invoice OCR pipeline
- Automated price tracking
- Email parsing for vendor invoices

**Phase 3**:
- Inventory tracking system
- Automated reorder points
- Integration with existing POS

**Phase 4**:
- Mobile-responsive dashboard
- Real-time reporting
- Staff training modules

---

## Security & Data Privacy

### Sensitive Data

**Never commit:**
- Actual invoice files (contain pricing, terms)
- `.env` file (contains secrets)
- Database files (contain business data)
- Export files with real business data

**Gitignored paths:**
- `data/invoices/*.jpg`, `*.png`, `*.pdf`
- `reports/*.xlsx`, `*.csv`, `*.pdf`
- `*.db`, `*.sqlite`, `*.sqlite3`
- `.env`, `.env.local`

### API Keys & Credentials

If vendor APIs are added:
- Store API keys in `.env`
- Never hardcode credentials
- Use environment variables
- Rotate keys regularly

---

## AI Assistant Guidelines

### When Working on This Codebase

1. **Understand the Business Context**
   - This is a real restaurant with real financial impact
   - Pricing accuracy matters ($52K in savings is significant)
   - Sean relies on this data for business decisions

2. **Be Careful with Calculations**
   - Margin calculations affect menu pricing
   - Vendor comparisons must be accurate
   - Test calculations with known examples

3. **Maintain Code Quality**
   - Run `black` and `flake8` before committing
   - Write docstrings for new functions
   - Add tests for new features
   - Update this CLAUDE.md when architecture changes

4. **Ask for Clarification**
   - Product matching rules (grind, quality, size)
   - Business logic (Why 45% vs 4% margin?)
   - Data sources (Where does this number come from?)

5. **Preserve Existing Patterns**
   - Follow established naming conventions
   - Use existing classes (extend, don't replace)
   - Maintain module separation
   - Keep the LariatBible class as integration point

6. **Document Decisions**
   - Add comments for complex business logic
   - Update docs when changing behavior
   - Note assumptions in code
   - Track TODOs with issue tracking

### Common Pitfalls to Avoid

❌ **Don't:**
- Compare products with different specifications
- Hardcode business metrics (use config)
- Skip input validation (garbage in = garbage out)
- Ignore unit conversions (pounds vs cases)
- Break existing APIs without migration path

✅ **Do:**
- Validate vendor names before comparison
- Check product matches are exact
- Handle edge cases (zero prices, missing data)
- Provide clear error messages
- Test with realistic data

---

## Quick Reference

### Import Paths
```python
# Main integration
from modules.core.lariat_bible import lariat_bible

# Vendor analysis
from modules.vendor_analysis import VendorComparator

# Recipes
from modules.recipes.recipe import Recipe, Ingredient, RecipeIngredient

# Menu items
from modules.menu.menu_item import MenuItem

# Order guides
from modules.order_guides.order_guide_manager import OrderGuideManager

# Equipment
from modules.equipment.equipment_manager import EquipmentManager
```

### Configuration Files
- `.env` - Environment variables
- `requirements.txt` - Python dependencies
- `.gitignore` - Files to exclude from git

### Data Directories
- `data/invoices/` - Vendor invoices
- `data/exports/` - Generated exports
- `reports/` - Business reports
- `logs/` - Application logs
- `backups/` - Database backups

### Useful Commands
```bash
# Run app
python app.py

# Setup project
python setup.py

# Format code
black .

# Lint code
flake8 .

# Run tests
pytest

# Install dependencies
pip install -r requirements.txt
```

---

## Getting Help

### Documentation
- **README.md** - Project overview and quick start
- **PRODUCT_MATCHING_VERIFICATION.md** - Vendor comparison rules
- **GITHUB_SETUP.md** - Git workflow
- **This file (CLAUDE.md)** - Comprehensive AI assistant guide

### Contact
- **Owner**: Sean
- **Restaurant**: The Lariat, Fort Collins, CO

### When Something Breaks
1. Check `.env` configuration
2. Verify virtual environment is activated
3. Ensure dependencies are installed
4. Check logs in `logs/` directory
5. Review recent git commits

---

## Changelog

### 2025-11-18
- Initial CLAUDE.md creation
- Documented current codebase structure (~2,422 lines)
- Established conventions and guidelines
- Added comprehensive examples and workflows

---

**Remember**: This system helps a real business make real decisions. Accuracy, clarity, and reliability are paramount. When in doubt, ask questions and verify assumptions.

Happy coding! 🤠
