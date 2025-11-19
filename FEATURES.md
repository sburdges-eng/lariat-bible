# The Lariat Bible - Enhanced Features

## Overview
This document describes the new interactive features and enhancements added to The Lariat Bible restaurant management system.

## New Features

### 1. Interactive Dashboard
- **Real-time Cost Analysis Charts**: Visual representation of savings trends, vendor comparisons, and cost breakdowns
- **Category Breakdown**: Doughnut charts showing spending distribution across categories
- **Revenue vs Costs**: Line charts tracking financial performance over time
- **Top Savings Opportunities**: Interactive table highlighting the best cost-saving opportunities
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

### 2. Vendor Analysis & Comparison
- **Side-by-Side Vendor Comparison**: Compare multiple vendors across all product categories
- **Savings by Category**: Visual breakdown of savings potential by product category
- **Price Trend Analysis**: Interactive Plotly charts showing price trends over time
- **Margin Impact Calculator**: See how vendor switching affects profit margins
- **Detailed Comparison Tables**: Filterable and searchable product-by-product comparisons

### 3. Excel Import/Export Functionality

#### Import Capabilities
- **Price Lists**: Import vendor price lists from Excel files (.xlsx, .xls)
- **Order Guides**: Import complete order guides with automatic field mapping
- **Drag & Drop Support**: Simply drag Excel files to upload areas
- **Data Validation**: Automatic validation and preview before import

#### Export Capabilities
- **Price Comparisons**: Export full vendor comparisons with multiple sheets
  - Main comparison data
  - Summary metrics
  - Category analysis
  - Top savings opportunities

- **Order Guides**: Export vendor order guides with:
  - Item codes and descriptions
  - Pack sizes and pricing
  - Category organization
  - Last updated timestamps

- **Savings Opportunities**: Export prioritized list of cost-saving items
  - Ranked by savings potential
  - Annual impact calculations
  - Current vs. best pricing

- **Recipe Cost Analysis**: Export detailed recipe costs
  - Ingredient breakdowns
  - Labor and overhead calculations
  - Suggested pricing
  - Margin analysis

#### Download Templates
- Pre-formatted templates for easy data import
- Available for:
  - Shamrock Foods price lists
  - SYSCO price lists
  - Generic vendor format
  - Order guide format
  - Recipe format

### 4. Profit Margin Calculator
- **Interactive Cost Input**: Enter food, labor, and overhead costs
- **Real-time Calculations**: Instant profit margin calculations
- **Visual Cost Breakdown**: Pie charts showing cost composition
- **Margin Comparison**: Current vs target margin visualization
- **Scenario Analysis**: Test different scenarios:
  - Reduce food cost by 10%
  - Increase price by 5%
  - Switch to Shamrock Foods
- **Bulk Analysis**: Import menu items for mass margin analysis

### 5. Recipe Cost Calculator
- **Recipe Builder**: Add ingredients with quantities and costs
- **Automatic Cost Calculation**: Real-time cost per serving
- **Labor & Overhead Inclusion**: 30% labor, 15% overhead estimates
- **Suggested Pricing**: Automatic price suggestion for 45% margin
- **Ingredient Breakdown Charts**: Visual representation of recipe costs
- **Vendor Impact Analysis**: See how vendor switching affects recipe costs
- **Batch Cost Calculator**: Calculate costs for large batches (catering)
- **Recipe Library**: Save and manage multiple recipes

### 6. Order Guide Management
- **Multi-Vendor Support**: Manage guides from multiple vendors
- **Import/Export**: Full Excel import/export capabilities
- **Guide Comparison**: Compare order guides side-by-side
- **Search & Filter**: Find products quickly
- **Version Tracking**: Track when guides were last updated

## Technical Enhancements

### Frontend
- **Chart.js Integration**: Beautiful, interactive charts
- **Plotly.js**: Advanced data visualization
- **Responsive CSS Grid**: Modern, flexible layouts
- **Custom Animations**: Smooth transitions and loading states
- **Font Awesome Icons**: Professional iconography
- **Google Fonts**: Clean, readable typography (Inter)

### Backend
- **Flask Routes**: RESTful API endpoints for all features
- **Excel Handler Module**: Robust Excel import/export with openpyxl
- **Data Validation**: Input validation and error handling
- **File Upload Support**: Secure file upload with size limits
- **CORS Enabled**: Cross-origin resource sharing for API access

