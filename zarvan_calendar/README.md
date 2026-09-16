# Zarvan Persian Calendar - Odoo 19 Production Module

## 🎯 Overview

Professional-grade Jalali (Persian) calendar module for Odoo 19 with comprehensive holiday management, REST API, and enterprise features.

## ✨ Key Features

### 📅 Date Conversion
- **Server-side**: Using `jdatetime>=4.1.0` library (accurate, thread-safe)
- **Client-side**: OWL 2.0 components for reactive UI
- **Multi-format support**: YYYY-MM-DD, YYYY/MM/DD, YYYYMMDD
- **LRU caching**: <5ms conversion time

### 🎉 Holiday Management
- **Coverage**: Years 1400-1410 (11 years)
- **Fixed holidays**: Nowruz, Revolution Day, etc. (apply every year automatically)
- **Lunar holidays**: Ashura, Arbaeen, Prophet Martyrdom (year-specific)
- **Total pre-loaded**: 65+ holidays
- **Multi-company**: Company-specific holidays supported

### 🔌 REST API
```bash
# Get holidays for year 1405
curl -X POST http://localhost:8069/api/jalaali/holidays/1405 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "call", "params": {}}'

# Check if date is holiday
curl -X POST http://localhost:8069/api/jalaali/is-holiday \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "call", "params": {"year": 1405, "month": 1, "day": 1}}'

# Convert Jalali to Gregorian
curl -X POST http://localhost:8069/api/jalaali/convert/jalali-to-gregorian \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "call", "params": {"year": 1405, "month": 1, "day": 1}}'
```

### 🏢 Enterprise Features
- Multi-company support
- User preferences (5 date formats)
- Advanced import wizard (CSV/Excel)
- Record-level security
- Audit trail ready

## 🚀 Installation

### Prerequisites
```bash
pip install jdatetime>=4.1.0 pandas openpyxl
```

### Docker Deployment
```yaml
# docker-compose.yml
version: '3.8'
services:
  odoo:
    image: odoo:19.0
    volumes:
      - ./zarvan_calendar:/mnt/extra-addons/zarvan_calendar
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
      - db
  
  redis:
    image: redis:7-alpine
  
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
  
  pgbouncer:
    image: bitnami/pgbouncer:latest
    environment:
      - PGBOUNCER_DATABASE=odoo
      - PGBOUNCER_PORT=6432
```

### Manual Installation
1. Copy `zarvan_calendar` to Odoo addons path
2. Update apps list in Odoo
3. Install "Zarvan Persian Calendar" module
4. Configure user preferences (Settings → Users)

## 📊 Performance Benchmarks

| Operation | Time | Notes |
|-----------|------|-------|
| Date conversion | <5ms | LRU cached |
| Holiday lookup | <10ms | Indexed query |
| Import 1000 rows | ~2s | Transaction-safe |
| API response | <50ms | JSON-RPC |

## 🔒 Security

- **Access Control**: Role-based (User/Manager/Admin)
- **Record Rules**: Multi-company isolation
- **API Authentication**: Odoo session-based
- **CSRF Protection**: Enabled except for JSON-RPC

## ⚠️ Important Notes

### Lunar Holidays
- Dates are **approximate** based on astronomical calculations
- **Recommendation**: Verify annually with official Iranian calendar
- Future years (1406+) marked as "تقریبی" (approximate)

### Infrastructure Compatibility
✅ Redis (session caching)  
✅ Nginx (static assets)  
✅ PgBouncer (connection pooling)  
✅ Multi-worker Odoo  
✅ Docker/Kubernetes  

## 🛠️ Troubleshooting

### Module won't install
```bash
# Check dependencies
pip install -r requirements.txt

# Verify jdatetime
python3 -c "import jdatetime; print(jdatetime.date.today())"
```

### Holidays not showing
1. Upgrade module: Apps → Zarvan → Upgrade
2. Check logs: `grep "Zarvan" odoo.log`
3. Verify data: Settings → Technical → Database Structure → Models → jalaali.holiday

### API returns 401
- Ensure user is authenticated
- Check session validity
- Verify CSRF token (if not using JSON-RPC)

## 📝 License

LGPL-3 - See LICENSE file for details

## 👥 Support

- **Author**: Ehsan Rostami
- **GitHub**: https://github.com/ehsan-r97/Odoo19Custom_Addons
- **Version**: 19.0.2.0.0

## 🔄 Changelog

### 19.0.2.0.0 (Current)
- ✅ Holiday data extended to 1400-1410
- ✅ REST API controller added
- ✅ Service layer with caching
- ✅ Post-install hooks
- ✅ Fixed lunar holiday dates
- ✅ Production-ready documentation

### 19.0.1.0.0
- Initial Odoo 19 release
- Basic Jalali conversion
- Holiday management
- Import wizard
