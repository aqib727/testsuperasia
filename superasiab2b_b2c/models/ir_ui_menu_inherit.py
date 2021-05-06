from odoo import models, api, tools


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    @api.model
    @tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'debug')
    def _visible_menu_ids(self, debug=False):
        menus = super(IrUiMenu, self)._visible_menu_ids(debug)

        userobj = self.env['res.users']
        superasiaid = self.env['ir.model.data'].get_object('superasiab2b_b2c', 'group_b2baccount')
        b2buser = userobj.search([('id', '=', self.env.uid), ('groups_id', 'in', superasiaid.id)])

        if b2buser:
            menus.discard(self.env.ref("mail.menu_root_discuss").id)

        return menus
