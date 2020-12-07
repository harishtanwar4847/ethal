# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = ["charges::180"]+["total::180"]
	data = get_data(filters)
	return columns, data

def get_data(filters):
	print("filters.account ======> ", filters.account)
	def transit_charges():
		transit_charges = frappe.db.sql("""select sum(base_net_amount) from `tabPurchase Invoice Item` where expense_account = "{0}" and item_name = "TRANSIT CHARGES";""".format(filters.account),as_list=True)
		print("transit charges ===> ", transit_charges)
		res = ""
		for i in transit_charges:
			res = i[0]
		return res

	def bank_charges():
		transit_charges = frappe.db.sql("""select sum(base_net_amount) from `tabPurchase Invoice Item` where expense_account = "{0}" and item_name = "BANK CHARGES";""".format(filters.account),as_list=True)
		print("transit charges ===> ", transit_charges)
		res = ""
		for i in transit_charges:
			res = i[0]
		return res

	def documentation_charges():
		transit_charges = frappe.db.sql("""select sum(base_net_amount) from `tabPurchase Invoice Item` where expense_account = "{0}" and item_name = "DOCUMENTATION CHARGES";""".format(filters.account),as_list=True)
		print("transit charges ===> ", transit_charges)
		res = ""
		for i in transit_charges:
			res = i[0]
		return res

	ans = []
	tc = transit_charges()
	bc = bank_charges()
	dc = documentation_charges()
	ans.append(tc)
	ans.append(bc)
	ans.append(dc)
	print("ans ====> ", ans)
	charges = ["TRANSIT CHARGES","BANK CHARGES","DOCUMENTATION CHARGES"]

	res = []
	for (i,j) in zip(charges,ans):
		res.append([i,j])
	return res


	