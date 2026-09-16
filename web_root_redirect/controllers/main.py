import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

try:
    from odoo.addons.web.controllers.home import Home as WebHome

    class Home(WebHome):

        @http.route('/', type='http', auth="none")
        def index(self, s_action=None, db=None, **kw):
            return request.redirect_query('/web', query=request.params)

except ImportError:
    _logger.warning(
        "web_root_redirect: Could not import Home controller. "
        "The root URL redirect will not be changed."
    )
