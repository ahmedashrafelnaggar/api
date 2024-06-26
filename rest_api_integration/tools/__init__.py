# -*- coding: utf-8 -*-

from .http import *
from . import ir_http


def get_translation(env, res_id, lang, field_name):
    record = env['ir.translation'].sudo().search([('lang', '=', lang), ('res_id', '=', res_id), ('name', '=', field_name)])
    return record and record.value


def get_translated_message(env, lang, source):
    record = env['ir.translation'].sudo().search([('lang', '=', lang), ('source', '=', source), ('type', '=', 'code')])
    return record and record.value
