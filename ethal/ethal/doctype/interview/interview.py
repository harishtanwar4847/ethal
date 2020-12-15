# -*- coding: utf-8 -*-
# Copyright (c) 2020, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Interview(Document):
	def get_interview_rounds(self, fields=None):
		return frappe.db.get_all("Interview Round", filters={"interview": self.name}, fields=fields or ["*"], order_by="round_number")

	# def get_interview_configuration(self):
	#     return frappe.get_doc("Interview Configuration", self.designation)


@frappe.whitelist()
def get_job_applicant_details(job_applicant_name):
    job_applicant = frappe.get_doc("Job Applicant", job_applicant_name)
    job_opening = frappe.get_doc(
        "Job Opening", job_applicant.job_title)
    return {
        'job_opening': job_opening.name,
        'designation': job_opening.designation
    }


@frappe.whitelist()
def set_interview_round(interview):
    # interview_obj = frappe.get_doc("Interview", interview)

    # get_doc_interview_round = interview_obj.get_interview_rounds(["round_number", "round", "designation", "status"])
    get_doc_interview_round = frappe.db.get_all("Interview Round", filters={
                                                "interview": interview}, fields=["round_number", "round", "designation", "status"])
    b_ = [i.get("round") for i in get_doc_interview_round]
    c_ = [i.get("designation") for i in get_doc_interview_round]
    a = frappe.db.get_all("Interview Round Configuration", filters={'parent': c_[0], 'round_name': [
                          "not in", b_]}, fields=["round_number", "round_name"], order_by="round_number")
    return None if len(a) == 0 else a[0]['round_name']


@frappe.whitelist()
def get_rounds(doctype, txt, searchfield, start, page_len, filters):
    print(filters['interview'])
    if filters['interview']:
        get_interview = frappe.get_doc("Job Applicant", filters['interview'])
        get_job_opening = frappe.get_doc(
            "Job Opening", get_interview.job_title)
        get_inerview_round_configuration = frappe.get_list("Interview Round Configuration", fields=[
                                                           'round_name', 'round_number'], filters={'parent': get_job_opening.designation}, as_list=1)
        return get_inerview_round_configuration


@frappe.whitelist()
def set_rounds(interview, round, designation, name):
	get_interview_round = frappe.get_doc("Interview Round", name)
	print(get_interview_round.status)
	get_inerview_round_configuration = frappe.get_list("Interview Round Configuration", fields=[
														'round_number'], filters={'parent': designation, 'round_name': round}, as_list=1)
	get_interview = frappe.get_doc("Interview", interview)
	get_interview.current_round = round
	get_interview.round_number = get_inerview_round_configuration[0][0]
	get_interview.current_round_status = get_interview_round.status
	get_interview.save(ignore_permissions=True)


	job_applicant = frappe.get_doc('Job Applicant', get_interview.job_applicant)
	job_applicant.current_round = 'Round' + " " + get_inerview_round_configuration[0][0]

	if get_interview.current_round_status == 'Selected':
		job_applicant.applicant_status = 'Round' + " " + get_inerview_round_configuration[0][0] + " " + 'Cleared'
	else:
		job_applicant.applicant_status = 'Round' + " " + get_inerview_round_configuration[0][0] + " " + 'Reject'    
	job_applicant.save(ignore_permissions=True)

	existing_rounds_ = frappe.get_list("Interview Round", fields=["round"], filters={
								'interview': interview}, as_list=1)
	existing_rounds = [i[0] for i in existing_rounds_]
	# print(designation[0][0])
	rounds = frappe.get_list("Interview Round Configuration", fields=['*'], filters={'parent': get_interview.designation, 'round_name': ['not in', existing_rounds]})
	print(rounds)
	if len(rounds) == 0:
		print("===========hello================")

		rounds_status = frappe.get_all('Interview Round', filters={'interview': interview}, fields=['status'], order_by = 'round_number')
		print(rounds_status[-1])
		
		if(rounds_status[-1]['status'] == 'Selected'):
			job_applicant.applicant_status = "Selected"
			job_applicant.save(ignore_permissions=True)
		else:
			job_applicant.applicant_status = "Rejected"
			job_applicant.save(ignore_permissions=True)

# @frappe.whitelist()
# def set_applicant_status(job_applicant, status):
#     job_applicant = frappe.get_doc('Job Applicant', job_applicant)
#     job_applicant.status =  status
#     job_applicant.save(ignore_permissions=True)
