"""
Report Generator Module
Generates comparison reports in various formats (JSON, CSV, text)
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

from modules.core.models import (
    VendorProduct,
    ProductComparison,
    SavingsSummary
)

logger = logging.getLogger(__name__)


# Target catering margin
TARGET_CATERING_MARGIN = 0.45


class ReportGenerator:
    """Generate vendor comparison reports in various formats"""

    def __init__(self):
        self.comparisons: List[ProductComparison] = []
        self.sysco_only: List[VendorProduct] = []
        self.shamrock_only: List[VendorProduct] = []

    def set_data(
        self,
        comparisons: List[ProductComparison],
        sysco_only: Optional[List[VendorProduct]] = None,
        shamrock_only: Optional[List[VendorProduct]] = None
    ):
        """
        Set the comparison data for report generation

        Args:
            comparisons: List of product comparisons
            sysco_only: Products only available at SYSCO
            shamrock_only: Products only available at Shamrock
        """
        self.comparisons = comparisons
        self.sysco_only = sysco_only or []
        self.shamrock_only = shamrock_only or []

    def calculate_summary(self) -> SavingsSummary:
        """
        Calculate savings summary from comparison data

        Returns:
            SavingsSummary with totals and counts
        """
        summary = SavingsSummary()

        for comp in self.comparisons:
            sysco_price = comp.sysco_product.unit_price
            shamrock_price = comp.shamrock_product.unit_price

            summary.total_sysco_cost += sysco_price
            summary.total_shamrock_cost += shamrock_price

            if shamrock_price < sysco_price:
                summary.products_cheaper_shamrock += 1
                summary.total_savings += (sysco_price - shamrock_price)
            elif sysco_price < shamrock_price:
                summary.products_cheaper_sysco += 1
            else:
                summary.products_equal += 1

        # Estimate monthly/annual savings
        # Assume comparison is for a typical order
        summary.monthly_savings = summary.total_savings * 4  # ~4 orders/month
        summary.annual_savings = summary.monthly_savings * 12

        return summary

    def generate_text_report(self) -> str:
        """
        Generate a formatted text report

        Returns:
            Formatted text report string
        """
        summary = self.calculate_summary()

        lines = []
        lines.append("=" * 70)
        lines.append("THE LARIAT - VENDOR COMPARISON REPORT")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 70)

        # Executive summary
        lines.append("\n📊 EXECUTIVE SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Total Products Compared: {len(self.comparisons)}")
        lines.append(f"Products Cheaper at Shamrock: {summary.products_cheaper_shamrock}")
        lines.append(f"Products Cheaper at SYSCO: {summary.products_cheaper_sysco}")
        lines.append(f"Products with Equal Pricing: {summary.products_equal}")
        lines.append(f"\nEstimated Monthly Savings: ${summary.monthly_savings:,.2f}")
        lines.append(f"Estimated Annual Savings: ${summary.annual_savings:,.2f}")

        # Products cheaper at Shamrock
        shamrock_wins = [
            c for c in self.comparisons
            if c.shamrock_product.unit_price < c.sysco_product.unit_price
        ]
        if shamrock_wins:
            lines.append("\n\n💚 PRODUCTS CHEAPER AT SHAMROCK")
            lines.append("-" * 40)
            shamrock_wins.sort(key=lambda x: x.price_difference, reverse=True)
            for comp in shamrock_wins[:20]:  # Top 20
                savings_pct = comp.savings_percent
                lines.append(
                    f"  {comp.sysco_product.product_name[:40]:<40} "
                    f"Save ${comp.price_difference:.2f}/unit ({savings_pct:.1f}%)"
                )

        # Products cheaper at SYSCO
        sysco_wins = [
            c for c in self.comparisons
            if c.sysco_product.unit_price < c.shamrock_product.unit_price
        ]
        if sysco_wins:
            lines.append("\n\n🔵 PRODUCTS CHEAPER AT SYSCO")
            lines.append("-" * 40)
            sysco_wins.sort(key=lambda x: -x.price_difference)
            for comp in sysco_wins[:20]:  # Top 20
                diff = abs(comp.price_difference)
                pct = abs(comp.savings_percent)
                lines.append(
                    f"  {comp.sysco_product.product_name[:40]:<40} "
                    f"Save ${diff:.2f}/unit ({pct:.1f}%)"
                )

        # Products only at one vendor
        if self.sysco_only:
            lines.append("\n\n⚪ PRODUCTS ONLY AT SYSCO")
            lines.append("-" * 40)
            for prod in self.sysco_only[:10]:
                lines.append(f"  {prod.product_name[:50]} - ${prod.case_price:.2f}/case")

        if self.shamrock_only:
            lines.append("\n\n⚪ PRODUCTS ONLY AT SHAMROCK")
            lines.append("-" * 40)
            for prod in self.shamrock_only[:10]:
                lines.append(f"  {prod.product_name[:50]} - ${prod.case_price:.2f}/case")

        # Margin impact analysis
        lines.append("\n\n📈 MARGIN IMPACT ANALYSIS")
        lines.append("-" * 40)
        lines.append(f"Target Catering Margin: {TARGET_CATERING_MARGIN * 100:.0f}%")

        catering_revenue = 28000  # Monthly
        if summary.monthly_savings > 0:
            margin_impact = (summary.monthly_savings / catering_revenue) * 100
            lines.append(f"Margin Improvement: +{margin_impact:.2f}%")
            lines.append(f"Additional Monthly Profit: ${summary.monthly_savings:,.2f}")

        # Recommendations
        lines.append("\n\n📋 RECOMMENDATIONS")
        lines.append("-" * 40)

        if summary.products_cheaper_shamrock > summary.products_cheaper_sysco:
            lines.append("1. ✅ Prioritize Shamrock Foods for primary ordering")
            lines.append("2. 📦 Use SYSCO for specific items where pricing is better")
        else:
            lines.append("1. ✅ Review individual product pricing carefully")
            lines.append("2. 📦 Consider split ordering between vendors")

        lines.append("3. 📊 Re-evaluate pricing quarterly")
        lines.append("4. 💰 Track actual vs projected savings monthly")

        lines.append("\n" + "=" * 70)

        return "\n".join(lines)

    def generate_json_report(self) -> Dict:
        """
        Generate a JSON-compatible report dictionary

        Returns:
            Dictionary containing all report data
        """
        summary = self.calculate_summary()

        return {
            'generated_at': datetime.now().isoformat(),
            'summary': summary.to_dict(),
            'comparisons': [
                {
                    'product_name': c.sysco_product.product_name,
                    'sysco_code': c.sysco_product.product_code,
                    'sysco_price': c.sysco_product.unit_price,
                    'sysco_pack': c.sysco_product.unit_size,
                    'shamrock_code': c.shamrock_product.product_code,
                    'shamrock_price': c.shamrock_product.unit_price,
                    'shamrock_pack': c.shamrock_product.unit_size,
                    'price_difference': c.price_difference,
                    'savings_percent': c.savings_percent,
                    'confidence': c.confidence,
                    'recommendation': c.recommendation
                }
                for c in self.comparisons
            ],
            'sysco_only': [p.to_dict() for p in self.sysco_only],
            'shamrock_only': [p.to_dict() for p in self.shamrock_only],
            'margin_analysis': {
                'target_margin': TARGET_CATERING_MARGIN,
                'monthly_catering_revenue': 28000,
                'monthly_restaurant_revenue': 20000,
                'potential_margin_improvement': (
                    summary.monthly_savings / 28000 * 100
                    if summary.monthly_savings > 0 else 0
                )
            }
        }

    def generate_csv_report(self, output_path: str):
        """
        Generate a CSV report file

        Args:
            output_path: Path to save the CSV file
        """
        headers = [
            'Product Name',
            'SYSCO Code',
            'SYSCO Pack',
            'SYSCO Price/Unit',
            'Shamrock Code',
            'Shamrock Pack',
            'Shamrock Price/Unit',
            'Price Difference',
            'Savings %',
            'Confidence',
            'Recommendation'
        ]

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for comp in self.comparisons:
                writer.writerow([
                    comp.sysco_product.product_name,
                    comp.sysco_product.product_code,
                    comp.sysco_product.unit_size,
                    f"{comp.sysco_product.unit_price:.4f}",
                    comp.shamrock_product.product_code,
                    comp.shamrock_product.unit_size,
                    f"{comp.shamrock_product.unit_price:.4f}",
                    f"{comp.price_difference:.4f}",
                    f"{comp.savings_percent:.2f}",
                    f"{comp.confidence:.2f}",
                    comp.recommendation
                ])

        logger.info(f"CSV report saved to {output_path}")

    def save_text_report(self, output_path: str):
        """Save text report to file"""
        report = self.generate_text_report()
        Path(output_path).write_text(report, encoding='utf-8')
        logger.info(f"Text report saved to {output_path}")

    def save_json_report(self, output_path: str):
        """Save JSON report to file"""
        report = self.generate_json_report()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        logger.info(f"JSON report saved to {output_path}")
