# The Lariat Bible - Independent UI with WiFi Management

## Overview

This update adds a **completely independent web UI** with comprehensive **WiFi management functionality** to The Lariat Bible restaurant management system.

## 🎯 Key Features

### 1. **Independent Web Interface**
- ✅ **Standalone Operation**: UI works independently with or without backend
- ✅ **No Framework Dependencies**: Pure HTML/CSS/JavaScript (no React, Vue, etc.)
- ✅ **Responsive Design**: Works on desktop, tablet, and mobile devices
- ✅ **Local Storage**: Saves configurations even in standalone mode
- ✅ **Mock Data**: Continues functioning even if backend is offline

### 2. **WiFi Management System**
- ✅ **Network Configuration**: Set up guest, staff, and POS networks
- ✅ **Captive Portal**: Custom welcome page for guest WiFi
- ✅ **Device Tracking**: Monitor connected devices in real-time
- ✅ **Network Statistics**: View bandwidth usage, uptime, and device counts
- ✅ **Network Scanner**: Scan and display available WiFi networks
- ✅ **Status Bar**: Always-visible WiFi connection indicator

### 3. **Restaurant Management Dashboard**
- ✅ **Vendor Comparison**: SYSCO vs Shamrock Foods analysis
- ✅ **Recipe Management**: Browse and search recipes
- ✅ **Menu Pricing**: Track menu items with cost analysis
- ✅ **Equipment Tracker**: Monitor equipment and maintenance schedules
- ✅ **Real-time Metrics**: Annual savings, recipe counts, menu items

## 📁 File Structure

```
lariat-bible/
├── static/
│   ├── index.html          # Main dashboard UI
│   ├── portal.html         # Captive portal page
│   ├── css/
│   │   ├── main.css        # Main application styles
│   │   └── wifi.css        # WiFi-specific styles
│   └── js/
│       ├── api.js          # API communication layer
│       ├── wifi.js         # WiFi management logic
│       └── main.js         # Main application logic
├── app.py                  # Flask backend (enhanced with WiFi endpoints)
└── data/                   # Configuration storage
    ├── wifi_config.json    # WiFi settings
    └── portal_config.json  # Captive portal settings
```

## 🚀 Getting Started

### Prerequisites

```bash
pip install flask flask-cors python-dotenv
```

### Running the Application

#### Option 1: With Backend (Full Features)

```bash
python app.py
```

Then open: http://127.0.0.1:5000

#### Option 2: Standalone (No Backend Required)

Simply open `static/index.html` in any web browser. The UI will:
- Run completely independently
- Use localStorage for configuration persistence
- Display mock data for demonstration
- Show "Standalone Mode" status indicators

## 📡 WiFi Features in Detail

### Network Configuration

Configure different network types:
- **Guest Network**: Public WiFi for customers
- **Staff Network**: Secured WiFi for employees
- **POS Systems**: Dedicated network for point-of-sale devices

**Location**: WiFi Manager Tab → Network Configuration

### Captive Portal

Custom landing page shown when guests connect to WiFi:
- Welcome message customization
- Terms of service acceptance
- Custom redirect URL
- Branding with restaurant logo

**Access**: http://127.0.0.1:5000/portal

### Connected Devices

Real-time monitoring of:
- Device names and IP addresses
- MAC addresses
- Connection timestamps
- Online/offline status

### Network Statistics

- Total connected devices
- Current bandwidth usage
- 30-day uptime percentage
- Peak device counts
- Daily data usage

## 🔌 API Endpoints

### WiFi Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/wifi/config` | GET | Get WiFi configuration |
| `/api/wifi/config` | POST | Save WiFi configuration |
| `/api/wifi/portal` | GET | Get captive portal config |
| `/api/wifi/portal` | POST | Save captive portal config |
| `/api/wifi/devices` | GET | List connected devices |
| `/api/wifi/stats` | GET | Network statistics |
| `/api/wifi/scan` | GET | Scan available networks |
| `/portal` | GET | Captive portal page |
| `/portal/connect` | POST | Handle portal login |

### Restaurant Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/vendors` | GET | List all vendors |
| `/api/recipes` | GET | List all recipes |
| `/api/recipes/:id` | GET | Get specific recipe |
| `/api/menu` | GET | List menu items |
| `/api/equipment` | GET | List equipment |

## 💾 Configuration Storage

### WiFi Configuration Example

```json
{
  "ssid": "The Lariat Guest WiFi",
  "password": "********",
  "type": "guest",
  "timestamp": "2025-11-19T12:00:00Z"
}
```

### Captive Portal Configuration Example

