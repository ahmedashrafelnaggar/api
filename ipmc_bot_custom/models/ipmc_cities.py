from odoo import api, fields, models


class IpmcCities(models.Model):
    _description = "Cities which located in Saudi Arabia"
    _inherit='res.country.state'

    ex_id=fields.Integer(string='External ID')