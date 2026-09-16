# -*- coding: utf-8 -*-
import logging
from . import models
from . import wizard
from . import controllers

_logger = logging.getLogger(__name__)

def post_init_hook(env):
    """Post-installation hook to initialize default data."""
    _logger.info("Zarvan Calendar: Running post-installation hook...")
    holiday_count = env['jalaali.holiday'].search_count([])
    if holiday_count == 0:
        _logger.warning("Zarvan Calendar: No holidays found. Please upgrade module.")
    else:
        _logger.info(f"Zarvan Calendar: {holiday_count} holidays loaded successfully.")

def uninstall_hook(env):
    """Pre-uninstallation hook."""
    _logger.info("Zarvan Calendar: Running pre-uninstallation hook...")
