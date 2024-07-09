# -*- coding: utf-8 -*-

from odoo import fields, models, _, api


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    sale_order_ref = fields.Char(string="Sale ref.", compute="_compute_sale_order_ref")
    sale_order_project = fields.Char(string="Project")

    @api.depends('picking_id.origin')
    def _compute_sale_order_ref(self):
        for line in self:
            line.sale_order_ref = ''
            line.sale_order_project = ''
            if line.picking_id.origin:
                line.sale_order_ref = line.picking_id.origin
                sale_order_id = self.env['sale.order'].search([('name','=',line.picking_id.origin)])
                project = self.env['project.project'].search([('sale_order_id','=',sale_order_id.id)], limit=1)
                line.sale_order_project = project.name
