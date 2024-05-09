# -*- coding: utf-8 -*-
# Part of schwarz. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.project.controllers.portal import ProjectCustomerPortal
from odoo.exceptions import AccessError, MissingError

class ProjectCustomerPortalExtend(ProjectCustomerPortal):

    @http.route()
    def portal_my_task(self, task_id, report_type=None, access_token=None, project_sharing=False, **kw):
        res = super(ProjectCustomerPortalExtend, self).portal_my_task(task_id, report_type, access_token, project_sharing, **kw)
        try:
            project_id = res.qcontext['task'].project_id.id
            project_sudo = self._document_check_access('project.project', project_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        if project_sudo.collaborator_count and project_sudo.with_user(request.env.user)._check_project_sharing_access():
            res.qcontext['allow_editable'] = True
        else:
            res.qcontext['allow_editable'] = False
        return res

    @http.route('/assignees/update', type='json', auth='public', website=True)
    def portal_chatter_init(self, is_added, user_id, task_id):
        user_id = int(user_id) if user_id else False
        if task_id:
            task = request.env['project.task'].sudo().browse(task_id)
            if task and is_added and user_id not in task.user_ids.ids:
                task.sudo().write({'user_ids':[(4,user_id)]})
                return True

            elif task and not is_added and user_id in task.user_ids.ids:
                task.sudo().write({'user_ids':[(3,user_id)]})
                return True
        return False