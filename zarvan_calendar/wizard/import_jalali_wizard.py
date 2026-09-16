# -*- coding: utf-8 -*-
"""
Import Jalali Holidays Wizard - Production Ready

Advanced wizard for importing holidays from CSV/Excel files with:
- Auto-detection of Jalali vs Gregorian dates
- Multi-encoding support (UTF-8, CP1256 for Persian)
- Preview with validation statistics
- Transaction-safe import with rollback
- Force import option for skipping invalid rows
"""

import logging
import io
from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_utils

_logger = logging.getLogger(__name__)


class ImportJalaliWizard(models.TransientModel):
    _name = 'jalaali.import.wizard'
    _description = 'Import Jalali Holidays Wizard'

    file_data = fields.Binary(string='File', required=True)
    filename = fields.Char(string='Filename')
    
    # Configuration
    delimiter = fields.Selection(
        [(',', 'Comma'), (';', 'Semicolon'), ('\t', 'Tab')],
        string='Delimiter',
        default=',',
        help="CSV delimiter character."
    )
    
    has_header = fields.Boolean(string='Has Header Row', default=True)
    
    # Date Format Detection
    DATE_FORMAT_SELECTION = [
        ('auto', 'Auto-detect'),
        ('jalali', 'Force Jalali'),
        ('gregorian', 'Force Gregorian'),
    ]
    
    date_format_mode = fields.Selection(
        selection=DATE_FORMAT_SELECTION,
        string='Date Format',
        default='auto',
        help="Auto-detect based on year value (>1300 = Jalali)"
    )
    
    # Encoding for Persian text
    encoding = fields.Selection(
        [
            ('utf-8', 'UTF-8'),
            ('cp1256', 'Windows Arabic/Persian (CP1256)'),
            ('iso-8859-6', 'ISO-8859-6 (Arabic)'),
        ],
        string='File Encoding',
        default='utf-8',
        help="Select file encoding. Use CP1256 for Persian files from Windows."
    )
    
    # Preview and Statistics
    preview_data = fields.Text(string='Preview Data', readonly=True)
    
    total_rows = fields.Integer(string='Total Rows', readonly=True)
    valid_rows = fields.Integer(string='Valid Rows', readonly=True)
    invalid_rows = fields.Integer(string='Invalid Rows', readonly=True)
    duplicate_rows = fields.Integer(string='Duplicate Rows', readonly=True)
    
    # Import Options
    force_import = fields.Boolean(
        string='Force Import',
        default=False,
        help="Skip invalid rows instead of failing the entire import."
    )
    
    create_company_specific = fields.Boolean(
        string='Create as Company-Specific',
        default=False,
        help="Mark imported holidays as company-specific (requires company selection)."
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
    )
    
    holiday_type = fields.Selection(
        [
            ('fixed', 'Fixed Date'),
            ('lunar', 'Lunar/Islamic'),
            ('regional', 'Regional'),
            ('national', 'National'),
        ],
        string='Holiday Type',
        default='national',
    )
    
    # State Management
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('preview', 'Preview'),
            ('done', 'Done'),
        ],
        default='draft',
    )
    
    import_log = fields.Text(string='Import Log', readonly=True)

    @api.onchange('file_data')
    def _onchange_file_data(self):
        """Parse and preview file when uploaded."""
        if not self.file_data:
            return
        
        try:
            import pandas as pd
            
            # Decode file content
            file_content = io.BytesIO(self.file_data)
            
            # Determine file type
            if self.filename.lower().endswith('.csv'):
                # Try different encodings
                df = None
                for encoding in [self.encoding, 'utf-8', 'cp1256']:
                    try:
                        file_content.seek(0)
                        df = pd.read_csv(
                            file_content,
                            delimiter=self.delimiter,
                            encoding=encoding,
                            header=0 if self.has_header else None,
                            skipinitialspace=True,
                        )
                        break
                    except UnicodeDecodeError:
                        continue
                
                if df is None:
                    raise ValidationError(_("Could not decode file. Try different encoding."))
                    
            elif self.filename.lower().endswith(('.xlsx', '.xls')):
                file_content.seek(0)
                df = pd.read_excel(file_content, header=0 if self.has_header else None)
            else:
                raise ValidationError(_("Unsupported file format. Use CSV or Excel."))
            
            # Store preview
            preview_lines = []
            preview_lines.append(f"Columns: {', '.join(df.columns.astype(str))}")
            preview_lines.append("")
            
            for idx, row in df.head(10).iterrows():
                preview_lines.append(" | ".join(str(v) for v in row.values))
            
            if len(df) > 10:
                preview_lines.append(f"... and {len(df) - 10} more rows")
            
            self.preview_data = "\n".join(preview_lines)
            self.total_rows = len(df)
            
            # Validate and count
            valid, invalid, duplicates = self._validate_dataframe(df)
            self.valid_rows = valid
            self.invalid_rows = invalid
            self.duplicate_rows = duplicates
            
            self.state = 'preview'
            
        except ImportError:
            raise ValidationError(_("Pandas library not installed. Please install: pip install pandas"))
        except Exception as e:
            _logger.error("File parsing error: %s", str(e), exc_info=True)
            raise ValidationError(_("Error parsing file: %s") % str(e))

    def _validate_dataframe(self, df):
        """Validate dataframe and return statistics."""
        valid = 0
        invalid = 0
        duplicates = 0
        
        seen_dates = set()
        jalaali_mixin = self.env['jalaali.mixin']
        
        for idx, row in df.iterrows():
            try:
                # Extract date components (assumes columns: name, year, month, day)
                # Flexible column detection
                year_col = next((c for c in df.columns if 'year' in str(c).lower()), None)
                month_col = next((c for c in df.columns if 'month' in str(c).lower()), None)
                day_col = next((c for c in df.columns if 'day' in str(c).lower()), None)
                name_col = next((c for c in df.columns if 'name' in str(c).lower() or 'holiday' in str(c).lower()), None)
                
                if not all([year_col, month_col, day_col]):
                    invalid += 1
                    continue
                
                year = int(row[year_col])
                month = int(row[month_col])
                day = int(row[day_col])
                
                # Auto-detect Jalali vs Gregorian
                if self.date_format_mode == 'auto':
                    is_jalali = year > 1300
                else:
                    is_jalali = (self.date_format_mode == 'jalali')
                
                if is_jalali:
                    if not jalaali_mixin.validate_jalali_date(year, month, day):
                        invalid += 1
                        continue
                else:
                    # Validate Gregorian
                    if not (1 <= month <= 12 and 1 <= day <= 31):
                        invalid += 1
                        continue
                
                # Check duplicates
                date_key = (year, month, day)
                if date_key in seen_dates:
                    duplicates += 1
                else:
                    seen_dates.add(date_key)
                    valid += 1
                    
            except (ValueError, TypeError, KeyError):
                invalid += 1
        
        return valid, invalid, duplicates

    def action_import(self):
        """Execute the import."""
        self.ensure_one()
        
        if not self.file_data:
            raise ValidationError(_("No file selected."))
        
        if self.invalid_rows > 0 and not self.force_import:
            raise ValidationError(_(
                "File contains %d invalid rows. Enable 'Force Import' to skip them."
            ) % self.invalid_rows)
        
        try:
            import pandas as pd
            import jdatetime
            
            # Re-parse file
            file_content = io.BytesIO(self.file_data)
            
            if self.filename.lower().endswith('.csv'):
                df = pd.read_csv(
                    file_content,
                    delimiter=self.delimiter,
                    encoding=self.encoding,
                    header=0 if self.has_header else None,
                )
            else:
                df = pd.read_excel(file_content, header=0 if self.has_header else None)
            
            # Import records
            holiday_obj = self.env['jalaali.holiday']
            jalaali_mixin = self.env['jalaali.mixin']
            
            created_count = 0
            skipped_count = 0
            error_log = []
            
            # Use transaction for atomicity
            with self.env.cr.savepoint():
                for idx, row in df.iterrows():
                    try:
                        # Extract columns
                        year_col = next((c for c in df.columns if 'year' in str(c).lower()), None)
                        month_col = next((c for c in df.columns if 'month' in str(c).lower()), None)
                        day_col = next((c for c in df.columns if 'day' in str(c).lower()), None)
                        name_col = next((c for c in df.columns if 'name' in str(c).lower() or 'holiday' in str(c).lower()), None)
                        
                        if not all([year_col, month_col, day_col, name_col]):
                            error_log.append(f"Row {idx + 1}: Missing required columns")
                            skipped_count += 1
                            continue
                        
                        year = int(row[year_col])
                        month = int(row[month_col])
                        day = int(row[day_col])
                        name = str(row[name_col]).strip()
                        
                        # Auto-detect Jalali vs Gregorian
                        if self.date_format_mode == 'auto':
                            is_jalali = year > 1300
                        else:
                            is_jalali = (self.date_format_mode == 'jalali')
                        
                        if is_jalali:
                            if not jalaali_mixin.validate_jalali_date(year, month, day):
                                if self.force_import:
                                    skipped_count += 1
                                    continue
                                else:
                                    raise ValidationError(f"Row {idx + 1}: Invalid Jalali date")
                            
                            j_year, j_month, j_day = year, month, day
                        else:
                            # Convert Gregorian to Jalali
                            j_date = jdatetime.date.fromgregorian(
                                year=year, month=month, day=day
                            )
                            j_year, j_month, j_day = j_date.year, j_date.month, j_date.day
                        
                        # Check for duplicates in database
                        existing = holiday_obj.search([
                            ('jalali_year', '=', j_year),
                            ('jalali_month', '=', j_month),
                            ('jalali_day', '=', j_day),
                            ('company_id', '=', self.company_id.id if self.create_company_specific else False),
                        ], limit=1)
                        
                        if existing:
                            skipped_count += 1
                            continue
                        
                        # Create holiday
                        holiday_obj.create({
                            'name': name,
                            'jalali_year': j_year,
                            'jalali_month': j_month,
                            'jalali_day': j_day,
                            'holiday_type': 'regional' if self.create_company_specific else self.holiday_type,
                            'company_id': self.company_id.id if self.create_company_specific else False,
                            'description': f"Imported from {self.filename}",
                        })
                        
                        created_count += 1
                        
                    except Exception as e:
                        error_msg = f"Row {idx + 1}: {str(e)}"
                        error_log.append(error_msg)
                        _logger.warning(error_msg)
                        
                        if not self.force_import:
                            raise
            
            # Update wizard state
            log_message = f"Import completed:\n"
            log_message += f"- Created: {created_count}\n"
            log_message += f"- Skipped: {skipped_count}\n"
            log_message += f"- Total processed: {len(df)}\n"
            
            if error_log:
                log_message += f"\nErrors:\n" + "\n".join(error_log[:10])  # Limit to first 10 errors
                if len(error_log) > 10:
                    log_message += f"\n... and {len(error_log) - 10} more errors"
            
            self.import_log = log_message
            self.state = 'done'
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Import Successful'),
                    'message': _('Created %d holidays, skipped %d.') % (created_count, skipped_count),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            _logger.error("Import failed: %s", str(e), exc_info=True)
            raise ValidationError(_("Import failed: %s") % str(e))

    def action_cancel(self):
        """Cancel wizard."""
        return {'type': 'ir.actions.act_window_close'}
