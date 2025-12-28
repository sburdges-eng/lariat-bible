"""
Hybrid Vendor Matching Engine
Combines automated fuzzy matching with critical specification validation

This module provides the best of both worlds:
- Automated matching for scalability (handles hundreds of products)
- Specification awareness to prevent dangerous mismatches (Fine ≠ Coarse pepper)
- Pack size intelligence (Shamrock vs SYSCO formats)
- Integration with LariatBible Ingredient dataclass
"""

import pandas as pd
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from difflib import SequenceMatcher
from datetime import datetime

from modules.recipes.recipe import Ingredient


# =====================================================
# CONFIGURATION
# =====================================================

class MatchingConfig:
    """Configuration for matching thresholds and behavior"""

    # Confidence thresholds
    HIGH_CONFIDENCE = 0.75
    MEDIUM_CONFIDENCE = 0.50
    LOW_CONFIDENCE = 0.25

    # Specification keywords that MUST match exactly
    CRITICAL_SPECS = {
        'FINE', 'COARSE', 'CRACKED', 'MEDIUM', 'RESTAURANT',
        'POWDER', 'GRANULATED', 'WHOLE', 'GROUND', 'MINCED',
        'SLICED', 'DICED', 'CHOPPED', 'CRUSHED',
        'EXTRA VIRGIN', 'VIRGIN', 'PURE', 'BLEND'
    }

    # Words to ignore during matching
    STOP_WORDS = {
        'THE', 'A', 'AN', 'AND', 'OR', 'BUT', 'IN', 'ON', 'AT',
        'BY', 'FOR', 'OF', 'TO', 'FROM', 'WITH', 'BRAND', 'QUALITY'
    }


# =====================================================
# PACK SIZE PARSER (from corrected_comparison.py)
# =====================================================

class PackSizeParser:
    """Parse and interpret vendor pack sizes correctly"""

    @staticmethod
    def parse(pack_str: str) -> Dict:
        """
        Parse pack size string into structured data

        Formats:
        - Shamrock: "1/6/LB" = 1 container × 6 lbs = 6 lbs total
        - SYSCO: "3/6LB" = 3 containers × 6 lbs each = 18 lbs total
        - Simple: "25 LB" = 25 pounds total
        """
        if not pack_str or pd.isna(pack_str):
            return {'total_pounds': None, 'total_ounces': None}

        pack_str = str(pack_str).upper().strip()
        result = {
            'original': pack_str,
            'total_pounds': None,
            'total_ounces': None,
            'containers': 1,
            'pounds_per_container': None
        }

        # Shamrock format: 1/6/LB
        shamrock_match = re.match(r'(\d+)/(\d+)/LB', pack_str)
        if shamrock_match:
            containers = int(shamrock_match.group(1))
            pounds_per = int(shamrock_match.group(2))
            result['containers'] = containers
            result['pounds_per_container'] = pounds_per
            result['total_pounds'] = containers * pounds_per
            result['total_ounces'] = containers * pounds_per * 16
            return result

        # SYSCO format: 3/6LB or 6/1LB
        sysco_match = re.match(r'(\d+)/(\d+)(LB|#)', pack_str)
        if sysco_match:
            containers = int(sysco_match.group(1))
            pounds_per = int(sysco_match.group(2))
            result['containers'] = containers
            result['pounds_per_container'] = pounds_per
            result['total_pounds'] = containers * pounds_per
            result['total_ounces'] = containers * pounds_per * 16
            return result

        # Simple pounds: 25 LB
        simple_lb = re.match(r'(\d+)\s*LB', pack_str)
        if simple_lb:
            pounds = int(simple_lb.group(1))
            result['total_pounds'] = pounds
            result['total_ounces'] = pounds * 16
            result['pounds_per_container'] = pounds
            return result

        return result


# =====================================================
# SPECIFICATION VALIDATOR
# =====================================================

