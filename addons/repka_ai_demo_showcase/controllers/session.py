from odoo import api, http
from odoo.addons.web.controllers.session import Session
from odoo.http import request


class DemoLogout(Session):
    @http.route('/web/session/logout', type='http', auth='none', readonly=False)
    def logout(self, redirect='/odoo'):
        if request.db == 'repka_test' and request.session.uid:
            env = api.Environment(request.env.cr, request.session.uid, request.session.context)
            if env.user.has_group('base.group_system'):
                sessions = env['repka.ai.demo.session'].search([
                    ('user_id', '=', env.uid), ('state', '=', 'active'),
                ])
                sessions.action_finish()
        return super().logout(redirect=redirect)
