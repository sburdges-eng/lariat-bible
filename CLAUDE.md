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
