#!/usr/bin/env python
"""
The Lariat Bible - Main Application
Restaurant Management System Web Interface
"""

from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import os
import io
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'data', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
CORS(app)

# Ensure upload folder exists
Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)

# Import modules (when implemented)
try:
    from modules.vendor_analysis import VendorComparator, VendorCSVProcessor
    vendor_comparator = VendorComparator()
    csv_processor = VendorCSVProcessor(output_dir=os.path.join(os.path.dirname(__file__), 'data'))
except ImportError as e:
    print(f"Warning: Could not import vendor modules: {e}")
    vendor_comparator = None
    csv_processor = None

try:
    from modules.recipes import UnifiedRecipeBook, UnifiedRecipe
    recipe_book = UnifiedRecipeBook(data_dir=os.path.join(os.path.dirname(__file__), 'data'))
except ImportError as e:
    print(f"Warning: Could not import recipe modules: {e}")
    recipe_book = None

@app.route('/')
def index():
    """Main dashboard"""
    return jsonify({
        'message': 'Welcome to The Lariat Bible',
        'status': 'operational',
        'modules': {
            'vendor_analysis': 'ready' if vendor_comparator else 'pending',
            'inventory': 'pending',
            'recipes': 'pending',
            'catering': 'pending',
            'maintenance': 'pending',
            'reporting': 'pending'
        },
        'metrics': {
            'monthly_catering_revenue': 28000,
            'monthly_restaurant_revenue': 20000,
            'potential_annual_savings': 52000
        }
    })

@app.route('/api/vendor-comparison')
def vendor_comparison():
    """Get vendor comparison data"""
    if vendor_comparator:
        savings = vendor_comparator.compare_vendors('Shamrock Foods', 'SYSCO')
        margin_impact = vendor_comparator.calculate_margin_impact(savings)
        
        return jsonify({
            'monthly_savings': savings,
            'annual_savings': savings * 12,
            'margin_impact': margin_impact,
            'timestamp': datetime.now().isoformat()
        })
    
    return jsonify({'error': 'Vendor analysis module not available'}), 503

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'restaurant': os.getenv('RESTAURANT_NAME', 'The Lariat')
    })

@app.route('/api/modules')
def list_modules():
    """List all available modules and their status"""
    modules = [
        {
            'name': 'Vendor Analysis',
            'endpoint': '/vendor-analysis',
            'status': 'active' if vendor_comparator else 'development',
            'description': 'Compare vendor prices and identify savings'
        },
        {
            'name': 'CSV Upload & Compare',
            'endpoint': '/api/upload-vendor-csvs',
            'status': 'active' if csv_processor else 'development',
            'description': 'Upload Shamrock & Sysco CSVs and generate comparison Excel'
        },
        {
            'name': 'Recipe Book',
            'endpoint': '/api/recipes',
            'status': 'active' if recipe_book else 'development',
            'description': 'Unified recipe book with yields and instructions'
        },
        {
            'name': 'Inventory Management',
            'endpoint': '/inventory',
            'status': 'development',
            'description': 'Track stock levels and automate ordering'
        },
        {
            'name': 'Recipe Management',
            'endpoint': '/recipes',
            'status': 'development',
            'description': 'Standardize recipes and calculate costs'
        },
        {
            'name': 'Catering Operations',
            'endpoint': '/catering',
            'status': 'development',
            'description': 'Manage catering quotes and events'
        },
        {
            'name': 'Maintenance Tracking',
            'endpoint': '/maintenance',
            'status': 'development',
            'description': 'Schedule and track equipment maintenance'
        },
        {
            'name': 'Reporting Dashboard',
            'endpoint': '/reports',
            'status': 'development',
            'description': 'Business intelligence and analytics'
        }
    ]
    
    return jsonify(modules)


# ============ VENDOR CSV UPLOAD ENDPOINTS ============

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}


