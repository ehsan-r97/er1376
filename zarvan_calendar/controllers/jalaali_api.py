# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class JalaaliAPIController(http.Controller):
    """RESTful API controller for Jalali calendar operations."""

    @http.route('/api/jalaali/holidays/<int:year>', type='json', auth='user', methods=['GET'], csrf=False)
    def get_holidays(self, year, company_id=None):
        try:
            service = request.env['jalaali.service'].sudo()
            holidays = service.get_holidays_for_year(year, company_id)
            return {'success': True, 'data': {'year': year, 'holidays': holidays, 'count': len(holidays)}}
        except Exception as e:
            _logger.error(f"Error getting holidays: {e}")
            return {'success': False, 'error': str(e)}

    @http.route('/api/jalaali/is-holiday', type='json', auth='user', methods=['POST'], csrf=False)
    def check_holiday(self, **kwargs):
        try:
            year = kwargs.get('year')
            month = kwargs.get('month')
            day = kwargs.get('day')
            company_id = kwargs.get('company_id')
            if not all([year, month, day]):
                return {'success': False, 'error': 'Missing required parameters: year, month, day'}
            service = request.env['jalaali.service'].sudo()
            result = service.is_holiday(year, month, day, company_id)
            return {'success': True, 'data': result}
        except Exception as e:
            _logger.error(f"Error checking holiday: {e}")
            return {'success': False, 'error': str(e)}

    @http.route('/api/jalaali/convert/jalali-to-gregorian', type='json', auth='user', methods=['POST'], csrf=False)
    def jalali_to_gregorian(self, **kwargs):
        try:
            year = kwargs.get('year')
            month = kwargs.get('month')
            day = kwargs.get('day')
            if not all([year, month, day]):
                return {'success': False, 'error': 'Missing required parameters: year, month, day'}
            service = request.env['jalaali.service'].sudo()
            gregorian_date = service.jalali_to_gregorian(year, month, day)
            if gregorian_date:
                return {'success': True, 'data': {'jalali': f"{year}/{month:02d}/{day:02d}", 'gregorian': gregorian_date.strftime('%Y-%m-%d')}}
            return {'success': False, 'error': 'Invalid Jalali date'}
        except Exception as e:
            _logger.error(f"Error converting to Gregorian: {e}")
            return {'success': False, 'error': str(e)}

    @http.route('/api/jalaali/convert/gregorian-to-jalali', type='json', auth='user', methods=['POST'], csrf=False)
    def gregorian_to_jalali(self, **kwargs):
        try:
            year = kwargs.get('year')
            month = kwargs.get('month')
            day = kwargs.get('day')
            if not all([year, month, day]):
                return {'success': False, 'error': 'Missing required parameters: year, month, day'}
            service = request.env['jalaali.service'].sudo()
            jalali_date = service.gregorian_to_jalali(year, month, day)
            if jalali_date:
                j_year, j_month, j_day = jalali_date
                return {'success': True, 'data': {'gregorian': f"{year}-{month:02d}-{day:02d}", 'jalali': f"{j_year}/{j_month:02d}/{j_day:02d}"}}
            return {'success': False, 'error': 'Invalid Gregorian date'}
        except Exception as e:
            _logger.error(f"Error converting to Jalali: {e}")
            return {'success': False, 'error': str(e)}

    @http.route('/api/jalaali/current', type='json', auth='user', methods=['GET'], csrf=False)
    def get_current_date(self):
        try:
            service = request.env['jalaali.service'].sudo()
            current = service.get_current_jalali_date()
            return {'success': True, 'data': current}
        except Exception as e:
            _logger.error(f"Error getting current date: {e}")
            return {'success': False, 'error': str(e)}

    @http.route('/api/jalaali/working-days/<int:year>/<int:month>', type='json', auth='user', methods=['GET'], csrf=False)
    def get_working_days(self, year, month, company_id=None):
        try:
            service = request.env['jalaali.service'].sudo()
            result = service.get_working_days_in_month(year, month, company_id)
            if result:
                return {'success': True, 'data': result}
            return {'success': False, 'error': 'Failed to calculate working days'}
        except Exception as e:
            _logger.error(f"Error getting working days: {e}")
            return {'success': False, 'error': str(e)}
