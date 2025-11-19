"""
Integration Example: Using HybridVendorMatcher with LariatBible System

This script demonstrates how to:
1. Load vendor catalogs from Excel/CSV
2. Run hybrid fuzzy matching with domain validation
3. Convert matches to Ingredient objects
4. Save to database/inventory system
5. Generate comprehensive reports
"""

import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.vendor_analysis import HybridVendorMatcher
from modules.recipes.recipe import Ingredient


def load_vendor_catalog(file_path: str, vendor: str) -> pd.DataFrame:
    """
    Load vendor catalog from Excel or CSV

    Expected columns:
    - code: Vendor product code
    - description: Product description
    - pack: Pack size (e.g., "6/1LB", "25 LB")
    - price: Case/unit price
    - split_price: (optional) Split case price

    Args:
        file_path: Path to Excel or CSV file
        vendor: "SYSCO" or "Shamrock"

    Returns:
        DataFrame with standardized columns
    """
    file_path = Path(file_path)

    if file_path.suffix == '.xlsx':
        df = pd.read_excel(file_path)
    elif file_path.suffix == '.csv':
        df = pd.read_csv(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")

    # Standardize column names
    column_mapping = {
        'item_code': 'code',
        'product_code': 'code',
        'sku': 'code',
        'item_description': 'description',
        'product_description': 'description',
        'product_name': 'description',
        'pack_size': 'pack',
        'case_price': 'price',
        'unit_price': 'price',
    }

    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})

    # Ensure required columns exist
    required_columns = ['code', 'description', 'pack', 'price']
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for {vendor}: {missing}")

    # Add split_price column if not present
    if 'split_price' not in df.columns:
        df['split_price'] = None

    print(f"✅ Loaded {len(df)} products from {vendor} catalog")
    return df[['code', 'description', 'pack', 'price', 'split_price']]


def run_vendor_matching(sysco_file: str, shamrock_file: str,
                        output_excel: str = None,
                        similarity_threshold: float = 0.6) -> dict:
    """
    Run complete vendor matching workflow

    Args:
        sysco_file: Path to SYSCO catalog
        shamrock_file: Path to Shamrock catalog
        output_excel: Optional path for Excel output
        similarity_threshold: Minimum similarity score (0-1)

    Returns:
        Dictionary with matches and ingredient objects
    """
    print("\n" + "="*80)
    print("VENDOR MATCHING WORKFLOW")
    print("="*80)

    # Step 1: Load vendor catalogs
    print("\n📂 Step 1: Loading vendor catalogs...")
    sysco_df = load_vendor_catalog(sysco_file, "SYSCO")
    shamrock_df = load_vendor_catalog(shamrock_file, "Shamrock")

    # Step 2: Initialize matcher
    print("\n🔧 Step 2: Initializing hybrid matcher...")
    matcher = HybridVendorMatcher()

    # Step 3: Find matches
    print("\n🔍 Step 3: Finding matches with fuzzy matching + domain validation...")
    matches = matcher.find_matches(
        sysco_df,
        shamrock_df,
        similarity_threshold=similarity_threshold
    )

    # Step 4: Print summary
    print("\n📊 Step 4: Generating summary...")
    matcher.print_summary()

    # Step 5: Export to Excel
    if output_excel:
        print(f"\n📝 Step 5: Exporting to Excel...")
        matcher.export_to_excel(output_excel)

    # Step 6: Convert to Ingredient objects
    print("\n🏗️  Step 6: Converting to Ingredient objects...")
    ingredient_data = matcher.to_ingredient_models(matches)

    # Create actual Ingredient instances
    ingredients = []
    for data in ingredient_data:
        ing = Ingredient(**data)
        ingredients.append(ing)

    print(f"✅ Created {len(ingredients)} Ingredient objects")

    # Step 7: Analyze savings
    print("\n💰 Step 7: Analyzing savings potential...")
    analyze_savings(ingredients)

    return {
        'matches': matches,
        'ingredients': ingredients,
        'matcher': matcher
    }


