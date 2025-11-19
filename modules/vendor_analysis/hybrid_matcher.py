"""
Hybrid Vendor Matcher - Best of Both Worlds
Combines automated fuzzy matching with domain-specific validation

This module integrates:
- Fuzzy text matching for scalability (handles hundreds of products)
- Product specification awareness (Fine ≠ Coarse pepper)
- Accurate pack size parsing (Shamrock vs SYSCO formats)
- Confidence scoring (HIGH/MEDIUM/LOW)
- Integration with Ingredient dataclass
- Professional Excel output with multiple sheets
"""

import pandas as pd
import re
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

# Import existing domain knowledge
from .corrected_comparison import CorrectedVendorComparison
from .accurate_matcher import ProductMatch


@dataclass
class FuzzyMatch:
    """Fuzzy matching result with confidence scoring"""
    sysco_product: str
    shamrock_product: str
    similarity_score: float
    word_overlap_score: float
    combined_score: float
    confidence: str  # HIGH, MEDIUM, LOW
    specification_match: bool  # Does specification actually match?
    specification_notes: str = ""

    # Pricing data
    sysco_code: str = ""
    sysco_pack: str = ""
    sysco_price: float = 0.0
    sysco_split_price: Optional[float] = None

    shamrock_code: str = ""
    shamrock_pack: str = ""
    shamrock_price: float = 0.0

    # Calculated values
    sysco_per_lb: Optional[float] = None
    shamrock_per_lb: Optional[float] = None
    savings_per_lb: Optional[float] = None
    savings_percent: Optional[float] = None
    preferred_vendor: str = ""


