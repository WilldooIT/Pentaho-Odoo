# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessDenied

from odoo import sql_db, SUPERUSER_ID

PENTAHO_TOKEN = 'PENTAHO_TOKEN'

import logging
_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.multi
    def pentaho_pass_token(self):
        return '%s%s' % (PENTAHO_TOKEN, self.decide_on_password())

    @api.multi
    def pentaho_undo_token(self, token):
        if token[0:len(PENTAHO_TOKEN)] == PENTAHO_TOKEN:
            self.reverse_password(token.replace(PENTAHO_TOKEN, ''))

    def decide_on_password(self):
        return self.sudo().password

    def reverse_password(self, password):
        pass

    @api.model
    def strip_password(self, password):
        if password[0:len(PENTAHO_TOKEN)] == PENTAHO_TOKEN:
            password = password.replace(PENTAHO_TOKEN, '')
        return password

    @api.model
    def check_credentials(self, password):
        password = self.strip_password(password)
        return super(ResUsers, self).check_credentials(password)

    @classmethod
    def _login(cls, db, login, password):
        if not password:
            return False
        if password == PENTAHO_TOKEN:
            _logger.error('*** Install pentaho_reports_auth_crypt to run with encrypted passwords. ***')
            return False
        user_id = False
        try:
            with cls.pool.cursor() as cr:
                self = api.Environment(cr, SUPERUSER_ID, {})[cls._name]
                user = self.search([('login', '=', login)])
                if user:
                    user_id = user.id
                    user.sudo(user_id).check_credentials(password)
                    user.sudo(user_id)._update_last_login()
        except AccessDenied:
            _logger.info("Login failed for db:%s login:%s", db, login)
            user_id = False
        return user_id
