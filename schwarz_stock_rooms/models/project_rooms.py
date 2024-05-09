# -*- coding: utf-8 -*-
# Part of schwarz. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _


class ProjectRooms(models.Model):
    _name = 'project.rooms'
    _description = 'Project Rooms'

    name = fields.Char(string='Name', required=True)