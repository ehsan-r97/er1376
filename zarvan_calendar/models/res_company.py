# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import jdatetime

class ResCompany(models.Model):
    _inherit = 'res.company'

    jalali_weekend_type = fields.Selection([
        ('friday', 'Friday Only'),
        ('thu_fri', 'Thursday & Friday'),
        ('custom', 'Custom Days')
    ], string='Weekend Type', default='thu_fri')
    
    jalali_weekend_custom = fields.Char(string='Custom Weekend Days', help="Comma-separated Jalali weekday numbers (0=Sat to 6=Fri). Example: '5,6'")

    def is_weekend(self, check_date, weekday=None, company_id=None):
        """Checks if a given date is a weekend for a specific company."""
        if not self:
            return False
            
        # Determine target company
        if company_id:
            company = self.env['res.company'].browse(company_id)
            if not company:
                raise UserError(_("Company not found."))
        else:
            company = self[0] if self else self.env.company

        if weekday is None:
            if isinstance(check_date, str):
                check_date = jdatetime.date.fromgregorian(datetime.strptime(check_date, '%Y-%m-%d'))
            elif not isinstance(check_date, jdatetime.date):
                check_date = jdatetime.date.fromgregorian(date=check_date)
            weekday = check_date.weekday()  # 0=Saturday, 6=Friday in jdatetime

        if company.jalali_weekend_type == 'friday':
            return weekday == 6
        elif company.jalali_weekend_type == 'thu_fri':
            return weekday in (5, 6)
        elif company.jalali_weekend_type == 'custom' and company.jalali_weekend_custom:
            # FIXED: Parse comma-separated string instead of relational field
            custom_days = [int(d.strip()) for d in company.jalali_weekend_custom.split(',')]
            return weekday in custom_days
        
        return False
