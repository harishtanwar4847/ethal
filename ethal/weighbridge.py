import frappe
import csv
from datetime import datetime
import os, sys, subprocess

# DATABASE = "/home/user/Desktop/Weighbridge/Main2002.mdb"
# table_names = subprocess.Popen(['mdb-tables', '-1', DATABASE], stdout=subprocess.PIPE).communicate()[0]
# tables = table_names.split('\n')
# for table in tables:
#     if table == "tare":
#         filename = table.replace(' ','_') + '.csv'
#         filename = "/home/user/ERPNEXT/ethal-bench/sites/ethal/private/files/"+filename
#         print('Exporting ' + table)
#         with open(filename, 'wb') as f:
#             subprocess.check_call(['mdb-export', DATABASE, table], stdout=f)


@frappe.whitelist(allow_guest=True)
def set_values_for_weighbridge():

    file_path = frappe.db.get_single_value("Weighbridge Sync","mdb_file_path")
    file_name = frappe.db.get_single_value("Weighbridge Sync","mdb_file_name")
    print(file_path)
    print(file_name)
    
    # mdb = frappe.get_site_path("private","files","Main2002.mdb")
    mdb = file_path+file_name
    print("mdb === ",mdb)
    
    # DATABASE = "/home/user/Desktop/Weighbridge/Main2002.mdb"
    table_names = subprocess.Popen(['mdb-tables', '-1', mdb], stdout=subprocess.PIPE).communicate()[0]
    print("table_names ===> ",table_names)
    print("table_names type =====> ",type(table_names))
    tables = table_names.split(b'\n')
    tables_lst = []
    for i in tables:
        valu = i.decode("utf-8")
        tables_lst.append(valu)
    print("tables_lst ========> ",tables_lst)
    print("tables type ========> ",type(tables_lst))
    # frappe.throw("ruk ja bhai")
    for table in tables_lst:
        if table == "Truck":
            filename = table.replace(' ','_') + '.csv'
            print('Exporting ' + table)
            with open(filename, 'wb') as f:
                subprocess.check_call(['mdb-export', mdb, table], stdout=f)
                print("completed")

    print("filename ===> ",filename)
    print("inside weighbridge function")
    lst = []
    with open(filename,'r') as file:
        reader = csv.reader(file)
        for row in reader:
            lst.append(row)

    for table in tables_lst:
        if table == "Matl":
            item_data = table.replace(' ','_') + '.csv'
            print('Exporting ' + table)
            with open(item_data, 'wb') as f:
                subprocess.check_call(['mdb-export', mdb, table], stdout=f)
                print("completed")

    print("item_data ===> ",item_data)
    print("inside weighbridge function")
    item_lst = []
    with open(item_data,'r') as file:
        reader = csv.reader(file)
        for row in reader:
            item_lst.append(row)  

    for item in item_lst:
        print(item) 
        existing_item = frappe.db.get_value('Weighbridge Material', {'name': item[1]}, 'name')
        print(existing_item)
        if not existing_item:
            weighbridge_material = frappe.get_doc({
                'doctype': 'Weighbridge Material',
                'weighbridge_material': item[1]
            })                    
            weighbridge_material.insert()
    frappe.db.commit()        

    srno = []
    sr = frappe.db.get_list("Weighbridge",fields=["sr_no"])
    if not sr:
        pass
    else:
        for i in sr:
            srno.append(i["sr_no"])
    # print("sr ===== ",sr)
    # srno.append(j)
    for i in lst:
        if lst.index(i) >= 1:
            if i[28] not in srno:
                # prd = frappe.db.get_value("Weighbridge Material",{"weighbridge_material":i[12]},"item_code")
                wb = frappe.get_doc({
                    'doctype':'Weighbridge',
                    'sr_no' : i[28],
                    'vehicle_no':i[0],
                    'challan':i[9],
                    'customer':i[11],
                    'product':i[12],
                    # 'product': prd,
                    'source':i[13],
                    'destination':i[14],
                    'transporter':i[17],
                    'gross':i[2],
                    'tare':i[3],
                    'net':i[4],
                    'date':datetime.strptime(i[26][:8], '%m/%d/%y'),
                    'time':datetime.strptime(i[27][9:],'%H:%M:%S').time()
                })
                wb.insert()
    frappe.db.commit()

