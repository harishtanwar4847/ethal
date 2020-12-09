# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = get_column()
	data = get_data()
	return columns, data

def get_column():
    columns = ["CPV Posting Date ::150"]+["Jv Posting Date ::150"]+["Voucher No CPV ::250"]+["Voucher No JV ::150"]+["Debit ::150"]+["Credit ::150"]+["Balance ::350"]+["Reference No ::150"]+["PO ::150"]+["PRF ::150"]+["GRN ::150"]+["Purchase Invoice ::150"]
    return columns

def get_data():
	# a = frappe.db.get_all('Payment Entry', fields=['name'], as_list = 1)
	# a_ = [i[0] for i in a]
	# b = frappe.db.get_all('Payment Entry Reference', filters = {'parent' : ['in', a_]}, fields=['parent'], as_list = 1)
	# b_ = [j[0] for j in b]
	# c = frappe.db.get_all('Payment Entry', filters={'name': ['not in', b_], 'payment_type': 'Pay'}, fields=['name'], as_list = 1)
	# c_ = [k[0] for k in c]
	# c_ = tuple(c_)
	
	
	# return frappe.db.sql("""
	# 	select pe.posting_date, je.posting_date, pe.name, je.name, pe.paid_amount, je.total_debit, (pe.paid_amount - je.total_debit), je.user_remark, pi.purchase_order, poi.material_request, pi.purchase_receipt, jea.reference_name 
	# 	from `tabPayment Entry` as pe
	# 	left join `tabJournal Entry` as je
	# 	on je.cheque_no = pe.name
	# 	left join `tabJournal Entry Account` as jea
	# 	on je.name = jea.parent
	# 	left join `tabAccount` as ac
	# 	on jea.account = ac.name
	# 	left join `tabPurchase Invoice Item` as pi
	# 	on jea.reference_name = pi.parent
	# 	left join `tabPurchase Order Item` as poi
	# 	on pi.purchase_order = poi.name
	# 	where pe.paid_to like "%11210%" and jea.party_type = "Supplier" and je.docstatus = 1 group by jea.reference_name;
	# 	""")


	return frappe.db.sql("""
	select pe.posting_date, je.posting_date, pe.name, je.name, pe.paid_amount, je.total_debit, (pe.paid_amount - je.total_debit), je.user_remark, pi.purchase_order, poi.material_request, pi.purchase_receipt, jea.reference_name
	from `tabPayment Entry` as pe 
	left join `tabJournal Entry` as je 
	on je.cheque_no = pe.name
	left join `tabJournal Entry Account` as jea
	on je.name = jea.parent
	left join `tabPurchase Invoice Item` as pi
	on jea.reference_name = pi.parent
	left join `tabPurchase Order Item` as poi
	on pi.purchase_order = poi.name
	where pe.paid_to like "%11210%";
	""")