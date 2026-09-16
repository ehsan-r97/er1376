# -*- coding: utf-8 -*-
"""
User Preferences for Persian Calendar

Extends res.users with Jalali calendar preferences including:
- Date format selection
- Display options
- Default calendar view settings
"""

import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    # Date Format Preference
    JALALI_DATE_FORMAT_SELECTION = [
        ('YYYY-MM-DD', 'YYYY-MM-DD (e.g., 1403-01-01)'),
        ('YYYY/MM/DD', 'YYYY/MM/DD (e.g., 1403/01/01)'),
        ('YYYYMMDD', 'YYYYMMDD (e.g., 14030101)'),
        ('DD-MM-YYYY', 'DD-MM-YYYY (e.g., 01-01-1403)'),
        ('DD/MM/YYYY', 'DD/MM/YYYY (e.g., 01/01/1403)'),
    ]

    jalali_date_format = fields.Selection(
        selection=JALALI_DATE_FORMAT_SELECTION,
        string='Jalali Date Format',
        default='YYYY-MM-DD',
        help="Select your preferred Jalali date format for display and input."
    )

    # Display Options
    jalali_show_gregorian = fields.Boolean(
        string='Show Gregorian Dates',
        default=True,
        help="Display Gregorian dates alongside Jalali dates."
    )

    jalali_use_persian_numbers = fields.Boolean(
        string='Use Persian Numbers',
        default=False,
        help="Display dates using Persian numerals (۰, ۱, ۲, ...)."
    )

    jalali_default_view = fields.Selection(
        selection=[
            ('jalali', 'Jalali Calendar'),
            ('gregorian', 'Gregorian Calendar'),
        ],
        string='Default Calendar View',
        default='jalali',
        help="Choose which calendar to show by default in calendar views."
    )

    @api.model
    def get_jalali_preferences(self, user_id=None):
        """
        Get Jalali preferences for a user.
        
        Args:
            user_id: User ID (defaults to current user)
        
        Returns:
            dict: User's Jalali preferences
        """
        user = self.browse(user_id) if user_id else self.env.user
        
        return {
            'date_format': user.jalali_date_format,
            'show_gregorian': user.jalali_show_gregorian,
            'use_persian_numbers': user.jalali_use_persian_numbers,
            'default_view': user.jalali_default_view,
        }

    @staticmethod
    def convert_to_persian_numbers(text):
        """
        Convert Latin numbers to Persian numbers in text.
        
        Args:
            text: String containing numbers
        
        Returns:
            str: Text with Persian numbers
        """
        if not text:
            return text
        
        persian_digits = {
            '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
            '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
        }
        
        result = text
        for latin, persian in persian_digits.items():
            result = result.replace(latin, persian)
        
        return result
