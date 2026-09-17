# -*- coding: utf-8 -*-
import logging
from odoo import models, api
import jdatetime

_logger = logging.getLogger(__name__)

class JalaaliService(models.Model):
    _name = 'jalaali.service'
    _description = 'Jalali Service Logic'

    @api.model
    def get_current_jalali_date(self):
        """Returns current Jalali date details."""
        today = jdatetime.date.today()
        # jdatetime.weekday(): 0=Saturday, ..., 6=Friday
        # Python weekday(): 0=Monday, ..., 6=Sunday
        # Conversion: (j_weekday + 2) % 7
        python_weekday = (today.weekday() + 2) % 7
        
        mixin = self.env['jalaali.mixin']
        return {
            'year': today.year,
            'month': today.month,
            'day': today.day,
            'weekday': python_weekday,
            'weekday_name': mixin.get_jalali_weekday_name(python_weekday),
            'full_date': today.strftime('%Y/%m/%d')
        }

    @api.model
    def get_working_days_in_month(self, year, month, company_id=None):
        """Calculates working days in a Jalali month."""
        if not (1 <= month <= 12):
            return 0
            
        try:
            # Determine days in month
            if month < 12:
                next_month = jdatetime.date(year, month + 1, 1)
                last_day = (next_month - jdatetime.date(year, month, 1)).days
            else:
                if jdatetime.jalali.isleap(year):
                    last_day = 30
                else:
                    last_day = 29
            
            working_days = 0
            company = self.env['res.company'].browse(company_id) if company_id else self.env.company
            
            # Optimization: Fetch all holidays for this month/year in ONE query
            holidays_domain = [
                ('jalali_year', '=', year),
                ('jalali_month', '=', month),
                ('is_active', '=', True),
                '|', ('company_id', '=', False), ('company_id', '=', company.id)
            ]
            holidays = self.env['jalaali.holiday'].search(holidays_domain)
            holiday_days = set(h.mapped('jalali_day'))

            for day in range(1, last_day + 1):
                j_date = jdatetime.date(year, month, day)
                weekday = j_date.weekday()  # 0=Sat, 6=Fri
                
                is_weekend = False
                if company.jalali_weekend_type == 'friday' and weekday == 6:
                    is_weekend = True
                elif company.jalali_weekend_type == 'thu_fri' and weekday in (5, 6):
                    is_weekend = True
                
                is_holiday = day in holiday_days

                if not is_weekend and not is_holiday:
                    working_days += 1
                    
            return working_days
            
        except Exception as e:
            # FIXED: Specific exception handling with logging
            _logger.warning("Error calculating working days for %s/%s: %s", year, month, e)
            return 0
