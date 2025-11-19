#!/usr/bin/env python3
"""
Invoice OCR Example
Demonstrates how to use the invoice processing system
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))

from invoice_ocr import InvoiceProcessor, InvoiceDataExtractor
from rich.console import Console
from rich.table import Table
from rich import print as rprint

console = Console()


def example_basic_usage():
    """Example 1: Basic invoice processing"""
    console.print("\n[bold cyan]Example 1: Basic Invoice Processing[/bold cyan]\n")

    # Initialize processors
    processor = InvoiceProcessor()
    extractor = InvoiceDataExtractor()

    # Sample OCR text (simulating what would come from an invoice photo)
    sample_invoice_text = """
    SYSCO CORPORATION
    Invoice #: INV-2024-12345
    Order #: PO-98765
    Invoice Date: 11/18/2024
    Delivery Date: 11/19/2024

    Item Code    Description              Pack      Qty    Unit Price    Total
    -------------------------------------------------------------------------
    123456       PEPPER BLACK GROUND      6/1#      2      $45.99        $91.98
    234567       SALT KOSHER              25 LB     1      $12.50        $12.50
    345678       TOMATO PASTE             6/#10     3      $28.75        $86.25
    456789       OLIVE OIL EXTRA VIRGIN   4/1 GAL   2      $67.00        $134.00

    SUBTOTAL:  $324.73
    TAX:       $25.98
    TOTAL:     $350.71
    """

    # Extract data
    invoice_data = extractor.extract_all(sample_invoice_text)

    # Display results
    console.print(f"[green]✓ Distributor:[/green] {invoice_data.distributor}")
    console.print(f"[green]✓ Invoice #:[/green] {invoice_data.invoice_number}")
    console.print(f"[green]✓ Order #:[/green] {invoice_data.order_number}")

    if invoice_data.invoice_date:
        console.print(f"[green]✓ Invoice Date:[/green] {invoice_data.invoice_date.strftime('%Y-%m-%d')}")

    console.print(f"\n[yellow]Found {len(invoice_data.items)} line items[/yellow]")

    return invoice_data


def example_export_data(invoice_data):
    """Example 2: Exporting data to JSON and CSV"""
    console.print("\n[bold cyan]Example 2: Exporting Data[/bold cyan]\n")

    extractor = InvoiceDataExtractor()

    # Create output directory
    import os
    os.makedirs('examples/output', exist_ok=True)

    # Export to JSON
    json_path = 'examples/output/sample_invoice.json'
    extractor.export_to_json(invoice_data, json_path)
    console.print(f"[green]✓ Exported to JSON:[/green] {json_path}")

    # Export to CSV
    csv_path = 'examples/output/sample_invoice.csv'
    extractor.export_to_csv(invoice_data, csv_path)
    console.print(f"[green]✓ Exported to CSV:[/green] {csv_path}")

    # Display JSON preview
    import json
    with open(json_path, 'r') as f:
        data = json.load(f)

    console.print("\n[yellow]JSON Preview:[/yellow]")
    console.print(json.dumps({k: v for k, v in data.items() if k != 'raw_text' and k != 'items'}, indent=2))


def example_data_analysis(invoice_data):
    """Example 3: Analyzing invoice data"""
    console.print("\n[bold cyan]Example 3: Data Analysis[/bold cyan]\n")

    # Calculate statistics
    if invoice_data.items:
        total_items = len(invoice_data.items)
        total_quantity = sum(item.quantity for item in invoice_data.items)
        avg_price = sum(item.total_price for item in invoice_data.items) / total_items

        stats_table = Table(title="Invoice Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")

        stats_table.add_row("Total Items", str(total_items))
        stats_table.add_row("Total Quantity", f"{total_quantity:.1f}")
        stats_table.add_row("Average Item Price", f"${avg_price:.2f}")

        if invoice_data.total:
            stats_table.add_row("Invoice Total", f"${invoice_data.total:,.2f}")

        console.print(stats_table)

        # Find most expensive item
        most_expensive = max(invoice_data.items, key=lambda x: x.total_price)
        console.print(f"\n[yellow]Most Expensive Item:[/yellow] {most_expensive.description} (${most_expensive.total_price:.2f})")


def example_batch_comparison():
    """Example 4: Comparing multiple invoices"""
    console.print("\n[bold cyan]Example 4: Multi-Vendor Comparison[/bold cyan]\n")

    extractor = InvoiceDataExtractor()

    # Sample SYSCO invoice
    sysco_text = """
    SYSCO CORPORATION
    Invoice #: INV-001
    Date: 11/18/2024

    123456 PEPPER BLACK GROUND 6/1# 2 $45.99 $91.98
    234567 SALT KOSHER 25 LB 1 $12.50 $12.50

    TOTAL: $104.48
    """

    # Sample Shamrock invoice
    shamrock_text = """
    SHAMROCK FOODS
    Invoice #: SF-002
    Date: 11/18/2024

    789012 PEPPER BLACK GROUND 25 LB 1 $79.71 $79.71
    890123 SALT KOSHER 25 LB 1 $9.85 $9.85

    TOTAL: $89.56
    """

    # Process both
    sysco_data = extractor.extract_all(sysco_text)
    shamrock_data = extractor.extract_all(shamrock_text)

    # Compare
    comparison_table = Table(title="Vendor Comparison")
    comparison_table.add_column("Metric", style="cyan")
    comparison_table.add_column("SYSCO", style="yellow")
    comparison_table.add_column("Shamrock", style="green")

    comparison_table.add_row(
        "Total Items",
        str(len(sysco_data.items)),
        str(len(shamrock_data.items))
    )

    comparison_table.add_row(
        "Invoice Total",
        f"${sysco_data.total:.2f}" if sysco_data.total else "N/A",
        f"${shamrock_data.total:.2f}" if shamrock_data.total else "N/A"
    )

    console.print(comparison_table)

    # Show potential savings
    if sysco_data.total and shamrock_data.total:
        savings = abs(sysco_data.total - shamrock_data.total)
        cheaper = "Shamrock" if shamrock_data.total < sysco_data.total else "SYSCO"
        console.print(f"\n[green]💰 Potential Savings:[/green] ${savings:.2f} with {cheaper}")


def example_distributor_detection():
    """Example 5: Testing distributor detection"""
    console.print("\n[bold cyan]Example 5: Distributor Detection[/bold cyan]\n")

    extractor = InvoiceDataExtractor()

    test_cases = [
        ("SYSCO CORPORATION\nInvoice 12345", "SYSCO"),
        ("Shamrock Foods Company\nOrder Confirmation", "SHAMROCK"),
        ("US Foods Inc.\nInvoice", "US FOODS"),
        ("Performance Food Group\nPO# 999", "PERFORMANCE FOOD"),
        ("Local Vendor\nInvoice", "UNKNOWN"),
    ]

    results_table = Table(title="Distributor Detection Test")
    results_table.add_column("Sample Text", style="cyan")
    results_table.add_column("Detected", style="green")

    for text, expected in test_cases:
        detected = extractor.extract_distributor(text)
        status = "✓" if detected == expected else "✗"
        results_table.add_row(
            text.split('\n')[0][:30],
            f"{status} {detected}"
        )

    console.print(results_table)


def main():
    """Run all examples"""
    console.print("\n[bold white on blue] THE LARIAT - Invoice OCR Examples [/bold white on blue]\n")

    # Run examples
    invoice_data = example_basic_usage()
    example_export_data(invoice_data)
    example_data_analysis(invoice_data)
    example_batch_comparison()
    example_distributor_detection()

    console.print("\n[bold green]✓ All examples completed![/bold green]\n")
    console.print("[yellow]Next steps:[/yellow]")
    console.print("  1. Take photos of your invoices")
    console.print("  2. Run: python process_invoices.py -i your_invoice.jpg")
    console.print("  3. Review extracted data and exports")
    console.print("\n[cyan]See INVOICE_OCR_GUIDE.md for complete documentation[/cyan]\n")


if __name__ == "__main__":
    main()
