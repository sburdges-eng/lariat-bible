# The Lariat Bible - AI Assistant Guide

## Executive Summary

**The Lariat Bible** is a comprehensive restaurant management system for **The Lariat**, a restaurant in Fort Collins, Colorado that operates both dine-in and catering businesses. The system integrates vendor price comparison, inventory management, recipe costing, equipment tracking, and order optimization to improve profitability and operational efficiency.

**Key Business Metrics:**
- Monthly Catering Revenue: $28,000
- Monthly Restaurant Revenue: $20,000
- Identified Annual Savings Opportunity: $52,000 (Shamrock vs SYSCO pricing)

**Codebase Size:** ~2,650 lines of Python code across 11 modules

---

## Project Structure & Architecture

### Directory Organization
```
lariat-bible/
├── app.py                          # Flask web application entry point
├── setup.py                        # Installation and configuration setup
├── requirements.txt                # Python dependencies
├── modules/                        # Core business logic
│   ├── core/                       # Central integration module
│   │   └── lariat_bible.py        # Main coordinator class
│   ├── vendor_analysis/            # Vendor price comparison
│   │   ├── __init__.py
│   │   ├── comparator.py          # VendorComparator class
│   │   ├── accurate_matcher.py    # ProductMatch & AccurateVendorMatcher
│   │   └── corrected_comparison.py # CorrectedVendorComparison
│   ├── recipes/                    # Recipe management and costing
│   │   └── recipe.py              # Ingredient, RecipeIngredient, Recipe classes
│   ├── menu/                       # Menu item management
│   │   ├── __init__.py
│   │   └── menu_item.py           # MenuItem class
│   ├── equipment/                  # Equipment tracking and maintenance
│   │   └── equipment_manager.py   # Equipment, MaintenanceRecord, EquipmentManager
│   ├── order_guides/              # Vendor catalog management
│   │   └── order_guide_manager.py # OrderGuideManager class
│   └── email_parser/              # Order confirmation email processing
│       └── email_parser.py        # EmailOrderParser, PackSizeNormalizer
├── data/                          # Data storage
│   ├── corrected_spice_comparison.csv
│   └── matched_products_comparison.csv
├── README.md                       # Project overview
├── GITHUB_SETUP.md                # GitHub configuration instructions
├── GITHUB_QUICK_SETUP.md          # Abbreviated setup guide
└── PRODUCT_MATCHING_VERIFICATION.md # Product matching checklist
```

---

## Core Modules & Their Responsibilities

### 1. **Vendor Analysis Module** (`modules/vendor_analysis/`)
**Purpose:** Compare prices between food vendors (SYSCO vs Shamrock Foods) and identify cost-saving opportunities.

**Key Classes:**

#### `VendorComparator` (comparator.py)
- Analyzes pricing differences between vendors
- Methods:
  - `compare_vendors(vendor1, vendor2)` - Returns monthly savings amount
  - `analyze_category(category, items)` - Category-level price analysis
  - `identify_top_savings(products, top_n)` - Top N savings opportunities
  - `generate_report(output_path)` - Creates formatted vendor analysis report
  - `calculate_margin_impact(monthly_savings)` - Shows how savings affect profit margins

**Key Finding:** Shamrock Foods offers ~29.5% better pricing than SYSCO on average, translating to $4,333/month savings potential.

#### `AccurateVendorMatcher` (accurate_matcher.py)
- Ensures accurate product matching between vendors
- Handles product specifications (e.g., "Black Pepper Fine" ≠ "Black Pepper Coarse")
- Parses pack sizes and calculates per-pound costs
- Critical for preventing incorrect product comparisons

#### `CorrectedVendorComparison` (corrected_comparison.py)
- Properly interprets vendor pack size formats:
  - Shamrock: `1/6/LB` = 1 container of 6 lbs
  - SYSCO: `3/6LB` = 3 containers of 6 lbs each (18 lbs total)
