# -*- coding: utf-8 -*-

from odoo import fields, models, _, api


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    sale_order_ref = fields.Char(string="Sale ref.", compute="_compute_sale_order_ref")
    sale_order_deliveries = fields.Char(string="Sale order")
    sale_order_project = fields.Char(string="Project")

    @api.depends('origin')
    def _compute_sale_order_ref(self):
        for line in self:
            line.sale_order_ref = ''
            line.sale_order_deliveries = ''
            line.sale_order_project = ''
            if line.origin:
                purchase_order = self.env['purchase.order'].search([('name','=',line.origin)], limit=1)
                if purchase_order:
                    sale_orders = purchase_order._get_sale_orders()
                    if sale_orders:
                        sale_order_id = sale_orders.sorted(lambda x:x.id)[-1]
                        line.sale_order_ref = sale_order_id.name
                        if line.sale_order_ref:
                            picking = self.env['stock.picking'].search([('origin','=',line.sale_order_ref)], limit=1)
                            line.sale_order_deliveries = picking.name

                            project = self.env['project.project'].search([('sale_order_id','=',sale_order_id.id)], limit=1)
                            line.sale_order_project = project.name
