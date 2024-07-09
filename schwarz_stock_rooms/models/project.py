# -*- coding: utf-8 -*-
# Part of schwarz. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _


class Project(models.Model):
    _inherit = "project.project"

    rooms_ids = fields.Many2many("project.rooms", string="Rooms")
