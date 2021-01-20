# -*- coding: utf-8 -*-
# Copyright (c) 2020, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class InterviewRound(Document):
    def before_insert(self):
        print("======== in insert =================")
        filters = {
                'doctype': 'Interview Round',
                'interview': self.interview,
                'round': self.round
                }

        if frappe.db.exists(filters):
            frappe.throw('Interview Round already exists.')

        interview = frappe.get_doc('Interview', self.interview)
        print(interview.designation)

        interview_configuration = frappe.get_doc("Interview Configuration", interview.designation)

        # set feedback child table
        for feedback in interview_configuration.feedback_parameters:
            print(feedback.round_name, feedback.skill)
            if feedback.round_name == self.round:
                self.append('feedback', {
                    'skill': feedback.skill,
                    'rating': 0
                })

        # set round number
        round_number = None
        for r in interview_configuration.rounds:
            if r.round_name == self.round:
                round_number = r.round_number

        self.round_number = round_number
        for row in self.interviewers:
            print(row.employee)

            if frappe.session.user == row.employee:
                print("heloooooooooooo")
                # print(self._comments)
                if self._comments is not None:
                    self.comments =  self._comments

    def before_save(self):    

        for row in self.interviewers:
            print(row.employee)
            employee = frappe.get_all("Employee", filters={'name': row.employee}, fields=['user_id'], as_list=1)

            # notification = frappe.get_doc('Notification', 'Interview Submission')

            # args={'doc': self}
            # # recipients, cc, bcc = notification.get_list_of_recipients(doc, args)
            
            # frappe.enqueue(method=frappe.sendmail, recipients= employee[0][0], sender=None, 
            # subject=frappe.render_template(notification.subject, args), message=frappe.render_template(notification.message, args))

        Applicant = frappe.get_all('Job Applicant', filters={'name': self.job_applicant}, fields=['email_id'], as_list = 1)

        # notification = frappe.get_doc('Notification', 'Interview Processing')

        # args={'doc': self}
        # # recipients, cc, bcc = notification.get_list_of_recipients(doc, args)
        
        # frappe.enqueue(method=frappe.sendmail, recipients=Applicant[0][0] , sender=None, 
        # subject=frappe.render_template(notification.subject, args), message=frappe.render_template(notification.message, args))


        print("email send ===================")

@frappe.whitelist()
def previous_interview_rounds(interview, interview_round):
    print("========", interview, "==============")
    rounds = frappe.get_all('Interview Round', filters={'interview': interview, 'name': ["not in", interview_round]}, fields=['*'], order_by='round_number')
    if len(rounds) == 0:
        return "No Rounds"
    else:  

        list2 = []
        for i in rounds:
            comment = []
            print((i['_comments']))
            if i['_comments'] is not None:
                a = json.loads(i['_comments'])
                for j in a:
                    comment.append(j['comment'])
                
            print(comment)
            interviewer = frappe.get_all('Interviewer', filters={'parent': i['name']}, fields=['employee', 'employee_name'] )
            l_ = []
            for row in interviewer:
                l_.append("{}-{}".format(row['employee'], row['employee_name']))
            k =  [
                    {
                        'label': 'Round Number',
                        'fieldname': 'round_number',
                        'fieldtype': 'Data',
                        'default': i['round_number'],
                        'read_only': 1
                    },
                    {
                        'label': 'Date',
                        'fieldname': 'date',
                        'fieldtype': 'Datetime',
                        'read_only': 1,
                        'default': i['date']
                    },
                    {
                        'label': '',
                        'fieldname': '',
                        'fieldtype': 'Column Break'
                    },
                    {
                        'label': 'Round Name',
                        'fieldname': 'round_name',
                        'fieldtype': 'Data',
                        'default': i['round'],
                        'read_only': 1
                    },
                    {
                        'label': 'Status',
                        'fieldname': 'status',
                        'fieldtype': 'Data',
                        'default': i['status'],
                        'read_only': 1
                    },
                    {
                        'label': '',
                        'fieldname': '',
                        'fieldtype': 'Column Break'
                    },
                    {
                        "label": "Interviewer's",
                        'fieldname': "interviewers",
                        "fieldtype": "Small Text",
                        "options": "Interviewer",
                        '_link_field':'employee',
                        'default': '\n'.join(l_),
                        'read_only': 1
                    },
                    {
                        "label": "Overall Recommendation",
                        'fieldname': "overall_recommendation",
                        "fieldtype": "Data",
                        'read_only': 1,
                        'default': i['overall_recommendation']
                    },
                    {
                        'label': '',
                        'fieldname': '',
                        'fieldtype': 'Section Break'

                    }
                    
                ]  
            list2.append(k)
            
            rounds_feedback = frappe.get_all('Interview Round Feedback', filters={'parent': i['name']}, fields=['*'])
            print(rounds_feedback, 'rounds feedback')
            if len(rounds_feedback) > 0:
                for i in rounds_feedback:
                    l = [
                        {
                            'label': 'Skill',
                            'fieldname': 'skill',
                            'fieldtype': 'Link',
                            'read_only': 1,
                            'default': i['skill']
                        },
                        {
                            'label': '',
                            'fieldname': '',
                            'fieldtype': 'Column Break'
                        },
                        {
                            'label': 'Remark',
                            'fieldname': 'remark',
                            'fieldtype': 'Small Text',
                            'read_only': 1,
                            'default': i['remark']
                        },
                        {
                            'label': '',
                            'fieldname': '',
                            'fieldtype': 'Column Break'
                        },
                        {
                            'label': 'Rating',
                            'fieldname': 'rating',
                            'fieldtype': 'Rating',
                            'read_only': 1,
                            'default': i['rating1']
                        },
                        {
                            'label': '',
                            'fieldname': '',
                            'fieldtype': 'Section Break'
                        }
                    ]
                    list2.append(l)
            c = [
                {
                    'label': 'Comment',
                    'fieldname': 'comment',
                    'fieldtype': 'HTML Editor',
                    'read_only': 1,
                    'default': comment,
                    'Bold': 1
                    # 'default': a[0]['comment']
                },
                {
                    'label': '',
                    'fieldname': '',
                    'fieldtype': 'Section Break'
                }
            ]   
            list2.append(c) 
    interview_rounds = [val for sublist in list2 for val in sublist] 
    return interview_rounds    

