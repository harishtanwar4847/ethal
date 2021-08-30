# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = ["QC:Link/QC:200"]+["Item:Link/Item:250"]+["Item Name:Data:300"]+["Rejection Ash:Float:100"]+["Rejection Blister:Float:100"]+["Rejection Rolling:Float:100"]+["Rejection Others:Float:100"]+["OK Circle Received:Float:100"]+["OK Circle Received(Pieces):Int:100"]+["Total Rejection:Float:100"]+["Melting Rejection:Float:100"]+["Total Circle Received:Float:100"]
	data = get_data(filters)
	return columns, data

def get_data(filters):
	if filters.qc:
		return frappe.db.sql("""
			select parent, item_name, item, rejection_ash, rejection_blister, rejection_rolling, rejection_others, ok_circle_received,
				ok_circle_receivedpieces, total_rejection, melting_rejection, total_circle_received
			from `tabQC Items` 
			where parent = '{0}'
			order by parent	
		""".format(filters.qc))
	elif filters.from_date and filters.to_date:
		return frappe.db.sql("""
			select parent, item_name, item, rejection_ash, rejection_blister, rejection_rolling, rejection_others, ok_circle_received,
				ok_circle_receivedpieces, total_rejection, melting_rejection, total_circle_received
			from `tabQC Items` 
			where creation between '{0}' and '{1}'
			order by parent	
		""".format(filters.from_date, filters.to_date))
	elif filters.qc and filters.from_date and filters.to_date:
		return frappe.db.sql("""
			select parent, item_name, item, rejection_ash, rejection_blister, rejection_rolling, rejection_others, ok_circle_received,
				ok_circle_receivedpieces, total_rejection, melting_rejection, total_circle_received
			from `tabQC Items` 
			where parent = '{0}'
			and creation between '{1}' and '{2}'
			order by parent	
		""".format(filters.qc, filters.from_date, filters.to_date))
	else: 
		return frappe.db.sql("""
			select parent, item_name, item, rejection_ash, rejection_blister, rejection_rolling, rejection_others, ok_circle_received,
				ok_circle_receivedpieces, total_rejection, melting_rejection, total_circle_received
			from `tabQC Items` 
			order by parent	
		""")