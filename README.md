# The Lariat Bible 🤠

## Comprehensive Restaurant Management System

A unified platform for managing all aspects of The Lariat restaurant operations in Fort Collins, Colorado.

## 🎯 Project Vision

The Lariat Bible serves as the single source of truth for:
- Vendor pricing and analysis
- Inventory management
- Recipe standardization and costing
- Catering operations
- Equipment maintenance
- Financial reporting
- Staff training and documentation

## 📊 Key Metrics
- **Monthly Catering Revenue**: $28,000
- **Monthly Restaurant Revenue**: $20,000
- **Potential Annual Savings** (Shamrock vs SYSCO): $52,000

## 🗂️ Project Structure

```
lariat-bible/
├── core/                   # Core functionality
│   ├── database/          # Database models and connections
│   ├── authentication/    # User authentication and permissions
│   └── shared_utilities/  # Shared helper functions
├── modules/               # Business logic modules
│   ├── vendor_analysis/   # Vendor price comparison and optimization
│   ├── inventory/         # Stock management and tracking
│   ├── recipes/           # Recipe management and costing
│   ├── catering/          # Catering operations and quotes
│   ├── maintenance/       # Equipment maintenance schedules
│   └── reporting/         # Business intelligence and reports
├── web_interface/         # Web application frontend
├── data/                  # Data storage
│   └── invoices/         # Invoice images and OCR data
├── documentation/         # Additional documentation
└── tests/                # Test suites
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/[your-username]/lariat-bible.git
cd lariat-bible

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run initial setup
python setup.py
```

### Basic Usage

```python
# Example: Upload vendor CSVs and generate comparison Excel
from modules.vendor_analysis import VendorCSVProcessor
import pandas as pd

processor = VendorCSVProcessor()

# Load your vendor CSVs
shamrock_df = pd.read_csv('shamrock_order_guide.csv')
sysco_df = pd.read_csv('sysco_order_guide.csv')

processor.load_shamrock_dataframe(shamrock_df)
processor.load_sysco_dataframe(sysco_df)

# Generate comparison Excel with multiple sheets
combined = processor.combine_vendor_data()
excel_path = processor.generate_comparison_excel('vendor_comparison.xlsx')
print(f"Comparison saved to: {excel_path}")

# Get summary statistics
stats = processor.get_summary_stats()
print(f"Products matched: {stats['total_matched']}")
print(f"Shamrock cheaper: {stats['shamrock_cheaper_count']}")
print(f"Sysco cheaper: {stats['sysco_cheaper_count']}")
```

```python
# Example: Create unified recipe book
from modules.recipes import UnifiedRecipeBook, UnifiedRecipe

book = UnifiedRecipeBook()

# Create a recipe
recipe = UnifiedRecipe(
    recipe_id='LARIAT001',
    name='House Blackened Chicken',
    category='Entree',
    yield_quantity=10,
    yield_unit='portions'
)

# Add ingredients
recipe.add_ingredient('Chicken Breast', 3.75, 'lb', cost=8.50)
recipe.add_ingredient('Blackening Spice', 2, 'tbsp', cost=0.50)

# Add instructions
recipe.cooking_instructions = [
    'Heat cast iron until smoking',
    'Cook chicken 4-5 minutes per side'
]

# Calculate cost and add to book
recipe.calculate_cost()
book.add_recipe(recipe)

# Export to Excel with all sheets
excel_path = book.export_to_excel('recipe_book.xlsx')
```

## 🌐 API Endpoints

### Vendor CSV Upload
```bash
# Upload vendor CSVs and generate comparison Excel
POST /api/upload-vendor-csvs
Content-Type: multipart/form-data

# Form fields:
# - shamrock_csv: Shamrock Foods CSV file
# - sysco_csv: Sysco CSV file
# - match_threshold (optional): 0.6 default

# Response includes download link for Excel file
```

### Recipe Management
```bash
# List all recipes
GET /api/recipes

# Get specific recipe
GET /api/recipes/<recipe_id>

# Create new recipe
POST /api/recipes
Content-Type: application/json

# Export to Excel
GET /api/recipes/export/excel
```

### Download Files
```bash
# Download generated files
GET /api/download/<filename>
```

## 📦 Modules Overview

### Vendor Analysis & CSV Upload
Automated price comparison between vendors with CSV upload and Excel report generation.
- **Upload vendor CSVs**: Upload original Shamrock and Sysco CSVs directly
- **Automatic matching**: Products are automatically matched between vendors
- **Multi-sheet Excel report**: Generates Excel with sheets for:
  - Best Prices (cheapest option for each product)
  - Shamrock More Expensive items
  - Sysco More Expensive items
  - All Matched Products
  - Summary Statistics
- Invoice OCR and data extraction
- Price trend analysis
- Savings opportunity identification

### Recipe Management & Unified Recipe Book
Standardized recipes with automatic cost calculation and unified format.
- **Unified recipe format**: Consistent structure for all recipes
- **Total yields**: Yield quantities and portion sizes
- **Complete instructions**: Prep, cooking, and plating instructions
- **Multi-sheet Excel export**: Recipe Index, Full Recipes, Ingredients Master, Category Summary
- Recipe scaling for different serving sizes
- Ingredient cost tracking
- Margin analysis

### Catering Operations
Streamlined catering workflow from quote to execution.
- Quick quote generator
- Event planning tools
- Profit margin calculator (Target: 45%)

### Maintenance Tracking
Equipment maintenance scheduling and history.
- Preventive maintenance schedules
- Repair history logging
- Vendor contact management

### Reporting Dashboard
Comprehensive business intelligence and analytics.
- Daily/weekly/monthly sales reports
- Labor cost analysis
- Profit margin tracking

## 🔧 Configuration

Copy `.env.example` to `.env` and configure:

```env
DATABASE_URL=sqlite:///lariat.db
SECRET_KEY=your-secret-key
INVOICE_STORAGE_PATH=./data/invoices
```

## 📈 Development Roadmap

### Phase 1: Foundation ✅
- [x] Project structure setup
- [x] Core utilities implementation
- [x] Vendor CSV upload and comparison
- [x] Unified recipe book format

### Phase 2: Vendor Analysis ✅
- [x] CSV upload for Shamrock and Sysco
- [x] Automatic product matching
- [x] Multi-sheet Excel comparison reports
- [x] Price per unit calculations
- [ ] OCR pipeline for invoices

### Phase 3: Inventory & Recipes ✅
- [x] Unified recipe format with yields
- [x] Complete instructions (prep, cooking, plating)
- [x] Multi-sheet recipe book export
- [x] Ingredient cost tracking
- [ ] Inventory tracking system

### Phase 4: Web Interface
- [x] REST API endpoints
- [x] File upload support
- [ ] Dashboard creation
- [ ] Mobile-responsive design
- [ ] Real-time updates

## 🤝 Contributing

This is a private repository for The Lariat restaurant operations.

## 📝 License

Proprietary - The Lariat Restaurant, Fort Collins, CO

## 👤 Owner

**Sean** - Restaurant Owner & Operator

## 🆘 Support

For questions or issues, contact Sean directly.

---

*Building a data-driven future for The Lariat, one module at a time.*
