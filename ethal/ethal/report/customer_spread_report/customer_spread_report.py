# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = ["Customer:Link/Customer:300", "1-5.1:Currency:150", "5.1-10:Currency:150", "10.1-20:Currency:150", "20.1-40:Currency:150", "40.1-60:Currency:150", "60.1-70:Currency:150", "< 70:Currency:150"]
	data = get_data(filters)
	return columns, data

def get_data(filters):
	return frappe.db.sql("""
		select customer,
		(case when total <= 500000 then total else 0 end) as "1-5", 
		(case when total >500000 and total <= 1000000 then total else 0 end) as "5.1-10",
		(case when total >1000000 and total <= 2000000 then total else 0 end) as "10.1-20", 
		(case when total >2000000 and total <= 4000000 then total else 0 end) as "20.1-40", 
		(case when total >4000000 and total <= 6000000 then total else 0 end) as "40.1-60", 
		(case when total >6000000 and total <= 7000000 then total else 0 end) as "60.1-70",  
		(case when total > 7000000 then total else 0 end) as "< 70 " 
		from  (select sum(total) as total, customer from `tabSales Invoice` where posting_date between '{0}' and '{1}' group by customer) as t;
	""".format(filters.from_date, filters.to_date), as_list=True)