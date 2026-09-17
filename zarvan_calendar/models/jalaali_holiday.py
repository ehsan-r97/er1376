# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import jdatetime

class JalaaliHoliday(models.Model):
    _name = 'jalaali.holiday'
    _description = 'Jalali Holiday'
    _order = 'jalali_year desc, jalali_month desc, jalali_day desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Holiday Name', required=True, tracking=True)
    jalali_year = fields.Integer(string='Jalali Year', index=True, tracking=True)
    jalali_month = fields.Integer(string='Jalali Month', required=True, index=True, tracking=True)
    jalali_day = fields.Integer(string='Jalali Day', required=True, index=True, tracking=True)
    
    holiday_type = fields.Selection([
        ('fixed', 'Fixed Date'),
        ('lunar', 'Lunar Based (Calculated)'),
        ('weekend', 'Weekend Extension')
    ], string='Type', default='fixed', required=True, tracking=True)
    
    is_national = fields.Boolean(string='National Holiday', default=False, index=True, tracking=True)
    is_active = fields.Boolean(string='Active', default=True, tracking=True)
    description = fields.Text(string='Description')
    
    gregorian_date = fields.Date(string='Gregorian Date', compute='_compute_gregorian_date', store=True, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, index=True)
    created_by = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.uid, readonly=True)

    # Odoo 19 Compatibility: Replaces deprecated name_get()
    display_name = fields.Char(compute='_compute_display_name', store=True)

    _sql_constraints = [
        ('unique_holiday_date', 
         'unique(jalali_month, jalali_day, holiday_type, company_id)', 
         'A holiday with this date, type, and company already exists!')
    ]

    @api.depends('name', 'jalali_year', 'jalali_month', 'jalali_day', 'gregorian_date')
    def _compute_display_name(self):
        """Computes a human-readable display name."""
        for record in self:
            if record.name:
                date_part = f"{record.jalali_year}/{record.jalali_month:02d}/{record.jalali_day:02d}" if record.jalali_year else f"{record.jalali_month:02d}/{record.jalali_day:02d}"
                greg_part = f" ({record.gregorian_date})" if record.gregorian_date else ""
                record.display_name = f"{record.name} - {date_part}{greg_part}"
            else:
                record.display_name = False

    @api.depends('jalali_year', 'jalali_month', 'jalali_day')
    def _compute_gregorian_date(self):
        """Converts Jalali date to Gregorian safely."""
        for record in self:
            record.gregorian_date = False
            if record.jalali_year and record.jalali_month and record.jalali_day:
                try:
                    if not (1300 <= record.jalali_year <= 1500):
                        continue
                    j_date = jdatetime.date(record.jalali_year, record.jalali_month, record.jalali_day)
                    g_date = j_date.togregorian()
                    record.gregorian_date = g_date
                except (ValueError, IndexError):
                    record.gregorian_date = False

    @api.constrains('jalali_month', 'jalali_day')
    def _check_jalali_date_validity(self):
        """Validates Jalali month and day ranges."""
        for record in self:
            if not (1 <= record.jalali_month <= 12):
                raise ValidationError(_("Jalali month must be between 1 and 12."))
            if not (1 <= record.jalali_day <= 31):
                raise ValidationError(_("Jalali day must be between 1 and 31."))
            
            if record.jalali_year:
                try:
                    jdatetime.date(record.jalali_year, record.jalali_month, record.jalali_day)
                except ValueError:
                    raise ValidationError(_("Invalid Jalali date: %s/%s/%s") % (
                        record.jalali_year, record.jalali_month, record.jalali_day
                    ))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.setdefault('created_by', self.env.uid)
        return super().create(vals_list)
