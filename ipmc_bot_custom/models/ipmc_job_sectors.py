from odoo import api, fields, models


class IpmcSectors(models.Model):
    _description = "Sectors of Applicants"
    _inherit = 'hr.department'

    ex_id = fields.Integer(string='External ID')
