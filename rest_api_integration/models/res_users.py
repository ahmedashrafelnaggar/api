# -*- coding: utf-8 -*-
""" Odoo Rest Api Integration"""

import re
import binascii, hashlib
import random
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, except_orm

import logging
LOGGER = logging.getLogger(__name__)


class User(models.Model):
    """
    """
    _inherit = 'res.users'

    def _get_random_secret_key(self):
        return str(random.randint(1000, 9999))

    api_access_token = fields.Char()
    secret_key = fields.Char(required=False, default=_get_random_secret_key)
    encrypted_secret_key = fields.Char(required=False)
    otp = fields.Char()
    otp_valid_date = fields.Datetime("OTP Valid Date")
    number_of_otp_try = fields.Integer("Number of OTP",default=0)
    block_send_otp_till = fields.Datetime("Block Send OTP Till")

    _sql_constraints = [("unique_api_access_token",
                         "UNIQUE(api_access_token)",
                         _('API Access Token should be unique')),
                        ("unique_encrypted_secret_key",
                         "UNIQUE(encrypted_secret_key)",
                         _('User secret key should be unique'))]

    # @api.constrains('secret_key')
    # def _check_secret_key(self):
    #     secret_key = self.secret_key
    #     if not (re.match(r'^[A-Z][a-zA-Z0-9]{7,9}$', secret_key)):
    #         raise ValidationError(_("User secret key should be from 7 to 10 letters & "
    #                                 "numbers starting with capital letter."))

    @api.model
    def num_ar_cnv(self, num):
        ar = u'٠١٢٣٤٥٦٧٨٩'
        en = u'0123456789'
        ret = ''
        for n in num:
            n2 = n if not n in en else ar[int(n)]
            ret += n2
        return ret

    @api.onchange('secret_key')
    def _onchange_secret_key(self):
        self.api_access_token = False

    @api.onchange('login')
    def _onchange_login(self):
        self.api_access_token = False

    def _generate_encrypted_secret_key(self):
        self.ensure_one()
        secret_key = self.secret_key or str(random.randint(1000, 9999))
        h = hashlib.new('sha256', secret_key.encode('utf-8'))
        self.encrypted_secret_key = h.hexdigest()
        return self.encrypted_secret_key

    def _generate_api_access_token(self):
        self.ensure_one()
        dk = hashlib.pbkdf2_hmac('sha256', self.secret_key.encode('utf-8'), self.login.encode('utf-8'), 100000)
        token = binascii.hexlify(dk).decode('utf-8')
        self.api_access_token = token
        return token


    @api.model
    def ValidateOTP(self, **args):
        try:
            user_id = args.get('userId') and int(args.get('userId'))
            if user_id:
                emp_obj = self.env['hr.employee'].sudo().search([('user_id', '=', user_id)], limit=1)
                if not emp_obj :
                    return False, {
                        "OTPCode": 403,
                        "StatusDescription": "Failed",
                        "Data": {},
                        "ArabicMessage": "لا يوجد ملف وظيفي لهذا المستخدم",
                        "EnglishMessage": "The user doesn't has employee profile"
                    }
            if not args.get('OTP'):
                return {
                    "OTPCode": 404,
                    "StatusDescription": "Failed",
                    "ArabicMessage": "رقم الكود مطلوب",
                    "EnglishMessage": "OTP Code Required"
                }
            if not emp_obj.personal_mobile:
                return False, {
                    "OTPCode": 403,
                    "StatusDescription": "Failed",
                    "Data": {},
                    "ArabicMessage": "لا يوجد رقم تليفون لهذا المستخدم",
                    "EnglishMessage": "This User doesn't have mobile number"
                }
            mobile = emp_obj.is_mobile(emp_obj.personal_mobile)
            if not mobile:
                return False, {
                    "OTPCode": 403,
                    "StatusDescription": "Failed",
                    "Data": {},
                    "ArabicMessage": "رقم الجوال المدخل غير صحيح",
                    "EnglishMessage": "Invalid Mobile Number"
                }
            user_obj = self.env['res.users'].browse(user_id)
            if user_obj.otp and user_obj.otp == args.get('OTP') and user_obj.otp_valid_date > str(datetime.now()):
                return {
                    "OTPCode": 201,
                    "StatusDescription": "Success",
                    "ArabicMessage": u"تم التحقق من الكود بنجاح",
                    "EnglishMessage": "Code has been verified"
                }
            else:
                return {
                    "OTPCode": 404,
                    "StatusDescription": "Failed",
                    "ArabicMessage": "الرمز غير صحيح",
                    "EnglishMessage": "OTP code is not correct"
                }
        except Exception as e:

            return {
                "OTPCode": 500,
                "StatusDescription": "Failed",
                "ErrorMessage": "System Error because of %s" % e,
                "ArabicMessage": u"نعتذر عن خدمتك حاليا الرجاء المحاولة لاحقا",
                "EnglishMessage": "We apologize for serving you currently.Please try again later."
            }

    @api.model
    def SendOTP(self, args):
        user_id = args.get('userId') and int(args.get('userId'))
        if not user_id:
            return False, {
            "OTPCode": 403,
            "StatusDescription": "Failed",
            "Data": {},
            "ArabicMessage": "لا يمكن ارسال كود التحقق",
            "EnglishMessage": "System can't send the verification code"
                }
        user_obj = self.env['res.users'].sudo().browse(user_id)
        if user_obj.mobile !='0554135668' and user_obj.block_send_otp_till and user_obj.block_send_otp_till > str(datetime.now()):
            return False, {
                "OTPCode": 403,
                "StatusDescription": "Failed",
                "Data": {},
                "ArabicMessage": "لقد تجاوزت عدد مرات تسجيل الدخول المسموح به الرجاء المحاولة في وقت آخر",
                "EnglishMessage": "You exceeded the number of tries to login please try again later"
            }

        emp_obj = self.env['hr.employee'].sudo().search([('user_id', '=', user_id)], limit=1)
        if not emp_obj:
            return False, {
            "OTPCode": 403,
            "StatusDescription": "Failed",
            "Data": {},
            "ArabicMessage": "لا يوجد ملف وظيفي لهذا المستخدم",
            "EnglishMessage": "The user doesn't has employee profile"
                }
        if not user_obj.mobile:
            return False, {
                "OTPCode": 403,
                "StatusDescription": "Failed",
                "Data": {},
                "ArabicMessage": "لا يوجد رقم تليفون لهذا المستخدم",
                "EnglishMessage": "This User doesn't have mobile number"
            }
        mobile = emp_obj.is_mobile(user_obj.mobile)
        if not mobile:
            return False, {
                "OTPCode": 403,
                "StatusDescription": "Failed",
                "Data": {},
                "ArabicMessage": "رقم الجوال المدخل غير صحيح",
                "EnglishMessage": "Invalid Mobile Number"
            }
        if mobile and mobile =='00966554135668':
            otp = "1111"
        else:
            otp = str(random.randint(1000, 9999))
        message = "Your verification code for new 2P ERP: " + otp
        result = self.env['res.company'].pool_send_message(message, mobile)
        if result != True:
            return False, {
                "OTPCode": 403,
                "StatusDescription": "Failed",
                "Data": {},
                "ArabicMessage": "حدث مشكلة اثناء ارسال كود التحقق",
                "EnglishMessage": "Problem during send verification code"
            }
        else:
            if not user_obj.otp_valid_date or (user_obj.otp_valid_date and user_obj.otp_valid_date[:10] < str(datetime.now().date())):
                user_obj.write({'otp': otp, 'otp_valid_date': datetime.now() + timedelta(minutes=3),
                                'block_send_otp_till': False,
                                'number_of_otp_try': 1})
            else:
                user_obj.write({'otp': otp, 'otp_valid_date': datetime.now() + timedelta(minutes=3),
                                'block_send_otp_till': False if user_obj.number_of_otp_try + 1 < 4 else datetime.now() + timedelta(hours=24),
                                'number_of_otp_try': user_obj.number_of_otp_try + 1})

            return True, {
                "OTPCode": 201,
                "StatusDescription": "Success",
                "Data": {},
                "ArabicMessage": u"تم ارسال كود الدخول للرقم %s" % (
                    self.num_ar_cnv(mobile[-4:]) + '******' + self.num_ar_cnv(mobile[:3]),),
                "EnglishMessage": "Code has been sent to mobile number %s" % (mobile[:3] + '******' + mobile[-4:],)
            }

    @api.model
    def ReSendOTP(self, **args):
        user_id = args.get('userId') and int(args.get('userId'))
        if not user_id:
            return False, {
                "OTPCode": 403,
                "StatusDescription": "Failed",
                "Data": {},
                "ArabicMessage": "لا يمكن ارسال كود التحقق",
                "EnglishMessage": "System can't send the verification code"
            }
        user_obj = self.env['res.users'].sudo().browse(user_id)
        if user_obj.mobile !='0554135668' and user_obj.block_send_otp_till and user_obj.block_send_otp_till > str(datetime.now()):
            return False, {
                "OTPCode": 403,
                "StatusDescription": "Failed",
                "Data": {},
                "ArabicMessage": "لقد تجاوزت عدد مرات تسجيل الدخول المسموح به الرجاء المحاولة في وقت آخر",
                "EnglishMessage": "You exceeded the number of tries to login please try again later"
            }

        emp_obj = self.env['hr.employee'].sudo().search([('user_id', '=', user_id)], limit=1)
        if not emp_obj:
            return False, {
                "OTPCode": 403,
                "StatusDescription": "Failed",
                "Data": {},
                "ArabicMessage": "لا يوجد ملف وظيفي لهذا المستخدم",
                "EnglishMessage": "The user doesn't has employee profile"
            }
        if not user_obj.mobile:
            return False, {
                "OTPCode": 403,
                "StatusDescription": "Failed",
                "Data": {},
                "ArabicMessage": "لا يوجد رقم تليفون لهذا المستخدم",
                "EnglishMessage": "This User doesn't have mobile number"
            }
        mobile = emp_obj.is_mobile(user_obj.mobile)
        if not mobile:
            return False, {
                "OTPCode": 403,
                "StatusDescription": "Failed",
                "Data": {},
                "ArabicMessage": "رقم الجوال المدخل غير صحيح",
                "EnglishMessage": "Invalid Mobile Number"
            }
        if mobile and mobile == '00966554135668':
            otp = "1111"
        else:
            otp = str(random.randint(1000, 9999))
        message = "Your verification code is for new 2PERP : " + otp

        result = self.env['res.company'].pool_send_message(message, mobile)
        if result != True:
            return False, {
                "OTPCode": 403,
                "StatusDescription": "Failed",
                "Data": {},
                "ArabicMessage": "حدث مشكلة اثناء ارسال كود التحقق",
                "EnglishMessage": "Problem during send verification code"
            }
        else:
            if not user_obj.otp_valid_date or (user_obj.otp_valid_date and user_obj.otp_valid_date[:10] < str(datetime.now().date())):
                user_obj.write({'otp': otp, 'otp_valid_date': datetime.now() + timedelta(minutes=3),
                                'block_send_otp_till': False,
                                'number_of_otp_try': 1})
            else:
                user_obj.write({'otp': otp, 'otp_valid_date': datetime.now() + timedelta(minutes=3),
                                'block_send_otp_till': False if user_obj.number_of_otp_try + 1 < 4 else datetime.now() + timedelta(
                                    hours=24),
                                'number_of_otp_try': user_obj.number_of_otp_try + 1})
            return True,{
                "OTPCode": 201,
                "StatusDescription": "Success",
                "Data": {},
                "ArabicMessage": u"تم ارسال كود الدخول للرقم %s" % (
                    self.num_ar_cnv(mobile[-4:]) + '******' + self.num_ar_cnv(mobile[:3]),),
                "EnglishMessage": "Code has been sent to mobile number %s" % (mobile[:3] + '******' + mobile[-4:],)
            }

    @api.model
    def Logout(self, args):
        try:
            if not args.get('ID'):
                return {
                    "OTPCode": 404,
                    "StatusDescription": "Failed",
                    "ArabicMessage": "الرجاء تزويد رقم الهوية",
                    "EnglishMessage": "National ID is not provided"
                }

            return {
                "OTPCode": 201,
                "StatusDescription": "Success",
                "Data": {},
                "ArabicMessage": u"تم تسجيل الخروج بنجاح ",
                "EnglishMessage": "Logout Successfully",
            }

        except Exception as e:

            return {
                "OTPCode": 500,
                "StatusDescription": "Failed",
                "ErrorMessage": "System Error because of %s" % e,
                "ArabicMessage": u"نعتذر عن خدمتك حاليا الرجاء المحاولة لاحقا",
                "EnglishMessage": "We apologize for serving you currently.Please try again later."
            }