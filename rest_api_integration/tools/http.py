# -*- coding: utf-8 -*-

from odoo import _
from functools import wraps
import json
import odoo
from odoo.http import JsonRequest, AuthenticationError, SessionExpiredException, serialize_exception, Response
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import AccessDenied, except_orm
from odoo.tools import ustr
from psycopg2 import IntegrityError
import werkzeug.contrib.sessions
import werkzeug.datastructures
import werkzeug.exceptions
import werkzeug.local
import werkzeug.routing
import werkzeug.wrappers
import werkzeug.wsgi


import logging

_logger = logging.getLogger(__name__)


class CustomJsonRequest(JsonRequest):

    def __init__(self, *args):
        super(JsonRequest, self).__init__(*args)
        self.jsonp_handler = None
        self.params = {}
        args = self.httprequest.args
        jsonp = args.get('jsonp')
        self.jsonp = jsonp
        request = None
        request_id = args.get('id')
        api = self.httprequest.headers.get('Api-Access')
        if jsonp and self.httprequest.method == 'POST':
            # jsonp 2 steps step1 POST: save call
            def handler():
                self.session['jsonp_request_%s' % (request_id,)] = self.httprequest.form['r']
                self.session.modified = True
                headers = [('Content-Type', 'text/plain; charset=utf-8')]
                r = werkzeug.wrappers.Response(request_id, headers=headers)
                return r

            self.jsonp_handler = handler
            return
        elif jsonp and args.get('r'):
            # jsonp method GET
            request = args.get('r')
        elif jsonp and request_id:
            # jsonp 2 steps step2 GET: run and return result
            request = self.session.pop('jsonp_request_%s' % (request_id,), '{}')
        elif api and api == 'application/api' and self.httprequest.method == 'GET':
            request = json.dumps(args.to_dict())
        else:
            # regular jsonrpc2
            request = self.httprequest.get_data().decode(self.httprequest.charset)

        # Read POST content or POST Form Data named "request"
        try:
            self.jsonrequest = json.loads(request)
        except ValueError:
            msg = 'Invalid JSON data: %r' % (request,)
            _logger.info('%s: %s', self.httprequest.path, msg)
            raise werkzeug.exceptions.BadRequest(msg)

        self.params = dict(self.jsonrequest.get("params", {}))
        self.context = self.params.pop('context', dict(self.session.context))

    def _handle_exception(self, exception):
        """Called within an except block to allow converting exceptions
           to arbitrary responses. Anything returned (except None) will
           be used as response."""
        try:
            return super(JsonRequest, self)._handle_exception(exception)
        except Exception:
            if not isinstance(exception, (odoo.exceptions.Warning, SessionExpiredException,
                                          odoo.exceptions.except_orm, werkzeug.exceptions.NotFound)):
                _logger.exception("Exception during JSON request handling.")

            error = {
                'code': 200,
                'message': "Odoo Server Error",
                'data': serialize_exception(exception)
            }
            if self.httprequest.headers.get('Api-Access') == 'application/api':
                error = {
                    'http_status': 500,
                    'message': exception.args and str(list(exception.args)[0]) or str(exception),
                }
            lang = self.httprequest.headers.get('lang') or 'en'
            lang = 'ar_AA' if lang == 'ar' else 'en_US'

            if isinstance(exception, AccessDenied):
                error['http_status'] = 403
                error['message'] = _("Unauthorized User")
                if lang == 'ar_AA':
                    record = self.env['ir.translation'].sudo().search(
                        [('lang', '=', lang), ('source', '=', "Unauthorized User"),
                         ('type', '=', 'code')])
                    if record:
                        error['message'] = record.value
            if isinstance(exception, IntegrityError):
                error['message'] = "Missing Required Fields"
            if isinstance(exception, werkzeug.exceptions.NotFound):
                error['http_status'] = 404
                error['code'] = 404
                error['message'] = "404: Not Found"
            if isinstance(exception, AuthenticationError):
                error['code'] = 100
                error['message'] = "Odoo Session Invalid"
            if isinstance(exception, SessionExpiredException):
                error['code'] = 100
                error['message'] = "Odoo Session Expired"
            return self._json_response(error=error)


JsonRequest.__init__ = CustomJsonRequest.__init__
JsonRequest._handle_exception = CustomJsonRequest._handle_exception


class make_response():
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = decode_bytes(func(*args, **kwargs))
            result = {'data': result, 'http_status': 200}
            return result
        return wrapper


def eval_request_params(kwargs):
    for k, v in kwargs.items():
        try:
            kwargs[k] = safe_eval(v)
        except Exception:
            continue


def decode_bytes(result):
    if isinstance(result, (list, tuple)):
        decoded_result = []
        for item in result:
            decoded_result.append(decode_bytes(item))
        return decoded_result
    if isinstance(result, dict):
        decoded_result = {}
        for k, v in result.items():
            decoded_result[decode_bytes(k)] = decode_bytes(v)
        return decoded_result
    if isinstance(result, bytes):
        return result.decode('utf-8')
    return result
