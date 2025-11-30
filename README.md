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
- **Target Catering Margin**: 45%

## 🗂️ Project Structure

```
lariat-bible/
├── modules/
│   ├── vendor_analysis/   # Vendor price comparison and optimization
│   │   ├── vendor_parser.py       # Parse SYSCO/Shamrock spreadsheets
│   │   ├── accurate_matcher.py    # Fuzzy product matching
│   │   ├── unit_converter.py      # Unit conversion utilities
│   │   ├── report_generator.py    # Generate comparison reports
│   │   └── comparator.py          # Price comparison logic
│   ├── beo_integration/   # BEO file processing
│   │   ├── beo_parser.py          # Parse BEO Excel files
│   │   ├── order_calculator.py    # Calculate ingredient quantities
│   │   └── prep_sheet_generator.py # Generate kitchen prep sheets
│   ├── core/              # Core functionality
│   │   ├── models.py              # Data models
│   │   └── db.py                  # Database utilities
│   ├── inventory/         # Stock management
│   └── recipes/           # Recipe management
├── scripts/
│   └── vendor_cli.py      # CLI for vendor operations
├── data/                  # Data storage
│   ├── sample_sysco.xlsx  # Sample SYSCO data
│   └── sample_shamrock.xlsx # Sample Shamrock data
├── tests/                 # Test suites
├── app.py                 # Flask web application
└── requirements.txt       # Python dependencies
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
# Example: Vendor price comparison
from modules.vendor_analysis import VendorComparator

comparator = VendorComparator()
savings = comparator.compare_vendors('SYSCO', 'Shamrock Foods')
print(f"Potential monthly savings: ${savings}")
```

## 🔧 Vendor Comparison Feature

### CLI Commands

```bash
# Parse SYSCO spreadsheet
python -m scripts.vendor_cli parse sysco invoice.xlsx --output products.json

# Parse Shamrock spreadsheet
python -m scripts.vendor_cli parse shamrock order_guide.xlsx

# Compare vendors (with input files)
python -m scripts.vendor_cli compare --sysco sysco.xlsx --shamrock shamrock.xlsx --output report.csv

# Compare vendors (sample data)
python -m scripts.vendor_cli compare --output report.csv

# Show savings summary
python -m scripts.vendor_cli savings

# Generate prep sheet from BEO
python -m scripts.vendor_cli prep-sheet event.xlsx --output kitchen_prep.html
```

### API Endpoints

Start the server:
```bash
python app.py
```

**Vendor Analysis Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/vendor/upload` | POST | Upload vendor spreadsheet for parsing |
| `/api/vendor/comparison` | GET | Get full comparison data |
| `/api/vendor/savings` | GET | Get savings summary |

**BEO Integration Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/beo/parse` | POST | Parse uploaded BEO file |
| `/api/beo/events` | GET | List all parsed events |
| `/api/beo/prep-sheet/<event_id>` | GET | Generate prep sheet |

**Example: Upload SYSCO File**
```bash
curl -X POST -F "file=@sysco_invoice.xlsx" -F "vendor=sysco" \
  http://localhost:5000/api/vendor/upload
```

**Example: Get Comparison**
```bash
curl http://localhost:5000/api/vendor/comparison
```

**Example: Get Prep Sheet**
```bash
curl http://localhost:5000/api/beo/prep-sheet/BEO-2024-001?format=html
```

### Python API

```python
from modules.vendor_analysis import VendorParser, AccurateVendorMatcher, ReportGenerator

# Parse vendor files
parser = VendorParser()
sysco_products = parser.parse_sysco('sysco_invoice.xlsx')
shamrock_products = parser.parse_shamrock('shamrock_order.xlsx')

# Match products
matcher = AccurateVendorMatcher()
matched, sysco_only, shamrock_only = matcher.fuzzy_match_products(
    sysco_products,
    shamrock_products,
    min_confidence=0.6
)

# Generate report
generator = ReportGenerator()
generator.set_data(matched, sysco_only, shamrock_only)
generator.generate_csv_report('comparison.csv')
print(generator.generate_text_report())
```

## 📦 Modules Overview

### Vendor Analysis
Automated price comparison between vendors.
- Parse SYSCO and Shamrock spreadsheets
- Fuzzy product name matching with confidence scoring
- Unit normalization (oz to lb, cases to units)
- Brand-aware matching
- Generate comparison reports (JSON, CSV, text)
- Calculate margin impact

### BEO Integration
Process Banquet Event Order files.
- Parse BEO Excel files from BEO-Master format
- Calculate ingredient quantities based on guest count
- Generate kitchen prep sheets (text/HTML)
- Recipe-based ingredient calculation

### Inventory Management
Real-time inventory tracking and automated reordering.
- Stock level monitoring
- Expiration date tracking
- Automated purchase order generation

### Recipe Management
Standardized recipes with automatic cost calculation.
- Recipe scaling for different serving sizes
- Ingredient cost tracking
- Margin analysis

### Catering Operations
Streamlined catering workflow from quote to execution.
- Quick quote generator
- Event planning tools
- Profit margin calculator (Target: 45%)

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
- [x] Core data models
- [x] Database utilities

### Phase 2: Vendor Analysis ✅
- [x] Vendor spreadsheet parser
- [x] Product matching engine
- [x] Price comparison engine
- [x] Report generator
- [x] CLI interface
- [x] API endpoints

### Phase 3: BEO Integration ✅
- [x] BEO file parser
- [x] Ingredient calculator
- [x] Prep sheet generator

### Phase 4: Inventory & Recipes
- [ ] Inventory tracking system
- [ ] Recipe database
- [ ] Cost calculation engine

### Phase 5: Web Interface
- [ ] Dashboard creation
- [ ] Mobile-responsive design
- [ ] Real-time updates

## 🧪 Testing

Run tests:
```bash
python -m pytest tests/ -v
```

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
