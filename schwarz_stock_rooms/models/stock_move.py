# -*- coding: utf-8 -*-
# Part of schwarz. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _

class StockMove(models.Model):
    _inherit = 'stock.move'


    room_ids = fields.Many2many("project.rooms", 'project_room_rel',string="Room",compute ='_compute_project_rooms')
    room_id = fields.Many2one("project.rooms", string="Room")

    def _compute_project_rooms(self):
        for record in self:
            room_ids = []
            if record.sale_line_id:
                if record.sale_line_id.order_id.project_count>0 and record.sale_line_id.order_id.project_ids:
                    projects = record.sale_line_id.order_id.project_ids
                    project_records =  self.env['project.project'].search([('id','in',projects.ids)])
                    if project_records:
                        for project in project_records:
                            for room in project.rooms_ids:
                                if room.id not in room_ids:
                                    room_ids.append(room.id)
            if room_ids:
                project_rooms = self.env['project.rooms'].search([('id','in',room_ids)])
                if project_rooms:
                    record.room_ids = [(6,0,project_rooms.ids)]
            else:
                record.room_ids = False
                
