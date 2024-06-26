from odoo import api, fields, models


class IpmcBanks(models.Model):
    _description = "Banks which works in Saudi Arabia"
    _inherit = 'res.bank'

    ex_id = fields.Integer(string='External ID')
