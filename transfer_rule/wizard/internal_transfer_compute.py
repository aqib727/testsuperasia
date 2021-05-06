from odoo import api, models, tools

import logging


class InternalTransferScheduler(models.TransientModel):
    _name = 'internal.scheduler.compute'
    _description = 'Run Scheduler Manually'

    def internal_transfer(self):
        rules_ids = self.env['internal.stock.orderpoint'].search([])
        rules_ids.run_rule()