```json
{
  "enabled": true,
  "message": "Welcome to The Lariat! Free WiFi for our guests.",
  "redirect": "https://thelariat.com",
  "timestamp": "2025-11-19T12:00:00Z"
}
```

Configurations are saved to:
- **Backend mode**: `data/wifi_config.json` and `data/portal_config.json`
- **Standalone mode**: Browser localStorage

## 🎨 UI Components

### Tab Navigation
- Dashboard
- Vendors
- Recipes
- Menu
- Equipment
- WiFi Manager

### WiFi Status Bar
- Always visible at top of page
- Shows connection status with icon
- Quick access to WiFi settings
- Real-time status updates

### Responsive Design
- Mobile-friendly layout
- Touch-optimized controls
- Adaptive grid layouts
- Hamburger menu on mobile (future enhancement)

## 🔧 Technical Details

### Independent Operation

The UI is designed to work completely independently:

1. **API Fallback**: If backend unavailable, uses mock data
2. **Local Storage**: Saves settings in browser
3. **No Build Step**: No webpack, npm, or compilation required
4. **Progressive Enhancement**: Basic features work everywhere

### Browser Compatibility

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

### Performance

- Zero dependencies = fast loading
- CSS animations for smooth UX
- Lazy loading of tab content
- Efficient DOM updates

## 📱 Mobile Features

- Responsive grid layouts
- Touch-friendly buttons (min 44px)
- Optimized font sizes
- Swipe-friendly navigation
- Mobile-optimized forms

## 🔐 Security Considerations

### Production Deployment

For production use, implement:

1. **HTTPS**: Enable SSL/TLS for all connections
2. **Authentication**: Add user authentication for admin features
3. **WiFi Password Security**: Store passwords securely (hashed)
4. **Rate Limiting**: Prevent abuse of captive portal
5. **Input Validation**: Sanitize all user inputs
6. **CORS Configuration**: Restrict allowed origins

### Current Implementation

- Passwords stored in plain text (development only)
- No authentication required (demo mode)
- Open CORS policy (allow all origins)

**⚠️ Do not deploy to production without security enhancements!**

## 🎯 Use Cases

### Restaurant Owners
- Monitor WiFi usage and connected devices
- Configure guest WiFi with custom portal
- Track equipment maintenance
- Analyze vendor costs

### Staff
- Access network information
- Check device connectivity
- View maintenance schedules
- Access recipe costs

### Guests
- Connect to free WiFi via captive portal
- Seamless connection experience
- No registration required

## 🛠️ Customization

### Branding

Edit `static/css/main.css`:

```css
:root {
    --primary-color: #8B4513;    /* Your brand color */
    --secondary-color: #D2691E;  /* Accent color */
    /* ... */
}
```

### Captive Portal

Edit `static/portal.html` to customize:
- Welcome message
- Logo/branding
- Terms of service
- Redirect behavior

### Mock Data

Edit `static/js/api.js` → `getMockData()` to customize demo data

## 📊 Future Enhancements

Potential additions:
- [ ] Real WiFi hardware integration (e.g., UniFi Controller API)
- [ ] Guest WiFi analytics dashboard
- [ ] Automated device blocking/allowlisting
- [ ] QR code generation for easy WiFi access
- [ ] Email collection before WiFi access
- [ ] Time-limited guest access
- [ ] Bandwidth throttling controls
- [ ] Multiple language support

## 🐛 Troubleshooting

### UI Not Loading
- Check that `static/` folder exists
- Verify Flask static folder configuration
- Check browser console for errors

### API Errors
- Verify Flask app is running: `python app.py`
- Check endpoint URLs match API routes
- Verify CORS is enabled

### Standalone Mode Issues
- Clear browser localStorage: `localStorage.clear()`
- Check browser console for JavaScript errors
- Verify file paths are correct

## 📖 Documentation

- Main project README: `README.md`
- Architecture: See codebase exploration report
- API docs: `/api/modules` endpoint

## 🤝 Contributing

When adding features:
1. Maintain independence (UI should work standalone)
2. Add mock data for offline mode
3. Update this README
4. Test on mobile devices
5. Follow existing code style

## 📄 License

Part of The Lariat Bible project.

## ✅ Status

- [x] Independent UI implemented
- [x] WiFi management functional
- [x] Captive portal working
- [x] Responsive design complete
- [x] API endpoints operational
- [x] Standalone mode tested
- [ ] Production deployment (pending)
- [ ] Real WiFi hardware integration (pending)

---

**Built with ❤️ for The Lariat Restaurant, Fort Collins, CO**
