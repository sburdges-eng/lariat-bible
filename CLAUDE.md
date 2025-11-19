# CLAUDE.md - AI Assistant Guide for The Lariat Bible

## Project Overview

**The Lariat Bible** is a comprehensive restaurant management system for The Lariat restaurant in Fort Collins, Colorado. This is a private, business-critical application designed to optimize operations, reduce costs, and improve profitability through data-driven decision-making.

### Business Context

- **Owner**: Sean (restaurant owner & operator)
- **Monthly Catering Revenue**: $28,000
- **Monthly Restaurant Revenue**: $20,000
- **Key Business Goal**: Optimize vendor relationships to capture $52,000/year in savings (29.5% cost reduction vs SYSCO by using Shamrock Foods)
- **Target Margins**: 45% catering, 4% restaurant operations

### Critical Business Intelligence

The system has already identified **29.5% savings** by switching from SYSCO to Shamrock Foods for most ingredients. However, product matching MUST be exact (e.g., "Black Pepper Fine" ≠ "Black Pepper Coarse"). See `PRODUCT_MATCHING_VERIFICATION.md` for critical matching rules.

## Repository Structure

```
lariat-bible/
├── app.py                          # Flask web application entry point
├── setup.py                        # Setup script for initialization
├── requirements.txt                # Python dependencies
├── modules/                        # Core business logic modules
│   ├── core/
│   │   └── lariat_bible.py        # Main integration class
│   ├── vendor_analysis/           # Vendor price comparison
│   │   ├── comparator.py          # Main comparison engine
│   │   ├── accurate_matcher.py    # Product matching logic
│   │   └── corrected_comparison.py
│   ├── recipes/
│   │   └── recipe.py              # Recipe, Ingredient, RecipeIngredient classes
│   ├── menu/
│   │   ├── __init__.py
│   │   └── menu_item.py           # MenuItem class with pricing logic
│   ├── order_guides/
│   │   └── order_guide_manager.py # Order guide import/comparison
│   ├── equipment/
│   │   └── equipment_manager.py   # Equipment tracking & maintenance
│   └── email_parser/
│       └── email_parser.py        # Invoice email parsing (future)
├── data/                          # Data storage
│   ├── matched_products_comparison.csv
│   ├── corrected_spice_comparison.csv
│   └── invoices/                  # Invoice storage (future)
├── static/                        # Web assets (future)
├── templates/                     # HTML templates (future)
├── logs/                          # Application logs
├── reports/                       # Generated reports
└── backups/                       # Data backups

```

## Core Architecture

### Design Philosophy

1. **Modular Design**: Each business function is isolated in its own module
2. **Data-Driven**: All decisions backed by actual pricing data
3. **Vendor Agnostic**: Support for multiple vendors with easy comparison
4. **Cost Optimization**: Primary focus on reducing food costs while maintaining quality
5. **Single Source of Truth**: The LariatBible class integrates all modules

### Key Classes

#### LariatBible (`modules/core/lariat_bible.py`)
- **Purpose**: Main integration point for all modules
- **Responsibilities**: Coordinates menu, recipes, ingredients, vendors, equipment
- **Usage**: Singleton instance at module level

#### Ingredient (`modules/recipes/recipe.py`)
- **Purpose**: Represents a purchasable ingredient with multi-vendor pricing
- **Key Properties**:
  - `sysco_price`, `sysco_unit_price`, `sysco_item_code`
  - `shamrock_price`, `shamrock_unit_price`, `shamrock_item_code`
  - `preferred_vendor` (auto-calculated based on best price)
  - `price_difference`, `price_difference_percent`
- **Critical Method**: `calculate_best_price()` - Determines optimal vendor

#### Recipe (`modules/recipes/recipe.py`)
- **Purpose**: Standardized recipe with automatic cost calculation
- **Key Properties**: `total_cost`, `cost_per_portion`
- **Critical Methods**:
  - `get_shopping_list(multiplier)` - Generates vendor-optimized shopping list
  - `analyze_vendor_impact()` - Shows cost differences between vendors