@app.route('/api/upload-vendor-csvs', methods=['POST'])
def upload_vendor_csvs():
    """
    Upload Shamrock and Sysco CSV files, combine them, and generate comparison Excel.
    
    Expects multipart form with:
    - shamrock_csv: Shamrock Foods CSV file
    - sysco_csv: Sysco CSV file
    - match_threshold (optional): Similarity threshold for matching (default: 0.6)
    
    Returns: JSON with summary stats and download link for Excel
    """
    if csv_processor is None:
        return jsonify({'error': 'CSV processor module not available'}), 503
    
    # Check for required files
    if 'shamrock_csv' not in request.files or 'sysco_csv' not in request.files:
        return jsonify({
            'error': 'Both shamrock_csv and sysco_csv files are required',
            'usage': 'POST multipart/form-data with shamrock_csv and sysco_csv files'
        }), 400
    
    shamrock_file = request.files['shamrock_csv']
    sysco_file = request.files['sysco_csv']
    
    # Validate files
    if shamrock_file.filename == '' or sysco_file.filename == '':
        return jsonify({'error': 'No files selected'}), 400
    
    if not (allowed_file(shamrock_file.filename) and allowed_file(sysco_file.filename)):
        return jsonify({'error': 'Only CSV files are allowed'}), 400
    
    try:
        # Get match threshold from form or use default
        match_threshold = float(request.form.get('match_threshold', 0.6))
        
        # Read CSV files into DataFrames with row limit for security
        # Limit to 10000 rows to prevent memory exhaustion
        MAX_ROWS = 10000
        shamrock_df = pd.read_csv(shamrock_file, nrows=MAX_ROWS)
        sysco_df = pd.read_csv(sysco_file, nrows=MAX_ROWS)
        
        # Validate that we got valid data
        if shamrock_df.empty or sysco_df.empty:
            return jsonify({'error': 'One or both CSV files are empty'}), 400
        
        # Load into processor
        csv_processor.load_shamrock_dataframe(shamrock_df)
        csv_processor.load_sysco_dataframe(sysco_df)
        
        # Combine and match
        combined = csv_processor.combine_vendor_data(match_threshold=match_threshold)
        
        if combined.empty:
            return jsonify({
                'message': 'No matching products found',
                'shamrock_products': len(shamrock_df),
                'sysco_products': len(sysco_df),
                'tip': 'Try lowering the match_threshold (default: 0.6)'
            }), 200
        
        # Generate Excel
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        excel_filename = f"vendor_comparison_{timestamp}.xlsx"
        excel_path = csv_processor.generate_comparison_excel(excel_filename)
        
        # Get summary stats
        stats = csv_processor.get_summary_stats()
        
        return jsonify({
            'message': 'Vendor comparison generated successfully',
            'excel_file': excel_filename,
            'download_url': f'/api/download/{excel_filename}',
            'summary': stats,
            'shamrock_products_loaded': len(shamrock_df),
            'sysco_products_loaded': len(sysco_df),
            'products_matched': stats.get('total_matched', 0),
            'timestamp': datetime.now().isoformat()
        })
        
    except pd.errors.EmptyDataError:
        return jsonify({'error': 'One or both CSV files are empty or invalid'}), 400
    except pd.errors.ParserError as e:
        return jsonify({'error': f'CSV parsing error: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<filename>')
def download_file(filename):
    """Download generated files."""
    safe_filename = secure_filename(filename)
    
    # Use pathlib to ensure path stays within data directory
    data_dir = Path(os.path.dirname(__file__)) / 'data'
    file_path = (data_dir / safe_filename).resolve()
    
    # Security check: ensure resolved path is still within data directory
    try:
        file_path.relative_to(data_dir.resolve())
    except ValueError:
        return jsonify({'error': 'Invalid file path'}), 400
    
    if not file_path.exists():
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(
        str(file_path),
        as_attachment=True,
        download_name=safe_filename
    )


@app.route('/api/vendor-comparison-stats')
def get_vendor_comparison_stats():
    """Get the latest vendor comparison statistics."""
    if csv_processor is None:
        return jsonify({'error': 'CSV processor module not available'}), 503
    
    stats = csv_processor.get_summary_stats()
    
    if not stats:
        return jsonify({
            'message': 'No comparison data available. Upload vendor CSVs first.',
            'upload_endpoint': '/api/upload-vendor-csvs'
        }), 200
    
    return jsonify({
        'stats': stats,
        'timestamp': datetime.now().isoformat()
    })


# ============ RECIPE BOOK ENDPOINTS ============

@app.route('/api/recipes', methods=['GET'])
def list_recipes():
    """List all recipes in the recipe book."""
    if recipe_book is None:
        return jsonify({'error': 'Recipe module not available'}), 503
    
    category = request.args.get('category')
    recipes = recipe_book.list_recipes(category=category)
    
    return jsonify({
        'recipes': [r.to_dict() for r in recipes],
        'total': len(recipes),
        'category_filter': category
    })


@app.route('/api/recipes/<recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    """Get a specific recipe by ID."""
    if recipe_book is None:
        return jsonify({'error': 'Recipe module not available'}), 503
    
    recipe = recipe_book.get_recipe(recipe_id)
    
    if recipe is None:
        return jsonify({'error': f'Recipe {recipe_id} not found'}), 404
    
    return jsonify(recipe.to_dict())


@app.route('/api/recipes', methods=['POST'])
def create_recipe():
    """Create a new recipe."""
    if recipe_book is None:
        return jsonify({'error': 'Recipe module not available'}), 503
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'JSON body required'}), 400
    
    try:
        from modules.recipes import UnifiedRecipe
        recipe = UnifiedRecipe.from_dict(data)
        recipe_id = recipe_book.add_recipe(recipe)
        
        return jsonify({
            'message': 'Recipe created successfully',
            'recipe_id': recipe_id,
            'recipe': recipe.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/recipes/import', methods=['POST'])
def import_recipes():
    """Import recipes from a CSV file."""
    if recipe_book is None:
        return jsonify({'error': 'Recipe module not available'}), 503
    
    if 'file' not in request.files:
        return jsonify({'error': 'CSV file required'}), 400
    
    file = request.files['file']
    
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Valid CSV file required'}), 400
    
    try:
        # Save temporarily
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        file.save(temp_path)
        
        # Import
        count = recipe_book.import_from_csv(temp_path)
        
        # Clean up
        os.remove(temp_path)
        
        return jsonify({
            'message': f'Imported {count} recipes successfully',
            'recipes_imported': count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recipes/export/json')
def export_recipes_json():
    """Export recipe book to JSON."""
    if recipe_book is None:
        return jsonify({'error': 'Recipe module not available'}), 503
    
    try:
        file_path = recipe_book.export_to_json()
        filename = os.path.basename(file_path)
        
        return jsonify({
            'message': 'Recipe book exported to JSON',
            'download_url': f'/api/download/{filename}',
            'recipes_exported': len(recipe_book.recipes)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recipes/export/excel')
def export_recipes_excel():
    """Export recipe book to Excel with multiple sheets."""
    if recipe_book is None:
        return jsonify({'error': 'Recipe module not available'}), 503
    
    try:
        file_path = recipe_book.export_to_excel()
        filename = os.path.basename(file_path)
        
        return jsonify({
            'message': 'Recipe book exported to Excel',
            'download_url': f'/api/download/{filename}',
            'recipes_exported': len(recipe_book.recipes),
            'sheets': ['Recipe Index', 'Full Recipes', 'Ingredients Master', 'Category Summary']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recipes/summary')
def recipe_summary():
    """Get recipe book summary statistics."""
    if recipe_book is None:
        return jsonify({'error': 'Recipe module not available'}), 503
    
    return jsonify(recipe_book.get_summary())

if __name__ == '__main__':
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"\n🤠 The Lariat Bible - Starting server...")
    print(f"📍 Access at: http://{host}:{port}")
    print(f"📊 API Health: http://{host}:{port}/api/health")
    print(f"🔧 Debug mode: {debug}")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(host=host, port=port, debug=debug)
