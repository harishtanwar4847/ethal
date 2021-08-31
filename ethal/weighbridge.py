import frappe
import csv
from datetime import datetime
import os, sys, subprocess

@frappe.whitelist(allow_guest=True)
def set_values_for_weighbridge():

    file_path = frappe.db.get_single_value("Weighbridge Sync","file_path")
    file_name = frappe.db.get_single_value("Weighbridge Sync","file_name")

    mdb = file_path+file_name

    # importing csv module
    import csv

    # csv file name
    filename = mdb

    # initializing the titles and rows list
    fields = []
    rows = []
    try:
    # reading csv file
        with open(filename, 'r') as csvfile:
            # creating a csv reader object
            csvreader = csv.reader(csvfile)
            
            # extracting field names through first row
            fields = next(csvreader)

            # extracting each data row one by one
            for row in csvreader:
                rows.append(row)

        for row in rows:
            weighbridge = frappe.db.exists('Weighbridge', row[10])
            if not weighbridge:
                wb = frappe.new_doc('Weighbridge')
                wb.unique_id = row[10]
                wb.vehicle_no = row[0]
                wb.time_in = row[1]
                wb.wb1 = row[2]
                wb.cabin1 = row[3]
                wb.carriage1 = row[4]
                wb.net_wt = row[8]
                wb.time_out = row[9]
                wb.wb2 = row[5]
                wb.cabin2 = row[6]
                wb.carriage2 = row[7]
                wb.save()
               
        frappe.db.commit()    
    except:
        return            