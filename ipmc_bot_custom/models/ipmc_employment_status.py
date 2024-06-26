from odoo import api, fields, models


class IpmcEmploymentStatus(models.Model):
    _name = "employment.status"
    _description = "Employment status for Applicants"


    name = fields.Char('Name')
    code=fields.Char(string='Code')
    description = fields.Text('Description')
    ex_id=fields.Integer(string='External ID')
