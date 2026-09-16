# -*- coding: utf-8 -*-
"""
Company Settings for Persian Calendar

Extends res.company with Jalali calendar configuration including:
- Fiscal year settings
- Weekend days
- Default holiday policies
"""

import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    # Fiscal Year Settings (Jalali)
    jalali_fiscal_year_start = fields.Char(
        string='Fiscal Year Start Day',
        default='01',
        help="Day of the month when fiscal year starts (Jalali calendar)."
    )

    jalali_fiscal_year_month = fields.Char(
        string='Fiscal Year Start Month',
        default='01',
        help="Month when fiscal year starts (Jali calendar, 1=Farvardin)."
    )

    # Weekend Configuration (Jalali calendar)
    # In Iran, weekend is typically Thursday and Friday
    JALALI_WEEKEND_SELECTION = [
        ('thu_fri', 'Thursday-Friday (Iran Standard)'),
        ('fri_sat', 'Friday-Saturday'),
        ('sat_sun', 'Saturday-Sunday (Western)'),
        ('custom', 'Custom'),
    ]

    jalali_weekend_type = fields.Selection(
        selection=JALALI_WEEKEND_SELECTION,
        string='Weekend Type',
        default='thu_fri',
        help="Select the weekend pattern for your company."
    )

    jalali_weekend_custom = fields.Char(
        string='Custom Weekend Days',
        default='5,6',  # Friday=5, Saturday=6 (0=Monday)
        help="Comma-separated weekday numbers for custom weekend (0=Monday, 6=Sunday)."
    )

    # Holiday Policies
    jalali_auto_create_holidays = fields.Boolean(
        string='Auto-create Yearly Holidays',
        default=True,
        help="Automatically generate holidays for each new Jalali year."
    )

    jalali_include_lunar_holidays = fields.Boolean(
        string='Include Lunar/Islamic Holidays',
        default=True,
        help="Include approximate lunar/Islamic holidays in company calendar."
    )

    @api.model
    def get_jalali_settings(self, company_id=None):
        """
        Get Jalali settings for a company.
        
        Args:
            company_id: Company ID (defaults to current company)
        
        Returns:
            dict: Company's Jalali settings
        """
        company = self.browse(company_id) if company_id else self.env.company
        
        return {
            'fiscal_year_start': company.jalali_fiscal_year_start,
            'fiscal_year_month': company.jalali_fiscal_year_month,
            'weekend_type': company.jalali_weekend_type,
            'weekend_custom': company.jalali_weekend_custom,
            'auto_create_holidays': company.jalali_auto_create_holidays,
            'include_lunar_holidays': company.jalali_include_lunar_holidays,
        }

    def is_weekend(self, check_date, weekday=None):
        """
        Check if a given date/weekday is a weekend for this company.
        
        Args:
            check_date: Date to check (Gregorian)
            weekday: Weekday number (0=Monday, 6=Sunday). If None, computed from date.
        
        Returns:
            bool: True if weekend, False otherwise
        """
        from datetime import datetime
        
        if weekday is None:
            if isinstance(check_date, str):
                check_date = datetime.strptime(check_date, '%Y-%m-%d').date()
            weekday = check_date.weekday()  # 0=Monday, 6=Sunday
        
        self.ensure_one()
        weekend_type = self.jalali_weekend_type
        
        if weekend_type == 'thu_fri':
            # Thursday=3, Friday=4 in Python weekday
            return weekday in [3, 4]
        elif weekend_type == 'fri_sat':
            # Friday=4, Saturday=5
            return weekday in [4, 5]
        elif weekend_type == 'sat_sun':
            # Saturday=5, Sunday=6
            return weekday in [5, 6]
        elif weekend_type == 'custom':
            try:
                custom_days = [int(x.strip()) for x in self.jalali_weekend_custom.split(',')]
                return weekday in custom_days
            except (ValueError, AttributeError):
                return False
        
        return False
