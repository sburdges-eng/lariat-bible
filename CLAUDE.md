# CLAUDE.md - AI Assistant Guide for The Lariat Bible

## Project Overview

**The Lariat Bible** is a comprehensive restaurant management system for The Lariat restaurant in Fort Collins, Colorado. This system serves as the single source of truth for vendor pricing, inventory management, recipe costing, catering operations, equipment maintenance, and business analytics.

### Key Business Metrics
- **Monthly Catering Revenue**: $28,000 (Target Margin: 45%)
- **Monthly Restaurant Revenue**: $20,000 (Target Margin: 4%)
- **Potential Annual Savings** (Shamrock vs SYSCO): $52,000 (29.5% price difference)

### Primary Business Goals
1. Optimize vendor selection to minimize food costs
2. Maintain accurate recipe costing and menu pricing
3. Track equipment maintenance and prevent downtime
4. Streamline catering operations and improve margins
5. Provide data-driven business intelligence

---

## Repository Structure

```
lariat-bible/
├── app.py                          # Main Flask application entry point
├── setup.py                        # Project initialization script
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules (includes .env, *.db, invoices)
│
├── modules/                        # Business logic modules
│   ├── core/
│   │   └── lariat_bible.py        # Main integration class (LariatBible)
│   ├── vendor_analysis/
│   │   ├── __init__.py
│   │   ├── comparator.py          # VendorComparator class
│   │   ├── accurate_matcher.py    # Product matching logic
│   │   └── corrected_comparison.py
│   ├── recipes/
│   │   └── recipe.py              # Recipe, Ingredient, RecipeIngredient dataclasses
│   ├── menu/
│   │   ├── __init__.py
│   │   └── menu_item.py           # MenuItem dataclass
│   ├── order_guides/
│   │   └── order_guide_manager.py # Order guide comparison
│   ├── equipment/
│   │   └── equipment_manager.py   # Equipment tracking
│   └── email_parser/
│       └── email_parser.py        # Email/invoice parsing
│
├── data/                           # Data storage (gitignored)
│   ├── invoices/                  # Invoice images (JPG, PNG, PDF)
│   └── exports/                   # Generated reports
│
└── Documentation/
    ├── README.md                   # User-facing project overview
    ├── PRODUCT_MATCHING_VERIFICATION.md  # Critical product matching guidelines
    ├── GITHUB_SETUP.md
    └── GITHUB_QUICK_SETUP.md
```

---

## Technology Stack

### Core Framework
- **Python 3.8+**: Primary language
- **Flask 3.0.0**: Web framework
- **SQLAlchemy 2.0**: Database ORM
- **Flask-Login**: Authentication

### Data Processing
- **pandas 2.1.4**: Data analysis and manipulation
- **numpy 1.26.2**: Numerical operations
- **openpyxl 3.1.2**: Excel file handling

### OCR & Document Processing
- **pytesseract 0.3.10**: OCR for invoice processing
- **Pillow 10.1.0**: Image manipulation
- **opencv-python 4.8.1**: Advanced image processing
- **PyPDF2 3.0.1**: PDF processing

### Development Tools
- **pytest 7.4.3**: Testing framework
- **black 23.12.0**: Code formatting (enforced)
- **flake8 6.1.0**: Linting
- **pre-commit 3.5.0**: Git hooks

### Security
- **python-jose**: JWT handling
- **passlib**: Password hashing
- **bcrypt**: Encryption

---

## Core Data Models

### 1. Ingredient (`modules/recipes/recipe.py:12-68`)

```python
@dataclass
class Ingredient:
    ingredient_id: str
    name: str
    category: str  # Protein, Produce, Dairy, Dry Goods
    unit_of_measure: str  # lb, oz, each, bunch
    case_size: str  # "6/10#", "25 lb bag"

    # Critical: Dual vendor pricing
    sysco_item_code: Optional[str]
    sysco_price: Optional[float]
    sysco_unit_price: Optional[float]

    shamrock_item_code: Optional[str]
    shamrock_price: Optional[float]
    shamrock_unit_price: Optional[float]

    # Auto-calculated based on pricing
    preferred_vendor: Optional[str]
    price_difference: Optional[float]
```

**Key Method**: `calculate_best_price()` - Determines optimal vendor based on unit pricing

### 2. Recipe (`modules/recipes/recipe.py:94-201`)

