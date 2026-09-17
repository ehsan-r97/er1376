# Zarvan Persian Calendar - Odoo 19 Production Module

[![Odoo Version](https://img.shields.io/badge/Odoo-19.0-green.svg)](https://www.odoo.com)
[![License](https://img.shields.io/badge/License-LGPL--3-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-19.0.1.0.0-orange.svg)]()

## Overview

Production-ready Jalali (Persian) calendar module for Odoo 19 with comprehensive holiday support, multi-company functionality, and REST API integration.

## Key Features

### Core Functionality
- **Bidirectional Date Conversion**: Accurate Jalali ↔ Gregorian conversion using `jdatetime` library
- **Iranian National Holidays**: Pre-loaded holidays for years 1400-1410
- **Fixed Holidays**: Automatically apply every year (Nowruz, Revolution Day, etc.)
- **Lunar Holidays**: Year-specific dates for Ashura, Arbaeen, etc.
- **Multi-Company Support**: Company-specific holidays and weekend configurations
- **User Preferences**: 5 different date format options

### Technical Excellence
- **Memory-Safe Caching**: Uses Odoo's native `@ormcache` instead of `@lru_cache` to prevent worker OOM crashes
- **Timezone-Safe**: No pytz on Date fields - prevents off-by-one errors
- **Client-Side Conversion**: JavaScript widget performs instant conversions without RPC calls
- **OWL 2.0 Components**: Modern frontend architecture with proper lifecycle management
- **Standard Field Props**: Proper form state management - Save button works correctly

### Infrastructure Ready
- ✅ Redis session caching compatible
- ✅ Nginx static asset serving ready
- ✅ PgBouncer connection pool safe
- ✅ Docker deployment supported
- ✅ Multi-worker Odoo compatible

## Installation

### Prerequisites
```bash
pip install jdatetime>=4.1.0 openpyxl>=3.0.10 python-dateutil>=2.8.2
```

### Module Installation
1. Copy `zarvan_calendar` to your Odoo addons directory
2. Update apps list: `Apps → Update Apps List`
3. Install "Zarvan Persian Calendar" from Apps menu

## Configuration

### Company Settings
Navigate to **Settings → Companies** and configure:
- **Fiscal Year Start**: Choose Jalali month for fiscal year
- **Weekend Type**: Select weekend pattern (Thu-Fri, Fri-Sat, Sat-Sun, or custom)
- **Auto-create Holidays**: Enable automatic holiday creation

### User Preferences
Navigate to **Settings → Users** and select:
- **Date Format**: Choose from 5 Persian date display formats

## API Endpoints

The module provides RESTful API endpoints for external integrations:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/jalaali/holidays/<year>` | GET | Get all holidays for a Jalali year |
| `/api/jalaali/is-holiday` | POST | Check if a date is a holiday |
| `/api/jalaali/convert/jalali-to-gregorian` | POST | Convert Jalali to Gregorian |
| `/api/jalaali/convert/gregorian-to-jalali` | POST | Convert Gregorian to Jalali |
| `/api/jalaali/current` | GET | Get current Jalali date |
| `/api/jalaali/working-days/<year>/<month>` | GET | Calculate working days in a month |

## Usage Examples

### Python Code
```python
# In your model
from odoo import models, api

class MyModel(models.Model):
    _inherit = ['jalaali.mixin']
    
    @api.model
    def some_method(self):
        # Convert Jalali to Gregorian
        g_date = self.jalali_to_gregorian(1405, 1, 1)
        
        # Auto-detect and parse date strings
        result = self.detect_and_parse_date("1405-01-01")
        if result['success']:
            gregorian_date = result['gregorian_date']
```

### Import Wizard
```python
# Process CSV/Excel with Persian dates
result = self.env['jalaali.mixin'].process_import_rows_with_dates(
    imported_rows,
    date_columns=['order_date', 'delivery_date']
)

if result['errors']:
    raise ValidationError("\n".join(result['errors']))

self.env['sale.order'].create(result['processed_rows'])
```

## Technical Details

### Fixed Issues in This Version
1. **Memory Leaks**: Replaced `@lru_cache` with Odoo's `@ormcache` decorator
2. **Data Corruption**: Removed pytz from Date field handling
3. **UI Data Loss**: Widget now uses `standardFieldProps` and `this.props.update()`
4. **Network Overload**: Client-side date conversion - no RPC calls on picker interaction
5. **Deployment Bloat**: Removed pandas dependency (~150MB savings)
6. **Leap Year Accuracy**: Uses `jdatetime.jalali.isleap()` for astronomical accuracy
7. **Empty Recordsets**: Added guards before `ensure_one()` calls
8. **XML Validation**: Fixed holiday_data.xml structure

### File Structure
```
zarvan_calendar/
├── __init__.py
├── __manifest__.py          # Module metadata (v19.0.1.0.0)
├── requirements.txt         # Python dependencies
├── data/
│   └── holiday_data.xml     # Iranian holidays 1400-1410
├── models/
│   ├── jalaali_holiday.py   # Holiday model
│   ├── jalaali_mixin.py     # Date conversion mixin
│   ├── jalaali_service.py   # Service layer API
│   └── res_company.py       # Company extensions
├── static/
│   └── src/
│       ├── js/
│       │   ├── components/
│       │   │   ├── jalali_status.js
│       │   │   └── holiday_badge.js
│       │   └── widgets/
│       │       └── jalali_date_picker.js
│       └── css/
│           └── zarvan_calendar.css
├── views/
│   ├── jalaali_holiday_views.xml
│   ├── res_users_views.xml
│   ├── res_company_views.xml
│   └── menu_views.xml
├── security/
│   ├── jalaali_security.xml
│   └── ir.model.access.csv
└── wizards/
    └── holiday_import_wizard.py
```

## Changelog

### 19.0.1.0.0 (Current)
- **FIXED**: Memory leaks from `@lru_cache` → `@ormcache`
- **FIXED**: Timezone issues on Date fields
- **FIXED**: OWL widget data loss with standardFieldProps
- **FIXED**: Client-side date conversion (no RPC)
- **FIXED**: Removed pandas dependency
- **FIXED**: Leap year calculation accuracy
- **FIXED**: Empty recordset guards
- **FIXED**: XML structure validation

## Support & Contact

- **Author**: Ehsan Rezaei
- **Email**: ehsan.r97@gmail.com
- **GitHub**: https://github.com/ehsan-r97/Odoo19Custom_Addons

## License

This module is licensed under LGPL-3. See LICENSE file for details.

---

**Note**: This module is production-ready and has been tested for multi-tenant, multi-worker environments with Redis, Nginx, and PgBouncer infrastructure.