### Data Processing
- **Pandas Integration**: Efficient data manipulation
- **DataFrame Operations**: Fast data transformations
- **Excel Styling**: Professional formatting with colors and borders
- **Multi-Sheet Exports**: Comprehensive reports with multiple worksheets

## File Structure

```
lariat-bible/
├── templates/
│   ├── base.html                  # Base template with navigation
│   ├── dashboard.html             # Main dashboard
│   ├── vendor_analysis.html       # Vendor comparison
│   ├── price_comparison.html      # Price comparison & import
│   ├── order_guides.html          # Order guide management
│   ├── profit_calculator.html     # Profit margin calculator
│   └── recipe_costing.html        # Recipe cost analysis
├── static/
│   ├── css/
│   │   └── main.css              # Main stylesheet (800+ lines)
│   └── js/
│       ├── main.js               # Common utilities
│       ├── dashboard.js          # Dashboard functionality
│       ├── vendor_analysis.js    # Vendor comparison
│       ├── price_comparison.js   # Price comparison
│       ├── order_guides.js       # Order guide management
│       ├── profit_calculator.js  # Profit calculations
│       └── recipe_costing.js     # Recipe costing
├── modules/
│   └── core/
│       └── excel_handler.py      # Excel import/export engine
└── app.py                        # Main Flask application
```

## API Endpoints

### Page Routes
- `GET /` - Dashboard
- `GET /vendor-analysis` - Vendor analysis page
- `GET /price-comparison` - Price comparison page
- `GET /order-guides` - Order guide management
- `GET /profit-calculator` - Profit calculator
- `GET /recipe-costing` - Recipe costing

### API Routes

#### Vendor Comparison
- `GET /api/vendor-comparison` - Get vendor comparison summary
- `GET /api/vendor-comparison/detailed` - Get detailed comparison data

#### Excel Export
- `POST /api/export/price-comparison` - Export price comparison
- `POST /api/export/order-guide` - Export order guide
- `POST /api/export/savings-opportunities` - Export top savings
- `POST /api/export/recipe-costs` - Export recipe costs

#### Excel Import
- `POST /api/import/price-list` - Import price list
- `POST /api/import/order-guide` - Import order guide

#### Templates
- `GET /api/template/<type>` - Download import template
  - Types: `price_list`, `order_guide`, `recipe`

#### System
- `GET /api/health` - Health check
- `GET /api/modules` - List available modules

## Usage Examples

### Importing a Price List
1. Navigate to Price Comparison page
2. Click "Select Files" or drag Excel file to upload area
3. System validates and previews data
4. Data is automatically imported and ready for comparison

### Exporting Vendor Comparison
1. Go to Vendor Analysis page
2. Select vendors to compare
3. Click "Export Full Report"
4. Download Excel file with multiple analysis sheets

### Calculating Recipe Costs
1. Navigate to Recipe Costing page
2. Enter recipe name and details
3. Add ingredients with quantities and costs
4. System automatically calculates:
   - Total ingredient cost
   - Labor cost (30%)
   - Overhead (15%)
   - Suggested price for 45% margin
5. Save recipe or export to Excel

### Analyzing Profit Margins
1. Go to Profit Calculator
2. Enter costs (food, labor, overhead) and selling price
3. View real-time margin calculations
4. Test different scenarios:
   - What if food costs drop 10%?
   - What if we increase prices 5%?
   - What if we switch vendors?
5. Export analysis to Excel

## Key Metrics Tracked

- **Annual Savings Potential**: $52,000
- **Monthly Savings**: $4,333
- **Average Savings Percentage**: 29.5%
- **Catering Margin**: 45% (target: 52.7% with Shamrock)
- **Restaurant Margin**: 4% (target: 8.7% with Shamrock)
- **Monthly Revenue**: $48,000
  - Restaurant: $20,000
  - Catering: $28,000

## Future Enhancements

Potential additions include:
- Real-time price tracking with alerts
- Predictive analytics for cost trends
- Inventory integration
- Mobile app
- Automated vendor order generation
- Email invoice parsing
- Machine learning price prediction
- Budget forecasting tools

## Support

For questions or issues with the new features, refer to the main README.md or contact the system administrator.