class SpecificationValidator:
    """Validates that product specifications match exactly"""

    @staticmethod
    def extract_specifications(text: str) -> set:
        """Extract critical specification keywords from product description"""
        if not text:
            return set()

        text = str(text).upper()
        found_specs = set()

        for spec in MatchingConfig.CRITICAL_SPECS:
            if spec in text:
                found_specs.add(spec)

        return found_specs

    @staticmethod
    def validate_match(shamrock_desc: str, sysco_desc: str) -> Tuple[bool, str]:
        """
        Validate that specifications match between products

        Returns:
            (is_valid, reason)
        """
        sham_specs = SpecificationValidator.extract_specifications(shamrock_desc)
        sysco_specs = SpecificationValidator.extract_specifications(sysco_desc)

        # If either has critical specs, they MUST match
        if sham_specs or sysco_specs:
            if sham_specs != sysco_specs:
                missing_in_sysco = sham_specs - sysco_specs
                missing_in_sham = sysco_specs - sham_specs

                reason = "SPECIFICATION MISMATCH: "
                if missing_in_sysco:
                    reason += f"Shamrock has {missing_in_sysco} not in SYSCO. "
                if missing_in_sham:
                    reason += f"SYSCO has {missing_in_sham} not in Shamrock."

                return False, reason

        return True, "Specifications match"


# =====================================================
# FUZZY MATCHER (from streamlined script)
# =====================================================