#### MenuItem (`modules/menu/menu_item.py`)
- **Purpose**: Menu item with recipe linkage and pricing analysis
- **Key Properties**: `margin`, `margin_variance`, `suggested_price`
- **Critical Methods**:
  - `update_food_cost()` - Recalculates margins when costs change

#### VendorComparator (`modules/vendor_analysis/comparator.py`)
- **Purpose**: Analyzes pricing between vendors
- **Key Data**: 29.5% average savings with Shamrock Foods
- **Critical Methods**:
  - `compare_vendors()` - Calculates monthly/annual savings
  - `calculate_margin_impact()` - Shows how savings affect margins

## Code Conventions

### Python Style
- **Formatting**: Use `black` for code formatting (configured in requirements.txt)
- **Linting**: Use `flake8` for linting
- **Type Hints**: Use type hints where helpful, especially in function signatures
- **Docstrings**: Use triple-quoted strings for all classes and non-trivial functions
- **Dataclasses**: Prefer `@dataclass` for data models (see Ingredient, Recipe, MenuItem)

### Naming Conventions
- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Methods**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private Methods**: `_leading_underscore`

### File Organization
- **One class per file** for major business entities
- **Group related utilities** in manager classes (e.g., OrderGuideManager, EquipmentManager)
- **Keep modules focused** on a single business domain

## Data Flow

### Vendor Price Comparison Flow
```
1. Import order guides (CSV/Excel) → OrderGuideManager
2. Match products between vendors → accurate_matcher.py
3. Calculate price differences → VendorComparator
4. Update Ingredient pricing → Ingredient.calculate_best_price()
5. Recalculate Recipe costs → Recipe.total_cost
6. Update MenuItem margins → MenuItem.update_food_cost()
7. Generate recommendations → LariatBible.optimize_menu_pricing()
```

### Recipe Costing Flow
```
1. Create Ingredient objects with vendor pricing
2. Add Ingredients to Recipe via RecipeIngredient
3. Recipe automatically calculates total_cost and cost_per_portion
4. Link Recipe to MenuItem
5. MenuItem calculates margin and suggested_price
6. Generate pricing recommendations
```

## Environment Configuration

The system uses environment variables via `.env` file:

```bash
# Database
DATABASE_URL=sqlite:///lariat.db

# Security
SECRET_KEY=<random-secret-key>

# Paths
INVOICE_STORAGE_PATH=./data/invoices
BACKUP_PATH=./backups

# Business Settings
RESTAURANT_NAME=The Lariat
LOCATION=Fort Collins, CO
DEFAULT_CATERING_MARGIN=0.45      # 45% target
DEFAULT_RESTAURANT_MARGIN=0.04    # 4% target

# Vendors
PRIMARY_VENDOR=Shamrock Foods
COMPARISON_VENDOR=SYSCO

# Web Interface
FLASK_ENV=development
FLASK_DEBUG=True
HOST=127.0.0.1
PORT=5000
```

## Development Workflow

### Setup
```bash
# Clone and setup
git clone <repo-url>
cd lariat-bible
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python setup.py
```

### Running the Application
```bash
# Start web interface
python app.py

# Access at http://127.0.0.1:5000
# Health check: http://127.0.0.1:5000/api/health
```

### Testing
```bash
# Run tests
pytest

# With coverage
pytest --cov=modules --cov-report=html
```

### Code Quality
```bash
# Format code
black modules/ app.py setup.py

# Lint code
flake8 modules/ app.py
```

## API Endpoints

### Current Endpoints (app.py)

- `GET /` - Dashboard with system status and metrics
- `GET /api/health` - Health check
- `GET /api/modules` - List all modules and their status
- `GET /api/vendor-comparison` - Get vendor comparison data with savings

### Future Endpoints (Planned)
- `/api/recipes` - Recipe CRUD operations
- `/api/menu-items` - Menu item management
- `/api/ingredients` - Ingredient pricing updates
- `/api/catering/quote` - Generate catering quotes
- `/api/reports/*` - Various business reports

## Common AI Assistant Tasks

