# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
import logging
logger = logging.getLogger('Script log')

class StockPicking(models.Model):
    _inherit= "stock.picking"

    def button_validate(self):
        """
        On picking validate check for processed qty is not more then reserved
        Quantity in stock move.
        :return:
        """
        no_more_qty = any(self.move_lines.filtered(lambda move:
                            move.quantity_done > move.reserved_availability
                            and move.product_uom_qty and move.state not in ('done','cancel')))
        if False and no_more_qty and self.picking_type_code in ('internal','outgoing'):
            raise UserError(_(
                "Cannot process products more than reserved Quantity."))
        return super(StockPicking, self).button_validate()

    def mass_picking_unreserve(self):
        """
        Mass Unreserve
        """
        reject_rec_ids = self.filtered(lambda r: r.state == 'assigned')
        for rec in reject_rec_ids:
            rec.do_unreserve()
            rec._cr.commit()
            logger.info('Unreserve======: %s' % rec.name)
        logger.info('********Unreserve Done********')
        return True

    def mass_picking_reserve(self):
        """
        Mass Reservation
        """
        # reject_rec_ids = self.search([('state','=','confirmed'),
        #                               ('id','in',tuple(self.ids))],
        #                               order="scheduled_date,id")
        reject_rec_ids = self.search([('state','in',('confirmed','assigned')),
                                      ('id','in',tuple(self.ids))],
                                     order="scheduled_date,id")
        for rec in reject_rec_ids:
            rec.action_assign()
            rec._cr.commit()
            logger.info('Reserve=====: %s %s %s',rec,rec.name,rec.origin)
        logger.info('******Reserve Done******')
        return True
