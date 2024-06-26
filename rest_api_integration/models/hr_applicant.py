from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging
from . import api_global_function

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"
class hr_applicant(models.Model):
    _inherit = "hr.applicant"

    def check_applicant_vals(self, args):
        applicant_vals = {'active': True}
        if args.get("RequestID", False):
            applicant_vals.update({'id': args.get("RequestID", False)})
        try:
            if not args.get('name', False):
                return False, api_global_function.return_failed_request_vals("Customer Name Not provided",
                                                                             "عفوا العميل مش موجود")
            applicant_vals.update({'name': args.get("name", False),'partner_name': args.get("name", False)})

            if not args.get('identifier', False):
                return False, api_global_function.return_failed_request_vals("Iqama Number Not provided",
                                                                             "عفوا رقم الهويه مش موجود")
            applicant_vals.update({'iqama_number': args.get("identifier", False)})

            if not args.get('expire_date', False):
                return False, api_global_function.return_failed_request_vals("Iqama Expiry Date Not provided",
                                                                             "عفوا تاريخ انتهاء الاقامه مش موجود")
            # you put this field  iqama_exp_date in postman when you want to update
            # but you want to create you will put this field expire_date in postman when you create
             # this case meaning when you create you will make iqama_exp_date == value this field expire_date when you put in postman
            applicant_vals.update({'iqama_exp_date': args.get("expire_date", False)})

            if not args.get('source_id', False):
                return False, api_global_function.return_failed_request_vals(
                    "Residential Source Not Provided",
                    "عفوا مصدر الاقامه غير موجود ")
            if not self.env['res.country.state'].sudo().search([('id', '=', args.get('source_id', False))]):
                return False, api_global_function.return_failed_request_vals("Residential Source Not Correct",
                                                                             "عفوا مصدر الاقامة غير صحيح")
            applicant_vals['iqama_src_id'] = args.get('source_id', False)

            if not args.get('nationality_id', False):
                return False, api_global_function.return_failed_request_vals(
                    "Nationality Not Provided",
                    "عفوا الجنسية غير موجود ")
            if not self.env['res.country'].sudo().search([('id', '=', args.get('nationality_id', False))]):
                return False, api_global_function.return_failed_request_vals("Nationality Not Correct",
                                                                             "عفوا الجنسية غير صحيح")
            applicant_vals['nationality_id'] = args.get('nationality_id', False)
            #
            # # this is selection
            if not args.get('gender', False):
                return False, api_global_function.return_failed_request_vals(
                    "Gender Not Provided",
                    "عفوا النوع غير موجود ")
            if args.get('gender', False) not in ['male', 'female']:
                return False, api_global_function.return_failed_request_vals("Gender Not Correct",
                                                                             "عفوا النوع غير صحيح")

            # this mean field called gender in odoo == same valu in field gender in postman
            applicant_vals['gender'] = args.get('gender', False)
            # ####################### Education Details #####################################
            if not args.get('qualification_id', False):
                return False, api_global_function.return_failed_request_vals(
                    "Recruitment Degree Id Not Provided",
                    "عفوا درجة التوظيف  غير موجود ")
            if not self.env['hr.recruitment.degree'].sudo().search([('id', '=', args.get('qualification_id', False))]):
                return False, api_global_function.return_failed_request_vals("Recruitment Degree Not Provided",
                                                                             "عفوا درجة التوظيف  غير موجود")
            applicant_vals['hr_recruitment_degree_id'] = int(args.get('qualification_id', False))
            applicant_vals['type_id'] = int(args.get('qualification_id', False))
            if not args.get('speciality', False):
                return False, api_global_function.return_failed_request_vals("speciality Not Provided",
                                                                             "عفوا التخصص غير موجود ")
            applicant_vals.update({'speciality': args.get("speciality", False)})
            #
            if not args.get('birth_date', False):
                return False, api_global_function.return_failed_request_vals("Birth Date Not provided",
                                                                                     "عفوا تاريخ الميلاد مش موجود")
            applicant_vals.update({'birth_date': args.get("birth_date", False)})
            if not args.get('phone', False):
                return False, api_global_function.return_failed_request_vals("Customer Mobile Not provided",
                                                                             "عفوا الجوال مش موجود")
            applicant_vals.update(
                {'partner_mobile': args.get("phone", False)})
            #
            if not args.get('email', False):
                return False, api_global_function.return_failed_request_vals("Customer Mobile Not provided",
                                                                             "عفوا الجوال مش موجود")
            applicant_vals.update(
                {'email_from': args.get("email", False)})
            if not args.get('address', False):
                return False, api_global_function.return_failed_request_vals("Address Not provided",
                                                                                     "عفوا العنوان مش موجود")
            applicant_vals.update({'address': args.get("address", False)})

            # if not args.get('employement_status', False):
            #     return False, api_global_function.return_failed_request_vals(
            #         "Employement Status Not Provided",
            #         "عفوا الحالة الوظيفية غير موجود ")
            # if not self.env['employment.status'].sudo().search([('id', '=', args.get('employement_status', False))]):
            #     return False, api_global_function.return_failed_request_vals("Employement Status Not Correct",
            #                                                                  "عفوا الحالة الوظيفية غير صحيح")
            # applicant_vals['Employement_Status'] = args.get('employement_status', False)

            # if not args.get('years_of_experience', False) :
            #     return False, api_global_function.return_failed_request_vals(" Years Of Experience Not provided",
            #                                                                  "عفوا سنوات  الخبرة غير موجود")
            if args.get('years_of_experience', 0) :
                if args.get('years_of_experience', 0) <= 0:
                    return False, api_global_function.return_failed_request_vals(" Years Of Experience Not Valid",
                                                                             "عفوا سنوات  الخبرة غيرصالح")
                applicant_vals['years_of_experience'] = args.get('years_of_experience', False)
            if not args.get('employer', False):
                return False, api_global_function.return_failed_request_vals(" Employer Not provided",
                                                                                     "عفوا المستخدم مش موجود")
            applicant_vals.update({'employer': args.get("employer", False)})
            if not args.get('workplace', False):
                return False, api_global_function.return_failed_request_vals(" Workplace Not provided",
                                                                             "عفوا  موقع العمل  مش موجود")
            applicant_vals.update({'workplace': args.get("workplace", False)})
            ######################### Work Experience In Haj ############################
            if not args.get('years_of_experience_in_haj', False):
                return False, api_global_function.return_failed_request_vals(
                    " Years Of Experience  In Hag Works Not Provided",
                    "عفوا سنوات  الخبرة في أعمال الحج غيرموجود")
            if args.get('years_of_experience_in_haj', False) <=0:
                return False, api_global_function.return_failed_request_vals(" Years Of Experience  In Hag Works Not Valid",
                                                                             "عفوا سنوات  الخبرة في أعمال الحج غيرصالح")
            applicant_vals['years_of_experience_in_haj'] = args.get('years_of_experience_in_haj', False)

            if not args.get('job_title_in_haj', False):
                return False, api_global_function.return_failed_request_vals(
                    "Job Title In Haj  Not Provided",
                    "عفوا المسمى الوظيفي في الحج غير موجود ")
            if not self.env['hr.job'].sudo().search([('id', '=', args.get('job_title_in_haj', False))]):
                return False, api_global_function.return_failed_request_vals("Job Title In Haj  Not Correct",
                                                                                 "عفوا المسمى الوظيفي في الحج غير صحيح")
            applicant_vals['job_title_in_haj'] = args.get('job_title_in_haj', False)

            if not args.get('party_name_in_haj', False):
                return False, api_global_function.return_failed_request_vals(" Party Name In Haj Not provided",
                                                                             "عفوا الاسم المحدد في الحج  مش موجود")
            applicant_vals.update({'party_name_in_haj': args.get("party_name_in_haj", False)})
            ################### Required job information ##########################
            if not args.get('job_app_announcement_id', False):
                return False, api_global_function.return_failed_request_vals(
                    "Job App Announcement Id Not Provided",
                    "عفوا المعلن عن تطبيق الوظيفة  غير موجود ")
            if not self.env['ipmc.application.announcement'].sudo().search([('id', '=', args.get('job_app_announcement_id', False))]):
                return False, api_global_function.return_failed_request_vals("Job App Announcement Id Not Provided",
                                                                             "عفوا المعلن عن تطبيق الوظيفة  غير موجود")
            applicant_vals['job_app_announcement_id'] = args.get('job_app_announcement_id', False)

            if not args.get('applied_job_workplace_id', False):
                return False, api_global_function.return_failed_request_vals(
                    "  Applied Job  WorkPlace Id Not Provided",
                    "عفوا المعلن عن  مكان العمل   غير موجود ")
            if not self.env['res.country.state'].sudo().search(
                    [('id', '=', args.get('applied_job_workplace_id', False))]):
                return False, api_global_function.return_failed_request_vals(" Applied Job  WorkPlace  Id Not Provided",
                                                                             "عفوا المعلن عن  مكان العمل   غير موجود")
            applicant_vals['applied_job_workplace_id'] = args.get('applied_job_workplace_id', False)

            if not args.get('first_job_id_applied', False):
                return False, api_global_function.return_failed_request_vals(
                    " First Job Id Applied Not Provided",
                    "عفوا المتقدم للوظيفة الأولى   غير موجود ")
            if not self.env['hr.job'].sudo().search([('id', '=', args.get('first_job_id_applied', False))]):
                return False, api_global_function.return_failed_request_vals("  First Job Id Applied Not Provided",
                                                                             "عفوا المتقدم للوظيفة الأولى  غير موجود")
            applicant_vals['first_job_id_applied'] = args.get('first_job_id_applied', False)

            if not args.get('first_job_sector_id', False):
                return False, api_global_function.return_failed_request_vals(
                    " First Job Sector Id  Not Provided",
                    "عفوامعرف قطاع الوظيفة الأولى  غير موجود ")
            if not self.env['hr.department'].sudo().search([('id', '=', args.get('first_job_sector_id', False))]):
                return False, api_global_function.return_failed_request_vals("  First Job Sector Id  Not Provided",
                                                                                     "عفوا معرف قطاع الوظيفة الأولى  غير موجود")
            applicant_vals['first_job_sector_id'] = args.get('first_job_sector_id', False)

            if args.get('second_job_id_applied', False):
                if not self.env['hr.job'].sudo().search([('id', '=', args.get('second_job_id_applied', False))]):
                    return False, api_global_function.return_failed_request_vals("  Second Job Id Applied  Not Provided",
                                                                                 "عفوا معرف قطاع الوظيفة الثانية  غير موجود")
                applicant_vals['second_job_id_applied'] = args.get('second_job_id_applied', False)

            if args.get('second_job_sector_id', False):
                if not self.env['hr.department'].sudo().search([('id', '=', args.get('second_job_sector_id', False))]):
                    return False, api_global_function.return_failed_request_vals("  Second Job Sector Id  Not Provided",
                                                                                 "عفوا معرف قطاع الوظيفة الثانية  غير موجود")
                applicant_vals['second_job_sector_id'] = args.get('second_job_sector_id', False)

            if args.get('third_job_id_applied', False):
                if not self.env['hr.job'].sudo().search([('id', '=', args.get('third_job_id_applied', False))]):
                    return False, api_global_function.return_failed_request_vals("  Third Job Id Applied  Not Provided",
                                                                                 "عفوا معرف قطاع الوظيفة الثالثة  غير موجود")
                applicant_vals['third_job_id_applied'] = args.get('third_job_id_applied', False)

            if args.get('third_job_sector_id', False):
                if not self.env['hr.department'].sudo().search([('id', '=', args.get('third_job_sector_id', False))]):
                    return False, api_global_function.return_failed_request_vals("  Third Job Sector Id  Not Provided",
                                                                                 "عفوا معرف قطاع الوظيفة الثالثة  غير موجود")
                applicant_vals['third_job_sector_id'] = args.get('third_job_sector_id', False)
            ################## Financial Data ###########################
            # if not args.get('bank_id', False):
            #     return False, api_global_function.return_failed_request_vals(
            #         " Bank Id  Not Provided",
            #         "عفوا البنك  غير موجود ")
            # if not self.env['res.bank'].sudo().search([('id', '=', args.get('bank_id', False))]):
            #     return False, api_global_function.return_failed_request_vals("  Bank Id  Not Provided",
            #                                                                  "عفوا  البنك  غير موجود")
            # applicant_vals['bank_id'] = args.get('bank_id', False)
            #
            # if not args.get('iban', False):
            #     return False, api_global_function.return_failed_request_vals(" IBAN Number Not provided",
            #                                                                  "عفوا رقم IBAN مش موجود")
            # applicant_vals.update({'iban': args.get("iban", False)})
            # ####################### Attachment #######################
            # if not args.get('cv', False):
            #     return False, api_global_function.return_failed_request_vals(" CV Not provided",
            #                                                                  "عفوا سيرتك الذاتية مش موجود")
            # applicant_vals.update({'cv': args.get("cv", False)})
            # if not args.get('notarized_iban', False):
            #     return False, api_global_function.return_failed_request_vals(" IBAN Image Not provided",
            #                                                                  "عفوا صورة IBAN مش موجود")
            # applicant_vals.update({'authorized_iban': args.get("notarized_iban", False)})
            # if not args.get('profile_image', False):
            #     return False, api_global_function.return_failed_request_vals(" Profile Image Not provided",
            #                                                                  "عفوا صورة الملف الشخصي مش موجود")
            # applicant_vals.update({'profile_image': args.get("profile_image", False)})
            # if not args.get('instructionandcondition', False):
            #     return False, api_global_function.return_failed_request_vals("Instruction and Condition Not provided",
            #                                                                  "عفوا التعليمات والشروط مش موجود")
            # applicant_vals.update({'instructionandcondition': args.get("instructionandcondition", False)})

        except Exception as e:
            arabic_message = "%s  " % _(str(e)),
            englishmessage = "%s." % _(str(e))
            return False, api_global_function.return_failed_request_vals(englishmessage, arabic_message)
        return True, applicant_vals


    def add_update_hr_applicant(self, **args):
        request_id = args.get("RequestID", False)
        check_vals, applicant_vals = self.check_applicant_vals(args)
        if not check_vals:
            return applicant_vals
        try:
            if not request_id:
                # applicant_vals['iqama_number'] = self.iqama_number,

                hr_applicant_obj = self.with_user(args.get('userId')).sudo().create(applicant_vals)
            else:
                # this mean i tell hin field iqama_number in form id beta3o 3 do update khallih = same value in which i put it on postman
                # this mean update and create togither if the field niot exist do create and if the field exist do update and you will put all field which you need update it
                # like this but this method collect us update and create  sothat in postman type of method post
                #Update Request ID

                # this mean field called gender in odoo == same value in field gender in postman
                applicant_vals['iqama_number'] = self.iqama_number,
                applicant_vals['gender'] = self.gender,
                applicant_vals['name'] = self.name,
                applicant_vals['partner_phone'] = self.partner_phone,
                applicant_vals['email_from'] = self.email_from,
                applicant_vals['iqama_exp_date'] = self.iqama_exp_date,


                hr_applicant_obj = self.with_user(args.get('userId')).sudo().browse(request_id)
                hr_applicant_obj.with_user(args.get('userId')).sudo().write(applicant_vals)
        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        if not request_id:
            return api_global_function.return_success_creation_api(hr_applicant_obj.id, hr_applicant_obj.id)
        else:
            return api_global_function.return_success_update_api(hr_applicant_obj.id, hr_applicant_obj.id)

