# -*- coding: utf-8 -*-
# Copyright (c) 2020, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class InterviewConfiguration(Document):
	def get_total_rounds():
		return len(list(self.get('rounds')))

	def validate(self):
		self.validate_if_round_names_in_interview_round_configuration_are_unique()
		self.validate_if_every_rounds_in_rounds_there_in_feedback_parameters()
		self.validate_if_combination_of_round_and_skill_in_feedback_parameters_is_unique()

	def validate_if_round_names_in_interview_round_configuration_are_unique(self):
		list1 = list(self.get('rounds'))
		a = list({v.get('round_name'): v for v in list1}.values())
		if len(a) != len(list1):
			return frappe.throw("All the Round Names in Rounds should be unique")

	def validate_if_every_rounds_in_rounds_there_in_feedback_parameters(self):
		list1 = list(self.get('rounds'))
		rounds_in_rounds = list(
			{v.get('round_name'): v.get('round_name') for v in list1}.values())
		list2 = list(self.get('feedback_parameters'))
		rounds_in_feedback_parameters = list(
			{v.get('round_name'): v.get('round_name') for v in list2}.values())
		if len(rounds_in_rounds) != len(rounds_in_feedback_parameters):
			return frappe.throw("There should be atleat one skill for each round")

	def validate_if_combination_of_round_and_skill_in_feedback_parameters_is_unique(self):
		list1 = list(self.get('feedback_parameters'))
		a = list({"{round}-{skill}".format(round=v.get('round_name'),
											skill=v.get('skill')): v for v in list1}.values())
		if len(a) != len(list1):
			return frappe.throw("Combination of Round and Skill in Feedback Parameters should be unique")


def generate_round_numbers(doc, method):
    for key, round in enumerate(doc.get('rounds')):
        round.round_number = key + 1

@frappe.whitelist()
def set_no_of_rounds(name):
    interview_rounds = frappe.get_list('Interview Round Configuration', filters={'parent': name}, fields=['round_number'], order_by = 'round_number')
    
    interview_configuration = frappe.get_doc('Interview Configuration', name)
   
    interview_configuration.no_of_rounds = interview_rounds[-1:][0]['round_number']
    interview_configuration.save(ignore_permissions=True)

@frappe.whitelist()
def get_designation(doctype, txt, searchfield, start, page_len, filters):
    interview_configuration = frappe.get_list('Interview Configuration', fields=['designation'], as_list = 1)
    
    interview_configuration_ = [i[0] for i in interview_configuration]
    designation = frappe.get_list('Designation', filters={'name': ['not in', interview_configuration_]}, as_list = 1)
    return designation