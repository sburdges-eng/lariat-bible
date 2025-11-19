#!/usr/bin/env python3
"""
Invoice Photo Processing Script
Analyzes invoice photos and extracts dates, items, prices, and distributor information
"""

import os
import sys
from pathlib import Path
from typing import List
import argparse
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from invoice_ocr.invoice_processor import InvoiceProcessor
from invoice_ocr.data_extractor import InvoiceDataExtractor

console = Console()


def find_invoice_images(directory: str) -> List[str]:
    """
    Find all image files in a directory

    Args:
        directory: Path to directory containing invoice images

    Returns:
        List of image file paths
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    image_paths = []

    path = Path(directory)
    if not path.exists():
        console.print(f"[red]Error: Directory not found: {directory}[/red]")
        return []

    for file_path in path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            image_paths.append(str(file_path))

    return sorted(image_paths)


def process_single_invoice(image_path: str, output_dir: str = None) -> None:
    """
    Process a single invoice image

    Args:
        image_path: Path to invoice image
        output_dir: Optional directory to save results
    """
    console.print(f"\n[bold cyan]Processing:[/bold cyan] {image_path}")

    # Initialize processors
    processor = InvoiceProcessor()
    extractor = InvoiceDataExtractor()

    try:
        # Step 1: OCR text extraction
        console.print("[yellow]Step 1:[/yellow] Extracting text from image...")
        ocr_result = processor.process_invoice(image_path)

        console.print(f"  ✓ Extracted {len(ocr_result['raw_text'])} characters")
        console.print(f"  ✓ Confidence: {ocr_result['average_confidence']:.1f}%")

        # Step 2: Data extraction
        console.print("[yellow]Step 2:[/yellow] Extracting structured data...")
        invoice_data = extractor.extract_all(ocr_result['raw_text'])

        # Display results
        console.print("\n[bold green]═══ EXTRACTED INVOICE DATA ═══[/bold green]\n")

        # Basic info
        info_table = Table(show_header=False, box=None)
        info_table.add_row("[cyan]Distributor:[/cyan]", f"[white]{invoice_data.distributor}[/white]")
        info_table.add_row("[cyan]Invoice Number:[/cyan]", f"[white]{invoice_data.invoice_number}[/white]")
        if invoice_data.order_number:
            info_table.add_row("[cyan]Order Number:[/cyan]", f"[white]{invoice_data.order_number}[/white]")
        if invoice_data.invoice_date:
            info_table.add_row("[cyan]Invoice Date:[/cyan]", f"[white]{invoice_data.invoice_date.strftime('%Y-%m-%d')}[/white]")
        if invoice_data.delivery_date:
            info_table.add_row("[cyan]Delivery Date:[/cyan]", f"[white]{invoice_data.delivery_date.strftime('%Y-%m-%d')}[/white]")

        console.print(info_table)

        # Line items
        if invoice_data.items:
            console.print(f"\n[bold]Line Items:[/bold] ({len(invoice_data.items)} items found)\n")

            items_table = Table(show_header=True)
            items_table.add_column("Code", style="cyan")
            items_table.add_column("Description", style="white")
            items_table.add_column("Pack", style="yellow")
            items_table.add_column("Qty", justify="right", style="magenta")
            items_table.add_column("Unit Price", justify="right", style="green")
            items_table.add_column("Total", justify="right", style="bold green")

            for item in invoice_data.items:
                items_table.add_row(
                    item.item_code[:10],
                    item.description[:40],
                    item.pack_size or '-',
                    f"{item.quantity:.1f}",
                    f"${item.unit_price:.2f}",
                    f"${item.total_price:.2f}"
                )

            console.print(items_table)
        else:
            console.print("\n[yellow]⚠ No line items extracted[/yellow]")

        # Totals
        if invoice_data.subtotal or invoice_data.tax or invoice_data.total:
            console.print("\n[bold]Totals:[/bold]")
            totals_table = Table(show_header=False, box=None)
            if invoice_data.subtotal:
                totals_table.add_row("Subtotal:", f"${invoice_data.subtotal:,.2f}")
            if invoice_data.tax:
                totals_table.add_row("Tax:", f"${invoice_data.tax:,.2f}")
            if invoice_data.total:
                totals_table.add_row("[bold]Total:[/bold]", f"[bold]${invoice_data.total:,.2f}[/bold]")
            console.print(totals_table)

        # Save results if output directory specified
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Generate filename from invoice
            base_name = Path(image_path).stem
            json_file = output_path / f"{base_name}_data.json"
            csv_file = output_path / f"{base_name}_items.csv"

            # Save JSON
            extractor.export_to_json(invoice_data, str(json_file))
            console.print(f"\n[green]✓ Saved JSON:[/green] {json_file}")

            # Save CSV
            if invoice_data.items:
                extractor.export_to_csv(invoice_data, str(csv_file))
                console.print(f"[green]✓ Saved CSV:[/green] {csv_file}")

    except Exception as e:
        console.print(f"[red]✗ Error processing invoice:[/red] {str(e)}")
        import traceback
        traceback.print_exc()


def process_batch(directory: str, output_dir: str = None) -> None:
    """
    Process all invoices in a directory

    Args:
        directory: Directory containing invoice images
        output_dir: Directory to save results
    """
    console.print(f"\n[bold]Scanning directory:[/bold] {directory}")

    # Find all images
    image_paths = find_invoice_images(directory)

    if not image_paths:
        console.print("[yellow]No invoice images found.[/yellow]")
        return

    console.print(f"[green]Found {len(image_paths)} invoice image(s)[/green]")

    # Process each invoice
    with Progress() as progress:
        task = progress.add_task("[cyan]Processing invoices...", total=len(image_paths))

        for image_path in image_paths:
            process_single_invoice(image_path, output_dir)
            progress.advance(task)

    console.print("\n[bold green]✓ Batch processing complete![/bold green]")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Process invoice photos and extract data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single invoice
  python process_invoices.py -i data/invoices/sysco_invoice.jpg

  # Process all invoices in a directory
  python process_invoices.py -d data/invoices/

  # Process and save results
  python process_invoices.py -d data/invoices/ -o data/processed/

  # Process with custom tesseract path (Windows example)
  python process_invoices.py -i invoice.jpg --tesseract "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
        """
    )

    parser.add_argument('-i', '--image', help='Path to single invoice image')
    parser.add_argument('-d', '--directory', help='Directory containing invoice images')
    parser.add_argument('-o', '--output', help='Output directory for extracted data')
    parser.add_argument('--tesseract', help='Path to tesseract executable (if not in PATH)')

    args = parser.parse_args()

    # Validate arguments
    if not args.image and not args.directory:
        parser.print_help()
        console.print("\n[red]Error: Please specify either -i/--image or -d/--directory[/red]")
        sys.exit(1)

    # Set tesseract path if provided
    if args.tesseract:
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = args.tesseract

    # Print header
    console.print("\n[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]   THE LARIAT - Invoice Photo Processor   [/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════[/bold cyan]\n")

    # Process invoices
    if args.image:
        process_single_invoice(args.image, args.output)
    elif args.directory:
        process_batch(args.directory, args.output)


if __name__ == "__main__":
    main()
