# -*- coding: utf-8 -*-
""" Odoo Rest Api Integration"""

from odoo import http, _, models
from odoo.exceptions import AccessDenied
from odoo.http import request
from odoo.tools import config
import hashlib
import ast
import odoo
def _generate_encrypted_secret_key(secret_key):
    h = hashlib.new('sha256', secret_key.encode('utf-8'))
    encrypted_secret_key = h.hexdigest()
    return encrypted_secret_key


def _check_authenticated_user():
    if not request.httprequest.headers.get('Token'):
        raise Exception(_("Invalid Access Token"))
    access_token = request.httprequest.headers['Token']
    user = request.env['res.users'].sudo().search([('api_access_token', '=', access_token)])
    if not user:
        raise AccessDenied()

    return {
        'userId': user.id,
    }

class RestApi(http.Controller):
    """
    There are URIs available:

    /api/auth                   POST    - Login in Odoo

    /api/<model>                GET     - Read all (with optional domain, fields, offset, limit, order)
    /api/<model>/<id>           GET     - Read one (with optional fields)
    /api/<model>                POST    - Create one
    /api/<model>/<id>           POST     - Update one
    /api/<model>/<id>           DELETE  - Delete one
    /api/<model>/<id>/<method>  POST     - Call method (with optional parameters)
    /api/<model>/<method>  POST     - Call method (with optional parameters)
    /api/<model>/<method>  GET     - Call method (with optional parameters)
    """

    @http.route('/web/session/erp_authenticate', auth='none', type="json", methods=["POST"], csrf=False)
    def authenticate(self,  login, password, base_location=None):
        db = config['api_db_name']
        authenticate_test = request.session.authenticate(db, login, password)
        session_info = request.session
        # return session_info
        # session_info = request.env['ir.http'].sudo().session_info()
        if 'uid' in session_info and session_info.get('uid') not in [False,None]:
            uid = session_info.get('uid')
        elif 'pre_uid' in session_info and session_info.get('pre_uid') not in [False,None]:
            uid = session_info.get('pre_uid')
        else:
            session_info.update({
                "Code": 404,
                "StatusDescription": "Failed",
                "ArabicMessage": "عفوا البيانات المدخلة خاطئة",
                "EnglishMessage": "Invalid Username or password"
            })
        request.session.db = db
        registry = odoo.modules.registry.Registry(db)
        with registry.cursor() as cr:
            env = odoo.api.Environment(cr, request.session.uid, request.session.context)
            user = env['res.users'].sudo().browse(uid)
            token = user.api_access_token
            if not token:
                token = user.sudo()._generate_api_access_token()
            session_info.update({'token': token, "Code": 200, "StatusDescription": "Failed",
                                     "ArabicMessage": "تم تسجيل الدخول بنجاح",
                                 "EnglishMessage": "Login Successfully"
                                 })
        return session_info

    @http.route(['/api/<string:model>',
            '/api/<string:model>/<int:id>'],
           type="json", auth='none', methods=["GET"], csrf=False)
    def search_read_record(self, model, id=None):
        """ Read all records or a specific record with optional domain, fields, offset,
         limit & order. """
        _check_authenticated_user()
        if not request.env['ir.model'].sudo().search([('model', '=', model)]):
            raise Exception('There is no model named %s' % model)
            data = dict()
        if request.httprequest.args:
            data = request.httprequest.args.to_dict()
        # eval_request_params(data)
        keys = ['domain', 'fields', 'offset', 'limit', 'order']
        for key in data.keys():
            if key not in keys:
                raise Exception("unexpected argument %s", key)
        if id:
            record = request.env[model].sudo().search([('id', '=', id)])
            if not record:
                raise Exception('There is no record with id %s' % str(id))
            result = record.sudo().read(**data)
            result = result and result[0] or {}
            return result
        return request.env[model].sudo().search_read(**data)

    @http.route(['/api/<string:model>',
            '/api/<string:model>/<int:id>'], type='json', auth="none",
           methods=["POST"], csrf=False)
    def create_update_record(self, model, id=None):
        """ create or update a record of a model. """
        _check_authenticated_user()
        if not request.env['ir.model'].sudo().search([('model', '=', model)]):
            raise Warning('There is no model named %s' % model)
        data = request.httprequest.data.decode('utf-8')
        data = ast.literal_eval(data)
        if not data:
            raise Exception("Invalid record data")
        # eval_request_params(data)
        fields = request.env[model].sudo().fields_get().keys()
        for key in data.keys():
            if key not in fields:
                raise Warning('There is no attribute named %s' % key)
        if id:
            record = request.env[model].sudo().search([('id', '=', id)])
            if not record:
                raise Exception('There is no record with id %s' % str(id))
            result = record.sudo().write(data)
            return result and 'Record with id %s successfully updated ' % str(id)
        spec = request.env[model]._onchange_spec()
        updates = request.env[model].sudo().onchange(data, list(fields), spec)
        values = updates.get('value', {})
        values = {k: v for k, v in values.items() if v}
        for name, val in values.items():
            if isinstance(val, tuple):
                values[name] = val[0]
        data.update(values)
        result = request.env[model].sudo().create(data)
        # result = request.env[model].sudo().write(data)
        if result:
            return{
               "id": result.id,
               # "iqama_number": result.iqama_number,
               "message": 'Record created successfully with id %s' % str(result.id)
           }

    @http.route('/api/<string:model>/<int:id>', auth='none', type="json", methods=["DELETE"])
    def unlink(self, model, id):
        """ Delete a record of a model if found. """
        _check_authenticated_user()
        if not request.env['ir.model'].sudo().search([('model', '=', model)]):
            raise Exception('There is no model named %s' % model)
        record = request.env[model].sudo().search([('id', '=', id)])
        if not record:
            raise Exception('There is no record with id %s' % str(id))
        record.sudo().unlink()
        return {
               "id": id,
               "message": 'Record with id %s  deleted successfully' % str(id)
           }

    @http.route(['/api/<string:model>/<int:id>/<string:method>',
            '/api/<string:model>/<string:method>'], auth='none',
           methods=["POST"], type='json', csrf=False)
    def record_method(self, model, method, id=None, **kwargs):
        lang = request.httprequest.headers.get('lang') or 'en'
        if lang not in ['ar', 'en']:
            raise Exception("Invalid Application Language")
        if not request.env['ir.model'].sudo().search([('model', '=', model)]):
            raise Exception('There is no model named %s' % model)

        record = request.env[model].sudo().search([('id', '=', id)])
        data = request.httprequest.data.decode('utf-8')
        data = ast.literal_eval(data)
        # eval_request_params(data)
        data['lang'] = lang
        user_dict = _check_authenticated_user()
        data.update(user_dict)
        if record:
            method = getattr(record, method)
            return method(**data)
        return getattr(request.env[model], method)(**data)

    @http.route('/api/<string:model>/<string:method>', auth='none', methods=["GET"], type='json', csrf=False)
    def model_method(self, model, method):
        url_params = dict()
        lang = request.httprequest.headers.get('lang') or 'en'
        if lang not in ['ar', 'en']:
            raise Exception("Invalid Application Language")
        url_params['lang'] = lang
        if not request.env['ir.model'].sudo().search([('model', '=', model)]):
            raise Exception('There is no model named %s' % model)
        if request.httprequest.args:
            args = request.httprequest.args.to_dict()
            url_params.update(args)
        user_dict = _check_authenticated_user()
        url_params.update(user_dict)
        return getattr(request.env[model], method)(**url_params)
