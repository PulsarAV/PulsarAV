# -*- coding: utf-8 -*-
# Part of schwarz. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _


class StockLot(models.Model):
    _inherit = "stock.lot"

    rooms_ids = fields.Many2many("project.rooms", string="Project Rooms",compute="_compute_set_room_tags")

    def _compute_set_room_tags(self):
        for rec in self:
            rec.rooms_ids = False
            stock_move_ids = self.env['stock.move.line'].search([('lot_id', '=', rec.id)])
            move = stock_move_ids.move_id.filtered(lambda x: x.picking_id)
            if move and move.room_id:
                rec.rooms_ids =  move.room_id.mapped('id')
               
