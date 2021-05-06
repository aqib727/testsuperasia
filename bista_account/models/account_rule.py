# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)
logger = logging.getLogger('Quick Order')



class AccountMove(models.Model):
    _inherit= 'account.move'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.user.has_group('bista_account.group_own_customer'):
            args += [('user_id','=', self.env.user.id)]
        return super(AccountMove, self).search(args,offset,limit,order,count)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self.env.user.has_group('bista_account.group_own_customer'):
            domain += [('user_id', '=', self.env.user.id)]
        return super(AccountMove, self).read_group(domain, fields, groupby, offset, limit, orderby, lazy)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.user.has_group('bista_account.group_own_customer'):
            args += [('user_id', '=', self.env.user.id)]
        return super(ResPartner, self).search(args, offset, limit, order,
                                               count)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        if self.env.user.has_group('bista_account.group_own_customer'):
            domain += [('user_id', '=', self.env.user.id)]
        return super(ResPartner, self).read_group(domain, fields, groupby,
                                                   offset, limit, orderby,
                                                   lazy)

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.user.has_group('bista_account.group_own_customer'):
            args += [('partner_id.user_id', '=', self.env.user.id)]
        return super(AccountPayment, self).search(args, offset, limit, order,
                                               count)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        if self.env.user.has_group('bista_account.group_own_customer'):
            domain += [('partner_id.user_id', '=', self.env.user.id)]
        return super(AccountPayment, self).read_group(domain, fields, groupby,
                                                   offset, limit, orderby,
                                                   lazy)
