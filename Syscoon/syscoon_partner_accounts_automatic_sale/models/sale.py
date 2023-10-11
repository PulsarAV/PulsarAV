# See LICENSE file for full copyright and licensing details.


from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        company = self.env.company
        for rec in res:
            create_accounts = [auto.code for auto in company.create_auto_account_on]
            types = {}
            partner = rec.partner_id.commercial_partner_id
            if (
                company.use_separate_partner_numbers
                and "sale_order_customer_numbers" in create_accounts
            ):
                types["customer_number"] = True
            if types:
                partner.create_accounts(company, types)
        return res

    def action_confirm(self):
        context = self._context.copy()
        res = super().action_confirm()
        company = self.env.company
        create_accounts = [auto.code for auto in company.create_auto_account_on]
        types = {}
        if not self:
            if context.get('params'):
                order = self.browse([context['params'].get('id')])
            else:
                return res
        else:
            order = self
        partner = order.partner_id.commercial_partner_id
        if 'sale_order_customer' in create_accounts:
            types['asset_receivable'] = True
        if company.use_separate_accounts:
            types['use_separate'] = True
        if company.add_number_to_partner_number:
            types["add_number"] = True
        if (
            company.use_separate_partner_numbers
            and "sale_order_customer_numbers" in create_accounts
        ):
            types["customer_number"] = True
        if types:
            partner.create_accounts(company, types)
        return res
