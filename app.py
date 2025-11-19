#!/usr/bin/env python
"""
The Lariat Bible - Main Application
Restaurant Management System Web Interface
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
CORS(app)

# WiFi configuration storage (in production, use a database)
WIFI_CONFIG_FILE = 'data/wifi_config.json'
PORTAL_CONFIG_FILE = 'data/portal_config.json'

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Import modules (when implemented)
try:
    from modules.vendor_analysis import VendorComparator
    vendor_comparator = VendorComparator()
except ImportError:
    vendor_comparator = None

@app.route('/')
def index():
    """Main dashboard - serve the web UI"""
    return send_from_directory('static', 'index.html')

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

@app.route('/health')
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

# ============================================================================
# VENDOR API ENDPOINTS
# ============================================================================

@app.route('/api/vendors')
def get_vendors():
    """Get all vendor information"""
    return jsonify({
        'vendors': [
            {
                'name': 'SYSCO',
                'products': 150,
                'total_cost': 12500,
                'avg_savings': '18%'
            },
            {
                'name': 'Shamrock Foods',
                'products': 145,
                'total_cost': 8900,
                'avg_savings': '29.5%'
            }
        ],
        'total_savings': 52000
    })

# ============================================================================
# RECIPE API ENDPOINTS
# ============================================================================

@app.route('/api/recipes')
def get_recipes():
    """Get all recipes"""
    return jsonify({
        'recipes': [
            {
                'id': 1,
                'name': 'Western Burger',
                'ingredients': 12,
                'cost': 4.50,
                'category': 'Burgers'
            },
            {
                'id': 2,
                'name': 'BBQ Ribs',
                'ingredients': 8,
                'cost': 8.75,
                'category': 'Entrees'
            },
            {
                'id': 3,
                'name': 'House Salad',
                'ingredients': 10,
                'cost': 2.25,
                'category': 'Salads'
            }
        ]
    })

@app.route('/api/recipes/<int:recipe_id>')
def get_recipe(recipe_id):
    """Get specific recipe details"""
    return jsonify({
        'id': recipe_id,
        'name': 'Western Burger',
        'ingredients': [],
        'cost': 4.50
    })

# ============================================================================
# MENU API ENDPOINTS
# ============================================================================

@app.route('/api/menu')
def get_menu():
    """Get all menu items"""
    return jsonify({
        'items': [
            {
                'id': 1,
                'name': 'Western Burger',
                'price': 12.99,
                'cost': 4.50,
                'margin': '65%'
            },
            {
                'id': 2,
                'name': 'BBQ Ribs',
                'price': 18.99,
                'cost': 8.75,
                'margin': '54%'
            }
        ]
    })

# ============================================================================
# EQUIPMENT API ENDPOINTS
# ============================================================================

@app.route('/api/equipment')
def get_equipment():
    """Get all equipment"""
    return jsonify({
        'equipment': [
            {
                'id': 1,
                'name': 'Industrial Oven',
                'purchase_date': '2022-03-15',
                'cost': 8500,
                'status': 'operational',
                'next_maintenance': '2025-12-01'
            },
            {
                'id': 2,
                'name': 'Walk-in Freezer',
                'purchase_date': '2021-06-20',
                'cost': 12000,
                'status': 'operational',
                'next_maintenance': '2025-11-25'
            }
        ]
    })

# ============================================================================
# WIFI API ENDPOINTS
# ============================================================================

@app.route('/api/wifi/config', methods=['GET', 'POST'])
def wifi_config():
    """Get or set WiFi configuration"""
    if request.method == 'POST':
        config = request.get_json()

        # Save configuration to file
        try:
            with open(WIFI_CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)

            return jsonify({
                'success': True,
                'message': 'WiFi configuration saved',
                'config': config
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # GET request - return current config
    try:
        if os.path.exists(WIFI_CONFIG_FILE):
            with open(WIFI_CONFIG_FILE, 'r') as f:
                config = json.load(f)
            return jsonify(config)
        else:
            return jsonify({
                'ssid': '',
                'type': 'guest',
                'message': 'No configuration saved yet'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/wifi/portal', methods=['GET', 'POST'])
def captive_portal_config():
    """Get or set captive portal configuration"""
    if request.method == 'POST':
        config = request.get_json()

        # Save configuration to file
        try:
            with open(PORTAL_CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)

            return jsonify({
                'success': True,
                'message': 'Captive portal configuration saved',
                'config': config
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # GET request - return current config
    try:
        if os.path.exists(PORTAL_CONFIG_FILE):
            with open(PORTAL_CONFIG_FILE, 'r') as f:
                config = json.load(f)
            return jsonify(config)
        else:
            return jsonify({
                'enabled': False,
                'message': 'Welcome to The Lariat! Free WiFi for our guests.',
                'redirect': 'https://thelariat.com'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/wifi/devices')
def get_connected_devices():
    """Get list of connected devices"""
    return jsonify({
        'devices': [
            {
                'name': 'Kitchen POS #1',
                'ip': '192.168.1.101',
                'mac': '00:11:22:33:44:55',
                'online': True,
                'connected_at': '2025-11-19T08:00:00Z'
            },
            {
                'name': 'Bar POS #2',
                'ip': '192.168.1.102',
                'mac': '00:11:22:33:44:56',
                'online': True,
                'connected_at': '2025-11-19T08:00:00Z'
            },
            {
                'name': 'Guest-Device-A3F2',
                'ip': '192.168.1.203',
                'mac': '00:11:22:33:44:57',
                'online': True,
                'connected_at': '2025-11-19T10:30:00Z'
            }
        ],
        'total': 3
    })

@app.route('/api/wifi/stats')
def get_network_stats():
    """Get network statistics"""
    return jsonify({
        'devices': 3,
        'bandwidth': '45 MB/s',
        'uptime': 99.8,
        'total_data_today': '2.3 GB',
        'peak_devices': 12,
        'avg_devices': 7
    })

@app.route('/api/wifi/scan')
def scan_networks():
    """Scan for available WiFi networks"""
    return jsonify({
        'networks': [
            {
                'ssid': 'The Lariat Guest WiFi',
                'signal': 95,
                'secured': True,
                'channel': 6
            },
            {
                'ssid': 'The Lariat Staff',
                'signal': 92,
                'secured': True,
                'channel': 11
            },
            {
                'ssid': 'The Lariat POS',
                'signal': 88,
                'secured': True,
                'channel': 1
            }
        ]
    })

# ============================================================================
# CAPTIVE PORTAL PAGE
# ============================================================================

@app.route('/portal')
def captive_portal():
    """Captive portal landing page for guest WiFi"""
    return send_from_directory('static', 'portal.html')

@app.route('/portal/connect', methods=['POST'])
def portal_connect():
    """Handle captive portal connection"""
    data = request.get_json()

    # In production, you would validate the connection here
    # For now, just accept it

    return jsonify({
        'success': True,
        'message': 'Connected to The Lariat Guest WiFi',
        'redirect': data.get('redirect', 'https://thelariat.com')
    })

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
