# -*- coding: utf-8 -*-

from odoo import fields, models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    stock_move_line_count = fields.Integer(string="Number of move lines", compute="_compute_stock_move_line_count")

    def view_purchase_stock_move_lines(self):
        product_ids = self.order_line.mapped('product_id').ids
        outgoing_move_lines = self.env['stock.move.line'].search([('product_id','in',product_ids),
                                                                  ('picking_type_id.code','=','outgoing'),
                                                                  ('state','!=','done')]).ids

        return {
            'name': _('Moves History'),
            'res_model': 'stock.move.line',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'view_mode': 'tree,form',
            'context':{'search_default_groupby_product_id': True},
            'domain':[('id','in',outgoing_move_lines)]
        }

    def _compute_stock_move_line_count(self):
        for purchase in self:
            purchase.stock_move_line_count = 0
            product_ids = purchase.order_line.mapped('product_id').ids
            if product_ids:
                outgoing_move_lines = self.env['stock.move.line'].search([('product_id','in',product_ids),
                                                                        ('picking_type_id.code','=','outgoing'),
                                                                        ('state','!=','done')]).ids
                purchase.stock_move_line_count = len(outgoing_move_lines) if outgoing_move_lines else 0