@frappe.whitelist()
def set_round_number_and_feedback(interview, round, designation, name):
    get_doc_inerview_round_configuration = frappe.get_list("Interview Round Configuration", fields=[
                                                           'round_number'], filters={'parent': designation, 'round_name': round}, as_list=1)
    get_doc_feedback = frappe.get_list("Interview Round Feedback Parameter", fields=[
                                       "skill"], filters={"parent": designation, "round_name": round}, as_list=1)
    return get_doc_inerview_round_configuration[0][0], get_doc_feedback


@frappe.whitelist()
def date_validation(doc, method):
    Today = date.today()
    To_date = Today.strftime("%Y-%m-%d")
    if doc.date < To_date:
        frappe.throw("You can not select past date")

    get_interview = frappe.get_list("Interview Round", fields=[
                                    "round", "date", "interview"], filters={"interview": doc.interview}, as_list=1)
    print(get_interview)


@frappe.whitelist()
def set_feedback(designation):
    print(designation)
    # get_inerview_round_configuration = frappe.get_doc("Interview Configuration", designation)
    # return get_inerview_round_configuration


@frappe.whitelist()
def get_interviewer(doctype, txt, searchfield, start, page_len, filters):
    res = frappe.get_list('Has Role', filters=[{"role": "Interviewers"}, {"parenttype": "User"}], fields=[
                          "parent"], as_list=1, start=start, page_length=page_len)
    return [(user[0], frappe.db.get_value('User', user[0], 'full_name')) for user in res]


@frappe.whitelist()
def interview_round_permissions_query_conditions(user):
    user_roles = frappe.get_roles(user)
    employee = frappe.get_list('Employee', filters={'user_id': user}, fields=['name'], as_list = 1)
    if 'Interviewers' in user_roles and not 'System Manager' in user_roles:
        return """(`tabInterview Round form`.`name` in(select parent from `tabInterviewer` where `employee`= '{0}')) """.format(employee[0][0])
        # return """(`tabInterview Round form`.`interviewers` = '{0}')""".format(employee[0][0])


@frappe.whitelist()
def get_rounds(doctype, txt, searchfield, start, page_len, filters):
    if filters['interview']:
        designation = frappe.db.get_value(
            'Interview', filters['interview'], 'designation')
        existing_rounds_ = frappe.get_list("Interview Round", fields=["round"], filters={
                                           'interview': filters['interview']}, as_list=1)
        existing_rounds = [i[0] for i in existing_rounds_]
        rounds = frappe.get_list("Interview Round Configuration", fields=[
            'round_name', 'round_number'], filters={'parent': designation, 'round_name': ['not in', existing_rounds]}, as_list=1, start=start, page_length=page_len)
        return [r for r in rounds]