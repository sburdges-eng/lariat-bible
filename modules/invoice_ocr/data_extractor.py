"""
Invoice Data Extractor
Parses OCR text to extract structured data: dates, items, prices, distributors
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import json


@dataclass
class InvoiceItem:
    """Single line item from invoice"""
    item_code: str
    description: str
    quantity: float
    unit_price: float
    total_price: float
    pack_size: Optional[str] = None
    unit_of_measure: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class InvoiceData:
    """Complete invoice data structure"""
    distributor: str
    invoice_number: str
    order_number: Optional[str]
    invoice_date: Optional[datetime]
    delivery_date: Optional[datetime]
    items: List[InvoiceItem]
    subtotal: Optional[float]
    tax: Optional[float]
    total: Optional[float]
    raw_text: str

    def to_dict(self) -> Dict:
        """Convert to dictionary with serializable dates"""
        data = asdict(self)
        # Convert datetime to ISO format strings
        if self.invoice_date:
            data['invoice_date'] = self.invoice_date.isoformat()
        if self.delivery_date:
            data['delivery_date'] = self.delivery_date.isoformat()
        return data


class InvoiceDataExtractor:
    """Extract structured data from invoice OCR text"""

    # Known distributors and their patterns
    DISTRIBUTORS = {
        'SYSCO': [r'SYSCO', r'SYSCO\s+FOODS?', r'SYSCO\s+CORPORATION'],
        'SHAMROCK': [r'SHAMROCK\s+FOODS?', r'SHAMROCK'],
        'US FOODS': [r'US\s+FOODS?', r'USFOODS'],
        'PERFORMANCE FOOD': [r'PERFORMANCE\s+FOOD\s+GROUP', r'PFG'],
        'GORDON FOOD': [r'GORDON\s+FOOD\s+SERVICE', r'GFS'],
    }

    # Date patterns
    DATE_PATTERNS = [
        r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',  # MM/DD/YYYY or MM-DD-YYYY
        r'\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b',    # YYYY-MM-DD
        r'\b([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4})\b',  # Month DD, YYYY
        r'\b(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})\b',    # DD Month YYYY
    ]

    # Price patterns
    PRICE_PATTERN = r'\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)'

    # Invoice/Order number patterns
    INVOICE_NUMBER_PATTERNS = [
        r'INVOICE\s*#?\s*:?\s*(\w+[-\w]*)',
        r'INV\s*#?\s*:?\s*(\w+[-\w]*)',
        r'INVOICE\s+(?:NO|NUMBER)\s*:?\s*(\w+[-\w]*)',
    ]

    ORDER_NUMBER_PATTERNS = [
        r'ORDER\s*#?\s*:?\s*(\w+[-\w]*)',
        r'PO\s*#?\s*:?\s*(\w+[-\w]*)',
        r'ORDER\s+(?:NO|NUMBER)\s*:?\s*(\w+[-\w]*)',
    ]

    def __init__(self):
        """Initialize the data extractor"""
        pass

    def extract_distributor(self, text: str) -> str:
        """
        Extract distributor name from invoice text

        Args:
            text: OCR extracted text

        Returns:
            Distributor name or 'UNKNOWN'
        """
        text_upper = text.upper()

        for distributor, patterns in self.DISTRIBUTORS.items():
            for pattern in patterns:
                if re.search(pattern, text_upper):
                    return distributor

        return 'UNKNOWN'

    def extract_dates(self, text: str) -> Dict[str, Optional[datetime]]:
        """
        Extract dates from invoice text

        Args:
            text: OCR extracted text

        Returns:
            Dictionary with invoice_date and delivery_date
        """
        dates = {
            'invoice_date': None,
            'delivery_date': None
        }

        # Look for labeled dates first
        invoice_date_match = re.search(
            r'(?:INVOICE\s+DATE|DATE)\s*:?\s*([A-Za-z0-9\s,/-]+)',
            text,
            re.IGNORECASE
        )
        if invoice_date_match:
            dates['invoice_date'] = self._parse_date(invoice_date_match.group(1))

        delivery_date_match = re.search(
            r'(?:DELIVERY\s+DATE|DEL\s+DATE|SHIP\s+DATE)\s*:?\s*([A-Za-z0-9\s,/-]+)',
            text,
            re.IGNORECASE
        )
        if delivery_date_match:
            dates['delivery_date'] = self._parse_date(delivery_date_match.group(1))

        # If no labeled dates, try to find any dates in the text
        if not dates['invoice_date']:
            all_dates = self._find_all_dates(text)
            if all_dates:
                dates['invoice_date'] = all_dates[0]  # Use first found date

        return dates

    def _find_all_dates(self, text: str) -> List[datetime]:
        """Find all dates in text"""
        found_dates = []

        for pattern in self.DATE_PATTERNS:
            matches = re.findall(pattern, text)
            for match in matches:
                parsed_date = self._parse_date(match)
                if parsed_date:
                    found_dates.append(parsed_date)

        return found_dates

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string into datetime object

        Args:
            date_str: Date string

        Returns:
            Datetime object or None
        """
        date_str = date_str.strip()

        # Common date formats to try
        formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%m/%d/%y', '%m-%d-%y',
            '%Y-%m-%d', '%Y/%m/%d',
            '%B %d, %Y', '%b %d, %Y',
            '%d %B %Y', '%d %b %Y',
            '%B %d %Y', '%b %d %Y',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None

    def extract_invoice_number(self, text: str) -> str:
        """Extract invoice number"""
        for pattern in self.INVOICE_NUMBER_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return 'UNKNOWN'

    def extract_order_number(self, text: str) -> Optional[str]:
        """Extract order number"""
        for pattern in self.ORDER_NUMBER_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def extract_line_items(self, text: str) -> List[InvoiceItem]:
        """
        Extract line items from invoice

        Args:
            text: OCR extracted text

        Returns:
            List of InvoiceItem objects
        """
        items = []
        lines = text.split('\n')

        # Pattern for typical invoice line items
        # Matches: ITEM_CODE DESCRIPTION QUANTITY UNIT_PRICE TOTAL
        # Example: "123456 PEPPER BLACK GROUND 6/1# 2 $45.99 $91.98"
        item_patterns = [
            # Pattern 1: Code Description Pack Qty Price Total
            r'(\d{4,8})\s+([A-Z\s&,\(\)]+?)\s+([\d/\.#A-Z\s]+?)\s+(\d+(?:\.\d+)?)\s+\$?(\d+(?:\.\d{2})?)\s+\$?(\d+(?:\.\d{2})?)',
            # Pattern 2: Code Description Qty Price Total
            r'(\d{4,8})\s+([A-Z\s&,\(\)]+?)\s+(\d+(?:\.\d+)?)\s+\$?(\d+(?:\.\d{2})?)\s+\$?(\d+(?:\.\d{2})?)',
            # Pattern 3: Description only with price and total
            r'([A-Z][A-Z\s&,\(\)]{10,}?)\s+(\d+(?:\.\d+)?)\s+\$?(\d+(?:\.\d{2})?)\s+\$?(\d+(?:\.\d{2})?)',
        ]

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Try each pattern
            for pattern in item_patterns:
                match = re.match(pattern, line.upper())
                if match:
                    groups = match.groups()

                    # Parse based on which pattern matched
                    if len(groups) == 6:  # Pattern 1: Code, Desc, Pack, Qty, Price, Total
                        items.append(InvoiceItem(
                            item_code=groups[0],
                            description=groups[1].strip(),
                            pack_size=groups[2].strip(),
                            quantity=float(groups[3]),
                            unit_price=float(groups[4]),
                            total_price=float(groups[5])
                        ))
                    elif len(groups) == 5:  # Pattern 2: Code, Desc, Qty, Price, Total
                        items.append(InvoiceItem(
                            item_code=groups[0],
                            description=groups[1].strip(),
                            quantity=float(groups[2]),
                            unit_price=float(groups[3]),
                            total_price=float(groups[4])
                        ))
                    elif len(groups) == 4:  # Pattern 3: Desc, Qty, Price, Total
                        items.append(InvoiceItem(
                            item_code='',
                            description=groups[0].strip(),
                            quantity=float(groups[1]),
                            unit_price=float(groups[2]),
                            total_price=float(groups[3])
                        ))
                    break

        return items

    def extract_totals(self, text: str) -> Dict[str, Optional[float]]:
        """
        Extract subtotal, tax, and total from invoice

        Args:
            text: OCR extracted text

        Returns:
            Dictionary with subtotal, tax, and total
        """
        totals = {
            'subtotal': None,
            'tax': None,
            'total': None
        }

        # Look for subtotal
        subtotal_match = re.search(
            r'(?:SUB\s*TOTAL|SUBTOTAL)\s*:?\s*\$?\s*([\d,]+\.\d{2})',
            text,
            re.IGNORECASE
        )
        if subtotal_match:
            totals['subtotal'] = float(subtotal_match.group(1).replace(',', ''))

        # Look for tax
        tax_match = re.search(
            r'(?:TAX|SALES\s+TAX)\s*:?\s*\$?\s*([\d,]+\.\d{2})',
            text,
            re.IGNORECASE
        )
        if tax_match:
            totals['tax'] = float(tax_match.group(1).replace(',', ''))

        # Look for total
        total_match = re.search(
            r'(?:TOTAL|INVOICE\s+TOTAL|AMOUNT\s+DUE)\s*:?\s*\$?\s*([\d,]+\.\d{2})',
            text,
            re.IGNORECASE
        )
        if total_match:
            totals['total'] = float(total_match.group(1).replace(',', ''))

        return totals

    def extract_all(self, text: str) -> InvoiceData:
        """
        Extract all data from invoice text

        Args:
            text: OCR extracted text

        Returns:
            InvoiceData object with all extracted information
        """
        # Extract all components
        distributor = self.extract_distributor(text)
        invoice_number = self.extract_invoice_number(text)
        order_number = self.extract_order_number(text)
        dates = self.extract_dates(text)
        items = self.extract_line_items(text)
        totals = self.extract_totals(text)

        # Create InvoiceData object
        invoice_data = InvoiceData(
            distributor=distributor,
            invoice_number=invoice_number,
            order_number=order_number,
            invoice_date=dates['invoice_date'],
            delivery_date=dates['delivery_date'],
            items=items,
            subtotal=totals['subtotal'],
            tax=totals['tax'],
            total=totals['total'],
            raw_text=text
        )

        return invoice_data

    def export_to_json(self, invoice_data: InvoiceData, output_path: str) -> None:
        """
        Export invoice data to JSON file

        Args:
            invoice_data: InvoiceData object
            output_path: Path to save JSON file
        """
        with open(output_path, 'w') as f:
            json.dump(invoice_data.to_dict(), f, indent=2, default=str)

    def export_to_csv(self, invoice_data: InvoiceData, output_path: str) -> None:
        """
        Export invoice line items to CSV file

        Args:
            invoice_data: InvoiceData object
            output_path: Path to save CSV file
        """
        import csv

        with open(output_path, 'w', newline='') as f:
            if not invoice_data.items:
                return

            fieldnames = [
                'distributor', 'invoice_number', 'order_number', 'invoice_date',
                'item_code', 'description', 'pack_size', 'quantity',
                'unit_price', 'total_price'
            ]

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for item in invoice_data.items:
                row = {
                    'distributor': invoice_data.distributor,
                    'invoice_number': invoice_data.invoice_number,
                    'order_number': invoice_data.order_number or '',
                    'invoice_date': invoice_data.invoice_date.strftime('%Y-%m-%d') if invoice_data.invoice_date else '',
                    'item_code': item.item_code,
                    'description': item.description,
                    'pack_size': item.pack_size or '',
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'total_price': item.total_price
                }
                writer.writerow(row)
