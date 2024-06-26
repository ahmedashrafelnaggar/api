from odoo import api, fields, models


class IpmcNationalities(models.Model):
    _description = "Nationalities of Applicants"
    _inherit = 'res.country'

    ex_id = fields.Integer(string='External ID')
