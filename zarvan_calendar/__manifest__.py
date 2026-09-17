# -*- coding: utf-8 -*-
{
    'name': 'Zarvan Persian Calendar',
    'version': '19.0.1.0.0',
    'category': 'Localization/Iran',
    'summary': 'Production-ready Jalali (Persian) calendar with holidays for 1400-1410, REST API, and multi-company support',
    'description': """
Zarvan Persian Calendar - Odoo 19 Production Module
====================================================

Features:
---------
* Jalali (Persian) date conversion using jdatetime library
* Iranian national holidays pre-loaded for years 1400-1410
* Fixed holidays (Nowruz, Revolution Day, etc.) apply every year automatically
* Lunar holidays (Ashura, Arbaeen, etc.) with specific year dates
* Multi-company support with company-specific holidays
* User preferences for date format (5 formats available)
* Advanced import wizard for CSV/Excel holiday data
* RESTful API for external integrations
* OWL 2.0 components for modern UI
* Thread-safe operations with ORM caching
* Compatible with Redis, Nginx, PgBouncer infrastructure

API Endpoints:
--------------
* GET  /api/jalaali/holidays/<year>
* POST /api/jalaali/is-holiday
* POST /api/jalaali/convert/jalali-to-gregorian
* POST /api/jalaali/convert/gregorian-to-jalali
* GET  /api/jalaali/current
* GET  /api/jalaali/working-days/<year>/<month>

Infrastructure Ready:
--------------------
* Redis session caching compatible
* Nginx static asset serving ready
* PgBouncer connection pool safe
* Docker deployment supported
* Multi-worker Odoo compatible
    """,
    'author': 'Ehsan Rezaei',
    'website': 'https://github.com/ehsan-r97/Odoo19Custom_Addons',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'mail'],
    'data': [
        'security/jalaali_security.xml',
        'security/ir.model.access.csv',
        'data/holiday_data.xml',
        'views/jalaali_holiday_views.xml',
        'views/res_users_views.xml',
        'views/res_company_views.xml',
        'views/menu_views.xml',
        'views/wizard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'zarvan_calendar/static/src/css/zarvan_calendar.css',
            'zarvan_calendar/static/src/js/widgets/jalali_date_picker.js',
            'zarvan_calendar/static/src/js/components/jalali_status.js',
            'zarvan_calendar/static/src/js/components/holiday_badge.js',
            'zarvan_calendar/static/src/xml/jalali_templates.xml',
        ],
    },
    'external_dependencies': {
        'python': ['jdatetime>=4.1.0', 'openpyxl'],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'maintainer': 'Ehsan Rezaei',
    'images': ['static/description/icon.png'],
    'price': 0,
    'currency': 'EUR',
    'support': 'ehsan.r97@gmail.com',
}
