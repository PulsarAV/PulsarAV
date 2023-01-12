from odoo import fields, models

class ProjectTask(models.Model):
    _inherit = 'project.task'
    task_type = fields.Selection([
        ('As built drawing', 'As built drawing'),
        ('IP List', 'IP List'),
        ('Manual', 'Manual'),
        ('Programming', 'Programming'),
        ('Images - Pre and after', 'Bilder - Pre and after'),
        ('Dailyreport', 'Daily report')
    ], string='Task Type')