# Copyright (c) 2023, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.data import flt
import datetime

class DailyManufacturing(Document):
	def before_save(self):

		total_no = 0
		total_kg = 0
		total_heats = 0
		for i in self.shifts:
			total_no += flt(i.no)
			total_kg += flt(i.kg)
			total_heats += flt(i.heat)

		self.total_no = total_no
		self.total_kg = total_kg
		self.total_heats = total_heats

		total_present = 0
		total_absent = 0
		total_ot_hours = 0
		for i in self.attendance:
			total_present += flt(i.present)
			total_absent += flt(i.absent)
			total_ot_hours += flt(i.ot_hours)

		self.total_present = total_present
		self.total_absent = total_absent
		self.total_ot_hours = total_ot_hours

		if self.annealing:
			annealing= frappe.get_all("Annealing Items", filters = {"parent":self.annealing}, fields = ["*"])
			total = 0
			for i in annealing:
				if not frappe.db.exists("Manufacturing Annealing Items",{"Id":i.name}):
					self.append("manufacturing_annealing_items",{
						"in_time": i.in_time,
						"out_time": i.out_time,
						"box_no": i.box_no,
						"kg": flt(i.kg),
						"id": i.name,
					})
				

			for j in self.manufacturing_annealing_items:
				total += j.kg

			self.total = total

		# purchase_item_list = frappe.db.sql("""select item_code from `tabStock Ledger Entry`  where DATE(creation) = CURDATE() and voucher_type = 'Purchase Receipt'""")
		# lst1= []
		# for i in purchase_item_list:
		# 	lst1.append(i[0])
			
		# for i in self.raw_material_received:

		# 	if i.item_name in lst1:
		# 		ledger_doc = frappe.get_all("Stock Ledger Entry", filters = {"item_code":i.item_name, "voucher_type" : "Purchase Receipt",}, fields = ["*"])
		# 		if ledger_doc:
		# 			i.purchase_receipt_no = ledger_doc[0]["voucher_no"]
		# 			i.accepeted_qty = ledger_doc[0]["actual_qty"]
				
		# 			supplier = frappe.get_doc("Purchase Receipt", ledger_doc[0]['voucher_no']).as_dict()
		# 			i.supplier_name = supplier.supplier

		# 	else:
		# 		i.purchase_receipt_no = ""
		# 		i.accepeted_qty = 0
		# 		i.supplier_name = ""
		today = frappe.utils.nowdate()

		ledger_doc = frappe.get_all("Stock Ledger Entry", filters = {"posting_date":today, "voucher_type" : "Purchase Receipt",}, fields = ["*"])
		

		for i in ledger_doc:
			supplier = frappe.get_doc("Purchase Receipt", i.voucher_no).as_dict()
			if not frappe.db.exists("Raw Material Received",{"Id":i.name}):
				print("inside condition")
				self.append("raw_material_received",{
					"item_name": i.item_code,
					"purchase_receipt_no": i.voucher_no,
					"accepeted_qty": i.actual_qty,
					"supplier_name":supplier.supplier,
					"id": i.name
				})
				

		delivery_note = frappe.get_all("Stock Ledger Entry", filters = {"posting_date":today, "voucher_type" : "Delivery Note",}, fields = ["*"])
		

		for i in delivery_note:
			customer = frappe.get_doc("Delivery Note", i.voucher_no).as_dict()
			if not frappe.db.exists("Dispatched",{"Id":i.name}):
				self.append("dispatched",{
					"item_name": i.item_code,
					"delivery_note": i.voucher_no,
					"qty": abs(i.actual_qty),
					"customer":customer.customer,
					"id": i.name
				})

		# delivered_item_list = frappe.db.sql("""select item_code from `tabStock Ledger Entry`  where DATE(creation) = CURDATE() and voucher_type = 'Purchase Receipt'""")
		# lst2= []
		# for i in delivered_item_list:
		# 	lst2.append(i[0])


		# for i in self.dispatched:
		# 	if i.item_name in lst2:
		# 		ledger_doc = frappe.get_all("Stock Ledger Entry", filters = {"item_code":i.item_name, "voucher_type" : "Delivery Note",}, fields = ["*"])
		# 		if ledger_doc:
		# 			i.delivery_note	 = ledger_doc[0]["voucher_no"]
		# 			i.qty = abs(ledger_doc[0]["actual_qty"])
				
		# 			customer = frappe.get_doc("Delivery Note", ledger_doc[0]['voucher_no']).as_dict()
		# 			i.customer = customer.customer

		# 		else:
		# 			i.delivery_note	 = ""
		# 			i.qty = 0
		# 			i.customer = ""

		opening_total = 0
		receipt_total = 0
		issue_total = 0
		closing_total = 0
		for i in self.stock:
			if i.item:
				opening_qty = frappe.db.sql("""select qty_after_transaction from `tabStock Ledger Entry` where item_code = %s and DATE(creation) < CURDATE() order by creation desc limit 1""",i.item)
				
				receipt_qty = frappe.db.sql("""select sum(actual_qty) from `tabStock Ledger Entry` where item_code = %s and DATE(creation) = CURDATE() and voucher_type = 'Purchase Receipt' """,i.item)

				issue = frappe.db.sql("""select abs(sum(actual_qty)) from `tabStock Ledger Entry` where item_code = %s and DATE(creation) = CURDATE() and voucher_type = 'Stock Entry' and actual_qty < 0 """,i.item)

				i.opening_stock = flt(opening_qty[0][0])
				i.receipt = flt(receipt_qty[0][0])
				i.issue = flt(issue[0][0])
				i.closing_stock = flt(i.opening_stock + i.receipt - i.issue) 
			
			opening_total += flt(i.opening_stock)
			receipt_total += flt(i.receipt)
			issue_total += flt(i.issue)
			closing_total += flt(i.closing_stock)

		self.total_opening_stock = opening_total
		self.total_receipt = receipt_total
		self.total_issue = issue_total
		self.total_closing_stock = closing_total


		total_opening = 0
		total_change = 0
		total_closing = 0
		for i in self.receipts_of_this_month:
			if i.item:
				i.closing = flt(i.opening) + flt(i.change)

			total_opening += flt(i.opening)
			total_change += flt(i.change)
			total_closing += flt(i.closing)

		self.total_opening = total_opening
		self.total_change = total_change
		self.total_closing = total_closing



	def on_update(self):

		if self.receipts_of_this_month: 
			item = frappe.get_all("Receipt Month", filters = {"Parent":self.name,"item":"Good circle"}, fields = ["*"])
			if item:
				self.good = flt(item[0]['change'])
			else: 
				self.good = 0
			print(self.good)
			self.rejection = flt(self.melting) + flt(self.rolling) + flt(self.sizing) + flt(self.others)
			self.received = flt(self.good) + flt(self.rejection)