```python
@dataclass
class Recipe:
    recipe_id: str
    name: str
    category: str
    yield_amount: float
    yield_unit: str
    ingredients: List[RecipeIngredient]

    @property
    def total_cost(self) -> float

    @property
    def cost_per_portion(self) -> float

    def analyze_vendor_impact(self) -> Dict
```

**Critical Properties**:
- `total_cost`: Sum of all ingredient costs using preferred vendors
- `cost_per_portion`: Total cost / yield_amount
- `analyze_vendor_impact()`: Compares SYSCO-only vs Shamrock-only vs optimized mix

### 3. MenuItem (`modules/menu/menu_item.py:11-142`)

```python
@dataclass
class MenuItem:
    item_id: str
    name: str
    category: str
    menu_price: float  # Customer-facing price
    food_cost: float   # Actual cost to make
    target_margin: float  # 0.45 for catering, 0.04 for restaurant
    recipe_id: Optional[str]

    @property
    def margin(self) -> float  # (menu_price - food_cost) / menu_price

    @property
    def suggested_price(self) -> float  # food_cost / (1 - target_margin)
```

### 4. VendorComparator (`modules/vendor_analysis/comparator.py:11-192`)

Main class for vendor analysis:
- `compare_vendors(vendor1, vendor2)`: Calculate monthly savings
- `analyze_category(category, items)`: Category-level analysis
- `identify_top_savings(products, top_n)`: Find highest-value opportunities
- `calculate_margin_impact(monthly_savings)`: Impact on profit margins
- `generate_report(output_path)`: Executive summary

### 5. LariatBible (`modules/core/lariat_bible.py:20-360`)

**Main integration class** - coordinates all modules:
- Manages collections of ingredients, recipes, menu_items
- Orchestrates vendor comparisons
- Generates executive summaries
- Exports data for analysis

---

## Development Workflows

### Starting Development

1. **Initial Setup**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python setup.py  # Creates .env, directories, initializes DB
   ```

2. **Configuration** (`.env` file):
   ```env
   DATABASE_URL=sqlite:///lariat.db
   SECRET_KEY=<generate-secure-key>
   RESTAURANT_NAME=The Lariat
   DEFAULT_CATERING_MARGIN=0.45
   DEFAULT_RESTAURANT_MARGIN=0.04
   PRIMARY_VENDOR=Shamrock Foods
   COMPARISON_VENDOR=SYSCO
   FLASK_DEBUG=True
   ```

3. **Running the Application**:
   ```bash
   python app.py  # Starts Flask on http://127.0.0.1:5000
   ```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=modules --cov-report=html

# Run specific test file
pytest tests/test_vendor_analysis.py
```

### Code Quality

```bash
# Format code (required before commits)
black .

# Check linting
flake8 modules/ app.py setup.py

# Run pre-commit hooks
pre-commit run --all-files
```

---

## Key Conventions & Patterns

### 1. Dataclasses for Models
- **Use `@dataclass`** for all data models (Ingredient, Recipe, MenuItem, Equipment)
- Provides automatic `__init__`, `__repr__`, `__eq__`
- Use `@property` for calculated fields (margin, total_cost, etc.)
- Implement `__post_init__` for initialization logic

### 2. Vendor Pricing Pattern
**CRITICAL**: Always maintain dual vendor pricing for comparison

```python
# Always store both vendors
sysco_price: Optional[float]
shamrock_price: Optional[float]

# Calculate preferred vendor dynamically
def calculate_best_price(self):
    if self.sysco_unit_price < self.shamrock_unit_price:
        self.preferred_vendor = "SYSCO"
    else:
        self.preferred_vendor = "Shamrock Foods"
```

### 3. Product Matching Rules

**⚠️ CRITICAL: See `PREVENTING_PRODUCT_MATCH_ERRORS.md` for comprehensive safeguard system**

**Also see**: `PRODUCT_MATCHING_VERIFICATION.md` for verification checklist

Product matching errors can invalidate entire savings calculations. The system uses multiple layers of defense:

**Enforced Rules**:
- **NEVER match different product specifications**
  - ❌ "Black Pepper Fine" ≠ "Black Pepper Coarse" (different culinary uses)
  - ❌ "Garlic Powder" ≠ "Garlic Granulated" (different textures)
- Match by BOTH product code AND description
- Verify grind size, pack size, and quality specifications
- Document any assumptions in `notes` field

**Implementation** (`accurate_matcher.py:10-30`):
```python
@dataclass
class ProductMatch:
    product_name: str
    specification: str  # REQUIRED: Fine, Coarse, Cracked, etc.

    sysco_code: str
    sysco_description: str  # Full description for validation

    shamrock_code: str
    shamrock_description: str  # Full description for validation

    notes: str  # Document WHY this is a match
```

