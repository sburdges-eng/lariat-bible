# Claude Code Integration Guide
## The Lariat Bible - Vendor Matching System

This document provides comprehensive guidance for Claude Code on the vendor matching system architecture, workflows, and best practices.

---

## 📋 Table of Contents
1. [System Architecture](#system-architecture)
2. [Vendor Matching Workflow](#vendor-matching-workflow)
3. [Module Reference](#module-reference)
4. [Critical Domain Knowledge](#critical-domain-knowledge)
5. [Data Flow](#data-flow)
6. [Usage Examples](#usage-examples)
7. [Troubleshooting](#troubleshooting)

---

## 🏗️ System Architecture

### Overview
The Lariat Bible uses a **hybrid vendor matching system** that combines:
- **Automated fuzzy matching** for scalability (handles hundreds of products)
- **Domain-specific validation** for accuracy (prevents dangerous mismatches)
- **Integration with core data models** (Ingredient dataclass)
- **Professional reporting** (Excel exports with multiple sheets)

### Key Components

```
modules/vendor_analysis/
├── hybrid_matcher.py          # PRIMARY: Fuzzy matching + domain validation
├── accurate_matcher.py         # Manual specification matching (domain knowledge)
├── corrected_comparison.py     # Pack size parsing and unit price calculation
├── comparator.py              # High-level vendor comparison and reporting
├── invoice_processor.py        # Invoice OCR (future)
└── integration_example.py      # Complete workflow example
```

### Component Relationships

```
┌─────────────────────────────────────────────────────────┐
│                  HybridVendorMatcher                    │
│  (Primary matching engine - RECOMMENDED)                │
│                                                          │
│  ┌──────────────────┐  ┌──────────────────────────┐   │
│  │ Fuzzy Matching   │  │ Domain Validation        │   │
│  │ - SequenceMatcher│  │ - Specification checking │   │
│  │ - Word overlap   │  │ - Product type matching  │   │
│  │ - Confidence     │  │ - Alias resolution       │   │
│  └────────┬─────────┘  └──────────┬───────────────┘   │
│           │                        │                    │
│           └────────┬───────────────┘                    │
│                    │                                     │
└────────────────────┼─────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                        │
         ▼                        ▼
┌─────────────────┐     ┌──────────────────┐
│ Pack Size Parser│     │ Ingredient Model │
│ (Corrected      │     │ (Recipe module)  │
│  Comparison)    │     │                  │
└─────────────────┘     └──────────────────┘
```

---

## 🔄 Vendor Matching Workflow

### Step-by-Step Process

#### 1. **Data Preparation**
```python
from modules.vendor_analysis import HybridVendorMatcher

# Load vendor catalogs (Excel or CSV)
# Expected columns: code, description, pack, price, [split_price]
sysco_df = pd.read_excel('sysco_catalog.xlsx')
shamrock_df = pd.read_excel('shamrock_catalog.xlsx')
```

#### 2. **Initialize Matcher**
```python
matcher = HybridVendorMatcher()

# Matcher automatically loads:
# - Critical product specifications (pepper, garlic, onion, etc.)
# - Specification aliases (fine ≈ table grind)
# - Pack size parser from CorrectedVendorComparison
```

#### 3. **Run Matching**
```python
matches = matcher.find_matches(
    sysco_df,
    shamrock_df,
    similarity_threshold=0.6,      # Text similarity minimum (0-1)
    word_overlap_threshold=0.5     # Word overlap minimum (0-1)
)

# Returns: List[FuzzyMatch] with confidence scoring
# Confidence levels: HIGH, MEDIUM, LOW, REJECTED
```

#### 4. **Validation Logic**
For each candidate match, the system:

1. **Calculates similarity scores:**
   - Text similarity (SequenceMatcher)
   - Word overlap (Jaccard similarity)
   - Combined score (weighted average)

2. **Validates product specifications:**
   ```
   ✅ ACCEPT: "BLACK PEPPER FINE" ↔ "PEPPER BLACK FINE"
              (same product, same specification)

   ❌ REJECT: "BLACK PEPPER FINE" ↔ "PEPPER BLACK COARSE"
              (same product, DIFFERENT specification)

   ✅ ACCEPT: "GARLIC POWDER" ↔ "GARLIC POWDERED"
              (specification alias)
   ```

3. **Assigns confidence level:**
   - **HIGH**: Score ≥ 0.85 + specifications match
   - **MEDIUM**: Score ≥ 0.7 + specifications match
   - **LOW**: Score < 0.7 + specifications match
   - **REJECTED**: Specifications don't match

4. **Calculates pricing:**
   - Uses pack size parser to extract total pounds
   - Calculates price per pound for both vendors
   - Determines preferred vendor
   - Calculates savings percentage

#### 5. **Export Results**
```python
# Generate Excel with multiple sheets
matcher.export_to_excel('vendor_matching_results.xlsx')

# Sheets created:
# 1. Matched Products - All validated matches
# 2. High Confidence - Only HIGH confidence (use these first)
# 3. Review Needed - MEDIUM/LOW confidence (manual review)
# 4. Unmatched Products - Items with no match found
# 5. Summary Analysis - Overall statistics
```

#### 6. **Convert to Ingredient Objects**
```python
from modules.recipes.recipe import Ingredient

# Convert matches to Ingredient dataclass instances
ingredient_data = matcher.to_ingredient_models(matches)

ingredients = [Ingredient(**data) for data in ingredient_data]

# Each Ingredient includes:
# - Vendor codes and prices (SYSCO and Shamrock)
# - Unit prices (per pound)
# - Preferred vendor (based on price)
# - Price difference (amount and percentage)
```

---

## 📚 Module Reference

### HybridVendorMatcher (Primary)

**Location:** `modules/vendor_analysis/hybrid_matcher.py`

**Purpose:** Automated vendor matching with domain validation

**Key Methods:**

```python
# Find matches between vendor catalogs
matches = matcher.find_matches(
    sysco_df: pd.DataFrame,
    shamrock_df: pd.DataFrame,
    similarity_threshold: float = 0.6,
    word_overlap_threshold: float = 0.5
) -> List[FuzzyMatch]

# Convert to Ingredient models
ingredients = matcher.to_ingredient_models(
    matches: List[FuzzyMatch]
) -> List[Dict]

# Export to Excel with multiple sheets
matcher.export_to_excel(
    output_path: str,
    matches: List[FuzzyMatch] = None
)

# Print summary statistics
matcher.print_summary()
```

**FuzzyMatch Dataclass:**

```python
@dataclass
class FuzzyMatch:
    # Product information
    sysco_product: str
    shamrock_product: str

    # Matching scores
    similarity_score: float        # 0-1
    word_overlap_score: float      # 0-1
    combined_score: float          # Weighted average
    confidence: str                # HIGH/MEDIUM/LOW

    # Validation
    specification_match: bool      # Do specifications match?
    specification_notes: str       # Explanation

    # Vendor data
    sysco_code: str
    sysco_pack: str
    sysco_price: float
    shamrock_code: str
    shamrock_pack: str
    shamrock_price: float

    # Calculated pricing
    sysco_per_lb: float
    shamrock_per_lb: float
    savings_per_lb: float
    savings_percent: float
    preferred_vendor: str
```

---

### AccurateVendorMatcher

**Location:** `modules/vendor_analysis/accurate_matcher.py`

**Purpose:** Manual product matching with exact specification control

**Use When:**
- Creating custom product matches
- Need exact control over specifications
- Building reference data for validation

**Key Methods:**

```python
matcher = AccurateVendorMatcher()

# Load pre-defined pepper products with exact grind matching
pepper_matches = matcher.load_pepper_products()

# Load all spice matches
all_matches = matcher.load_all_spice_matches()

# Generate comparison report
df = matcher.generate_comparison_report()
```

**ProductMatch Dataclass:**

```python
@dataclass
class ProductMatch:
    product_name: str          # Base product (e.g., "Black Pepper")
    specification: str         # Exact spec (e.g., "Fine Grind")

    # SYSCO data
    sysco_code: str
    sysco_description: str
    sysco_pack: str
    sysco_case_price: float
    sysco_split_price: Optional[float]

    # Shamrock data
    shamrock_code: str
    shamrock_description: str
    shamrock_pack: str
    shamrock_price: float

    notes: str

    # Methods
    def calculate_savings(self) -> Dict
    def _parse_pounds(self, pack_str: str) -> Optional[float]
```

---

### CorrectedVendorComparison

**Location:** `modules/vendor_analysis/corrected_comparison.py`

**Purpose:** Accurate pack size parsing and unit price calculation

**Critical for:** Understanding vendor-specific pack size formats

**Pack Size Formats:**

```python
# Shamrock format:
"1/6/LB"    → 1 container × 6 lbs = 6 lbs total

# SYSCO format:
"3/6LB"     → 3 containers × 6 lbs each = 18 lbs total
"6/1LB"     → 6 containers × 1 lb each = 6 lbs total

# Simple format:
"25 LB"     → 25 pounds total

# Can format:
"6/#10"     → 6 × #10 cans = 6 × 109 oz = 654 oz
```

**Key Methods:**

```python
comparator = CorrectedVendorComparison()

# Interpret pack size
parsed = comparator.interpret_pack_size("3/6LB")
# Returns: {
#     'original': '3/6LB',
#     'total_pounds': 18.0,
#     'containers': 3,
#     'pounds_per_container': 6.0,
#     'unit_type': 'LB'
# }

# Calculate price per unit
price_per_lb = comparator.calculate_price_per_unit(
    pack_size="3/6LB",
    case_price=213.19,
    target_unit='LB'
)
# Returns: 11.84 (price per pound)
```

---

## ⚠️ Critical Domain Knowledge

### Product Specifications MUST Match

**Why This Matters:**
Different product specifications serve **different culinary purposes**. Mixing them up can:
- Change recipe flavor profiles
- Affect cooking times
- Impact customer satisfaction
- Cause operational inefficiencies

### Black Pepper Specifications

```python
# ❌ NEVER MATCH THESE:
"BLACK PEPPER FINE"        → Table shakers, finishing
"BLACK PEPPER COARSE"      → Steaks, robust dishes
"BLACK PEPPER CRACKED"     → Visual appeal, marinades
"BLACK PEPPER GROUND"      → All-purpose kitchen use

# ✅ These are equivalent:
"BLACK PEPPER GROUND" ≈ "BLACK PEPPER RESTAURANT GRIND"
"BLACK PEPPER FINE" ≈ "BLACK PEPPER TABLE GRIND"
```

### Garlic Specifications

```python
# ❌ DIFFERENT PRODUCTS:
"GARLIC POWDER"        → Fine powder, strong flavor
"GARLIC GRANULATED"    → Coarser texture, milder
"GARLIC MINCED"        → Actual garlic pieces

# ✅ These are equivalent:
"GARLIC POWDER" ≈ "GARLIC POWDERED"
```

### Critical Specifications by Product

The HybridVendorMatcher automatically validates these:

```python
critical_specifications = {
    'pepper': ['fine', 'coarse', 'cracked', 'ground', 'whole', 'restaurant'],
    'garlic': ['powder', 'granulated', 'minced', 'chopped', 'roasted'],
    'onion': ['powder', 'granulated', 'minced', 'chopped', 'diced'],
    'salt': ['fine', 'coarse', 'kosher', 'sea', 'table'],
    'sugar': ['granulated', 'powdered', 'confectioners', 'brown', 'raw'],
    'flour': ['all-purpose', 'bread', 'cake', 'pastry', 'whole wheat'],
    'oil': ['vegetable', 'olive', 'canola', 'corn', 'peanut', 'extra virgin'],
}
```

---

## 🔀 Data Flow

### Complete Vendor Matching Pipeline

```
┌──────────────────────┐
│  Vendor Catalogs     │
│  (Excel/CSV)         │
│  - SYSCO catalog     │
│  - Shamrock catalog  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Load & Validate     │
│  - Check columns     │
│  - Standardize names │
│  - Clean data        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  HybridVendorMatcher │
│  1. Fuzzy matching   │
│  2. Spec validation  │
│  3. Pack parsing     │
│  4. Price calculation│
└──────────┬───────────┘
           │
           ├─────────────────┬─────────────────┬───────────────┐
           ▼                 ▼                 ▼               ▼
┌─────────────────┐  ┌──────────────┐  ┌────────────┐  ┌──────────┐
│ Matched         │  │ High         │  │ Review     │  │ Unmatched│
│ Products        │  │ Confidence   │  │ Needed     │  │ Items    │
│ (All validated) │  │ (Use first)  │  │ (Manual)   │  │ (No match│
└────────┬────────┘  └──────┬───────┘  └─────┬──────┘  └────┬─────┘
         │                  │                 │              │
         └──────────────────┴─────────────────┴──────────────┘
                            │
                            ▼
               ┌─────────────────────────┐
               │  Excel Report           │
               │  - Multiple sheets      │
               │  - Styling              │
               │  - Summary stats        │
               └────────┬────────────────┘
                        │
                        ▼
               ┌─────────────────────────┐
               │  Ingredient Objects     │
               │  - Vendor codes & prices│
               │  - Unit prices          │
               │  - Preferred vendor     │
               │  - Price differences    │
               └────────┬────────────────┘
                        │
                        ▼
               ┌─────────────────────────┐
               │  LariatBible System     │
               │  - Recipe costing       │
               │  - Inventory management │
               │  - Purchase orders      │
               │  - Savings tracking     │
               └─────────────────────────┘
```

---

## 💡 Usage Examples

### Example 1: Basic Matching

```python
from modules.vendor_analysis import HybridVendorMatcher
import pandas as pd

# Load catalogs
sysco_df = pd.read_excel('data/sysco_catalog.xlsx')
shamrock_df = pd.read_excel('data/shamrock_catalog.xlsx')

# Create matcher
matcher = HybridVendorMatcher()

# Find matches
matches = matcher.find_matches(sysco_df, shamrock_df)

# Print summary
matcher.print_summary()

# Export to Excel
matcher.export_to_excel('data/vendor_matching_results.xlsx')
```

### Example 2: Integration with Recipes

```python
from modules.vendor_analysis import HybridVendorMatcher
from modules.recipes.recipe import Ingredient, Recipe, RecipeIngredient

# Run matching
matcher = HybridVendorMatcher()
matches = matcher.find_matches(sysco_df, shamrock_df)

# Convert to Ingredients
ingredient_data = matcher.to_ingredient_models(matches)
ingredients = [Ingredient(**data) for data in ingredient_data]

# Use in recipe
black_pepper = next(ing for ing in ingredients if 'BLACK PEPPER' in ing.name)

recipe_ing = RecipeIngredient(
    ingredient=black_pepper,
    quantity=0.25,  # 0.25 lbs
    unit='lb',
    prep_instruction='freshly ground'
)

# Create recipe
my_recipe = Recipe(
    recipe_id='RCP001',
    name='Steak Seasoning',
    category='Seasoning',
    yield_amount=10,
    yield_unit='portions',
    portion_size='1 tbsp',
    ingredients=[recipe_ing]
)

# Calculate costs
print(f"Recipe cost: ${my_recipe.total_cost:.2f}")
print(f"Cost per portion: ${my_recipe.cost_per_portion:.2f}")
print(f"Using preferred vendor: {black_pepper.preferred_vendor}")
```

### Example 3: Savings Analysis

```python
from modules.vendor_analysis import HybridVendorMatcher

# Run matching
matcher = HybridVendorMatcher()
matches = matcher.find_matches(sysco_df, shamrock_df)

# Analyze savings
high_savings_items = [
    m for m in matches
    if m.savings_percent and m.savings_percent > 20
    and m.preferred_vendor == 'Shamrock'
]

print(f"\n🔥 HIGH SAVINGS OPPORTUNITIES (>20%)")
print("="*80)

for match in sorted(high_savings_items, key=lambda x: x.savings_percent, reverse=True):
    print(f"\n{match.sysco_product}")
    print(f"  SYSCO: ${match.sysco_per_lb:.2f}/lb")
    print(f"  Shamrock: ${match.shamrock_per_lb:.2f}/lb")
    print(f"  💰 Savings: ${match.savings_per_lb:.2f}/lb ({match.savings_percent:.1f}%)")

    # Estimate monthly impact (assuming 10 lbs/month usage)
    monthly_impact = match.savings_per_lb * 10
    print(f"  📅 Monthly impact: ${monthly_impact:.2f}")
```

### Example 4: Custom Specification Matching

```python
from modules.vendor_analysis import HybridVendorMatcher

matcher = HybridVendorMatcher()

# Add custom product specifications
matcher.critical_specifications['paprika'] = ['sweet', 'smoked', 'hot']

# Add custom aliases
matcher.specification_aliases['sweet'] = ['mild', 'hungarian']

# Run matching with custom rules
matches = matcher.find_matches(sysco_df, shamrock_df)
```

---

## 🔧 Troubleshooting

### Issue: Matches are rejected despite looking similar

**Cause:** Specification validation is preventing a match

**Solution:**
1. Check the `specification_notes` field in rejected matches
2. Verify if specifications actually match (e.g., Fine vs Coarse)
3. If they're equivalent, add to `specification_aliases`

```python
# Check rejected matches
for sysco_idx, sysco_row in sysco_df.iterrows():
    # ... matching logic ...
    spec_match, spec_notes = matcher.specifications_match(
        sysco_desc, shamrock_desc
    )
    if not spec_match:
        print(f"REJECTED: {sysco_desc} ↔ {shamrock_desc}")
        print(f"Reason: {spec_notes}")
```

### Issue: Pack size parsing returns None

**Cause:** Unknown pack size format

**Solution:**
1. Check the pack size format
2. Add parsing rule to `CorrectedVendorComparison.interpret_pack_size()`

```python
from modules.vendor_analysis import CorrectedVendorComparison

comparator = CorrectedVendorComparison()
result = comparator.interpret_pack_size("YOUR_PACK_FORMAT")
print(result)  # Check what's being parsed
```

### Issue: Too many LOW confidence matches

**Cause:** Similarity threshold is too low or product names are very different

**Solution:**
1. Increase similarity threshold (try 0.7 or 0.75)
2. Review Excel "Review Needed" sheet manually
3. For confirmed matches, create manual ProductMatch entries

```python
# Higher threshold for better quality
matches = matcher.find_matches(
    sysco_df,
    shamrock_df,
    similarity_threshold=0.75  # Increased from 0.6
)
```

### Issue: Missing vendor data in Ingredient objects

**Cause:** One vendor doesn't have pricing data

**Solution:**
1. Check source catalog for missing data
2. Use `Ingredient.calculate_best_price()` to see what data is available

```python
for ing in ingredients:
    result = ing.calculate_best_price()
    if 'message' in result:
        print(f"⚠️  {ing.name}: {result['message']}")
```

---

## 🎯 Best Practices

### 1. Always Review Medium/Low Confidence Matches

Even with domain validation, manual review is critical:
- Check "Review Needed" sheet in Excel export
- Verify product specifications match intended use
- Confirm pack sizes are comparable

### 2. Update Specification Rules Regularly

As you discover new products:
```python
# Add to critical_specifications
matcher.critical_specifications['cinnamon'] = ['ground', 'stick', 'vietnamese', 'ceylon']

# Add to aliases
matcher.specification_aliases['ground'] = ['powdered', 'powder']
```

### 3. Track Actual Savings vs Projections

```python
# After implementing vendor changes
from datetime import datetime

actual_savings_tracking = {
    'month': datetime.now().strftime('%Y-%m'),
    'projected_savings': sum(m.savings_per_lb * estimated_usage for m in matches),
    'actual_savings': 0,  # Update from actual invoices
    'variance': 0
}
```

### 4. Version Control for Vendor Catalogs

Keep historical catalogs to track price changes:
```
data/vendor_catalogs/
├── sysco_2024_01.xlsx
├── sysco_2024_02.xlsx
├── shamrock_2024_01.xlsx
└── shamrock_2024_02.xlsx
```

---

## 📊 Performance Metrics

### Matching Quality Targets

- **HIGH confidence matches**: Should represent >60% of total matches
- **Specification validation**: 100% of matches must pass
- **Unmatched rate**: Should be <20% (most products have equivalents)
- **False positive rate**: <5% (matches that look good but aren't)

### Savings Targets

Based on historical data:
- **Average savings**: 29.5% with Shamrock Foods
- **Monthly savings potential**: $4,333
- **Annual savings potential**: $52,000

---

## 🔄 Integration Checklist

When integrating vendor matching into LariatBible:

- [ ] Export vendor catalogs to Excel/CSV
- [ ] Run HybridVendorMatcher on catalogs
- [ ] Review HIGH confidence matches (use immediately)
- [ ] Manually validate MEDIUM/LOW confidence matches
- [ ] Convert validated matches to Ingredient objects
- [ ] Import Ingredients into inventory system
- [ ] Update recipes to use new Ingredients
- [ ] Generate baseline savings report
- [ ] Set up monthly tracking for actual vs projected savings
- [ ] Document any new specification rules discovered

---

## 📝 Notes for Claude Code

### When Working on Vendor Matching:

1. **ALWAYS** use HybridVendorMatcher for new matching tasks
2. **NEVER** bypass specification validation
3. **CHECK** pack size parsing for unusual formats
4. **VALIDATE** matches manually when confidence < HIGH
5. **DOCUMENT** new specification rules in this file
6. **TEST** with real vendor data before production use
7. **EXPORT** results to Excel for human review

### Code Modification Guidelines:

- To add new product types: Update `critical_specifications`
- To add specification aliases: Update `specification_aliases`
- To add pack formats: Modify `CorrectedVendorComparison.interpret_pack_size()`
- To adjust confidence thresholds: Modify score cutoffs in `find_matches()`

---

**Last Updated:** 2024
**Version:** 1.0
**Maintained by:** Sean (The Lariat)
