from odoo import _


def return_success_creation_api(request_id, request_number):
    return {
        "Code": 200,
        "StatusDescription": "Success",
        "Data": {'ID': request_id},
        "ArabicMessage": "تم انشاء الطلب بنجاح رقم(%s)  " % str(request_number),
        "EnglishMessage": "Request Number (%s)has been created successfully." % str(request_number)
    }

def return_success_update_api(request_id, request_number):
    return {
        "Code": 200,
        "StatusDescription": "Success",
        "Data": {'ID': request_id},
        "ArabicMessage": "تم تعديل الطلب بنجاح رقم(%s)  " % str(request_number),
        "EnglishMessage": "Request Number (%s)has been updated successfully." % str(request_number)
    }
def return_failed_request_vals(english_error_message, arabic_error_message):
    return {
        "Code": 404,
        "StatusDescription": "Falied",
        "Data": {},
        "ArabicMessage": arabic_error_message,
        "EnglishMessage": english_error_message
    }

def return_success_list_api(result):
    return {
        "Code": 200,
        "StatusDescription": "Success",
        "Data": result,
        "ArabicMessage": "تم رجوع القائمه بنجاح",
        "EnglishMessage": "List Returned Successfully"
    }

def return_success_submit_api(request_id, request_number):
    return {
        "Code": 200,
        "StatusDescription": "Success",
        "Data": {'ID': request_id},
        "ArabicMessage": "تم تاكيد الطلب بنجاح رقم(%s)  " % request_number,
        "EnglishMessage": "Request Number (%s)has been Submitted successfully." % request_number
    }

def return_success_delete_api(request_number):
    return {
        "Code": 200,
        "StatusDescription": "Success",
        "Data": {},
        "ArabicMessage": "تم حذف الطلب بنجاح رقم(%s)  " % request_number,
        "EnglishMessage": "Request Number (%s)has been Deleted successfully." % request_number
    }

def return_failed_api(error_message):
    return {
        "Code": 404,
        "StatusDescription": "Falied",
        "Data": {},
        "ArabicMessage": "%s  " % error_message,
        "EnglishMessage": "%s." % error_message
    }

def return_success_action_api(request_id, arabicmessage, englishmessage):
    return {
        "Code": 200,
        "StatusDescription": "Success",
        "Data": {'ID': request_id},
        "ArabicMessage": arabicmessage,
        "EnglishMessage":englishmessage
    }

def return_arabic_state(state):
    if state == 'draft':
        state = 'مسودة'
    elif state == 'inprogress':
        state = 'تحت الاجراء'
    elif state == 'refuse':
        state = 'مرفوض'
    elif state == 'cancel':
        state = 'ملغى'
    elif state == 'done':
        state = 'تمت الموافقة'
    elif state == 'validate1':
        state = 'تمت الموافقة الاولى'
    elif state == 'validate':
        state = 'تمت الموافقة'
    elif state == 'active':
        state = 'نشط'
    return state