from odoo import api, fields, models


class IpmcOpportunities(models.Model):
    _inherit='hr.job'
    _description = "Available Opportunities for Applicants"

    ex_id=fields.Integer(string='External ID')