### When Adding New Features

1. **Read relevant modules first** - Always understand existing code before modifying
2. **Maintain the modular structure** - Keep business logic separated
3. **Update LariatBible integration** - If adding a new module, integrate it into the main class
4. **Add to app.py if needed** - Create API endpoints for web access
5. **Test with real data** - Use actual vendor pricing data when available

### When Analyzing Vendor Data

1. **Verify product matching** - Ensure you're comparing identical products (grind size, pack size, etc.)
2. **Use unit prices** - Always compare price per pound/oz/unit, not case prices
3. **Consider quality differences** - Not all products are created equal even if names match
4. **Check date relevance** - Pricing data should be recent (check `*_last_updated` fields)
5. **Calculate impact** - Show how changes affect margins and revenue

### When Working with Recipes

1. **Link ingredients properly** - Every RecipeIngredient needs a valid Ingredient with pricing
2. **Calculate costs automatically** - Use the built-in properties, don't manually calculate
3. **Consider scaling** - Recipes should work for different batch sizes
4. **Track vendor optimization** - Use `analyze_vendor_impact()` to show savings opportunities

### When Updating Pricing

1. **Update unit prices** - Not just case prices
2. **Recalculate downstream** - Update Ingredient → Recipe → MenuItem chain
3. **Flag significant changes** - Alert if price changes affect margins by >5%
4. **Update timestamps** - Set `*_last_updated` fields

## Important Gotchas

### Product Matching is Critical
- **DON'T** match "Black Pepper Fine" with "Black Pepper Coarse" - they're different products
- **DO** verify pack sizes match (6/1LB vs 25LB requires unit price calculation)
- **DO** check product codes in addition to descriptions
- See `PRODUCT_MATCHING_VERIFICATION.md` for detailed rules

### Margin Calculations
- Catering uses 45% target margin (high-end events)
- Restaurant uses 4% target margin (competitive pricing)
- Margin = (Price - Cost) / Price (NOT Cost / Price)
- Suggested Price = Cost / (1 - Target Margin)

### Vendor Pricing
- Shamrock Foods averages 29.5% cheaper than SYSCO
- Always store both case price AND unit price
- Unit price is what's used for recipe costing
- Prices should be updated regularly (check freshness)

### Database Not Yet Implemented
- Current state: In-memory data structures
- Planned: SQLAlchemy with SQLite
- For now: Export to JSON/Excel for persistence

### Flask App is Basic
- Currently serves JSON API only
- No frontend yet (planned)
- No authentication yet (planned)
- Use for testing and development

## Business Logic Rules

### Recipe Costing
1. Each ingredient has pricing from multiple vendors
2. System automatically selects cheapest vendor per ingredient
3. Recipe cost = sum of (quantity × unit_price) for each ingredient
4. Cost per portion = total_cost / yield_amount

### Menu Pricing
1. Menu price should achieve target margin for category
2. If margin variance > 5%, flag for review
3. suggested_price = food_cost / (1 - target_margin)
4. Consider popularity and competition when adjusting

### Vendor Selection
1. Default to preferred vendor (based on price)
2. Consider minimums, delivery schedules, relationships
3. Mixed vendor orders acceptable if savings justify complexity
4. Track actual purchases vs. optimal recommendations

### Catering Operations
1. 45% target margin (includes labor, overhead, profit)
2. Quote generation: cost per portion / (1 - 0.45)
3. Consider setup, delivery, service in pricing
4. Track quote acceptance rate

## Data Management

### Import/Export
- **CSV Import**: Order guides from vendors
- **Excel Export**: Comparison reports for analysis
- **JSON Export**: Data backups and integrations
- All exports include timestamp in filename

### Backup Strategy
- Export all data daily to `backups/` directory
- Keep 30 days of backups
- Critical before major changes
- Use `LariatBible.export_all_data()`

### Data Validation
- Prices must be > 0
- Margins must be 0-1 (0-100%)
- Quantities must be > 0
- Dates should be validated (not in future for historical data)

## Security Considerations

### Current State
- No authentication implemented yet
- Environment variables for configuration
- No user management
- Local deployment only

