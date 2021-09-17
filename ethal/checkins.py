import frappe
import csv
from datetime import datetime
import os, sys, subprocess
import xlrd

@frappe.whitelist()
def create_checkins():
    from six.moves.urllib.parse import urljoin
    file_path = frappe.db.get_single_value("Checkin Sync","attach_file")
    
    import ntpath
    filename = ntpath.basename(file_path)
   
    filepath = frappe.get_site_path('private', 'files', filename)
   
    # Import the library
    from sheet2dict import Worksheet

    # Create an object
    ws = Worksheet()

    # Convert 
    ws.xlsx_to_dict(path=filepath)

    # object.sheet_items returns converted rows as dictionaries in the array 

    for data in ws.sheet_items:
        if data['Number'] and data['Time']:
            try:
                employee_checkin = frappe.new_doc('Employee Checkin')
                employee_checkin.employee = data['Number']
                employee_checkin.log_type = 'IN'
                employee_checkin.time = data['Time']
                employee_checkin.save()
            except frappe.DuplicateEntryError:
                pass    