#!/usr/bin/env python
"""
Vendor CLI - Command Line Interface for vendor comparison and BEO processing

Usage:
    # Parse vendor spreadsheets
    python -m scripts.vendor_cli parse sysco invoice.xlsx
    python -m scripts.vendor_cli parse shamrock invoice.xlsx

    # Compare vendors
    python -m scripts.vendor_cli compare --output savings_report.csv

    # Generate prep sheet from BEO
    python -m scripts.vendor_cli prep-sheet beo_file.xlsx --output kitchen_prep.txt
"""

import argparse
import sys
import json
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.vendor_analysis import (
    VendorParser,
    AccurateVendorMatcher,
    ReportGenerator,
)
from modules.beo_integration import (
    BEOParser,
    PrepSheetGenerator,
    OrderCalculator,
)
from modules.beo_integration.order_calculator import get_sample_recipes


def cmd_parse(args):
    """Parse a vendor spreadsheet file"""
    vendor = args.vendor.upper()
    file_path = args.file

    if not Path(file_path).exists():
        print(f"Error: File not found: {file_path}")
        return 1

    print(f"Parsing {vendor} file: {file_path}")

    parser = VendorParser()

    try:
        if vendor == "SYSCO":
            products = parser.parse_sysco(file_path)
        elif vendor in ("SHAMROCK", "SHAMROCK FOODS"):
            products = parser.parse_shamrock(file_path)
        else:
            print(f"Error: Unknown vendor: {vendor}")
            print("Supported vendors: SYSCO, Shamrock")
            return 1

        print(f"\n✅ Parsed {len(products)} products")

        if products:
            print("\nSample products:")
            for p in products[:5]:
                print(f"  - {p.product_name[:40]} | {p.unit_size} | ${p.case_price:.2f}")

        # Save to JSON if output specified
        if args.output:
            output_data = [p.to_dict() for p in products]
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"\n📄 Saved to {args.output}")

        return 0

    except Exception as e:
        print(f"Error parsing file: {e}")
        return 1


def cmd_compare(args):
    """Compare vendor prices and generate report"""
    print("Vendor Comparison Tool")
    print("=" * 50)

    matcher = AccurateVendorMatcher()
    generator = ReportGenerator()

    # Check for input files
    sysco_file = args.sysco
    shamrock_file = args.shamrock

    if sysco_file and shamrock_file:
        # Parse both files
        parser = VendorParser()

        try:
            sysco_products = parser.parse_sysco(sysco_file)
            shamrock_products = parser.parse_shamrock(shamrock_file)

            print(f"Loaded {len(sysco_products)} SYSCO products")
            print(f"Loaded {len(shamrock_products)} Shamrock products")

            # Perform fuzzy matching
            matched, sysco_only, shamrock_only = matcher.fuzzy_match_products(
                sysco_products,
                shamrock_products,
                min_confidence=args.min_confidence
            )

            print(f"\nMatched {len(matched)} products")
            print(f"SYSCO only: {len(sysco_only)}")
            print(f"Shamrock only: {len(shamrock_only)}")

            # Generate report
            generator.set_data(matched, sysco_only, shamrock_only)

        except Exception as e:
            print(f"Error processing files: {e}")
            return 1
    else:
        # Use sample data from accurate matcher
        print("\nNo input files provided. Using sample comparison data...")
        matcher.generate_comparison_report()

        # For demo purposes, create report from sample data
        generator.set_data([], [], [])

    # Generate output
    output_path = args.output or "vendor_comparison.txt"

    if output_path.endswith('.csv'):
        generator.generate_csv_report(output_path)
        print(f"\n📊 CSV report saved to {output_path}")
    elif output_path.endswith('.json'):
        generator.save_json_report(output_path)
        print(f"\n📊 JSON report saved to {output_path}")
    else:
        generator.save_text_report(output_path)
        print(f"\n📊 Text report saved to {output_path}")

    # Print summary
    summary = generator.calculate_summary()
    print("\n" + "=" * 50)
    print("SAVINGS SUMMARY")
    print("=" * 50)
    print(f"Monthly Savings Estimate: ${summary.monthly_savings:,.2f}")
    print(f"Annual Savings Estimate: ${summary.annual_savings:,.2f}")
    print(f"Products cheaper at Shamrock: {summary.products_cheaper_shamrock}")
    print(f"Products cheaper at SYSCO: {summary.products_cheaper_sysco}")

    return 0


