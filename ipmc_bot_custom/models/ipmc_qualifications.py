from odoo import api, fields, models


class IpmcQualifications(models.Model):
    _description = "Qualifications for Applicants"
    _inherit = 'hr.recruitment.degree'

    ex_id = fields.Integer(string='External ID')
