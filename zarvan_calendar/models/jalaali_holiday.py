# -*- coding: utf-8 -*-
"""
Jalaali Holiday Management - Production Ready

Comprehensive holiday management system with support for:
- Fixed date holidays (e.g., Nowruz)
- Lunar/Islamic holidays (approximate, requires annual review)
- Regional/company-specific holidays
- Multi-company support
- Automatic Gregorian date computation
"""

import logging
from datetime import date, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class JalaaliHoliday(models.Model):
    _name = 'jalaali.holiday'
    _description = 'Persian Calendar Holiday'
    _order = 'jalali_year desc, jalali_month desc, jalali_day desc, name'
    _rec_name = 'name'

    name = fields.Char(string='Holiday Name', required=True, translate=True)
    
    # Jalali Date Fields
    jalali_year = fields.Integer(
        string='Jalali Year', 
        required=False,  # Optional: NULL means "Every Year" for fixed holidays
        index=True,
        help="Leave empty for fixed holidays that occur every year (e.g., Nowruz). Required for lunar holidays."
    )
    jalali_month = fields.Integer(string='Jalali Month', required=True, index=True)
    jalali_day = fields.Integer(string='Jalali Day', required=True, index=True)
    
    # Computed Gregorian Date (stored for performance and indexing)
    gregorian_date = fields.Date(
        string='Gregorian Date',
        compute='_compute_gregorian_date',
        store=True,
        index=True,
        readonly=True
    )
    
    # Holiday Type
    HOLIDAY_TYPE_SELECTION = [
        ('fixed', 'Fixed Date (Annual)'),
        ('lunar', 'Lunar/Islamic (Approximate)'),
        ('regional', 'Regional/Company Specific'),
        ('national', 'National Holiday'),
    ]
    
    holiday_type = fields.Selection(
        selection=HOLIDAY_TYPE_SELECTION,
        string='Holiday Type',
        default='fixed',
        required=True,
        index=True,
        help="Fixed: Same Jalali date every year\n"
             "Lunar: Islamic calendar based (requires annual update)\n"
             "Regional: Company-specific holidays\n"
             "National: Official national holidays"
    )
    
    # Multi-company Support
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        ondelete='cascade',
        index=True,
        default=lambda self: self.env.company,
        help="Leave empty for global holidays. Set company for company-specific holidays."
    )
    
    is_active = fields.Boolean(string='Active', default=True, index=True)
    description = fields.Text(string='Description', translate=True)
    
    # National holiday flag
    is_national = fields.Boolean(string='National Holiday', default=False, index=True,
        help="Check this if it's an official national holiday")
    
    # Metadata
    created_by = fields.Many2one('res.users', string='Created By', readonly=True)
    updated_by = fields.Many2one('res.users', string='Updated By', readonly=True)
    
    @api.depends('jalali_year', 'jalali_month', 'jalali_day')
    def _compute_gregorian_date(self):
        """Compute Gregorian date from Jalali date.
        
        For fixed holidays (jalali_year is NULL), computes the Gregorian date
        for the current year only. This field will be updated annually.
        """
        jalaali_mixin = self.env['jalaali.mixin']
        current_jalali_year = jalaali_mixin.get_current_jalali_year()
        
        for record in self:
            year_to_use = record.jalali_year if record.jalali_year else current_jalali_year
            
            if year_to_use and record.jalali_month and record.jalali_day:
                try:
                    g_date = jalaali_mixin.jalali_to_gregorian(
                        year_to_use,
                        record.jalali_month,
                        record.jalali_day
                    )
                    record.gregorian_date = g_date
                except Exception as e:
                    _logger.warning(
                        "Could not compute Gregorian date for %d-%02d-%02d: %s",
                        year_to_use, record.jalali_month, record.jalali_day, e
                    )
                    record.gregorian_date = False
            else:
                record.gregorian_date = False

    @api.constrains('jalali_year', 'jalali_month', 'jalali_day')
    def _check_jalali_date_validity(self):
        """Validate Jalali date components."""
        jalaali_mixin = self.env['jalaali.mixin']
        
        for record in self:
            # Only validate if year is provided (lunar holidays)
            # Fixed holidays (year=NULL) are always valid
            if record.jalali_year:
                if not jalaali_mixin.validate_jalali_date(
                    record.jalali_year, record.jalali_month, record.jalali_day
                ):
                    raise ValidationError(_(
                        "Invalid Jalali date: %(year)d-%(month)02d-%(day)02d. "
                        "Please verify the date components."
                    ) % {
                        'year': record.jalali_year,
                        'month': record.jalali_month,
                        'day': record.jalali_day
                    })

    @api.constrains('holiday_type', 'company_id')
    def _check_company_specific_holidays(self):
        """Ensure regional holidays have a company assigned."""
        for record in self:
            if record.holiday_type == 'regional' and not record.company_id:
                raise ValidationError(_(
                    "Regional holidays must be assigned to a specific company."
                ))

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to set creator."""
        for vals in vals_list:
            vals['created_by'] = self.env.uid
        return super().create(vals_list)

    def write(self, vals):
        """Override write to set updater."""
        vals['updated_by'] = self.env.uid
        return super().write(vals)

    def name_get(self):
        """Custom display name with both Jalali and Gregorian dates."""
        result = []
        for record in self:
            jalali_str = f"{record.jalali_year}/{record.jalali_month:02d}/{record.jalali_day:02d}"
            gregorian_str = record.gregorian_date.strftime('%Y/%m/%d') if record.gregorian_date else 'N/A'
            name = f"{record.name} ({jalali_str} / {gregorian_str})"
            result.append((record.id, name))
        return result

    @api.model
    def get_holidays_in_range(self, start_date, end_date, company_id=None):
        """
        Get all holidays within a date range.
        
        Args:
            start_date: Start date (Gregorian)
            end_date: End date (Gregorian)
            company_id: Company ID (optional, includes global holidays if None)
        
        Returns:
            recordset: Holidays in the range
        """
        domain = [
            ('gregorian_date', '>=', start_date),
            ('gregorian_date', '<=', end_date),
            ('is_active', '=', True),
        ]
        
        if company_id:
            domain.append('|')
            domain.append(('company_id', '=', company_id))
            domain.append(('company_id', '=', False))
        
        return self.search(domain)

    @api.model
    def is_holiday(self, check_date, company_id=None):
        """
        Check if a given date is a holiday.
        
        Args:
            check_date: Date to check (Gregorian)
            company_id: Company ID (optional)
        
        Returns:
            bool: True if holiday, False otherwise
        """
        domain = [
            ('gregorian_date', '=', check_date),
            ('is_active', '=', True),
        ]
        
        if company_id:
            domain.append('|')
            domain.append(('company_id', '=', company_id))
            domain.append(('company_id', '=', False))
        
        return bool(self.search_count(domain))

    @api.model
    def get_next_holiday(self, from_date, company_id=None):
        """
        Get the next holiday after a given date.
        
        Args:
            from_date: Starting date (Gregorian)
            company_id: Company ID (optional)
        
        Returns:
            record: Next holiday or None
        """
        domain = [
            ('gregorian_date', '>', from_date),
            ('is_active', '=', True),
        ]
        
        if company_id:
            domain.append('|')
            domain.append(('company_id', '=', company_id))
            domain.append(('company_id', '=', False))
        
        return self.search(domain, limit=1, order='gregorian_date asc')

    @api.model
    def generate_yearly_holidays(self, year, holiday_templates=None):
        """
        Generate holidays for a specific year based on templates.
        
        This is useful for creating recurring holidays.
        
        Args:
            year: Jalali year
            holiday_templates: List of holiday records to use as templates
        """
        if not holiday_templates:
            # Get all fixed national holidays as templates
            holiday_templates = self.search([
                ('holiday_type', '=', 'fixed'),
                ('company_id', '=', False),
            ])
        
        created_count = 0
        for template in holiday_templates:
            # Check if already exists
            existing = self.search([
                ('jalali_year', '=', year),
                ('jalali_month', '=', template.jalali_month),
                ('jalali_day', '=', template.jalali_day),
                ('company_id', '=', False),
            ], limit=1)
            
            if not existing:
                self.create({
                    'name': template.name,
                    'jalali_year': year,
                    'jalali_month': template.jalali_month,
                    'jalali_day': template.jalali_day,
                    'holiday_type': 'fixed',
                    'description': template.description,
                })
                created_count += 1
        
        _logger.info("Generated %d holidays for Jalali year %d", created_count, year)
        return created_count
