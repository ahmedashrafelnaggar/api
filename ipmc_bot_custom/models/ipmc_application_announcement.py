from odoo import api, fields, models


class IpmcApplicationAnnouncement(models.Model):
    _name = "ipmc.application.announcement"
    _description = "Jobs Application Announcement"

    ex_id = fields.Integer(string="External ID")
    name = fields.Char("Name")
    code = fields.Char("Code")
    start_at = fields.Date(string="Start In")
    closed_at = fields.Date(string="Closed At")
    terms = fields.Text(string="Termas")
    notes = fields.Text(string="Notes")
    descriptions = fields.Text(string="Description")