@frappe.whitelist()
def get_previous_record(doc):
	get_parent = frappe.db.get_all('Daily Manufacturing', ['name'], order_by='name desc', page_length=1)
	if get_parent:
		get_previous_record = frappe.db.get_all('Receipt Month', {'parent': get_parent[0]['name']}, ['*'], order_by='idx asc')
		
		return get_previous_record
	
@frappe.whitelist()
def get_previous_record_shift(doc):
	get_parent = frappe.db.get_all('Daily Manufacturing', ['name'], order_by='name desc', page_length=1)
	if get_parent:
		get_previous_record_shift = frappe.db.get_all('Shift', {'parent': get_parent[0]['name']}, ['*'], order_by='idx asc')
		
		return get_previous_record_shift
	
@frappe.whitelist()
def get_previous_record_attendence(doc):
	get_parent = frappe.db.get_all('Daily Manufacturing', ['name'], order_by='name desc', page_length=1)
	if get_parent:
		get_previous_record_attendence = frappe.db.get_all('Attendence', {'parent': get_parent[0]['name']}, ['*'], order_by='idx asc')
		
		return get_previous_record_attendence
	
@frappe.whitelist()
def get_previous_record_stock(doc):
	get_parent = frappe.db.get_all('Daily Manufacturing', ['name'], order_by='name desc', page_length=1)
	if get_parent:
		get_previous_record_stock = frappe.db.get_all('Daily Manufacturing Stock', {'parent': get_parent[0]['name']}, ['*'], order_by='idx asc')
		
		return get_previous_record_stock
						