class HybridVendorMatcher:
    """
    Hybrid matcher combining fuzzy matching automation
    with domain-specific product knowledge
    """

    def __init__(self):
        self.price_calculator = CorrectedVendorComparison()

        # Domain knowledge: product specifications that MUST match
        self.critical_specifications = {
            'pepper': ['fine', 'coarse', 'cracked', 'ground', 'whole', 'restaurant'],
            'garlic': ['powder', 'granulated', 'minced', 'chopped', 'roasted'],
            'onion': ['powder', 'granulated', 'minced', 'chopped', 'diced'],
            'salt': ['fine', 'coarse', 'kosher', 'sea', 'table'],
            'sugar': ['granulated', 'powdered', 'confectioners', 'brown', 'raw'],
            'flour': ['all-purpose', 'bread', 'cake', 'pastry', 'whole wheat'],
            'oil': ['vegetable', 'olive', 'canola', 'corn', 'peanut', 'extra virgin'],
        }

        # Specification aliases (these are equivalent)
        self.specification_aliases = {
            'ground': ['restaurant grind', 'medium grind'],
            'fine': ['table grind', 'finely ground'],
            'powder': ['powdered'],
            'granulated': ['granules'],
        }

        self.matches = []
        self.unmatched_sysco = []
        self.unmatched_shamrock = []

    def calculate_text_similarity(self, str1: str, str2: str) -> float:
        """Calculate text similarity using SequenceMatcher"""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    def calculate_word_overlap(self, str1: str, str2: str) -> float:
        """Calculate word-level overlap between two strings"""
        # Normalize and tokenize
        words1 = set(re.findall(r'\w+', str1.lower()))
        words2 = set(re.findall(r'\w+', str2.lower()))

        if not words1 or not words2:
            return 0.0

        # Calculate Jaccard similarity
        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union) if union else 0.0

    def extract_specification(self, product_name: str) -> Tuple[str, str]:
        """
        Extract base product and specification from product name

        Returns:
            (base_product, specification)
            e.g., "BLACK PEPPER COARSE" -> ("pepper", "coarse")
        """
        product_name_lower = product_name.lower()

        # Check for each known product type
        for product, specifications in self.critical_specifications.items():
            if product in product_name_lower:
                # Find which specification
                for spec in specifications:
                    if spec in product_name_lower:
                        return (product, spec)
                # Product found but no specification
                return (product, "unspecified")

        # No critical specification needed
        return ("unknown", "none")

    def specifications_match(self, product1: str, product2: str) -> Tuple[bool, str]:
        """
        Check if product specifications match

        Returns:
            (match_status, explanation)
        """
        base1, spec1 = self.extract_specification(product1)
        base2, spec2 = self.extract_specification(product2)

        # Different base products
        if base1 != base2 and base1 != "unknown" and base2 != "unknown":
            return (False, f"Different products: {base1} vs {base2}")

        # Same base product but different specifications
        if base1 == base2 and spec1 != spec2:
            # Check if they're aliases
            if self._are_specifications_equivalent(spec1, spec2):
                return (True, f"Equivalent specifications: {spec1} ≈ {spec2}")
            else:
                return (False, f"Different {base1} specifications: {spec1} vs {spec2}")

        # Specifications match or not critical
        return (True, f"Specifications match: {spec1}")

    def _are_specifications_equivalent(self, spec1: str, spec2: str) -> bool:
        """Check if two specifications are equivalent using aliases"""
        for canonical, aliases in self.specification_aliases.items():
            all_forms = [canonical] + aliases
            if spec1 in all_forms and spec2 in all_forms:
                return True
        return False

    def find_matches(self, sysco_df: pd.DataFrame, shamrock_df: pd.DataFrame,
                    similarity_threshold: float = 0.6,
                    word_overlap_threshold: float = 0.5) -> List[FuzzyMatch]:
        """
        Find fuzzy matches between vendor catalogs with validation

        Args:
            sysco_df: DataFrame with columns [code, description, pack, price, split_price]
            shamrock_df: DataFrame with columns [code, description, pack, price]
            similarity_threshold: Minimum text similarity (0-1)
            word_overlap_threshold: Minimum word overlap (0-1)

        Returns:
            List of validated FuzzyMatch objects
        """
        matches = []
        matched_shamrock_indices = set()

        print("\n" + "="*80)
        print("HYBRID VENDOR MATCHING - Fuzzy Matching with Domain Validation")
        print("="*80)

        for sysco_idx, sysco_row in sysco_df.iterrows():
            sysco_desc = str(sysco_row['description']).strip()
            best_match = None
            best_score = 0.0

            for shamrock_idx, shamrock_row in shamrock_df.iterrows():
                if shamrock_idx in matched_shamrock_indices:
                    continue

                shamrock_desc = str(shamrock_row['description']).strip()

                # Calculate similarity scores
                text_sim = self.calculate_text_similarity(sysco_desc, shamrock_desc)
                word_overlap = self.calculate_word_overlap(sysco_desc, shamrock_desc)
                combined_score = (text_sim * 0.6) + (word_overlap * 0.4)

                # Check if meets threshold
                if combined_score >= similarity_threshold or word_overlap >= word_overlap_threshold:
                    if combined_score > best_score:
                        best_score = combined_score
                        best_match = (shamrock_idx, shamrock_row, text_sim, word_overlap, combined_score)

            # Process best match if found
            if best_match:
                shamrock_idx, shamrock_row, text_sim, word_overlap, combined_score = best_match

                # CRITICAL: Validate product specifications
                spec_match, spec_notes = self.specifications_match(sysco_desc, shamrock_row['description'])

                # Determine confidence level
                if combined_score >= 0.85 and spec_match:
                    confidence = "HIGH"
                elif combined_score >= 0.7 and spec_match:
                    confidence = "MEDIUM"
                elif spec_match:
                    confidence = "LOW"
                else:
                    confidence = "REJECTED"  # Specifications don't match

                # Only accept matches with matching specifications
                if confidence != "REJECTED":
                    # Calculate pricing
                    sysco_per_lb = self.price_calculator.calculate_price_per_unit(
                        sysco_row['pack'], sysco_row['price'], 'LB'
                    )
                    shamrock_per_lb = self.price_calculator.calculate_price_per_unit(
                        shamrock_row['pack'], shamrock_row['price'], 'LB'
                    )

                    savings_per_lb = None
                    savings_percent = None
                    preferred_vendor = ""

                    if sysco_per_lb and shamrock_per_lb:
                        savings_per_lb = sysco_per_lb - shamrock_per_lb
                        savings_percent = (savings_per_lb / sysco_per_lb * 100) if sysco_per_lb > 0 else 0
                        preferred_vendor = "Shamrock" if shamrock_per_lb < sysco_per_lb else "SYSCO"

                    match = FuzzyMatch(
                        sysco_product=sysco_desc,
                        shamrock_product=shamrock_row['description'],
                        similarity_score=text_sim,
                        word_overlap_score=word_overlap,
                        combined_score=combined_score,
                        confidence=confidence,
                        specification_match=spec_match,
                        specification_notes=spec_notes,
                        sysco_code=sysco_row['code'],
                        sysco_pack=sysco_row['pack'],
                        sysco_price=sysco_row['price'],
                        sysco_split_price=sysco_row.get('split_price'),
                        shamrock_code=shamrock_row['code'],
                        shamrock_pack=shamrock_row['pack'],
                        shamrock_price=shamrock_row['price'],
                        sysco_per_lb=sysco_per_lb,
                        shamrock_per_lb=shamrock_per_lb,
                        savings_per_lb=savings_per_lb,
                        savings_percent=savings_percent,
                        preferred_vendor=preferred_vendor
                    )

                    matches.append(match)
                    matched_shamrock_indices.add(shamrock_idx)

        self.matches = matches

        # Track unmatched items
        self.unmatched_sysco = [
            row['description'] for idx, row in sysco_df.iterrows()
            if not any(m.sysco_product == row['description'] for m in matches)
        ]

        self.unmatched_shamrock = [
            row['description'] for idx, row in shamrock_df.iterrows()
            if idx not in matched_shamrock_indices
        ]

        print(f"\n✅ Found {len(matches)} validated matches")
        print(f"⚠️  {len(self.unmatched_sysco)} SYSCO products unmatched")
        print(f"⚠️  {len(self.unmatched_shamrock)} Shamrock products unmatched")

        return matches

    def to_ingredient_models(self, matches: List[FuzzyMatch]) -> List[Dict]:
        """
        Convert matches to Ingredient dataclass format

        Returns:
            List of dictionaries ready for Ingredient instantiation
        """
        ingredients = []

        for match in matches:
            # Extract base product name
            base_product, specification = self.extract_specification(match.sysco_product)

            ingredient_data = {
                'ingredient_id': f"ING_{match.sysco_code}",
                'name': match.sysco_product,
                'category': self._infer_category(base_product),
                'unit_of_measure': 'lb',
                'case_size': match.sysco_pack,
                'sysco_item_code': match.sysco_code,
                'sysco_price': match.sysco_price,
                'sysco_unit_price': match.sysco_per_lb,
                'sysco_last_updated': datetime.now(),
                'shamrock_item_code': match.shamrock_code,
                'shamrock_price': match.shamrock_price,
                'shamrock_unit_price': match.shamrock_per_lb,
                'shamrock_last_updated': datetime.now(),
                'preferred_vendor': match.preferred_vendor,
                'price_difference': abs(match.savings_per_lb) if match.savings_per_lb else None,
                'price_difference_percent': abs(match.savings_percent) if match.savings_percent else None,
            }

            ingredients.append(ingredient_data)

        return ingredients

    def _infer_category(self, product_type: str) -> str:
        """Infer ingredient category from product type"""
        category_map = {
            'pepper': 'Spices & Seasonings',
            'salt': 'Spices & Seasonings',
            'garlic': 'Spices & Seasonings',
            'onion': 'Spices & Seasonings',
            'oil': 'Oils & Fats',
            'flour': 'Dry Goods',
            'sugar': 'Dry Goods',
        }
        return category_map.get(product_type, 'Other')

    def export_to_excel(self, output_path: str, matches: List[FuzzyMatch] = None):
        """
        Export matches to Excel with multiple sheets and professional styling

        Sheets:
        1. Matched Products - All validated matches with pricing
        2. High Confidence - Only HIGH confidence matches
        3. Review Needed - MEDIUM/LOW confidence matches
        4. Unmatched Products - Items that couldn't be matched
        5. Summary Analysis - Overall statistics and savings
        """
        if matches is None:
            matches = self.matches

        output_path = Path(output_path)

        # Convert matches to DataFrames
        match_data = [asdict(m) for m in matches]
        df_all = pd.DataFrame(match_data)

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Sheet 1: All Matched Products
            if not df_all.empty:
                df_all_sorted = df_all.sort_values('combined_score', ascending=False)
                df_all_sorted.to_excel(writer, sheet_name='Matched Products', index=False)

            # Sheet 2: High Confidence Matches
            df_high = df_all[df_all['confidence'] == 'HIGH']
            if not df_high.empty:
                df_high.to_excel(writer, sheet_name='High Confidence', index=False)

            # Sheet 3: Review Needed
            df_review = df_all[df_all['confidence'].isin(['MEDIUM', 'LOW'])]
            if not df_review.empty:
                df_review.to_excel(writer, sheet_name='Review Needed', index=False)

            # Sheet 4: Unmatched Products
            unmatched_data = {
                'SYSCO Unmatched': pd.Series(self.unmatched_sysco),
                'Shamrock Unmatched': pd.Series(self.unmatched_shamrock)
            }
            df_unmatched = pd.DataFrame(unmatched_data)
            df_unmatched.to_excel(writer, sheet_name='Unmatched Products', index=False)

            # Sheet 5: Summary Analysis
            summary_data = self._generate_summary_stats(matches)
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Summary Analysis', index=False)

        print(f"\n✅ Exported to: {output_path}")
        return output_path

    def _generate_summary_stats(self, matches: List[FuzzyMatch]) -> List[Dict]:
        """Generate summary statistics"""
        df = pd.DataFrame([asdict(m) for m in matches])

        summary = []

        # Overall stats
        summary.append({
            'Metric': 'Total Matched Products',
            'Value': len(matches),
            'Notes': ''
        })

        # Confidence breakdown
        for conf in ['HIGH', 'MEDIUM', 'LOW']:
            count = len([m for m in matches if m.confidence == conf])
            summary.append({
                'Metric': f'{conf} Confidence Matches',
                'Value': count,
                'Notes': f'{count/len(matches)*100:.1f}%' if matches else '0%'
            })

        # Pricing stats
        valid_pricing = [m for m in matches if m.savings_per_lb is not None]
        if valid_pricing:
            avg_savings = sum(m.savings_per_lb for m in valid_pricing) / len(valid_pricing)
            shamrock_wins = len([m for m in valid_pricing if m.preferred_vendor == 'Shamrock'])

            summary.extend([
                {
                    'Metric': 'Average Savings Per Pound',
                    'Value': f'${avg_savings:.2f}',
                    'Notes': 'SYSCO price - Shamrock price'
                },
                {
                    'Metric': 'Products Where Shamrock is Cheaper',
                    'Value': shamrock_wins,
                    'Notes': f'{shamrock_wins/len(valid_pricing)*100:.1f}%'
                },
                {
                    'Metric': 'Products Where SYSCO is Cheaper',
                    'Value': len(valid_pricing) - shamrock_wins,
                    'Notes': f'{(len(valid_pricing)-shamrock_wins)/len(valid_pricing)*100:.1f}%'
                }
            ])

        # Unmatched items
        summary.extend([
            {
                'Metric': 'Unmatched SYSCO Products',
                'Value': len(self.unmatched_sysco),
                'Notes': 'No Shamrock equivalent found'
            },
            {
                'Metric': 'Unmatched Shamrock Products',
                'Value': len(self.unmatched_shamrock),
                'Notes': 'No SYSCO equivalent found'
            }
        ])

        return summary

    def print_summary(self):
        """Print a summary of matching results"""
        print("\n" + "="*80)
        print("MATCHING SUMMARY")
        print("="*80)

        high_conf = len([m for m in self.matches if m.confidence == 'HIGH'])
        med_conf = len([m for m in self.matches if m.confidence == 'MEDIUM'])
        low_conf = len([m for m in self.matches if m.confidence == 'LOW'])

        print(f"\nConfidence Distribution:")
        print(f"  HIGH:   {high_conf} matches")
        print(f"  MEDIUM: {med_conf} matches")
        print(f"  LOW:    {low_conf} matches")

        print(f"\nUnmatched Items:")
        print(f"  SYSCO:    {len(self.unmatched_sysco)} products")
        print(f"  Shamrock: {len(self.unmatched_shamrock)} products")

        # Pricing analysis
        valid_pricing = [m for m in self.matches if m.savings_per_lb is not None]
        if valid_pricing:
            shamrock_wins = len([m for m in valid_pricing if m.preferred_vendor == 'Shamrock'])
            avg_savings = sum(m.savings_per_lb for m in valid_pricing) / len(valid_pricing)

            print(f"\nPricing Analysis ({len(valid_pricing)} products with pricing):")
            print(f"  Shamrock cheaper: {shamrock_wins} products ({shamrock_wins/len(valid_pricing)*100:.1f}%)")
            print(f"  SYSCO cheaper: {len(valid_pricing)-shamrock_wins} products")
            print(f"  Average savings: ${avg_savings:.2f}/lb (when Shamrock is cheaper)")


