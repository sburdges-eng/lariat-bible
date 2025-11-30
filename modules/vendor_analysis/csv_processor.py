"""
Vendor CSV Processor
Handles uploading and combining original vendor CSVs from Shamrock and Sysco.
Generates Excel workbooks with price comparison sheets.
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import os


class VendorCSVProcessor:
    """
    Process and combine vendor CSVs from Shamrock Foods and Sysco.
    Generates comparison Excel workbooks with multiple sheets.
    """
    
    def __init__(self, output_dir: str = "./data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.shamrock_data: Optional[pd.DataFrame] = None
        self.sysco_data: Optional[pd.DataFrame] = None
        self.combined_data: Optional[pd.DataFrame] = None
        
        # Standard column mappings for each vendor
        self.shamrock_columns = {
            'item_code': ['item_code', 'code', 'sku', 'product_code', 'item #', 'item_#'],
            'description': ['description', 'item_description', 'product', 'name', 'item'],
            'pack_size': ['pack_size', 'pack', 'size', 'pack size', 'unit'],
            'price': ['price', 'case_price', 'cost', 'unit_price', 'amount'],
            'category': ['category', 'type', 'class']
        }
        
        self.sysco_columns = {
            'item_code': ['item_code', 'code', 'sku', 'product_code', 'item #', 'item_#', 'supc'],
            'description': ['description', 'item_description', 'product', 'name', 'item', 'product_description'],
            'pack_size': ['pack_size', 'pack', 'size', 'pack size', 'unit'],
            'price': ['price', 'case_price', 'cost', 'unit_price', 'amount'],
            'category': ['category', 'type', 'class']
        }
    
    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Find matching column name from list of possibilities."""
        df_columns_lower = {col.lower().strip(): col for col in df.columns}
        
        for name in possible_names:
            if name.lower() in df_columns_lower:
                return df_columns_lower[name.lower()]
        return None
    
    def _normalize_columns(self, df: pd.DataFrame, column_mapping: Dict[str, List[str]]) -> pd.DataFrame:
        """Normalize column names to standard format."""
        normalized = pd.DataFrame()
        
        for standard_name, possible_names in column_mapping.items():
            found_col = self._find_column(df, possible_names)
            if found_col:
                normalized[standard_name] = df[found_col]
            else:
                normalized[standard_name] = None
        
        return normalized
    
    def _parse_pack_size(self, pack_str: str) -> Optional[float]:
        """
        Parse total pounds/units from pack string.
        Handles formats like:
        - Shamrock: 1/6/LB, 25 LB
        - Sysco: 3/6LB, 6/1LB, 25 LB
        """
        if pd.isna(pack_str):
            return None
            
        pack_str = str(pack_str).upper().strip()
        
        # Shamrock format: 1/6/LB = 1 container × 6 lbs
        if '/LB' in pack_str:
            parts = pack_str.replace('/LB', '').split('/')
            if len(parts) == 2:
                try:
                    return float(parts[0]) * float(parts[1])
                except ValueError:
                    pass
        
        # Sysco format: 3/6LB or 6/1LB = containers × pounds each
        if 'LB' in pack_str and '/' in pack_str:
            parts = pack_str.replace('LB', '').replace('#', '').split('/')
            if len(parts) == 2:
                try:
                    return float(parts[0]) * float(parts[1])
                except ValueError:
                    pass
        
        # Simple: 25 LB
        if 'LB' in pack_str:
            match = re.search(r'(\d+\.?\d*)\s*LB', pack_str)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    pass
        
        # Handle # sign for pounds: 25#, 10#
        if '#' in pack_str:
            match = re.search(r'(\d+\.?\d*)\s*#', pack_str)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    pass
        
        return None
    
    def _normalize_description(self, desc: str) -> str:
        """Normalize product description for matching."""
        if pd.isna(desc):
            return ""
        
        desc = str(desc).upper()
        # Remove common abbreviations and standardize
        replacements = {
            'BNLS': 'BONELESS',
            'BNL': 'BONELESS',
            'SKLS': 'SKINLESS',
            'SKL': 'SKINLESS',
            'FRSH': 'FRESH',
            'FRZ': 'FROZEN',
            'FRZN': 'FROZEN',
            'GRD': 'GROUND',
            'GRND': 'GROUND',
            'PWD': 'POWDER',
            'PWDR': 'POWDER',
            'GRAN': 'GRANULATED',
            'BLK': 'BLACK',
            'WHT': 'WHITE',
            'CHKN': 'CHICKEN',
            'TKY': 'TURKEY',
        }
        
        for abbrev, full in replacements.items():
            desc = re.sub(rf'\b{abbrev}\b', full, desc)
        
        # Remove extra whitespace
        desc = ' '.join(desc.split())
        return desc
    
    def load_shamrock_csv(self, file_path: str) -> pd.DataFrame:
        """Load and normalize Shamrock Foods CSV."""
        df = pd.read_csv(file_path)
        normalized = self._normalize_columns(df, self.shamrock_columns)
        
        # Add vendor identifier
        normalized['vendor'] = 'Shamrock'
        
        # Parse pack size to pounds
        normalized['total_pounds'] = normalized['pack_size'].apply(self._parse_pack_size)
        
        # Calculate price per pound
        normalized['price_per_lb'] = np.where(
            normalized['total_pounds'] > 0,
            normalized['price'] / normalized['total_pounds'],
            None
        )
        
        # Normalize descriptions for matching
        normalized['normalized_desc'] = normalized['description'].apply(self._normalize_description)
        
        self.shamrock_data = normalized
        return normalized
    
    def load_sysco_csv(self, file_path: str) -> pd.DataFrame:
        """Load and normalize Sysco CSV."""
        df = pd.read_csv(file_path)
        normalized = self._normalize_columns(df, self.sysco_columns)
        
        # Add vendor identifier
        normalized['vendor'] = 'Sysco'
        
        # Parse pack size to pounds
        normalized['total_pounds'] = normalized['pack_size'].apply(self._parse_pack_size)
        
        # Calculate price per pound
        normalized['price_per_lb'] = np.where(
            normalized['total_pounds'] > 0,
            normalized['price'] / normalized['total_pounds'],
            None
        )
        
        # Normalize descriptions for matching
        normalized['normalized_desc'] = normalized['description'].apply(self._normalize_description)
        
        self.sysco_data = normalized
        return normalized
    
    def load_shamrock_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Load Shamrock data from a DataFrame (for API use)."""
        normalized = self._normalize_columns(df, self.shamrock_columns)
        normalized['vendor'] = 'Shamrock'
        normalized['total_pounds'] = normalized['pack_size'].apply(self._parse_pack_size)
        normalized['price_per_lb'] = np.where(
            normalized['total_pounds'] > 0,
            normalized['price'] / normalized['total_pounds'],
            None
        )
        normalized['normalized_desc'] = normalized['description'].apply(self._normalize_description)
        self.shamrock_data = normalized
        return normalized
    
    def load_sysco_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Load Sysco data from a DataFrame (for API use)."""
        normalized = self._normalize_columns(df, self.sysco_columns)
        normalized['vendor'] = 'Sysco'
        normalized['total_pounds'] = normalized['pack_size'].apply(self._parse_pack_size)
        normalized['price_per_lb'] = np.where(
            normalized['total_pounds'] > 0,
            normalized['price'] / normalized['total_pounds'],
            None
        )
        normalized['normalized_desc'] = normalized['description'].apply(self._normalize_description)
        self.sysco_data = normalized
        return normalized
    
    def _match_products(self, threshold: float = 0.6) -> pd.DataFrame:
        """
        Match products between Shamrock and Sysco based on description similarity.
        Uses word overlap for matching.
        """
        if self.shamrock_data is None or self.sysco_data is None:
            raise ValueError("Both Shamrock and Sysco data must be loaded first.")
        
        matches = []
        
        for _, sham_row in self.shamrock_data.iterrows():
            sham_desc = sham_row['normalized_desc']
            if not sham_desc:
                continue
            
            sham_words = set(sham_desc.split())
            
            best_match = None
            best_score = 0
            
            for _, sys_row in self.sysco_data.iterrows():
                sys_desc = sys_row['normalized_desc']
                if not sys_desc:
                    continue
                
                sys_words = set(sys_desc.split())
                
                # Calculate Jaccard similarity
                intersection = len(sham_words & sys_words)
                union = len(sham_words | sys_words)
                
                if union > 0:
                    similarity = intersection / union
                    
                    if similarity > best_score and similarity >= threshold:
                        best_score = similarity
                        best_match = sys_row
            
            if best_match is not None:
                matches.append({
                    'shamrock_code': sham_row['item_code'],
                    'shamrock_description': sham_row['description'],
                    'shamrock_pack_size': sham_row['pack_size'],
                    'shamrock_price': sham_row['price'],
                    'shamrock_price_per_lb': sham_row['price_per_lb'],
                    'sysco_code': best_match['item_code'],
                    'sysco_description': best_match['description'],
                    'sysco_pack_size': best_match['pack_size'],
                    'sysco_price': best_match['price'],
                    'sysco_price_per_lb': best_match['price_per_lb'],
                    'match_score': best_score,
                    'category': sham_row.get('category') or best_match.get('category')
                })
        
        return pd.DataFrame(matches)
    
    def combine_vendor_data(self, match_threshold: float = 0.6) -> pd.DataFrame:
        """
        Combine and match vendor data, calculating savings.
        """
        if self.shamrock_data is None or self.sysco_data is None:
            raise ValueError("Both vendor CSVs must be loaded first.")
        
        matched = self._match_products(threshold=match_threshold)
        
        if matched.empty:
            return matched
        
        # Calculate savings
        matched['savings_per_lb'] = matched['sysco_price_per_lb'] - matched['shamrock_price_per_lb']
        matched['savings_percent'] = np.where(
            matched['sysco_price_per_lb'] > 0,
            (matched['savings_per_lb'] / matched['sysco_price_per_lb']) * 100,
            0
        )
        
        # Determine cheaper vendor
        matched['cheaper_vendor'] = np.where(
            matched['shamrock_price_per_lb'] < matched['sysco_price_per_lb'],
            'Shamrock',
            np.where(
                matched['sysco_price_per_lb'] < matched['shamrock_price_per_lb'],
                'Sysco',
                'Same'
            )
        )
        
        # Best price
        matched['best_price_per_lb'] = matched[['shamrock_price_per_lb', 'sysco_price_per_lb']].min(axis=1)
        
        self.combined_data = matched
        return matched
    
    def generate_comparison_excel(self, output_filename: str = None) -> str:
        """
        Generate Excel workbook with multiple comparison sheets:
        - Sheet 1: Best prices (cheaper option for each product)
        - Sheet 2: Shamrock more expensive
        - Sheet 3: Sysco more expensive
        - Sheet 4: All matched products
        - Sheet 5: Summary statistics
        """
        if self.combined_data is None:
            self.combine_vendor_data()
        
        if self.combined_data is None or self.combined_data.empty:
            raise ValueError("No matched products to generate report.")
        
        if output_filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"vendor_comparison_{timestamp}.xlsx"
        
        output_path = self.output_dir / output_filename
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Sheet 1: Best Prices (cheaper option)
            best_prices = self.combined_data[[
                'shamrock_description',
                'cheaper_vendor',
                'best_price_per_lb',
                'shamrock_price_per_lb',
                'sysco_price_per_lb',
                'savings_per_lb',
                'savings_percent',
                'shamrock_pack_size',
                'sysco_pack_size',
                'category'
            ]].copy()
            best_prices.columns = [
                'Product',
                'Cheaper Vendor',
                'Best Price/LB',
                'Shamrock Price/LB',
                'Sysco Price/LB',
                'Savings/LB',
                'Savings %',
                'Shamrock Pack',
                'Sysco Pack',
                'Category'
            ]
            best_prices = best_prices.sort_values('Savings %', ascending=False)
            best_prices.to_excel(writer, sheet_name='Best Prices', index=False)
            
            # Sheet 2: Shamrock More Expensive
            shamrock_expensive = self.combined_data[
                self.combined_data['cheaper_vendor'] == 'Sysco'
            ][[
                'shamrock_description',
                'shamrock_price_per_lb',
                'sysco_price_per_lb',
                'savings_per_lb',
                'savings_percent',
                'shamrock_pack_size',
                'sysco_pack_size',
                'category'
            ]].copy()
            shamrock_expensive.columns = [
                'Product',
                'Shamrock Price/LB',
                'Sysco Price/LB',
                'Difference/LB',
                'Difference %',
                'Shamrock Pack',
                'Sysco Pack',
                'Category'
            ]
            # Invert the sign for Shamrock expensive items
            shamrock_expensive['Difference/LB'] = shamrock_expensive['Difference/LB'].abs()
            shamrock_expensive['Difference %'] = shamrock_expensive['Difference %'].abs()
            shamrock_expensive = shamrock_expensive.sort_values('Difference %', ascending=False)
            shamrock_expensive.to_excel(writer, sheet_name='Shamrock More Expensive', index=False)
            
            # Sheet 3: Sysco More Expensive
            sysco_expensive = self.combined_data[
                self.combined_data['cheaper_vendor'] == 'Shamrock'
            ][[
                'shamrock_description',
                'shamrock_price_per_lb',
                'sysco_price_per_lb',
                'savings_per_lb',
                'savings_percent',
                'shamrock_pack_size',
                'sysco_pack_size',
                'category'
            ]].copy()
            sysco_expensive.columns = [
                'Product',
                'Shamrock Price/LB',
                'Sysco Price/LB',
                'Savings/LB',
                'Savings %',
                'Shamrock Pack',
                'Sysco Pack',
                'Category'
            ]
            sysco_expensive = sysco_expensive.sort_values('Savings %', ascending=False)
            sysco_expensive.to_excel(writer, sheet_name='Sysco More Expensive', index=False)
            
            # Sheet 4: All Matched Products
            all_products = self.combined_data[[
                'shamrock_description',
                'shamrock_code',
                'sysco_code',
                'shamrock_pack_size',
                'sysco_pack_size',
                'shamrock_price',
                'sysco_price',
                'shamrock_price_per_lb',
                'sysco_price_per_lb',
                'cheaper_vendor',
                'savings_per_lb',
                'savings_percent',
                'match_score',
                'category'
            ]].copy()
            all_products.columns = [
                'Product',
                'Shamrock Code',
                'Sysco Code',
                'Shamrock Pack',
                'Sysco Pack',
                'Shamrock Case Price',
                'Sysco Case Price',
                'Shamrock Price/LB',
                'Sysco Price/LB',
                'Cheaper Vendor',
                'Savings/LB',
                'Savings %',
                'Match Score',
                'Category'
            ]
            all_products.to_excel(writer, sheet_name='All Matched Products', index=False)
            
            # Sheet 5: Summary Statistics
            summary_data = {
                'Metric': [
                    'Total Products Matched',
                    'Products Where Shamrock is Cheaper',
                    'Products Where Sysco is Cheaper',
                    'Products with Same Price',
                    'Average Savings % (when Shamrock cheaper)',
                    'Average Savings % (when Sysco cheaper)',
                    'Total Potential Savings/LB (Shamrock)',
                    'Total Potential Savings/LB (Sysco)',
                    'Report Generated'
                ],
                'Value': [
                    len(self.combined_data),
                    len(self.combined_data[self.combined_data['cheaper_vendor'] == 'Shamrock']),
                    len(self.combined_data[self.combined_data['cheaper_vendor'] == 'Sysco']),
                    len(self.combined_data[self.combined_data['cheaper_vendor'] == 'Same']),
                    f"{self.combined_data[self.combined_data['cheaper_vendor'] == 'Shamrock']['savings_percent'].mean():.2f}%" if len(self.combined_data[self.combined_data['cheaper_vendor'] == 'Shamrock']) > 0 else 'N/A',
                    f"{abs(self.combined_data[self.combined_data['cheaper_vendor'] == 'Sysco']['savings_percent']).mean():.2f}%" if len(self.combined_data[self.combined_data['cheaper_vendor'] == 'Sysco']) > 0 else 'N/A',
                    f"${self.combined_data[self.combined_data['cheaper_vendor'] == 'Shamrock']['savings_per_lb'].sum():.2f}",
                    f"${abs(self.combined_data[self.combined_data['cheaper_vendor'] == 'Sysco']['savings_per_lb']).sum():.2f}",
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        return str(output_path)
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics as a dictionary."""
        if self.combined_data is None:
            return {}
        
        shamrock_cheaper = self.combined_data[self.combined_data['cheaper_vendor'] == 'Shamrock']
        sysco_cheaper = self.combined_data[self.combined_data['cheaper_vendor'] == 'Sysco']
        
        return {
            'total_matched': len(self.combined_data),
            'shamrock_cheaper_count': len(shamrock_cheaper),
            'sysco_cheaper_count': len(sysco_cheaper),
            'same_price_count': len(self.combined_data[self.combined_data['cheaper_vendor'] == 'Same']),
            'avg_shamrock_savings_pct': float(shamrock_cheaper['savings_percent'].mean()) if len(shamrock_cheaper) > 0 else 0,
            'avg_sysco_savings_pct': float(abs(sysco_cheaper['savings_percent']).mean()) if len(sysco_cheaper) > 0 else 0,
            'total_shamrock_savings_per_lb': float(shamrock_cheaper['savings_per_lb'].sum()) if len(shamrock_cheaper) > 0 else 0,
            'total_sysco_savings_per_lb': float(abs(sysco_cheaper['savings_per_lb']).sum()) if len(sysco_cheaper) > 0 else 0,
        }


# Example usage
if __name__ == "__main__":
    processor = VendorCSVProcessor()
    
    # Example: Create sample data files for testing
    sample_shamrock = pd.DataFrame({
        'item_code': ['SHA001', 'SHA002', 'SHA003'],
        'description': ['Black Pepper Ground', 'Garlic Powder', 'Onion Powder'],
        'pack_size': ['25 LB', '1/6/LB', '25 LB'],
        'price': [95.88, 54.26, 39.80],
        'category': ['Spices', 'Spices', 'Spices']
    })
    
    sample_sysco = pd.DataFrame({
        'item_code': ['SYS001', 'SYS002', 'SYS003'],
        'description': ['Black Pepper Ground Restaurant', 'Garlic Powder California', 'Onion Powder White'],
        'pack_size': ['6/1LB', '3/6LB', '6/1LB'],
        'price': [295.89, 213.19, 148.95],
        'category': ['Spices', 'Spices', 'Spices']
    })
    
    # Load and process
    processor.load_shamrock_dataframe(sample_shamrock)
    processor.load_sysco_dataframe(sample_sysco)
    
    # Generate comparison
    combined = processor.combine_vendor_data(match_threshold=0.4)
    print("Combined Data:")
    print(combined)
    
    # Generate Excel
    excel_path = processor.generate_comparison_excel("test_comparison.xlsx")
    print(f"\nExcel saved to: {excel_path}")
    
    # Get summary
    stats = processor.get_summary_stats()
    print(f"\nSummary Stats: {stats}")
