# -*- coding: utf-8 -*-
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


# ------------------
# Migrate documents
# ------------------

def delete_views(domain, env):
    views_to_delete = env['ir.ui.view'].with_context(active_test=False).search(domain)
    _logger.info('DRGL-MIG: (%s) Views to delete: %s' % (len(views_to_delete.ids), views_to_delete.ids))
    if views_to_delete:
        child_views = views_to_delete.mapped('inherit_children_ids')
        _logger.info('DRGL-MIG: (%s) Child Views to delete: %s' % (len(child_views.ids), child_views.ids))
        child_views.unlink()
    dr_views_to_delete = views_to_delete.filtered(lambda v: not len(v.inherit_children_ids))
    if dr_views_to_delete:
        dr_views_to_delete.unlink()

def deactivate_assets(domain, env):
    assets_to_remove = env['ir.asset'].with_context(active_test=False).search(domain)
    _logger.info('DRGL-MIG: (%s) assets to delete: %s' % (len(assets_to_remove.ids), assets_to_remove.ids))
    if assets_to_remove:
        assets_to_remove.unlink()


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for product in env['product.template'].search([('dr_document_ids', '!=', False)]):
        att_without_document = product.dr_document_ids - product.product_document_ids.mapped('ir_attachment_id')
        att_with_document = product.product_document_ids.filtered(lambda doc: doc.ir_attachment_id not in att_without_document.ids)

        if att_with_document:
            att_with_document.write({'shown_on_product_page': True})

        if att_without_document:
            attachment_data = [{'ir_attachment_id': attachment.id, 'shown_on_product_page': True} for attachment in att_without_document]
            documents = env['product.document'].sudo().with_context(disable_product_documents_creation=True).create(attachment_data)
            _logger.info("[PRIME] Created prime documents product(%s): %s", product.id, documents.ids)

        _logger.info("[PRIME] Detached prime documents product: %s", product.dr_document_ids.ids)
        product.dr_document_ids = False

    _logger.info('DRGL-MIG START: -------------------------------------------- ')
    views_id_to_delete = ["droggol_theme_common"]
    domain = [('arch_fs', 'ilike', f'{view}/%') for view in views_id_to_delete]
    ors = ['|'] * (len(domain) - 1)
    domain = ors + domain
    delete_views(domain, env)
    paths = ['/droggol_theme_common/static/src/js/backend/res_config_settings.js', '/droggol_theme_common/static/src/scss/variants.scss', '/droggol_theme_common/static/src/js/backend/list_view_brand.js']
    domain = [('path', 'in', paths)]
    deactivate_assets(domain, env)