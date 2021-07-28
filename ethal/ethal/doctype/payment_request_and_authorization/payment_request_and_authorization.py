# -*- coding: utf-8 -*-
# Copyright (c) 2020, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json

class PaymentRequestandAuthorization(Document):
	pass

@frappe.whitelist()
def set_approver_name(data):
    data=json.loads(data)
    
    get_approver_name = frappe.db.get_value('Comment', {'reference_name':data['name'], 'content': 'Sent for Approval'}, 'owner')
    print(get_approver_name)
    get_approved_date = frappe.db.get_value('Comment', {'reference_name':data['name'], 'content': 'Sent for Approval'}, 'modified')
    print(get_approved_date)
    frappe.db.set_value(data['doctype'], {'name': data['name']}, 'checked_person', get_approver_name)
    frappe.db.set_value(data['doctype'], {'name': data['name']}, 'checked_date', get_approved_date)
    frappe.db.commit()

@frappe.whitelist()
def create_payment_entry(doc):
    doc = json.loads(doc)
    print(doc)
    a = frappe.new_doc('Payment Entry')
    a.payment_type = 'Pay'
    if 'payment_mode' in doc:
        a.mode_of_payment = doc['payment_mode']
    if 'party_type' in doc:    
        a.party_type = doc['party_type']
        a.party = doc['party']
    a.paid_amount = doc['amount']
    if 'payment_reason' in doc:
        a.notes = doc['payment_reason']
    a.documents_attached = doc['name']
    a.pra = doc['name']
    return a  