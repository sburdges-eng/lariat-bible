"""
BEO Parser Module
Parses Banquet Event Order (BEO) Excel files from BEO-Master format
"""

import re
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from modules.core.models import BanquetEvent, MenuItem, IngredientQuantity

logger = logging.getLogger(__name__)


class BEOParser:
    """Parse BEO (Banquet Event Order) Excel files"""

    def __init__(self):
        self.events: List[BanquetEvent] = []

    def parse_file(
        self,
        file_path: str,
        sheet_name: Optional[str] = None
    ) -> List[BanquetEvent]:
        """
        Parse a BEO Excel file

        Args:
            file_path: Path to the BEO Excel file
            sheet_name: Optional specific sheet name

        Returns:
            List of BanquetEvent objects
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        events = []

        try:
            # Try to read all sheets if no specific sheet given
            if sheet_name:
                sheets = [sheet_name]
            else:
                xl = pd.ExcelFile(file_path)
                sheets = xl.sheet_names

            for sheet in sheets:
                try:
                    event = self._parse_sheet(file_path, sheet)
                    if event:
                        events.append(event)
                except Exception as e:
                    logger.debug(f"Error parsing sheet {sheet}: {e}")
                    continue

            logger.info(f"Parsed {len(events)} events from BEO file")

        except Exception as e:
            logger.error(f"Error reading BEO file: {e}")
            raise

        self.events.extend(events)
        return events

    def _parse_sheet(
        self,
        file_path: str,
        sheet_name: str
    ) -> Optional[BanquetEvent]:
        """
        Parse a single sheet as a BEO

        Expected structure:
        - Event information in header rows
        - Menu items in a table format
        """
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

        if df.empty:
            return None

        # Extract event information from header
        event_info = self._extract_event_info(df)

        if not event_info.get('event_id'):
            # Generate event ID from sheet name
            event_info['event_id'] = sheet_name.replace(' ', '_')[:20]

        # Parse menu items
        menu_items = self._extract_menu_items(df)

        # Create event
        event_date = event_info.get('event_date')
        if isinstance(event_date, str):
            try:
                event_date = datetime.strptime(event_date, '%Y-%m-%d')
            except ValueError:
                try:
                    event_date = datetime.strptime(event_date, '%m/%d/%Y')
                except ValueError:
                    event_date = datetime.now()
        elif not isinstance(event_date, datetime):
            event_date = datetime.now()

        event = BanquetEvent(
            event_id=event_info.get('event_id', ''),
            client_name=event_info.get('client_name', ''),
            event_date=event_date,
            guest_count=int(event_info.get('guest_count', 0)),
            menu_items=menu_items,
            notes=event_info.get('notes', '')
        )

        return event

    def _extract_event_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract event information from the header rows"""
        info = {}

        # Search first 20 rows for event information
        for i, row in df.head(20).iterrows():
            for j, cell in enumerate(row):
                if pd.isna(cell):
                    continue

                cell_str = str(cell).upper()

                # Event ID / BEO Number
                if 'BEO' in cell_str or 'EVENT ID' in cell_str or 'EVENT #' in cell_str:
                    # Value is likely in the next column
                    if j + 1 < len(row):
                        info['event_id'] = str(row.iloc[j + 1])

                # Client name
                if 'CLIENT' in cell_str or 'CUSTOMER' in cell_str or 'NAME' in cell_str:
                    if j + 1 < len(row):
                        info['client_name'] = str(row.iloc[j + 1])

                # Event date
                if 'DATE' in cell_str and 'UPDATE' not in cell_str:
                    if j + 1 < len(row):
                        info['event_date'] = row.iloc[j + 1]

                # Guest count
                if 'GUEST' in cell_str or 'PAX' in cell_str or 'COUNT' in cell_str:
                    if j + 1 < len(row):
                        try:
                            info['guest_count'] = int(float(str(row.iloc[j + 1])))
                        except (ValueError, TypeError):
                            pass

                # Notes
                if 'NOTE' in cell_str or 'SPECIAL' in cell_str:
                    if j + 1 < len(row):
                        info['notes'] = str(row.iloc[j + 1])

        return info

    def _extract_menu_items(self, df: pd.DataFrame) -> List[MenuItem]:
        """Extract menu items from the BEO"""
        items = []

        # Find menu section - look for headers like "MENU", "ITEM", etc.
        menu_start = None
        header_row = None

        for i, row in df.iterrows():
            for cell in row:
                if pd.isna(cell):
                    continue
                cell_str = str(cell).upper()
                if 'MENU' in cell_str or 'ITEM' in cell_str:
                    menu_start = i + 1
                    header_row = i
                    break
            if menu_start:
                break

        if menu_start is None:
            # Try to find any table structure
            return items

        # Get column headers
        headers = df.iloc[header_row].tolist()
        headers = [str(h).upper() if not pd.isna(h) else '' for h in headers]

        # Find relevant columns
        item_col = None
        qty_col = None
        price_col = None

        for i, h in enumerate(headers):
            if 'ITEM' in h or 'MENU' in h or 'NAME' in h or 'DESCRIPTION' in h:
                item_col = i
            elif 'QTY' in h or 'QUANTITY' in h or 'COUNT' in h:
                qty_col = i
            elif 'PRICE' in h or 'COST' in h:
                price_col = i

        if item_col is None:
            return items

        # Parse menu items
        for i in range(menu_start, min(menu_start + 50, len(df))):
            row = df.iloc[i]

            item_name = row.iloc[item_col] if item_col < len(row) else None
            if pd.isna(item_name) or not str(item_name).strip():
                continue

            item_name = str(item_name).strip()

            # Skip if it looks like a header or section
            if item_name.upper() in ['TOTAL', 'SUBTOTAL', 'TAX', 'GRATUITY']:
                continue

            quantity = 1
            if qty_col is not None and qty_col < len(row):
                try:
                    quantity = int(float(str(row.iloc[qty_col])))
                except (ValueError, TypeError):
                    quantity = 1

            unit_price = 0.0
            if price_col is not None and price_col < len(row):
                try:
                    price_str = str(row.iloc[price_col]).replace('$', '').replace(',', '')
                    unit_price = float(price_str)
                except (ValueError, TypeError):
                    unit_price = 0.0

            item = MenuItem(
                name=item_name,
                quantity=quantity,
                unit_price=unit_price
            )
            items.append(item)

        return items

    def get_event_by_id(self, event_id: str) -> Optional[BanquetEvent]:
        """Get a parsed event by its ID"""
        for event in self.events:
            if event.event_id == event_id:
                return event
        return None

    def clear(self):
        """Clear all parsed events"""
        self.events = []