**Validation Layers**:
1. ✅ Data structure enforcement (specification required)
2. ✅ Separate ProductMatch per specification
3. ❌ Automated validation (to implement - see PREVENTING_PRODUCT_MATCH_ERRORS.md)
4. ❌ Human verification workflow (to implement)
5. ❌ Unit tests for matching (to implement)

### 4. Margin Calculations

```python
# Margin formula (NOT markup!)
margin = (selling_price - cost) / selling_price

# Suggested price from target margin
suggested_price = cost / (1 - target_margin)

# Example: $10 cost, 45% target margin
# suggested_price = $10 / (1 - 0.45) = $18.18
```

### 5. Database Pattern (Future)
- SQLAlchemy models will mirror dataclasses
- Use Alembic for migrations
- Keep data validation in dataclasses, persistence in SQLAlchemy

### 6. Error Handling
```python
# Return dicts with error keys for business logic
if ingredient_id not in self.ingredients:
    return {'error': f'Ingredient {ingredient_id} not found'}

# Raise exceptions for critical failures
if not vendor_price_available:
    raise ValueError("Cannot calculate cost without vendor pricing")
```

### 7. File Naming & Module Organization
- Use lowercase with underscores: `vendor_analysis.py`, `menu_item.py`
- Group related functionality in modules
- Each module has `__init__.py` exporting public API
- Main integration happens in `core/lariat_bible.py`

---

## API Endpoints (Flask App)

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | System status, module availability, key metrics |
| `/api/health` | GET | Health check endpoint |
| `/api/modules` | GET | List all modules and their status |
| `/api/vendor-comparison` | GET | Get current vendor comparison data |

### Example Response Format

```json
{
  "message": "Welcome to The Lariat Bible",
  "status": "operational",
  "modules": {
    "vendor_analysis": "ready",
    "inventory": "pending",
    "recipes": "pending"
  },
  "metrics": {
    "monthly_catering_revenue": 28000,
    "monthly_restaurant_revenue": 20000,
    "potential_annual_savings": 52000
  }
}
```

---

## Critical Business Logic

### Vendor Savings Calculation

Based on discovered 29.5% average savings with Shamrock Foods:

```python
monthly_food_cost = 8000  # Estimated
monthly_savings = monthly_food_cost * 0.295  # $2,360
annual_savings = monthly_savings * 12  # $28,320
```

**Breakdown by Impact**:
- 60% of savings apply to catering operations
- 40% of savings apply to restaurant operations

### Catering vs Restaurant Pricing

**Catering** (45% target margin):
- Higher margins due to delivery, setup, service
- Calculate: `price = food_cost / 0.55`
- Monthly revenue: $28,000

**Restaurant** (4% target margin):
- Slim margins, volume-based
- Calculate: `price = food_cost / 0.96`
- Monthly revenue: $20,000

---

## Common Tasks for AI Assistants

### Task 1: Add a New Ingredient with Vendor Pricing

```python
from modules.recipes.recipe import Ingredient
from modules.core.lariat_bible import lariat_bible

# Create ingredient with dual pricing
ingredient = Ingredient(
    ingredient_id="ING001",
    name="Black Pepper Fine Ground",
    category="Spices",
    unit_of_measure="lb",
    case_size="6/1lb",
    sysco_item_code="SYS12345",
    sysco_price=45.00,  # Case price
    sysco_unit_price=7.50,  # Per lb
    shamrock_item_code="SHA67890",
    shamrock_price=25.00,  # Case price
    shamrock_unit_price=4.17  # Per lb
)

# Add to system (auto-calculates preferred vendor)
result = lariat_bible.add_ingredient(ingredient)
print(result)  # "Added ingredient: Black Pepper Fine Ground - Preferred vendor: Shamrock Foods"
```

### Task 2: Create a Recipe with Cost Analysis

```python
from modules.recipes.recipe import Recipe, RecipeIngredient

# Assuming ingredients already exist in lariat_bible.ingredients
beef = lariat_bible.ingredients["ING_BEEF"]
onions = lariat_bible.ingredients["ING_ONIONS"]

recipe = Recipe(
    recipe_id="REC001",
    name="Classic Burger Patty",
    category="Entree",
    yield_amount=10,
    yield_unit="portions",
    portion_size="6 oz",
    ingredients=[
        RecipeIngredient(beef, quantity=4.0, unit="lb"),
        RecipeIngredient(onions, quantity=0.5, unit="lb", prep_instruction="diced")
    ]
)

result = lariat_bible.create_recipe_with_costing(recipe)
# Returns: total_cost, cost_per_portion, vendor_analysis, suggested_menu_price
```

