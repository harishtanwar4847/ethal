import frappe
import csv
from datetime import datetime
import os, sys, subprocess

@frappe.whitelist()
def set_values_for_weighbridge():

    file_path = frappe.db.get_single_value("Weighbridge Sync","file_path")
    file_name = frappe.db.get_single_value("Weighbridge Sync","file_name")

    filepath = os.path.join(file_path, file_name)
    # importing csv module
    import csv
    
    # initializing the titles and rows list
    try:
    # reading csv file
        people_list = []
        headers_list = []

        index = 0

        with open(filepath, 'r') as data:
            for line in csv.reader(data):
                index += 1
                if index > 1:
                    people_dict = {}
                    for i, elem in enumerate(headers_list):
                        people_dict[elem] = line[i]
                    people_list.append(people_dict)
                else:
                    headers_list = list(line)    

        for row in people_list:
            weighbridge = frappe.db.exists('Weighbridge', row['Name'])
            if not weighbridge:
                wb = frappe.new_doc('Weighbridge')
                wb.unique_id = row['Name']
                wb.vehicle_no = row['VH Num']
                wb.time_in = row['Time In']
                wb.wb1 = row['WB 1']
                wb.cabin1 = row['Cabin 1']
                wb.carriage1 = row['Carriage 1']
                wb.net_wt = row['Net Wt']
                wb.time_out = row['Time Out']
                wb.wb2 = row['WB 2']
                wb.cabin2 = row['Cabin 2']
                wb.carriage2 = row['Carriage 2']
                wb.save()
               
        frappe.db.commit()    
    except Exception:
        frappe.log_error(title='Weighbridge sync error')
           