def analyze_savings(ingredients: list):
    """Analyze potential savings from ingredient list"""
    high_savings = []
    total_potential_savings = 0

    for ing in ingredients:
        result = ing.calculate_best_price()
        if 'savings_per_unit' in result:
            # Estimate monthly usage (placeholder - should come from actual data)
            estimated_monthly_usage = 10  # lbs per month

            monthly_savings = result['savings_per_unit'] * estimated_monthly_usage
            total_potential_savings += monthly_savings

            if result['savings_percent'] > 20:  # High savings threshold
                high_savings.append({
                    'ingredient': ing.name,
                    'preferred_vendor': result['preferred_vendor'],
                    'savings_percent': result['savings_percent'],
                    'monthly_savings': monthly_savings
                })

    print(f"\n{'='*80}")
    print("SAVINGS ANALYSIS")
    print(f"{'='*80}")
    print(f"\nTotal ingredients analyzed: {len(ingredients)}")
    print(f"Estimated monthly savings: ${total_potential_savings:.2f}")
    print(f"Estimated annual savings: ${total_potential_savings * 12:.2f}")

    if high_savings:
        print(f"\n🔥 TOP SAVINGS OPPORTUNITIES (>20% savings):")
        print(f"{'='*80}")
        for item in sorted(high_savings, key=lambda x: x['savings_percent'], reverse=True)[:10]:
            print(f"  {item['ingredient']}")
            print(f"    Preferred: {item['preferred_vendor']}")
            print(f"    Savings: {item['savings_percent']:.1f}% (${item['monthly_savings']:.2f}/month)")
            print()


def save_ingredients_to_json(ingredients: list, output_file: str):
    """Save ingredients to JSON for database import"""
    import json

    data = []
    for ing in ingredients:
        # Convert Ingredient to dict (excluding datetime objects for JSON)
        ing_dict = {
            'ingredient_id': ing.ingredient_id,
            'name': ing.name,
            'category': ing.category,
            'unit_of_measure': ing.unit_of_measure,
            'case_size': ing.case_size,
            'sysco_item_code': ing.sysco_item_code,
            'sysco_price': ing.sysco_price,
            'sysco_unit_price': ing.sysco_unit_price,
            'shamrock_item_code': ing.shamrock_item_code,
            'shamrock_price': ing.shamrock_price,
            'shamrock_unit_price': ing.shamrock_unit_price,
            'preferred_vendor': ing.preferred_vendor,
            'price_difference': ing.price_difference,
            'price_difference_percent': ing.price_difference_percent,
        }
        data.append(ing_dict)

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n✅ Saved {len(ingredients)} ingredients to {output_file}")


# Example usage
if __name__ == "__main__":
    # Example file paths (adjust to your actual data files)
    sysco_catalog = "/home/user/lariat-bible/data/sysco_catalog.xlsx"
    shamrock_catalog = "/home/user/lariat-bible/data/shamrock_catalog.xlsx"
    output_excel = "/home/user/lariat-bible/data/vendor_matching_results.xlsx"
    output_json = "/home/user/lariat-bible/data/matched_ingredients.json"

    try:
        # Run matching workflow
        results = run_vendor_matching(
            sysco_catalog,
            shamrock_catalog,
            output_excel=output_excel,
            similarity_threshold=0.6
        )

        # Save ingredients for database import
        save_ingredients_to_json(results['ingredients'], output_json)

        print("\n" + "="*80)
        print("✅ INTEGRATION COMPLETE")
        print("="*80)
        print("\nGenerated files:")
        print(f"  📊 Excel Report: {output_excel}")
        print(f"  💾 JSON Data: {output_json}")
        print("\nNext steps:")
        print("  1. Review Excel report (especially 'Review Needed' sheet)")
        print("  2. Validate MEDIUM/LOW confidence matches manually")
        print("  3. Import JSON data to LariatBible inventory system")
        print("  4. Update recipes to use matched ingredients")
        print("  5. Track actual savings vs projections")

    except FileNotFoundError as e:
        print("\n⚠️  ERROR: Catalog file not found")
        print(f"    {e}")
        print("\n📝 To run this example:")
        print("  1. Export vendor catalogs to Excel/CSV")
        print("  2. Place files in /home/user/lariat-bible/data/")
        print("  3. Update file paths in this script")
        print("  4. Run: python integration_example.py")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
