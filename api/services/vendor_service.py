"""
Vendor Service
===============
Manages vendor file parsing and matching.
"""

import csv
import io
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
import re


class VendorService:
    """
    Service for vendor file processing and matching.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.sysco_products: List[Dict] = []
        self.shamrock_products: List[Dict] = []
        self.matches: List[Dict] = []
        self._initialized = True

    def parse_vendor_file(self, content: bytes, vendor: str) -> Dict:
        """
        Parse vendor file (CSV or Excel).

        Returns dict with items and metadata.
        """
        try:
            # Decode and parse CSV
            text = content.decode('utf-8-sig')
            reader = csv.DictReader(io.StringIO(text))

            items = []
            for row in reader:
                item = self._parse_vendor_row(row, vendor)
                if item:
                    items.append(item)

            # Store in service
            if vendor.upper() == 'SYSCO':
                self.sysco_products = items
            else:
                self.shamrock_products = items

            return {
                'vendor': vendor,
                'items': items,
                'count': len(items),
                'success': True
            }

        except Exception as e:
            return {
                'vendor': vendor,
                'items': [],
                'count': 0,
                'success': False,
                'error': str(e)
            }

    def _parse_vendor_row(self, row: Dict, vendor: str) -> Optional[Dict]:
        """Parse a single vendor row"""
        # Try to extract common fields
        item = {
            'vendor': vendor,
            'item_code': '',
            'description': '',
            'pack_size': '',
            'price': 0.0,
            'category': '',
            'brand': ''
        }

        # SYSCO format
        if vendor.upper() == 'SYSCO':
            item['item_code'] = row.get('SUPC', row.get('Item', row.get('item_code', '')))
            item['description'] = row.get('Description', row.get('Item Description', row.get('description', '')))
            item['pack_size'] = row.get('Pack', row.get('Pack Size', row.get('pack_size', '')))
            price_str = row.get('Price', row.get('Unit Price', row.get('price', '0')))
            item['brand'] = row.get('Brand', '')
            item['category'] = row.get('Category', '')

        # Shamrock format
        else:
            item['item_code'] = row.get('Item #', row.get('Item', row.get('item_code', '')))
            item['description'] = row.get('Description', row.get('Item Description', row.get('description', '')))
            item['pack_size'] = row.get('Pack/Size', row.get('Pack Size', row.get('pack_size', '')))
            price_str = row.get('Price', row.get('Each Price', row.get('price', '0')))
            item['brand'] = row.get('Brand', '')
            item['category'] = row.get('Category', '')

        # Parse price
        try:
            price_str = str(price_str).replace('$', '').replace(',', '').strip()
            item['price'] = float(price_str) if price_str else 0.0
        except:
            item['price'] = 0.0

        # Skip empty rows
        if not item['description']:
            return None

        return item

    def run_matching(self) -> Dict:
        """
        Match products between SYSCO and Shamrock.

        Returns match results with savings analysis.
        """
        if not self.sysco_products or not self.shamrock_products:
            return {
                'success': False,
                'error': 'Both vendor files must be uploaded first',
                'matches': []
            }

        matches = []

        # For each Shamrock product, try to find SYSCO match
        for shamrock in self.shamrock_products:
            best_match = self._find_best_match(shamrock, self.sysco_products)

            if best_match:
                sysco, score, confidence = best_match

                savings = sysco['price'] - shamrock['price']
                savings_pct = (savings / sysco['price'] * 100) if sysco['price'] > 0 else 0

                matches.append({
                    'id': len(matches) + 1,
                    'item': shamrock['description'][:50],
                    'shamrock_code': shamrock['item_code'],
                    'shamrock_price': shamrock['price'],
                    'shamrock_pack': shamrock['pack_size'],
                    'sysco_code': sysco['item_code'],
                    'sysco_price': sysco['price'],
                    'sysco_pack': sysco['pack_size'],
                    'savings': round(savings, 2),
                    'savings_pct': round(savings_pct, 1),
                    'confidence': confidence,
                    'match_score': score
                })

        self.matches = matches

        # Calculate summary
        total_savings = sum(m['savings'] for m in matches if m['savings'] > 0)
        high_confidence = sum(1 for m in matches if m['confidence'] == 'high')

        return {
            'success': True,
            'matches': matches,
            'summary': {
                'total_matches': len(matches),
                'high_confidence': high_confidence,
                'total_savings': round(total_savings, 2),
                'avg_savings': round(total_savings / len(matches), 2) if matches else 0
            }
        }

    def _find_best_match(
        self,
        product: Dict,
        candidates: List[Dict]
    ) -> Optional[Tuple[Dict, float, str]]:
        """Find best matching product from candidates"""
        best_score = 0
        best_match = None

        product_words = self._tokenize(product['description'])

        for candidate in candidates:
            candidate_words = self._tokenize(candidate['description'])

            # Calculate word overlap score
            if not product_words:
                continue

            common = product_words & candidate_words
            score = len(common) / max(len(product_words), len(candidate_words))

            # Boost score if brand matches
            if product.get('brand') and candidate.get('brand'):
                if product['brand'].lower() == candidate['brand'].lower():
                    score += 0.2

            if score > best_score:
                best_score = score
                best_match = candidate

        if best_match and best_score > 0.3:
            confidence = 'high' if best_score > 0.7 else 'medium' if best_score > 0.5 else 'low'
            return (best_match, best_score, confidence)

        return None

    def _tokenize(self, text: str) -> set:
        """Tokenize text into normalized words"""
        if not text:
            return set()

        # Lowercase and remove punctuation
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)

        # Split and filter short words
        words = text.split()
        words = [w for w in words if len(w) > 2]

        return set(words)

    def get_matches(self) -> List[Dict]:
        """Get current matches"""
        return self.matches

    def export_matches_csv(self) -> str:
        """Export matches to CSV string"""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            'Item', 'Shamrock Code', 'Shamrock Price', 'Shamrock Pack',
            'SYSCO Code', 'SYSCO Price', 'SYSCO Pack',
            'Savings', 'Savings %', 'Confidence'
        ])

        # Data
        for m in self.matches:
            writer.writerow([
                m['item'],
                m['shamrock_code'],
                f"${m['shamrock_price']:.2f}",
                m['shamrock_pack'],
                m['sysco_code'],
                f"${m['sysco_price']:.2f}",
                m['sysco_pack'],
                f"${m['savings']:.2f}",
                f"{m['savings_pct']:.1f}%",
                m['confidence']
            ])

        return output.getvalue()

    def get_comparison_summary(self) -> Dict:
        """Get vendor comparison summary"""
        if not self.matches:
            return {
                'sysco_items': len(self.sysco_products),
                'shamrock_items': len(self.shamrock_products),
                'matches': 0,
                'total_savings': 0,
                'message': 'Run matching to see comparison'
            }

        total_savings = sum(m['savings'] for m in self.matches if m['savings'] > 0)

        return {
            'sysco_items': len(self.sysco_products),
            'shamrock_items': len(self.shamrock_products),
            'matches': len(self.matches),
            'total_savings': round(total_savings, 2),
            'annual_savings': round(total_savings * 12, 2),
            'high_confidence_matches': sum(1 for m in self.matches if m['confidence'] == 'high')
        }
