# -*- coding: utf-8 -*-
import logging
from datetime import datetime, date
from odoo import models, fields, api
from odoo.tools import ormcache
import jdatetime

_logger = logging.getLogger(__name__)

class JalaaliMixin(models.AbstractModel):
    _name = 'jalaali.mixin'
    _description = 'Jalali Calendar Mixin'

    @api.model
    @ormcache('j_year', 'j_month', 'j_day')
    def _jalali_to_gregorian_cached(self, j_year, j_month, j_day):
        try:
            j_date = jdatetime.date(j_year, j_month, j_day)
            g_date = j_date.togregorian()
            return date(g_date.year, g_date.month, g_date.day)
        except (ValueError, IndexError):
            return False

    @api.model
    @ormcache('g_year', 'g_month', 'g_day')
    def _gregorian_to_jalali_cached(self, g_year, g_month, g_day):
        try:
            g_date = date(g_year, g_month, g_day)
            j_date = jdatetime.date.fromgregorian(date=g_date)
            return (j_date.year, j_date.month, j_date.day)
        except (ValueError, IndexError):
            return False

    def jalali_to_gregorian(self, j_year, j_month, j_day):
        return self._jalali_to_gregorian_cached(j_year, j_month, j_day)

    def gregorian_to_jalali(self, g_year, g_month, g_day):
        return self._gregorian_to_jalali_cached(g_year, g_month, g_day)

    def detect_and_parse_date(self, date_string, force_jalali=False, force_gregorian=False):
        """Parses a date string, auto-detecting format based on year magnitude."""
        if not date_string:
            return False
        
        import re
        match = re.match(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', str(date_string))
        if not match:
            return False
            
        y, m, d = map(int, match.groups())
        
        # FIXED LOGIC: Jalali years are typically < 1500. Gregorian are > 1900.
        # If year < 1500, assume Jalali. Otherwise Gregorian.
        is_jalali = force_jalali or (not force_gregorian and y < 1500)
        
        if is_jalali:
            g_date = self.jalali_to_gregorian(y, m, d)
            return g_date if g_date else False
        else:
            return date(y, m, d)

    @api.model
    def get_jalali_weekday_name(self, weekday):
        """Converts Python weekday (0=Monday) to Persian name."""
        # Python: 0=Mon, ..., 6=Sun
        # Persian: 0=Sat, ..., 6=Fri
        # Mapping: (weekday + 2) % 7
        persian_index = (weekday + 2) % 7
        weekdays = [
            'شنبه', 'یکشنبه', 'دوشنبه', 'سهشنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه'
        ]
        return weekdays[persian_index]
