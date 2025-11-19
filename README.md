# BEO Bible

## Banquet Event Order Management System

A comprehensive system for managing banquet events from booking through execution, with automated invoicing, kitchen preparation scheduling, and ingredient tracking.

## System Overview

The BEO Bible provides a complete workflow for restaurant banquet operations:
- **Client Invoicing** with automated pricing and calculations
- **Kitchen Prep Sheets** that auto-populate from invoices
- **Production Scheduling** across multiple prep days
- **Ingredient Scaling** from recipe database
- **Vendor Ordering** with inventory management
- **Event Execution** checklists and workflows

## Quick Start

### For New Users
1. Read [DOCUMENTATION/SYSTEM_OVERVIEW.md](DOCUMENTATION/SYSTEM_OVERVIEW.md) for a complete introduction
2. Review [DOCUMENTATION/WORKFLOW.md](DOCUMENTATION/WORKFLOW.md) for the 10-step process
3. Use the Invoice Template from `TEMPLATES/` for your first event

### For Experienced Users
1. Copy `TEMPLATES/Invoice_Template_MASTER.xlsx` to `ACTIVE_EVENTS/ClientName_Date/`
2. Fill in client details and menu selections
3. Generate kitchen prep sheet automatically
4. Follow the production schedule for your event

## Repository Structure

```
BEO-Bible/
├── TEMPLATES/              # Master templates (don't edit directly)
│   └── Invoice_Template_MASTER.xlsx
│
├── DOCUMENTATION/          # System guides and procedures
│   ├── PROJECT_RULES.md              # System rules and specifications
│   ├── WORKFLOW.md                   # 10-step detailed workflow
│   ├── QA_CUSTOMIZATION_GUIDE.md     # Customization questions
│   ├── SYSTEM_OVERVIEW.md            # Executive summary
│   └── BUILD_COMPLETE.md             # Implementation roadmap
│
├── REFERENCE/              # Read-only reference materials
│   ├── Recipe_Book.docx              # All recipes, sauces, brines
│   ├── Order_Guide.xlsx              # Vendor products and pricing
│   └── Ingredients_Master_List.xlsx  # Complete ingredient database
│
├── ACTIVE_EVENTS/          # Current events in progress
│   └── ClientName_EventDate/
│       ├── Invoice_v1.xlsx
│       ├── Production_Schedule.xlsx
│       ├── Ingredient_Orders.xlsx
│       └── NOTES.txt
│
├── ARCHIVE/                # Completed events
│   └── 2025/
│       ├── 01_January/
│       ├── 02_February/
│       └── ...
│
└── ANALYTICS/              # Reports and metrics
    ├── Monthly_Revenue_Report.xlsx
    ├── Food_Cost_Analysis.xlsx
    └── Client_Satisfaction_Tracker.xlsx
```

## Core Features

### Invoice Template
- **Automated Pricing**: VLOOKUP formulas pull prices from master list
- **Auto-Calculations**: Subtotals, tax (8.15%), service fee (20%)
- **Minimum Spend Validation**: Ensures profitability
- **53-Item Price List**: Complete menu with current pricing

### Kitchen Prep Sheet
- **Auto-Population**: Links directly from invoice sheet
- **Prep Day Assignment**: Thursday/Friday/Saturday scheduling
- **Task Details**: Specific prep instructions per item
- **Service Timing**: Plating and serving specifications

### Production Workflow
- **Thursday**: Long braises, stocks, sauces
- **Friday**: Main prep, marinades, butchering
- **Saturday**: Final prep and event execution

## Key Metrics

- **Target Food Cost**: 30-35%
- **Service Fee**: 20%
- **Sales Tax**: 8.15%
- **Minimum Event**: $500
- **Typical Lead Time**: 7-14 days
- **Standard Crew**: 3-5 people

## Getting Started

### Immediate Actions
1. Review all documentation in `/DOCUMENTATION/`
2. Familiarize yourself with the Invoice Template
3. Answer customization questions in QA_CUSTOMIZATION_GUIDE.md

### This Week
1. Customize pricing in the template
2. Add your recipes to REFERENCE/
3. Update vendor information
4. Train staff on the system

### Next 2 Weeks
1. Run a test event through the system
2. Refine workflows based on feedback
3. Establish metrics tracking
4. Go live with real events

## Documentation

- **[SYSTEM_OVERVIEW.md](DOCUMENTATION/SYSTEM_OVERVIEW.md)**: Executive summary and key features
- **[WORKFLOW.md](DOCUMENTATION/WORKFLOW.md)**: Complete 10-step process with timelines
- **[PROJECT_RULES.md](DOCUMENTATION/PROJECT_RULES.md)**: System specifications and formulas
- **[QA_CUSTOMIZATION_GUIDE.md](DOCUMENTATION/QA_CUSTOMIZATION_GUIDE.md)**: 30 questions to customize the system
- **[BUILD_COMPLETE.md](DOCUMENTATION/BUILD_COMPLETE.md)**: Implementation roadmap and training

## Support & Customization

This system is designed to be customizable for your specific operation. Use the QA Customization Guide to tailor:
- Pricing and margins
- Menu offerings
- Prep schedules
- Vendor preferences
- Staff workflows

## Success Metrics

Track these KPIs for continuous improvement:
- Event profitability (target: 45% margin)
- Food cost percentage (target: 30-35%)
- Client satisfaction scores
- Prep time accuracy
- Waste percentage
- Repeat booking rate

## Version Control

- Keep master templates unchanged
- Create new versions for each client revision
- Archive completed events monthly
- Document system changes in NOTES.txt

---

**Built for efficient banquet operations from booking to execution**

*Last Updated: 2025-11-19*
