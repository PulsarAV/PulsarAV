# -*- coding: utf-8 -*-
# Part of Schwarz. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, _lt


class Project(models.Model):
    _inherit = "project.project"

    so_move_line_count = fields.Integer(string="Delivery Move Count", compute="_compute_stock_move_line_count")


    def action_view_somoves(self):
        self.ensure_one()
        sale_order_items_per_project_id = self._fetch_sale_order_items_per_project_id({'project.task': [('state', 'in', self.env['project.task'].OPEN_STATES)]})
        for project in self:
            sale_order_lines = sale_order_items_per_project_id.get(project.id, self.env['sale.order.line'])
            stock_move_line_ids = []
            sale_orders = []
            if sale_order_lines:
               for line in sale_order_lines:
                   if line.order_id.id not in sale_orders:
                       sale_orders.append(line.order_id.id)
               
               if sale_orders:
                  for order in self.env['sale.order'].search([('id','in',sale_orders)]):
                      for line in order.order_line:
                          if line.product_id and line.product_id.type!='service' and line.move_ids:
                              for move in line.move_ids:
                                  if move.move_line_ids:
                                      for move_line in move.move_line_ids:
                                          if move_line.id not in stock_move_line_ids:
                                              stock_move_line_ids.append(move_line.id)
        action_window = {
            "type": "ir.actions.act_window",
            "res_model": "stock.move.line",
            'name': _("%(name)s's Deliveries", name=self.name),
            "context": {"create": self.env.context.get('create_for_project_id', False), "show_sale": True},
            "domain": [('id', 'in', stock_move_line_ids)],
            "views": [[False, "tree"], [False, "form"]],
        }
        return action_window
        
    def action_view_sale_stock_move_lines(self):
        sale_order_items_per_project_id = self._fetch_sale_order_items_per_project_id({'project.task': [('state', 'in', self.env['project.task'].OPEN_STATES)]})
        for project in self:
            sale_order_lines = sale_order_items_per_project_id.get(project.id, self.env['sale.order.line'])
            stock_move_line_ids = []
            sale_orders = []
            if sale_order_lines:
               for line in sale_order_lines:
                   if line.order_id not in sale_orders:
                       sale_orders.append(line.order_id.id)
               
               if sale_orders:
                  for order in self.env['sale.order'].search([('id','in',sale_orders)]):
                      for line in order.order_line:
                          if line.product_id and line.product_id.type!='service' and line.move_ids:
                              for move in line.move_ids:
                                  if move.move_line_ids:
                                      for move_line in move.move_line_ids:
                                          if move_line.id not in stock_move_line_ids:
                                              stock_move_line_ids.append(move_line.id)
        return {
            'name': _('Moves History'),
            'res_model': 'stock.move.line',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'context':{'search_default_groupby_product_id': True},
            'domain':[('state','!=','done'),('id','in',stock_move_line_ids)]
        }

    def _get_stat_buttons(self):
        buttons = super(Project, self)._get_stat_buttons()
        buttons.append({
                'icon': 'dollar',
                'text': _lt('Delivery Items'),
                'number': self.so_move_line_count,
                'action_type': 'object',
                'action': 'action_view_somoves',
                'show': True,
                'sequence': 40,
            })
        return buttons   

    def _compute_stock_move_line_count(self):
        sale_order_items_per_project_id = self._fetch_sale_order_items_per_project_id({'project.task': [('state', 'in', self.env['project.task'].OPEN_STATES)]})
        for project in self:
            sale_order_lines = sale_order_items_per_project_id.get(project.id, self.env['sale.order.line'])
            stock_move_line_ids = []
            sale_orders = []
            if sale_order_lines:
               for line in sale_order_lines:
                   if line.order_id not in sale_orders:
                       sale_orders.append(line.order_id.id)
               
               if sale_orders:
                  for order in self.env['sale.order'].search([('id','in',sale_orders)]):
                      for line in order.order_line:
                          if line.product_id and line.product_id.type!='service' and line.move_ids:
                              for move in line.move_ids:
                                  if move.move_line_ids:
                                      for move_line in move.move_line_ids:
                                          if move_line.id not in stock_move_line_ids:
                                              stock_move_line_ids.append(move_line.id)
                     

            project.so_move_line_count = len(stock_move_line_ids)
            

    