### Task 3: Run Vendor Comparison Report

```python
from modules.vendor_analysis.comparator import VendorComparator

comparator = VendorComparator()

# Compare vendors
monthly_savings = comparator.compare_vendors('Shamrock Foods', 'SYSCO')
print(f"Monthly savings: ${monthly_savings:,.2f}")

# Calculate margin impact
impact = comparator.calculate_margin_impact(monthly_savings)
print(f"New catering margin: {impact['catering']['new_margin']:.1%}")

# Generate report
report = comparator.generate_report(output_path="reports/vendor_analysis.txt")
print(report)
```

### Task 4: Optimize Menu Pricing

```python
# Get all menu items needing price adjustment
optimizations = lariat_bible.optimize_menu_pricing()

for item in optimizations:
    print(f"{item['item']}: Current ${item['current_price']:.2f} → "
          f"Suggested ${item['suggested_price']:.2f} ({item['action']})")
```

### Task 5: Generate Executive Summary

```python
# Full system summary
summary = lariat_bible.generate_executive_summary()
print(summary)

# Export all data
exports = lariat_bible.export_all_data()
# Creates: menu_items_YYYYMMDD.json, recipes_YYYYMMDD.json,
#          vendor_comparison_YYYYMMDD.xlsx, executive_summary_YYYYMMDD.txt
```

---

## Data Storage & Privacy

### Sensitive Data (Gitignored)

The following are **excluded from version control**:

1. **Environment Variables** (`.env`)
   - Database credentials
   - Secret keys
   - API tokens

2. **Invoice Data** (`data/invoices/`)
   - Contains proprietary vendor pricing
   - May include business-sensitive information
   - Store locally only

3. **Generated Reports** (`reports/*.xlsx`, `reports/*.csv`)
   - Contains financial data
   - Can be regenerated from code

4. **Database Files** (`*.db`, `*.sqlite`)
   - Regenerated via migrations
   - Contains operational data

### Version Control Included

- All Python source code
- Documentation (`.md` files)
- Requirements and configuration templates
- Directory structure (`.gitkeep` files)
- Test suites

---

## Testing Guidelines

### Test Structure

```
tests/
├── test_vendor_analysis.py
├── test_recipes.py
├── test_menu_items.py
└── fixtures/
    ├── sample_ingredients.json
    └── sample_recipes.json
```

### Writing Tests

```python
import pytest
from modules.recipes.recipe import Ingredient

def test_ingredient_best_price_calculation():
    """Test that preferred vendor is correctly identified"""
    ingredient = Ingredient(
        ingredient_id="TEST001",
        name="Test Product",
        category="Test",
        unit_of_measure="lb",
        case_size="10 lb",
        sysco_unit_price=5.00,
        shamrock_unit_price=3.50
    )

    result = ingredient.calculate_best_price()

    assert ingredient.preferred_vendor == "Shamrock Foods"
    assert result['savings_per_unit'] == 1.50
    assert result['savings_percent'] > 0

def test_recipe_cost_calculation():
    """Test recipe total cost uses preferred vendors"""
    # Setup ingredients with different preferred vendors
    # Create recipe
    # Assert total_cost is minimized
    pass
```

### Running Specific Test Categories

```bash
# Vendor analysis tests only
pytest tests/test_vendor_analysis.py -v

# Tests marked as integration
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

---

## Troubleshooting Common Issues

### Issue: Import errors when running modules

**Cause**: Python path not set correctly

**Solution**:
```bash
# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/lariat-bible"

# Or run as module
python -m modules.vendor_analysis.comparator
```

### Issue: "InvoiceProcessor not found" error

**Cause**: `invoice_processor.py` referenced in `__init__.py` but not yet implemented

**Solution**: Comment out the import in `modules/vendor_analysis/__init__.py`:
```python
# from .invoice_processor import InvoiceProcessor
# __all__ = ['VendorComparator', 'InvoiceProcessor']
__all__ = ['VendorComparator']
```

### Issue: Database initialization fails

**Cause**: Database module not yet implemented

**Solution**: The `setup.py` gracefully handles this:
```python
try:
    from core.database import init_db
    init_db()