- Methods:
  - `interpret_pack_size(pack_str)` - Parses and standardizes pack sizes
  - Handles cans (#10, #5, etc.), pounds, gallons, and case quantities

### 2. **Recipes Module** (`modules/recipes/`)
**Purpose:** Manage standardized recipes with automatic cost calculation and vendor impact analysis.

**Key Classes:**

#### `Ingredient` (dataclass)
- Represents individual ingredients with vendor pricing
- Attributes: `ingredient_id`, `name`, `category`, `unit_of_measure`, `case_size`
- Vendor info: `sysco_price`, `sysco_unit_price`, `shamrock_price`, `shamrock_unit_price`
- Methods:
  - `calculate_best_price()` - Determines preferred vendor based on price

#### `RecipeIngredient` (dataclass)
- Links ingredient to recipe with quantity
- Methods:
  - `cost` property - Calculates cost using preferred vendor pricing

#### `Recipe` (dataclass)
- Complete recipe with ingredients and instructions
- Attributes: `recipe_id`, `name`, `category`, `yield_amount`, `portion_size`
- Ingredients list with prep instructions and cooking instructions
- Methods:
  - `total_cost` property - Sums all ingredient costs
  - `cost_per_portion` property - Divides total cost by yield
  - `get_shopping_list(multiplier)` - Generates shopping list with vendor recommendations
  - `analyze_vendor_impact()` - Shows cost differences using different vendors

### 3. **Menu Module** (`modules/menu/`)
**Purpose:** Manage menu items with pricing, recipe links, and margin analysis.

**Key Classes:**

#### `MenuItem` (dataclass)
- Represents individual menu items
- Attributes: `item_id`, `name`, `category`, `menu_price`, `food_cost`, `target_margin`
- Availability info: `seasonal`, `days_available`, `meal_periods`
- Dietary info: `dietary_flags`, `allergens`
- Sales metrics: `popularity_score`, `monthly_sales`
- Methods:
  - `margin` property - Calculates actual profit margin
  - `suggested_price` property - Calculates price to achieve target margin
  - `update_food_cost(new_cost)` - Updates cost and provides pricing analysis
  - `to_dict()` and `from_dict()` - Serialization for storage/API

### 4. **Equipment Module** (`modules/equipment/`)
**Purpose:** Track kitchen equipment, maintenance schedules, and service history for preventive maintenance and depreciation tracking.

**Key Classes & Enums:**

#### `EquipmentStatus` (enum)
- `OPERATIONAL`, `NEEDS_MAINTENANCE`, `UNDER_REPAIR`, `OUT_OF_SERVICE`, `RETIRED`

#### `MaintenanceType` (enum)
- `DAILY_CLEANING`, `WEEKLY_CLEANING`, `MONTHLY_INSPECTION`, `QUARTERLY_SERVICE`, `ANNUAL_SERVICE`, `REPAIR`, `EMERGENCY`

#### `Equipment` (dataclass)
- Core equipment tracking
- Attributes: `equipment_id`, `name`, `category`, `brand`, `model`, `serial_number`
- Purchase info: `purchase_date`, `purchase_price`, `warranty_end_date`
- Maintenance: `daily_tasks`, `weekly_tasks`, `monthly_tasks`, etc.
- Methods:
  - `age_years` property - Equipment age calculation
  - `warranty_status` property - Warranty expiration tracking
  - `depreciated_value` property - 7-year straight-line depreciation
  - `is_maintenance_due()` - Checks if maintenance is overdue

#### `MaintenanceRecord` (dataclass)
- Records completed maintenance activities
- Tracks: `tasks_completed`, `issues_found`, `parts_replaced`
- Costs: `labor_hours`, `labor_cost`, `parts_cost`

#### `EquipmentManager`
- Manages all equipment and maintenance scheduling
- Methods:
  - `add_equipment(equipment)` - Adds equipment to inventory
  - `get_maintenance_schedule(days_ahead)` - Returns upcoming maintenance
  - `record_maintenance(record)` - Records completed maintenance
  - `get_maintenance_costs(start_date, end_date)` - Calculates maintenance expenses
  - `get_equipment_summary()` - Total value, depreciation, status breakdown

### 5. **Order Guides Module** (`modules/order_guides/`)
**Purpose:** Manage vendor catalogs and perform detailed price comparisons.

**Key Classes:**

#### `OrderGuideManager`
- Manages SYSCO and Shamrock order catalogs
- Methods:
  - `load_sysco_guide(data)` - Loads SYSCO catalog data
  - `load_shamrock_guide(data)` - Loads Shamrock catalog data
  - `find_matching_products(threshold)` - Finds products in both catalogs using fuzzy matching
  - `compare_prices(matched_products)` - Returns DataFrame with price comparisons
  - `get_category_analysis()` - Analyzes pricing by product category
  - `generate_purchase_recommendation(weekly_usage)` - Suggests optimal purchasing strategy
  - `export_comparison(filepath)` - Exports to Excel with multiple sheets

**Data Format:** Each item requires:
```python
{
    'item_code': 'CODE123',
    'description': 'PRODUCT DESCRIPTION',
    'pack_size': '6/10#' or '25 LB',
    'case_price': 45.99,
    'unit_price': 4.599,
    'unit': 'LB',
    'category': 'MEAT'
}
```

### 6. **Email Parser Module** (`modules/email_parser/`)
**Purpose:** Automatically parse SYSCO and Shamrock order confirmation emails to extract pricing and update vendor comparison data.

**Key Classes:**

#### `PackSizeNormalizer`
- Interprets diverse pack size formats from vendor emails
- Handles: pounds, gallons, cans (#10, #5, #2.5, etc.), cases
- Methods:
  - `parse_pack_size(pack_str)` - Parses pack format and returns component details
  - `normalize_to_price_per_pound(pack_str, case_price)` - Converts any format to price/lb

#### `OrderItem` (dataclass)
- Represents a single line item from order confirmation
- Properties:
  - `normalized_unit_price` - Standardized price per unit

#### `EmailOrderParser`
- Connects to email server and extracts order confirmations
- Methods:
  - `connect()` - Establishes IMAP connection
  - `parse_sysco_email(email_body)` - Extracts SYSCO order items
  - `parse_shamrock_email(email_body)` - Extracts Shamrock order items
  - `fetch_recent_orders(days_back)` - Fetches and parses recent emails, returns DataFrame
  - `compare_vendor_prices(df)` - Compares prices for matching items

### 7. **Core Integration Module** (`modules/core/`)
**Purpose:** Central coordinator that orchestrates all other modules for comprehensive restaurant management.

**Key Class:**

#### `LariatBible`
- Master integration class combining all functionality
- Attributes:
  - `menu_items`, `recipes`, `ingredients` - Data storage
  - `monthly_catering_revenue`, `monthly_restaurant_revenue` - Financial metrics
  - `target_catering_margin` (45%), `target_restaurant_margin` (4%)
  - Manager instances: `order_guide_manager`, `equipment_manager`, `vendor_comparator`

- **Ingredient Management Methods:**
  - `add_ingredient(ingredient)` - Adds ingredient with vendor pricing
  - `update_ingredient_pricing(ingredient_id, vendor, new_price)` - Updates pricing from specific vendor

- **Recipe Management Methods:**
  - `create_recipe_with_costing(recipe)` - Creates recipe and calculates total/per-portion costs
  - `link_recipe_to_menu(recipe_id, menu_item_id)` - Links recipe to menu item with cost update

- **Vendor Comparison Methods:**
  - `import_order_guides(sysco_file, shamrock_file)` - Loads vendor catalogs
  - `run_comprehensive_comparison()` - Full vendor analysis with recommendations

- **Menu Optimization Methods:**
  - `optimize_menu_pricing()` - Identifies menu items needing price adjustments

- **Reporting Methods:**
  - `generate_executive_summary()` - Creates comprehensive summary report
  - `export_all_data(export_dir)` - Exports all data to JSON/Excel files

---

## Key Technologies & Frameworks

### Web & API
- **Flask 3.0.0** - Web framework for REST API
- **Flask-CORS 4.0.0** - Cross-origin resource sharing
- **Flask-SQLAlchemy 3.1.1** - ORM integration
- **Flask-Login 0.6.3** - User authentication

### Database & ORM
- **SQLAlchemy 2.0.23** - Object-relational mapper
- **Alembic 1.13.0** - Database migration management
- Configured for **SQLite** by default (can be changed in .env)

### Data Processing & Analysis
- **Pandas 2.1.4** - DataFrames for price comparison, analytics
- **NumPy 1.26.2** - Numerical computations
- **OpenPyXL 3.1.2** - Excel file handling

### OCR & Image Processing
- **Pytesseract 0.3.10** - OCR for invoice processing
- **Pillow 10.1.0** - Image manipulation
- **OpenCV 4.8.1.78** - Computer vision (invoice analysis)

### Email & Communications
- **imaplib** (built-in) - Email retrieval via IMAP
- **smtplib** (built-in) - Potential email sending

### Data Validation & Serialization
- **Pydantic 2.5.2** - Data validation using type hints
- **Marshmallow 3.20.1** - Object serialization/deserialization

### Testing
- **Pytest 7.4.3** - Test framework
- **Pytest-Cov 4.1.0** - Coverage reporting
- **Pytest-Flask 1.3.0** - Flask testing utilities

### Development & Code Quality
- **Black 23.12.0** - Code formatting
- **Flake8 6.1.0** - Linting
- **Pre-commit 3.5.0** - Git hooks for code quality

### Utilities
- **Python-Dotenv 1.0.0** - Environment variable management
- **Click 8.1.7** - CLI interface creation
- **Schedule 1.2.0** - Task scheduling (for maintenance reminders)
- **Python-Crontab 3.0.0** - Cron job management
- **Python-JOSE 3.3.0** - JWT token handling
- **Passlib 1.7.4** - Password hashing
- **BCrypt 4.1.2** - Secure password hashing
- **Requests 2.31.0** - HTTP client
- **HTTPX 0.25.2** - Async HTTP client
- **Rich 13.7.0** - Terminal formatting
- **Tabulate 0.9.0** - ASCII tables

---

## Configuration & Environment

### Setup Process
1. **run setup.py** to initialize:
   - Creates `.env` file with default configuration
   - Creates necessary directories (data/invoices, logs, reports, backups, etc.)
   - Initializes database (when database module is implemented)

### Environment Variables (.env)
```
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

# OCR Settings
TESSERACT_PATH=/usr/bin/tesseract

# Web Interface
FLASK_ENV=development
FLASK_DEBUG=True
HOST=127.0.0.1
PORT=5000
```

### Key Configuration Files
- **.env** - Runtime configuration (DO NOT commit)
- **.gitignore** - Excludes sensitive data (invoices, reports, .env files)
- **requirements.txt** - Python dependencies with pinned versions

---

## Entry Points & Main Workflows

### 1. **Web Application (app.py)**
Flask application serving JSON API endpoints:

**Endpoints:**
- `GET /` - Main dashboard with module status and business metrics
- `GET /api/health` - Health check endpoint
- `GET /api/vendor-comparison` - Vendor comparison data and margin impact
- `GET /api/modules` - List all modules and their status

**Startup:**
```bash
python app.py
# Server runs on http://127.0.0.1:5000 (configurable via .env)
```

### 2. **System Initialization**
```bash
python setup.py
```
Creates directories, .env file, and initializes database.

### 3. **Core Integration Usage**
```python
from modules.core.lariat_bible import lariat_bible

# Import vendor catalogs
lariat_bible.import_order_guides()

# Run comprehensive comparison
results = lariat_bible.run_comprehensive_comparison()

# Generate report
summary = lariat_bible.generate_executive_summary()

# Export data
exports = lariat_bible.export_all_data()
```

### 4. **Vendor Analysis Workflow**
```python
from modules.vendor_analysis import VendorComparator

comparator = VendorComparator()
savings = comparator.compare_vendors('Shamrock Foods', 'SYSCO')
report = comparator.generate_report()
margin_impact = comparator.calculate_margin_impact(savings)
```

### 5. **Recipe Management Workflow**
```python
from modules.recipes.recipe import Recipe, Ingredient, RecipeIngredient
from modules.core.lariat_bible import lariat_bible

# Create ingredient with vendor pricing
ingredient = Ingredient(
    ingredient_id='ing001',
    name='Black Pepper Fine',
    category='Spices',
    unit_of_measure='LB',
    case_size='6/1#'
)

# Create recipe with ingredients
recipe = Recipe(
    recipe_id='recipe001',
    name='Beef Rub',
    category='Sauce',
    yield_amount=10,
    yield_unit='oz',
    portion_size='1 oz',
    ingredients=[RecipeIngredient(ingredient, 0.5, 'LB')]
)

# Add to system
lariat_bible.add_ingredient(ingredient)
costing = lariat_bible.create_recipe_with_costing(recipe)
```

### 6. **Email Order Parsing Workflow**
```python
from modules.email_parser.email_parser import EmailOrderParser

parser = EmailOrderParser('your_email@gmail.com', 'your_password')
parser.connect()

# Fetch recent orders from both vendors
orders_df = parser.fetch_recent_orders(days_back=7)

# Compare prices
comparison = parser.compare_vendor_prices(orders_df)
```

---

## Data Flow & Integration Points

### Vendor Price Comparison Flow
```
Email (SYSCO/Shamrock) 
    ↓
EmailOrderParser (parse_sysco_email/parse_shamrock_email)
    ↓
PackSizeNormalizer (normalize_to_price_per_pound)
    ↓
OrderGuideManager (compare_prices)
    ↓
VendorComparator (analyze_category, identify_top_savings)
    ↓
LariatBible (run_comprehensive_comparison)
    ↓
Report/Export
```

### Recipe Costing Flow
```
Ingredient (with vendor pricing)
    ↓
RecipeIngredient (quantity × unit_price)
    ↓
Recipe (sum all ingredient costs)
    ↓
MenuItem (food_cost property)
    ↓
Margin Analysis (menu_price vs food_cost)
    ↓
Price Optimization Recommendation
```

---

## Testing & Quality Assurance

### Testing Framework
- **Pytest** configured for unit and integration tests
- Coverage reporting with pytest-cov
- Flask-specific testing with pytest-flask

### Code Quality Tools
- **Black** for consistent code formatting
- **Flake8** for style/error detection
- **Pre-commit** hooks to enforce standards before commits

### Note
Currently, no test files exist in the repository. Tests should be created for:
- Vendor comparison calculations
- Pack size parsing accuracy
- Recipe costing logic
- Email parser regex patterns
- Equipment maintenance scheduling

---

## Critical Data Points & Business Logic

### Vendor Pricing Standards
- **Shamrock Foods:** Primary vendor, ~29.5% better pricing on average
- **SYSCO:** Comparison vendor, premium pricing
- **Monthly Savings Potential:** $4,333 (~29.5% of food costs)
- **Annual Savings Potential:** $52,000

### Profit Margin Targets
- **Catering Operations:** 45% target margin
- **Restaurant Operations:** 4% target margin (lower due to labor costs)

### Key Pack Size Interpretations
- Shamrock format: `1/6/LB` = 1 container × 6 pounds
- SYSCO format: `3/6LB` = 3 containers × 6 pounds each (18 total)
- Always verify grind/specification matches when comparing products

### Equipment Depreciation
- Standard useful life: 7 years
- Depreciation method: Straight-line
- Example: $10,000 equipment depreciates $1,428.57/year

---

## Known Implementation Status

### Completed & Ready
- ✅ Vendor comparison logic with accurate pack size handling
- ✅ Email parser for SYSCO/Shamrock order confirmations
- ✅ Recipe and ingredient costing system
- ✅ Menu item pricing and margin analysis
- ✅ Equipment tracking with maintenance scheduling
- ✅ Order guide management and category analysis
- ✅ Core integration module (LariatBible) coordinator

### In Development / Planned
- ⏳ Database schema and SQLAlchemy models
- ⏳ User authentication and permissions system
- ⏳ Web interface frontend (currently API only)
- ⏳ Invoice OCR processing (Tesseract configured, not implemented)
- ⏳ Automated inventory tracking
- ⏳ Real-time alerts for savings opportunities
- ⏳ Comprehensive test suite

---

## Quick Reference: Common Operations

### Compare Vendor Prices
```python
from modules.vendor_analysis import VendorComparator
c = VendorComparator()
savings = c.compare_vendors('Shamrock Foods', 'SYSCO')  # Returns $4,333
```

### Calculate Recipe Cost
```python
from modules.core.lariat_bible import lariat_bible
costing = lariat_bible.create_recipe_with_costing(recipe_object)
print(f"Cost per portion: ${costing['cost_per_portion']:.2f}")
```

### Export Price Comparison
```python
from modules.order_guides import OrderGuideManager
mgr = OrderGuideManager()
mgr.load_sysco_guide(sysco_data)
mgr.load_shamrock_guide(shamrock_data)
mgr.export_comparison('output.xlsx')
```

### Get Equipment Maintenance Schedule
```python
from modules.equipment import EquipmentManager
mgr = EquipmentManager()
schedule = mgr.get_maintenance_schedule(days_ahead=30)
```

---

## File Size & Code Metrics

- **Total Python Code:** ~2,650 lines
- **Main Application:** 130 lines (app.py)
- **Setup Script:** 103 lines (setup.py)
- **Largest Modules:**
  - lariat_bible.py: 360 lines
  - equipment_manager.py: 300 lines
  - email_parser.py: 328 lines
  - comparator.py: 192 lines

---

## Security & Best Practices

### Sensitive Data Handling
- `.env` file contains secrets (DO NOT commit)
- Invoice images excluded from version control
- Generated reports excluded (may contain business data)
- Database files (.db, .sqlite) excluded
- Configuration recommends using HTTPS in production

### Authentication
- Flask-Login configured for user sessions
- Passlib + BCrypt for password hashing
- Python-JOSE for JWT tokens
- Secret key must be changed from default

### Code Quality
- Pre-commit hooks for code standards
- Type hints used throughout (dataclasses, Pydantic)
- Docstrings in major functions
- Configuration management via environment variables

---

## Git Repository Information

- **Current Branch:** claude/claude-md-* (development branch)
- **Access Level:** Private repository (business-sensitive data)
- **Key Commits:**
  - Initial commit: Lariat Bible complete system
  - Creates baseline structure with all modules

---

## For AI Assistants: Working with This Codebase

### When helping users:
1. **Vendor Comparisons:** Always verify product specification matching (different grinds = different products)
2. **Pack Size Parsing:** Use `CorrectedVendorComparison.interpret_pack_size()` for accurate conversions
3. **Pricing:** Remember 29.5% is the average; verify specific products for accuracy
4. **Margins:** Catering = 45%, Restaurant = 4% (significant difference in pricing strategy)
5. **Email Parsing:** Current implementation uses regex; fuzzy matching would improve accuracy

### Common Tasks:
- **Add new vendor:** Update `VendorComparator.vendors` dict and create `load_[vendor]_guide()` method
- **Add product category:** Update `OrderGuideManager` comparison logic
- **Add equipment:** Create `Equipment` instance and add via `EquipmentManager.add_equipment()`
- **Create recipe:** Build `Recipe` with `RecipeIngredient` list, then add via `LariatBible.create_recipe_with_costing()`

### Testing Changes:
- Use Flask test client for API endpoints
- Mock email connections for email parser tests
- Validate pack size parsing with edge cases (gallons, cans, special formats)
- Verify margin calculations with known menu items

---

**Last Updated:** 2025-11-19
**Project Owner:** Sean (Restaurant Owner & Operator)
**Contact:** Direct communication with Sean for questions
