# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = ["Item Name:Link/Item:250"]+["Rejection Ash:Float:100"]+["Rejection Blister:Float:100"]+["Rejection Rolling:Float:100"]+["Rejection Others:Float:100"]+["OK Circle Received:Float:100"]+["OK Circle Received(Pieces):Int:100"]+["Total Rejection:Float:100"]+["Melting Rejection:Float:100"]+["Total Circle Received:Float:100"]
	data = get_data(filters)
	return columns, data

def get_data(filters):
	return frappe.db.sql("""
		select item_name, rejection_ash, rejection_blister, rejection_rolling, rejection_others, ok_circle_received,
			ok_circle_receivedpieces, total_rejection, melting_rejection, total_circle_received
		from `tabQC Items` 
		where parent = '{0}'
		order by idx	
	""".format(filters.qc))

