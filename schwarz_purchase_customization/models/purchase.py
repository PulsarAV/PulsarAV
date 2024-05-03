# -*- coding: utf-8 -*-

from odoo import fields, models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    stock_move_line_count = fields.Integer(string="Number of move lines", compute="_compute_stock_move_line_count")

    def view_purchase_stock_move_lines(self):
        outgoing_move_lines = self.env['stock.move.line'].search([('picking_id.origin','=',self.name)]).ids
        return {
            'name': _('Moves History'),
            'res_model': 'stock.move.line',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'view_mode': 'tree,form',
            'context':{'search_default_groupby_product_id': True},
            'domain':[('state','!=','done'),('id','in',outgoing_move_lines)]
        }

    def _compute_stock_move_line_count(self):
        outgoing_move_lines = self.env['stock.move.line'].search([('picking_id.origin','=',self.name)]).ids
        for purchase in self:
            purchase.stock_move_line_count = 0
            if outgoing_move_lines and self._get_sale_orders():
                purchase.stock_move_line_count = len(outgoing_move_lines)