except ImportError:
    print("⚠️  Database module not yet implemented - skipping")
```

### Issue: Black formatting conflicts with flake8

**Solution**: Black takes precedence (configured in `pyproject.toml`):
```toml
[tool.black]
line-length = 100
target-version = ['py38']

[tool.flake8]
max-line-length = 100
extend-ignore = E203, W503  # Conflicts with Black
```

---

## Future Development Areas

Based on the README roadmap, the following are planned:

### Phase 1: Foundation (In Progress)
- [x] Project structure
- [ ] Database schema design (SQLAlchemy models)
- [ ] Core utilities (logging, error handling)

### Phase 2: Vendor Analysis (Partially Complete)
- [x] Vendor comparison engine
- [ ] OCR pipeline for invoices (pytesseract integration)
- [ ] Automated invoice parsing
- [ ] Email integration for automatic invoice ingestion

### Phase 3: Inventory & Recipes (Partially Complete)
- [x] Recipe data models
- [ ] Inventory tracking system
- [ ] Automated reordering triggers
- [ ] Integration with vendor order systems

### Phase 4: Web Interface (Basic Structure Exists)
- [x] Basic Flask API
- [ ] React/Vue frontend dashboard
- [ ] Real-time updates (WebSockets)
- [ ] Mobile-responsive design
- [ ] User authentication & roles

### Phase 5: Advanced Analytics
- [ ] Predictive inventory management
- [ ] Sales forecasting
- [ ] Labor cost optimization
- [ ] Supplier negotiation insights

---

## AI Assistant Best Practices

### When Adding Features

1. **Understand the business context** - This is a real restaurant with actual financial impact
2. **Maintain dual vendor tracking** - Critical for price comparison
3. **Follow margin calculation patterns** - margin ≠ markup
4. **Write tests for business logic** - Financial calculations must be accurate
5. **Document assumptions** - Especially in product matching
6. **Use type hints** - Enables better IDE support and catches errors early

### When Modifying Existing Code

1. **Preserve backward compatibility** - Data might exist in production
2. **Update related tests** - Don't break existing functionality
3. **Check cross-module impacts** - LariatBible integrates everything
4. **Maintain dataclass patterns** - Consistency across models
5. **Update this CLAUDE.md** - Keep documentation current

### When Debugging

1. **Check vendor pricing first** - Most issues stem from missing price data
2. **Verify product matching** - Mismatches cause incorrect savings calculations
3. **Validate margin calculations** - Use the formula: `(price - cost) / price`
4. **Inspect recipe ingredient links** - Broken links = wrong costs
5. **Review git history** - `git log --oneline -- <file>` shows changes

### Communication Style

- **Be precise with financial figures** - Restaurant owners need accuracy
- **Explain trade-offs** - "This saves $X but requires Y change"
- **Provide examples with real data** - Use actual vendor names (Shamrock, SYSCO)
- **Suggest business impact** - "This could improve catering margins by 2%"

---

## Quick Reference Commands

```bash
# Setup
python setup.py                    # Initialize project
source venv/bin/activate           # Activate environment

# Development
python app.py                      # Run Flask app
black .                            # Format code
flake8 .                          # Lint code
pytest                            # Run tests
pytest --cov                      # Test coverage

# Data Management
python -c "from modules.core.lariat_bible import lariat_bible; print(lariat_bible.generate_executive_summary())"

# Git
git add .
git commit -m "feat: description"  # Use conventional commits
git push origin main

# Dependencies
pip install -r requirements.txt    # Install
pip freeze > requirements.txt      # Update
```

---

## Additional Resources

- **README.md**: User-facing project overview and quick start
- **PREVENTING_PRODUCT_MATCH_ERRORS.md**: ⚠️ Comprehensive safeguard system for accurate product matching
- **PRODUCT_MATCHING_VERIFICATION.md**: Manual verification checklist for product matches
- **GITHUB_SETUP.md**: Repository configuration guide
- **requirements.txt**: Definitive list of dependencies

---

## Contact & Support

**Owner**: Sean (Restaurant Owner & Operator)
**Location**: The Lariat, Fort Collins, Colorado
**Purpose**: Data-driven restaurant operations management

---

**Last Updated**: 2025-11-19
**Version**: 1.1.0
**Maintained by**: AI Assistant (Claude)

**Changelog**:
- v1.1.0 (2025-11-19): Added comprehensive product matching error prevention system
- v1.0.0 (2025-11-19): Initial CLAUDE.md creation with full codebase documentation