# Example usage and testing
if __name__ == "__main__":
    # Example data structure for testing
    sysco_data = {
        'code': ['SYS001', 'SYS002', 'SYS003', 'SYS004'],
        'description': ['BLACK PEPPER FINE TABLE GRIND', 'BLACK PEPPER COARSE',
                       'GARLIC POWDER CALIFORNIA', 'ONION POWDER WHITE'],
        'pack': ['6/1LB', '6/1LB', '3/6LB', '6/1LB'],
        'price': [295.89, 298.95, 213.19, 148.95],
        'split_price': [None, None, 78.25, None]
    }

    shamrock_data = {
        'code': ['SH001', 'SH002', 'SH003', 'SH004'],
        'description': ['PEPPER BLACK FINE', 'PEPPER BLACK COARSE GRIND',
                       'GARLIC POWDER CALIFORNIA', 'ONION POWDER WHITE'],
        'pack': ['25 LB', '25 LB', '1/6/LB', '25 LB'],
        'price': [95.88, 79.71, 54.26, 39.80]
    }

    sysco_df = pd.DataFrame(sysco_data)
    shamrock_df = pd.DataFrame(shamrock_data)

    # Create matcher and find matches
    matcher = HybridVendorMatcher()
    matches = matcher.find_matches(sysco_df, shamrock_df)

    # Print summary
    matcher.print_summary()

    # Export to Excel
    output_path = '/home/user/lariat-bible/data/vendor_matching_results.xlsx'
    matcher.export_to_excel(output_path)

    # Convert to Ingredient models
    ingredients = matcher.to_ingredient_models(matches)
    print(f"\n✅ Generated {len(ingredients)} Ingredient objects")

    print("\n" + "="*80)
    print("INTEGRATION COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Load actual vendor catalogs (Excel/CSV)")
    print("2. Run matching with real data")
    print("3. Review MEDIUM/LOW confidence matches manually")
    print("4. Import validated matches into LariatBible system")
    print("5. Use Ingredient objects in recipes and cost calculations")
