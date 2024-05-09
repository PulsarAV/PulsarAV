# -*- coding: utf-8 -*-
# Part of schwarz. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class Project(models.Model):
    _inherit = "project.project"

    responsible_ids = fields.Many2many('res.users',
                string="Responsible", domain="[('share', '=', False), ('active', '=', True)]")
