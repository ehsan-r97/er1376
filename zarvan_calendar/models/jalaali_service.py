# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError
import logging
from functools import lru_cache

_logger = logging.getLogger(__name__)

try:
    import jdatetime
    from jdatetime import JalaliDateConverter
except ImportError:
    _logger.error("jdatetime library not installed. Run: pip install jdatetime>=4.1.0")
    raise


class JalaaliService(models.AbstractModel):
    """
    Production-ready service layer for Jalali calendar operations.
    Provides API endpoints for holiday data, date conversions, and calendar utilities.
    
    Usage:
        service = env['jalaali.service']
        holidays = service.get_holidays_for_year(1405)
        gregorian_date = service.jalali_to_gregorian(1405, 1, 1)
    """
    _name = 'jalaali.service'
    _description = 'Jalali Calendar Service API'

    @api.model
    def get_holidays_for_year(self, jalali_year=None, company_id=None):
        """
        Get all holidays for a specific Jalali year.
        
        :param jalali_year: int - Jalali year (default: current year)
        :param company_id: int - Company ID for company-specific holidays
        :return: list of dict with holiday information
        """
        if jalali_year is None:
            jalali_year = jdatetime.date.today().year
        
        domain = [('active', '=', True)]
        
        # Fixed holidays (apply every year)
        fixed_domain = domain + [('holiday_type', '=', 'fixed')]
        fixed_holidays = self.env['jalaali.holiday'].search(fixed_domain)
        
        # Lunar holidays for specific year
        lunar_domain = domain + [
            ('holiday_type', '=', 'lunar'),
            ('jalali_year', '=', jalali_year)
        ]
        lunar_holidays = self.env['jalaali.holiday'].search(lunar_domain)
        
        results = []
        
        # Process fixed holidays
        for holiday in fixed_holidays:
            try:
                gregorian = self._jalali_to_gregorian_safe(
                    jalali_year, holiday.jalali_month, holiday.jalali_day
                )
                results.append({
                    'id': holiday.id,
                    'name': holiday.name,
                    'jalali_date': f"{jalali_year}/{holiday.jalali_month:02d}/{holiday.jalali_day:02d}",
                    'gregorian_date': gregorian.strftime('%Y-%m-%d') if gregorian else None,
                    'type': 'fixed',
                    'is_national': holiday.is_national,
                    'company_id': holiday.company_id.name if holiday.company_id else None,
                })
            except Exception as e:
                _logger.warning(f"Error processing fixed holiday {holiday.name}: {e}")
        
        # Process lunar holidays
        for holiday in lunar_holidays:
            try:
                gregorian = self._jalali_to_gregorian_safe(
                    holiday.jalali_year, holiday.jalali_month, holiday.jalali_day
                )
                results.append({
                    'id': holiday.id,
                    'name': holiday.name,
                    'jalali_date': f"{holiday.jalali_year}/{holiday.jalali_month:02d}/{holiday.jalali_day:02d}",
                    'gregorian_date': gregorian.strftime('%Y-%m-%d') if gregorian else None,
                    'type': 'lunar',
                    'is_national': holiday.is_national,
                    'company_id': holiday.company_id.name if holiday.company_id else None,
                })
            except Exception as e:
                _logger.warning(f"Error processing lunar holiday {holiday.name}: {e}")
        
        # Sort by date
        results.sort(key=lambda x: x['jalali_date'])
        
        return results

    @api.model
    def is_holiday(self, jalali_year, jalali_month, jalali_day, company_id=None):
        """
        Check if a specific Jalali date is a holiday.
        
        :return: dict with is_holiday boolean and holiday details if applicable
        """
        domain = [
            ('active', '=', True),
            ('jalali_month', '=', jalali_month),
            ('jalali_day', '=', jalali_day),
        ]
        
        # Check fixed holidays
        fixed_domain = domain + [('holiday_type', '=', 'fixed')]
        fixed_holiday = self.env['jalaali.holiday'].search(fixed_domain, limit=1)
        
        if fixed_holiday:
            if not fixed_holiday.company_id or fixed_holiday.company_id.id == company_id:
                return {
                    'is_holiday': True,
                    'holiday': fixed_holiday.name,
                    'type': 'fixed'
                }
        
        # Check lunar holidays for specific year
        lunar_domain = domain + [
            ('holiday_type', '=', 'lunar'),
            ('jalali_year', '=', jalali_year)
        ]
        lunar_holiday = self.env['jalaali.holiday'].search(lunar_domain, limit=1)
        
        if lunar_holiday:
            if not lunar_holiday.company_id or lunar_holiday.company_id.id == company_id:
                return {
                    'is_holiday': True,
                    'holiday': lunar_holiday.name,
                    'type': 'lunar'
                }
        
        return {'is_holiday': False, 'holiday': None, 'type': None}

    @api.model
    def jalali_to_gregorian(self, year, month, day):
        """
        Convert Jalali date to Gregorian.
        
        :return: datetime.date object or None if invalid
        """
        return self._jalali_to_gregorian_safe(year, month, day)

    @api.model
    def gregorian_to_jalali(self, year, month, day):
        """
        Convert Gregorian date to Jalali.
        
        :return: tuple (year, month, day) or None if invalid
        """
        try:
            g_date = jdatetime.date(year, month, day)
            j_date = jdatetime.GregorianToJalali(g_date)
            return (j_date.jyear, j_date.jmonth, j_date.jday)
        except Exception as e:
            _logger.error(f"Gregorian to Jalali conversion error: {e}")
            return None

    @api.model
    def get_current_jalali_date(self):
        """Get current date in Jalali format."""
        today = jdatetime.date.today()
        return {
            'year': today.year,
            'month': today.month,
            'day': today.day,
            'formatted': f"{today.year}/{today.month:02d}/{today.day:02d}",
            'weekday': today.strftime('%A'),
            'full_formatted': today.strftime('%Y/%m/%d - %A')
        }

    @api.model
    def get_working_days_in_month(self, year, month, company_id=None):
        """
        Calculate working days in a Jalali month (excluding holidays and weekends).
        
        :return: dict with working_days count and list of holiday dates
        """
        try:
            # Get last day of month
            if month == 12:
                if self._is_leap_year(year):
                    last_day = 30
                else:
                    last_day = 29
            elif month <= 6:
                last_day = 31
            else:
                last_day = 30
            
            holidays = []
            working_days = 0
            
            for day in range(1, last_day + 1):
                # Check if weekend (Friday = 4 in jdatetime)
                try:
                    j_date = jdatetime.date(year, month, day)
                    weekday = j_date.weekday()  # 0=Saturday, 6=Friday
                    
                    # Friday is weekend
                    if weekday == 4:  # Friday
                        holidays.append({
                            'day': day,
                            'reason': 'Weekend (Friday)'
                        })
                        continue
                    
                    # Check if holiday
                    holiday_check = self.is_holiday(year, month, day, company_id)
                    if holiday_check['is_holiday']:
                        holidays.append({
                            'day': day,
                            'reason': holiday_check['holiday']
                        })
                        continue
                    
                    working_days += 1
                except:
                    continue
            
            return {
                'working_days': working_days,
                'total_days': last_day,
                'holidays': holidays,
                'holiday_count': len(holidays)
            }
        except Exception as e:
            _logger.error(f"Error calculating working days: {e}")
            return None

    @staticmethod
    @lru_cache(maxsize=366)
    def _jalali_to_gregorian_safe(year, month, day):
        """Cached safe conversion with error handling."""
        try:
            j_date = jdatetime.date(year, month, day)
            return j_date.togregorian()
        except Exception as e:
            _logger.warning(f"Invalid Jalali date {year}/{month}/{day}: {e}")
            return None

    @staticmethod
    def _is_leap_year(year):
        """Check if a Jalali year is a leap year."""
        # Jalali leap year cycle (33-year cycle with occasional 29-year subcycles)
        remainder = year % 33
        return remainder in [1, 5, 9, 13, 17, 22, 26, 30]

    @api.model
    def generate_holiday_report(self, year_from, year_to, format='json'):
        """
        Generate comprehensive holiday report for multiple years.
        
        :param year_from: int - Starting Jalali year
        :param year_to: int - Ending Jalali year
        :param format: str - 'json' or 'csv'
        :return: formatted report data
        """
        all_holidays = []
        
        for year in range(year_from, year_to + 1):
            holidays = self.get_holidays_for_year(year)
            for h in holidays:
                h['report_year'] = year
                all_holidays.append(h)
        
        if format == 'csv':
            # Generate CSV format
            csv_lines = ['Year,Jalali Date,Gregorian Date,Name,Type,Is National']
            for h in all_holidays:
                csv_lines.append(
                    f"{h['report_year']},{h['jalali_date']},{h['gregorian_date']},"
                    f"{h['name']},{h['type']},{h['is_national']}"
                )
            return '\n'.join(csv_lines)
        
        return all_holidays