### Planned Security
- Flask-Login for authentication
- Role-based access (Owner, Manager, Staff)
- API keys for integrations
- HTTPS for production
- Encrypted backup storage

### Data Privacy
- This is proprietary business data
- Vendor pricing is confidential
- Recipe costs are trade secrets
- Handle all data as sensitive

## Testing Guidelines

### What to Test
1. **Price calculations** - Verify math is correct
2. **Vendor comparisons** - Ensure savings calculations accurate
3. **Recipe costing** - Test with real ingredient data
4. **Margin calculations** - Verify business logic
5. **Product matching** - Critical to avoid mismatches

### Test Data
- Use realistic prices from actual vendors
- Include edge cases (zero prices, missing data)
- Test with various pack sizes and units
- Include seasonal and discontinued items

### Test Files Location
- `tests/` directory (to be created)
- Mirror module structure
- Use pytest fixtures for common data

## Future Development Priorities

### Phase 1 (Current - Foundation)
- [x] Project structure
- [x] Core data models (Ingredient, Recipe, MenuItem)
- [x] Basic vendor comparison
- [ ] Database implementation
- [ ] Complete web API

### Phase 2 (Vendor Analysis)
- [ ] OCR for invoice processing
- [ ] Automated price tracking
- [ ] Email parser for order confirmations
- [ ] Historical price trending
- [ ] Vendor performance scoring

### Phase 3 (Inventory & Recipes)
- [ ] Real-time inventory tracking
- [ ] Automated reorder points
- [ ] Recipe scaling calculator
- [ ] Batch production planning
- [ ] Waste tracking

### Phase 4 (Web Interface)
- [ ] React/Vue frontend
- [ ] Interactive dashboards
- [ ] Mobile-responsive design
- [ ] Real-time notifications
- [ ] PDF report generation

### Phase 5 (Advanced Features)
- [ ] Machine learning for demand forecasting
- [ ] Seasonal menu optimization
- [ ] Labor cost integration
- [ ] Multi-location support (if expanded)
- [ ] Supplier portal integration

## Helpful Commands

```bash
# Generate executive summary
python -c "from modules.core.lariat_bible import lariat_bible; print(lariat_bible.generate_executive_summary())"

# Export all data
python -c "from modules.core.lariat_bible import lariat_bible; print(lariat_bible.export_all_data())"

# Run vendor comparison
python -c "from modules.vendor_analysis.comparator import VendorComparator; vc = VendorComparator(); print(vc.generate_report())"

# Start web interface
python app.py
```

## Getting Help

### Documentation Files
- `README.md` - Project overview and quick start
- `PRODUCT_MATCHING_VERIFICATION.md` - Critical product matching rules
- `GITHUB_SETUP.md` - GitHub repository setup
- This file (`CLAUDE.md`) - AI assistant guide

### Code Comments
- Docstrings in all major classes
- Inline comments for complex business logic
- Type hints for function signatures

### Contact
- **Owner**: Sean
- **Purpose**: All questions about business requirements, vendor relationships, menu decisions

## AI Assistant Principles

When working on this codebase:

1. **Understand the business context** - This is a real restaurant with real financial implications
2. **Verify calculations** - Money math must be precise
3. **Preserve data integrity** - Vendor pricing is critical business intelligence
4. **Maintain modularity** - Keep the clean separation of concerns
5. **Document assumptions** - Especially for business logic
6. **Test with real data** - Use actual vendor prices when possible
7. **Consider the owner** - Sean is non-technical; solutions should be practical
8. **Respect confidentiality** - This is proprietary business data
9. **Focus on value** - $52k/year in savings is the goal
10. **Keep it simple** - Over-engineering helps no one

## Version History

- **v1.0** (2024-11-19) - Initial CLAUDE.md creation
  - Comprehensive codebase documentation
  - Business context and goals
  - Module architecture and data flow
  - Development guidelines and conventions

---

**Remember**: This system exists to help The Lariat save $52,000 per year and improve profitability. Every feature should serve that mission.