class FuzzyMatcher:
    """Fuzzy text matching for product descriptions"""

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text for matching"""
        if not text or pd.isna(text):
            return ''

        text = str(text).upper()
        # Remove special characters but keep spaces and numbers
        text = re.sub(r'[^A-Z0-9\s]', ' ', text)
        # Remove stop words
        words = [w for w in text.split() if w not in MatchingConfig.STOP_WORDS]
        return ' '.join(words).strip()

    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """
        Calculate text similarity (0 to 1)

        Uses combination of:
        - String similarity (SequenceMatcher)
        - Word overlap
        """
        if not text1 or not text2:
            return 0.0

        # Basic string matching
        basic_score = SequenceMatcher(None, text1, text2).ratio()

        # Word overlap score
        words1 = set(text1.split())
        words2 = set(text2.split())
        if words1 and words2:
            overlap = len(words1 & words2) / len(words1 | words2)
        else:
            overlap = 0

        # Combined score (weighted)
        return (basic_score * 0.6) + (overlap * 0.4)

    @staticmethod
    def extract_pack_info(text: str) -> Optional[str]:
        """Extract pack size information from description"""
        if not text or pd.isna(text):
            return None

        text = str(text).upper()
        # Look for patterns like: 6/1LB, 25LB, 12CT, #10
        pack_patterns = [
            r'(\d+)/(\d+)(LB|OZ|CT)',
            r'(\d+)\s*(LB|OZ|CT|GAL)',
            r'#(\d+)',
        ]

        for pattern in pack_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None


# =====================================================
# HYBRID MATCHER (Main Integration)
# =====================================================

@dataclass
class MatchResult:
    """Result of a vendor product match"""
    shamrock_sku: str
    shamrock_description: str
    shamrock_price: float
    shamrock_pack: str

    sysco_sku: str
    sysco_description: str
    sysco_price: float
    sysco_pack: str

    match_score: float
    confidence: str  # HIGH, MEDIUM, LOW, REJECTED
    validation_status: str  # PASS, FAIL
    validation_reason: str

    price_per_lb_shamrock: Optional[float] = None
    price_per_lb_sysco: Optional[float] = None
    savings_per_lb: Optional[float] = None
    savings_percent: Optional[float] = None
    preferred_vendor: Optional[str] = None

    def to_ingredient(self, ingredient_id: str, category: str = "Unknown") -> Ingredient:
        """Convert match to Ingredient dataclass"""
        return Ingredient(
            ingredient_id=ingredient_id,
            name=self.shamrock_description,  # Use Shamrock as canonical name
            category=category,
            unit_of_measure="lb",
            case_size=f"Shamrock: {self.shamrock_pack}, SYSCO: {self.sysco_pack}",
            sysco_item_code=self.sysco_sku,
            sysco_price=self.sysco_price,
            sysco_unit_price=self.price_per_lb_sysco,
            shamrock_item_code=self.shamrock_sku,
            shamrock_price=self.shamrock_price,
            shamrock_unit_price=self.price_per_lb_shamrock,
            preferred_vendor=self.preferred_vendor,
            price_difference=abs(self.savings_per_lb) if self.savings_per_lb else None,
            price_difference_percent=abs(self.savings_percent) if self.savings_percent else None
        )


class HybridVendorMatcher:
    """
    Hybrid matching engine combining fuzzy matching with specification validation

    Workflow:
    1. Fuzzy match to find candidates
    2. Validate specifications match exactly
    3. Parse pack sizes and calculate unit prices
    4. Rank by confidence and savings
    """

    def __init__(self):
        self.fuzzy_matcher = FuzzyMatcher()
        self.spec_validator = SpecificationValidator()
        self.pack_parser = PackSizeParser()
        self.matches: List[MatchResult] = []

    def find_best_match(self, shamrock_item: Dict, sysco_items: pd.DataFrame) -> Optional[MatchResult]:
        """
        Find best SYSCO match for a Shamrock item with validation

        Args:
            shamrock_item: Dict with keys: sku, description, price, pack
            sysco_items: DataFrame with SYSCO products

        Returns:
            MatchResult or None if no valid match found
        """
        sham_clean = self.fuzzy_matcher.clean_text(shamrock_item['description'])

        best_match = None
        best_score = 0

        for _, sysco_row in sysco_items.iterrows():
            sysco_clean = self.fuzzy_matcher.clean_text(sysco_row.get('description', ''))

            # Calculate fuzzy similarity
            similarity = self.fuzzy_matcher.calculate_similarity(sham_clean, sysco_clean)

            # Bonus for matching pack info in description
            sham_pack_info = self.fuzzy_matcher.extract_pack_info(shamrock_item['description'])
            sysco_pack_info = self.fuzzy_matcher.extract_pack_info(sysco_row.get('description', ''))
            if sham_pack_info and sysco_pack_info and sham_pack_info == sysco_pack_info:
                similarity += 0.10

            # Only consider if meets minimum threshold
            if similarity < MatchingConfig.LOW_CONFIDENCE:
                continue

            # CRITICAL: Validate specifications
            is_valid, reason = self.spec_validator.validate_match(
                shamrock_item['description'],
                sysco_row.get('description', '')
            )

            if similarity > best_score:
                best_score = similarity
                best_match = {
                    'sysco_row': sysco_row,
                    'similarity': similarity,
                    'validation_status': 'PASS' if is_valid else 'FAIL',
                    'validation_reason': reason
                }

        if not best_match:
            return None

        # Build match result
        sysco_row = best_match['sysco_row']

        # Parse pack sizes and calculate unit prices
        sham_pack_parsed = self.pack_parser.parse(shamrock_item['pack'])
        sysco_pack_parsed = self.pack_parser.parse(sysco_row.get('pack', ''))

        price_per_lb_sham = None
        price_per_lb_sysco = None
        savings_per_lb = None
        savings_percent = None
        preferred_vendor = None

        if sham_pack_parsed['total_pounds'] and sysco_pack_parsed['total_pounds']:
            price_per_lb_sham = shamrock_item['price'] / sham_pack_parsed['total_pounds']
            price_per_lb_sysco = sysco_row.get('price', 0) / sysco_pack_parsed['total_pounds']
            savings_per_lb = price_per_lb_sysco - price_per_lb_sham

            if price_per_lb_sysco > 0:
                savings_percent = (savings_per_lb / price_per_lb_sysco) * 100

            preferred_vendor = "Shamrock Foods" if price_per_lb_sham < price_per_lb_sysco else "SYSCO"

        # Determine confidence level
        # REJECTED if validation fails, even with high similarity
        if best_match['validation_status'] == 'FAIL':
            confidence = 'REJECTED'
        elif best_score >= MatchingConfig.HIGH_CONFIDENCE:
            confidence = 'HIGH'
        elif best_score >= MatchingConfig.MEDIUM_CONFIDENCE:
            confidence = 'MEDIUM'
        else:
            confidence = 'LOW'

        return MatchResult(
            shamrock_sku=shamrock_item['sku'],
            shamrock_description=shamrock_item['description'],
            shamrock_price=shamrock_item['price'],
            shamrock_pack=shamrock_item['pack'],
            sysco_sku=sysco_row.get('sku', ''),
            sysco_description=sysco_row.get('description', ''),
            sysco_price=sysco_row.get('price', 0),
            sysco_pack=sysco_row.get('pack', ''),
            match_score=best_score,
            confidence=confidence,
            validation_status=best_match['validation_status'],
            validation_reason=best_match['validation_reason'],
            price_per_lb_shamrock=price_per_lb_sham,
            price_per_lb_sysco=price_per_lb_sysco,
            savings_per_lb=savings_per_lb,
            savings_percent=savings_percent,
            preferred_vendor=preferred_vendor
        )

    def match_all(self, shamrock_df: pd.DataFrame, sysco_df: pd.DataFrame,
                  progress_callback=None) -> List[MatchResult]:
        """
        Match all Shamrock items against SYSCO catalog

        Args:
            shamrock_df: DataFrame with columns: sku, description, price, pack
            sysco_df: DataFrame with columns: sku, description, price, pack
            progress_callback: Optional callback(current, total)

        Returns:
            List of MatchResult objects
        """
        results = []
        total = len(shamrock_df)

        print(f"\n🔄 Matching {total} Shamrock items against {len(sysco_df)} SYSCO items...")
        print("   Using hybrid fuzzy + specification validation...")

        for idx, (_, sham_row) in enumerate(shamrock_df.iterrows(), 1):
            # Extract Shamrock info
            shamrock_item = {
                'sku': str(sham_row.get('sku', sham_row.get('SKU', ''))),
                'description': str(sham_row.get('description', sham_row.get('Description', ''))),
                'price': float(sham_row.get('price', sham_row.get('Price', 0))),
                'pack': str(sham_row.get('pack', sham_row.get('Pack', '')))
            }

            # Find best match
            match_result = self.find_best_match(shamrock_item, sysco_df)

            if match_result:
                results.append(match_result)

            # Progress update
            if idx % 10 == 0:
                print(f"  Progress: {idx}/{total} ({idx/total*100:.0f}%)")

            if progress_callback:
                progress_callback(idx, total)

        self.matches = results

        # Print summary
        print(f"\n✅ Matching complete!")
        print(f"   Total matches: {len(results)}")
        print(f"   High confidence: {sum(1 for m in results if m.confidence == 'HIGH')}")
        print(f"   Medium confidence: {sum(1 for m in results if m.confidence == 'MEDIUM')}")
        print(f"   Low confidence: {sum(1 for m in results if m.confidence == 'LOW')}")
        print(f"   Rejected (spec mismatch): {sum(1 for m in results if m.confidence == 'REJECTED')}")

        return results

    def to_dataframe(self) -> pd.DataFrame:
        """Convert matches to pandas DataFrame for export"""
        if not self.matches:
            return pd.DataFrame()

        data = []
        for match in self.matches:
            data.append({
                'Shamrock_SKU': match.shamrock_sku,
                'Shamrock_Description': match.shamrock_description,
                'Shamrock_Price': match.shamrock_price,
                'Shamrock_Pack': match.shamrock_pack,
                'SYSCO_SKU': match.sysco_sku,
                'SYSCO_Description': match.sysco_description,
                'SYSCO_Price': match.sysco_price,
                'SYSCO_Pack': match.sysco_pack,
                'Match_Score': round(match.match_score * 100, 1),
                'Confidence': match.confidence,
                'Validation_Status': match.validation_status,
                'Validation_Reason': match.validation_reason,
                'Shamrock_per_lb': match.price_per_lb_shamrock,
                'SYSCO_per_lb': match.price_per_lb_sysco,
                'Savings_per_lb': match.savings_per_lb,
                'Savings_Percent': match.savings_percent,
                'Preferred_Vendor': match.preferred_vendor
            })

        return pd.DataFrame(data)

    def to_ingredients(self, category_map: Dict[str, str] = None) -> List[Ingredient]:
        """
        Convert high-confidence matches to Ingredient objects

        Args:
            category_map: Optional mapping of product names to categories

        Returns:
            List of Ingredient dataclass objects
        """
        ingredients = []
        category_map = category_map or {}

        # Only convert high-confidence, validated matches
        for idx, match in enumerate(self.matches):
            if match.confidence == 'HIGH' and match.validation_status == 'PASS':
                # Determine category
                category = category_map.get(match.shamrock_description, "Unknown")

                # Generate ingredient ID
                ingredient_id = f"ING{idx:04d}"

                ingredient = match.to_ingredient(ingredient_id, category)
                ingredients.append(ingredient)

        print(f"\n✅ Converted {len(ingredients)} high-confidence matches to Ingredient objects")

        return ingredients

    def get_savings_summary(self) -> Dict:
        """Calculate total savings potential"""
        approved_matches = [m for m in self.matches
                          if m.confidence in ['HIGH', 'MEDIUM']
                          and m.validation_status == 'PASS'
                          and m.savings_per_lb is not None]

        if not approved_matches:
            return {'error': 'No approved matches with pricing data'}

        total_savings_per_lb = sum(m.savings_per_lb for m in approved_matches if m.savings_per_lb > 0)
        avg_savings_percent = sum(m.savings_percent for m in approved_matches if m.savings_per_lb > 0) / len([m for m in approved_matches if m.savings_per_lb > 0]) if approved_matches else 0

        # Estimate monthly savings (assuming 10 lbs per product per month)
        estimated_monthly = total_savings_per_lb * 10

        return {
            'approved_matches': len(approved_matches),
            'items_with_savings': sum(1 for m in approved_matches if m.savings_per_lb > 0),
            'total_savings_per_lb': total_savings_per_lb,
            'average_savings_percent': avg_savings_percent,
            'estimated_monthly_savings': estimated_monthly,
            'estimated_annual_savings': estimated_monthly * 12
        }


# =====================================================
# CONVENIENCE FUNCTIONS
# =====================================================

def match_vendors_from_excel(excel_file: str, shamrock_sheet: str = 'Shamrock_Data',
                             sysco_sheet: str = 'Sysco_Data') -> HybridVendorMatcher:
    """
    Convenience function to match vendors from Excel file

    Args:
        excel_file: Path to Excel file
        shamrock_sheet: Name of Shamrock data sheet
        sysco_sheet: Name of SYSCO data sheet

    Returns:
        HybridVendorMatcher with completed matches
    """
    print(f"\n📂 Loading vendor data from: {excel_file}")

    shamrock_df = pd.read_excel(excel_file, sheet_name=shamrock_sheet)
    sysco_df = pd.read_excel(excel_file, sheet_name=sysco_sheet)

    print(f"   ✓ Loaded {len(shamrock_df)} Shamrock items")
    print(f"   ✓ Loaded {len(sysco_df)} SYSCO items")

    matcher = HybridVendorMatcher()
    matcher.match_all(shamrock_df, sysco_df)

    return matcher


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("="*80)
    print("HYBRID VENDOR MATCHER - Test Mode")
    print("="*80)

    # Test specification validation
    print("\n📋 Testing Specification Validation:")
    print("-"*80)

    test_cases = [
        ("BLACK PEPPER FINE", "BLACK PEPPER FINE TABLE GRIND", True),
        ("BLACK PEPPER FINE", "BLACK PEPPER COARSE", False),
        ("GARLIC POWDER", "GARLIC GRANULATED", False),
        ("GARLIC POWDER CALIFORNIA", "GARLIC POWDER", True),
        ("OLIVE OIL EXTRA VIRGIN", "OLIVE OIL PURE", False),
    ]

    validator = SpecificationValidator()
    for sham, sysco, expected in test_cases:
        is_valid, reason = validator.validate_match(sham, sysco)
        status = "✓" if is_valid == expected else "✗"
        print(f"{status} '{sham}' vs '{sysco}'")
        print(f"   Result: {is_valid} - {reason}")

    print("\n✅ Hybrid Vendor Matcher module ready for use!")