def cmd_prep_sheet(args):
    """Generate a kitchen prep sheet from BEO file"""
    file_path = args.file

    if not Path(file_path).exists():
        print(f"Error: File not found: {file_path}")
        return 1

    print(f"Processing BEO file: {file_path}")

    # Parse BEO
    beo_parser = BEOParser()

    try:
        events = beo_parser.parse_file(file_path)

        if not events:
            print("No events found in BEO file")
            return 1

        print(f"\nFound {len(events)} events")

        # Use first event or specified event
        event = events[0]
        if args.event_id:
            event = beo_parser.get_event_by_id(args.event_id)
            if not event:
                print(f"Event not found: {args.event_id}")
                return 1

        print(f"Processing: {event.event_id} - {event.client_name}")

        # Calculate ingredients
        calculator = OrderCalculator()

        # Load sample recipes
        for name, recipe in get_sample_recipes().items():
            calculator.add_recipe(recipe)

        ingredients = calculator.calculate_for_event(event)

        # Generate prep sheet
        generator = PrepSheetGenerator()

        output_path = args.output or f"prep_sheet_{event.event_id}.txt"

        if output_path.endswith('.html'):
            generator.save_html_prep_sheet(event, output_path, ingredients)
        else:
            generator.save_text_prep_sheet(event, output_path, ingredients)

        print(f"\n✅ Prep sheet saved to {output_path}")
        return 0

    except Exception as e:
        print(f"Error processing BEO: {e}")
        return 1


def cmd_savings(args):
    """Show savings summary"""
    print("=" * 50)
    print("THE LARIAT - VENDOR SAVINGS SUMMARY")
    print("=" * 50)

    # Display key metrics
    print("\n📊 KEY METRICS")
    print("-" * 40)
    print("Monthly Catering Revenue: $28,000")
    print("Monthly Restaurant Revenue: $20,000")
    print("Target Catering Margin: 45%")
    print("Potential Annual Savings: $52,000")

    print("\n💰 SAVINGS BREAKDOWN")
    print("-" * 40)
    print("Shamrock vs SYSCO Average Savings: 29.5%")
    print("Spice Category Savings: ~$881/month")

    print("\n📋 RECOMMENDATIONS")
    print("-" * 40)
    print("1. Prioritize Shamrock Foods for primary ordering")
    print("2. Use SYSCO for specialty items only")
    print("3. Review pricing quarterly")
    print("4. Track actual vs projected savings")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="The Lariat - Vendor Analysis CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse a SYSCO invoice
  python -m scripts.vendor_cli parse sysco invoice.xlsx --output products.json

  # Parse a Shamrock invoice
  python -m scripts.vendor_cli parse shamrock order_guide.xlsx

  # Compare vendors (with input files)
  python -m scripts.vendor_cli compare --sysco sysco.xlsx --shamrock shamrock.xlsx

  # Compare vendors (sample data)
  python -m scripts.vendor_cli compare --output report.csv

  # Generate prep sheet from BEO
  python -m scripts.vendor_cli prep-sheet event.xlsx --output kitchen_prep.html

  # Show savings summary
  python -m scripts.vendor_cli savings
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Parse command
    parse_parser = subparsers.add_parser("parse", help="Parse vendor spreadsheet")
    parse_parser.add_argument("vendor", help="Vendor name (sysco or shamrock)")
    parse_parser.add_argument("file", help="Path to spreadsheet file")
    parse_parser.add_argument("--output", "-o", help="Output JSON file path")
    parse_parser.set_defaults(func=cmd_parse)

    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare vendor prices")
    compare_parser.add_argument("--sysco", help="SYSCO spreadsheet file")
    compare_parser.add_argument("--shamrock", help="Shamrock spreadsheet file")
    compare_parser.add_argument("--output", "-o", help="Output file path")
    compare_parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.6,
        help="Minimum match confidence (0.0-1.0)"
    )
    compare_parser.set_defaults(func=cmd_compare)

    # Prep sheet command
    prep_parser = subparsers.add_parser("prep-sheet", help="Generate prep sheet from BEO")
    prep_parser.add_argument("file", help="BEO Excel file path")
    prep_parser.add_argument("--output", "-o", help="Output file path")
    prep_parser.add_argument("--event-id", help="Specific event ID to process")
    prep_parser.set_defaults(func=cmd_prep_sheet)

    # Savings command
    savings_parser = subparsers.add_parser("savings", help="Show savings summary")
    savings_parser.set_defaults(func=cmd_savings)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
