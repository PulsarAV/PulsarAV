# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol Infotech Private Limited. (<https://www.droggol.com/>)

from odoo import http
from odoo.http import request

from odoo.addons.sale_product_configurator.controllers.main import ProductConfiguratorController


class DroggolThemeCommon(http.Controller):

    @http.route(['/droggol_theme_common/design_content/<model("dr.website.content"):content>'], type='http', website=True, auth='user')
    def design_content(self, content, **post):
        return request.render('droggol_theme_common.design_content', {'content': content, 'no_header': True, 'no_footer': True})


class DroggolThemeProductConfiguratorController(ProductConfiguratorController):

    def _get_product_information(self, product_template, combination, currency_id, so_date, quantity=1, product_uom_id=None, pricelist_id=None, parent_combination=None):
        result = super(DroggolThemeProductConfiguratorController, self)._get_product_information(
            product_template=product_template, combination=combination, currency_id=currency_id,
            so_date=so_date, quantity=quantity, product_uom_id=product_uom_id, pricelist_id=pricelist_id, parent_combination=parent_combination)

        result['extra_info'] = {
            ptav.id: {
                'dr_thumb_image': ptav.dr_thumb_image,
                'dr_image': ptav.dr_image,
            } for ptav in product_template.attribute_line_ids.product_template_value_ids
        }

        return result
