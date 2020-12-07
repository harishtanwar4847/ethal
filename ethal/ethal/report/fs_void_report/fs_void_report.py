# Copyright (c) 2013, Atrina Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	data = get_data()
	columns = ["FS Number::15"]
	return columns, data
	 
def find_missing(lst):
	return [x for x in range(lst[0], lst[-1]+1) if x not in lst]

def extractDigits(lst): 
    res = [] 
    for el in lst: 
        sub = el.split(', ') 
        res.append(sub) 
      
    return(res)

def get_data():
	lst = frappe.db.sql("select fs_number from `tabSales Invoice` where docstatus != 2", as_list=True)
	# return lst
	last = []
	
	for i in lst:
		for z in i:
			last.append(z)

	print("this is last ======> ", last)

	last = [ x for x in last if "F" not in x ]
	print("this is last without FS ===> ",last)
	
	for i in range(0, len(last)):
		last[i] = int(last[i])
	
	last.sort()
	print("Last before missing values ===> ", last)
	res = find_missing(last)

	for i in range(0, len(res)):
		res[i] = str(res[i])

	print("res ======> ", res)

	res = extractDigits(res)
	
	return res


	