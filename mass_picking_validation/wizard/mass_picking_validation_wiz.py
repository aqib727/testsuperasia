
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

import logging
logger = logging.getLogger('Delivery Validation')

class MassPickingValidationWiz(models.TransientModel):
    _name = 'mass.picking.validation.wiz'

    def mass_picking_transfer(self):
        """
        Picking Mass Validation create force wizard if quantity done not inpute
        If picking is ready then validate multiple picking at a time.
        """
        picking = self.env[self._context.get('active_model')]
        picking_ids = picking.search([('id','in',self._context.get('active_ids'))])
        draft_order = picking_ids.filtered(lambda r: r.state == 'draft' and r.show_check_availability == False)
        do_order = picking_ids.filtered(lambda r: r.state == 'draft' and r.show_check_availability == False)

        for rec in do_order:
            if rec.state == 'draft':
                rec.action_confirm()
            if rec.state == 'confirmed':
                rec.action_assign()
            # rec.button_validate()
            # unreserved_lines = rec.move_line_ids_without_package.filtered\
            #     (lambda ml: ml.reserved_availability <= 0)
            # if not unreserved_lines:
            #     rec.button_validate()


        #transfer_ids = picking_ids.filtered(lambda r: r.picking_type_code != 'outgoing')
        msg = ''
        #if transfer_ids:
            #do_order = do_order - transfer_ids
            #msg += "You cannot validate the orders that are either Incoming Recepits or Internal Transfers. Check the following reference:\n" + ",".join(map(str, transfer_ids.mapped('name'))) + '\n'


        # not_do_pick_ids  = [pick.name for pick in picking_ids - do_order]
        not_do_pick_ids = picking_ids.filtered(lambda r: r.state == 'assigned' and r.show_check_availability == True).mapped('name')
        if not_do_pick_ids:
            msg += "You cannot validate the order since the products are not available. Check for the following reference \n" + ",".join(map(str, not_do_pick_ids)) + '\n'

        order_not_ready = picking_ids.filtered(lambda r: r.state != 'assigned').mapped('name')
        if order_not_ready:
            msg += "You cannot process the Orders that are in Waiting state, Done state or Cancelled state. Check for the reference \n" + ",".join(map(str, order_not_ready)) + '\n'



        lines_missing = []
        no_reserveed = []
        no_lot_assign = []
        overprocessed = []
        backorder = []
        ready_picking_ids = []
        picking_name = ''
        for record in do_order:
            picking_name = record.name
            if not record.move_lines and not record.move_line_ids:
                lines_missing.append(picking_name)


            # If no lots when needed, raise error
            picking_type = record.picking_type_id
            precision_digits = record.env['decimal.precision'].precision_get('Product Unit of Measure')
            no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in record.move_line_ids)
            no_reserved_quantities = all(float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in record.move_line_ids)
            if no_reserved_quantities and no_quantities_done:
                no_reserveed.append(picking_name)

            if picking_type.use_create_lots or picking_type.use_existing_lots:
                lines_to_check = record.move_line_ids
                if not no_quantities_done:
                    lines_to_check = lines_to_check.filtered(
                        lambda line: float_compare(line.qty_done, 0,
                                                   precision_rounding=line.product_uom_id.rounding)
                    )
                lot_product = ''
                for line in lines_to_check:
                    product = line.product_id
                    if product and product.tracking != 'none':
                        if not line.lot_name and not line.lot_id:
                            lot_product = product.display_name if not lot_product else lot_product + ',' + product.display_name

                if lot_product:
                    pick_no_lot_prod = picking_name + ': ' + lot_product +'\n'
                    no_lot_assign.append(pick_no_lot_prod)

            if no_quantities_done:
                ready_picking_ids.append(record)
                continue
            elif record._get_overprocessed_stock_moves() and not record._context.get('skip_overprocessed_check'):
                overprocessed.append(picking_name)
                continue
            elif record._check_backorder():
                backorder.append(picking_name)
                continue
            ready_picking_ids.append(record)

        if lines_missing:
            msg += 'Kindly add some lines to order: \n' + ",".join(map(str, lines_missing)) + '\n'
        if no_reserveed:
            msg += 'You cannot validate a transfer if you have not processed any quantity. You should rather cancel the transfer. \n' + ",".join(map(str, no_reserveed)) + '\n'
        if no_lot_assign:
            msg += 'You need to enter a lot/serial number for:  \n' + ",".join(map(str, no_lot_assign)) + '\n'
        if overprocessed:
            msg += 'You cannot process more than what was initially planned. Kindly validate manually for: \n' + ",".join(map(str, overprocessed)) + '\n'
        if backorder:
            msg += "You cannot validate a partial order. Kindly validate manually for:\n" + ",".join(map(str, backorder)) + '\n'
        if msg:
            raise ValidationError(msg)
        else:
            for picking in ready_picking_ids:
                logger.info('Processing== start======: %s' % picking.name)
                if all([x.qty_done == 0.0 for x in picking.move_line_ids]):
                    for move in picking.move_lines:
                        for move_line in move.move_line_ids:
                            move_line.qty_done = move_line.product_uom_qty
                            # move_line.qty_done = move_line.product_uom_qty
                picking.action_done()
            logger.info("All Transfers Complete===")
        return False
