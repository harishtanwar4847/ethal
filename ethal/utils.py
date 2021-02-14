import frappe
from frappe.utils import getdate, nowdate, cint, flt
import json
from datetime import date, timedelta, datetime
import time
from frappe.utils import formatdate
import ast
import itertools
from erpnext.hr.doctype.employee_checkin.employee_checkin import mark_attendance_and_link_log
from frappe.utils.background_jobs import enqueue

def override_job_applicant_dashboard(data):
    print(data)
    return {
        'fieldname': 'job_applicant',
        'transactions': [
            # {
            #     'items': ['Employee', 'Employee Onboarding']
            # },
            # {
            #     'items': ['Job Offer']
            # },
            # {
            #     'items': ['Interview']
            # },
        ],
    }

@frappe.whitelist()
def before_save_asset_maintenance_log(doc, method):  
    asset_maintenance_task = frappe.get_all('Asset Maintenance Task', filters={'parent': doc.asset_maintenance}, fields=['maintanence_category', 'maintenance_task'])
    if asset_maintenance_task:
        for row in asset_maintenance_task:
            print(row['maintenance_task'])
            frappe.db.set_value('Asset Maintenance Log', {'task_name': row['maintenance_task']}, 'maintanence_category', row['maintanence_category'])

@frappe.whitelist()
def create_stock_entry(doc, method):
    get_part_used = frappe.get_all('Parts Used Item Table', filters = {'parent': doc.name}, fields=['*'])
    print(get_part_used)
    stock_entry = frappe.new_doc('Stock Entry')
    stock_entry.stock_entry_type= 'Material Issue'
    for row in get_part_used:
        source_warehouse = frappe.db.get_all('Item Default', {'parent': row['item']}, ['default_warehouse'])
        stock_entry.append('items', {
            's_warehouse': source_warehouse[0].default_warehouse,
            'item_code': row['item'],
            'item_group': row['item_group'],
            'qty': row['quantity'],
            'uom': row['uom']
        })
        stock_entry.insert(ignore_permissions=True)
        stock_entry.docstatus = 1

@frappe.whitelist()
def create_stock_entry_from_asset_repair(doc, method):
    get_part_used = frappe.get_all('Parts Used Item Table', filters = {'parent': doc.name}, fields=['*'])
    print(get_part_used)
    stock_entry = frappe.new_doc('Stock Entry')
    stock_entry.stock_entry_type= 'Material Issue'
    for row in get_part_used:
        source_warehouse = frappe.db.get_all('Item Default', {'parent': row['item']}, ['default_warehouse'])
        stock_entry.append('items', {
            's_warehouse': source_warehouse[0].default_warehouse,
            'item_code': row['item'],
            'item_group': row['item_group'],
            'qty': row['quantity'],
            'uom': row['uom']
        })
    stock_entry.insert(ignore_permissions=True)
    stock_entry.docstatus = 1

@frappe.whitelist()
def set_items_from_stock_entry(name):
    stock_entry_detail = frappe.get_all('Stock Entry Detail', filters={'parent': name}, fields=['*'])
    for i in stock_entry_detail:
        return i

@frappe.whitelist()
def before_submit_all_doctypes(doc, method):
    user = frappe.get_roles(frappe.session.user)
    admin_settings = frappe.get_doc('Admin Settings')
    admin_settings_document = frappe.get_all('Admin Settings Document', {'parent': 'Admin Settings', 'document': doc.doctype}, ['date'], as_list=1)  
   
    if admin_settings.applicable_for_role not in user:
        if admin_settings_document:
            if admin_settings_document[0][0] == 'posting_date':
                if admin_settings.closure_date > doc.posting_date:
                    frappe.throw(frappe._("You are not authorized to add or update entries before {0}").format(formatdate(admin_settings.closure_date)))
            elif admin_settings_document[0][0] == 'transaction_date':
                if admin_settings.closure_date > doc.transaction_date:
                    frappe.throw(frappe._("You are not authorized to add or update entries before {0}").format(formatdate(admin_settings.closure_date)))

@frappe.whitelist()
def set_approver_name(doc, method):
    doc.approver_person = doc.modified_by
    doc.approver_date = doc.modified

@frappe.whitelist()
def before_submit_stock_entry(doc, method):
    if doc.value_difference > 1:
        frappe.throw('Incoming Value not equal to Outgoing Value! Please Correct the rate.')

@frappe.whitelist()
def on_update_employee(doc, method):
    get_salary_structure_ass = frappe.get_all('Salary Structure Assignment', filters={'employee': doc.employee, 'docstatus': 1})
    if get_salary_structure_ass:
        grade = frappe.db.get_value('Employee Grade', doc.grade, 'default_salary_structure')
        frappe.db.set_value('Salary Structure Assignment', {'name': get_salary_structure_ass[0].name}, 'salary_structure', grade)
        employee_grade = frappe.db.get_value('Employee Grade', doc.grade, 'base_amount')
        frappe.db.set_value('Salary Structure Assignment', {'name': get_salary_structure_ass[0].name}, 'base', employee_grade)
        frappe.db.set_value('Salary Structure Assignment', {'name': get_salary_structure_ass[0].name}, 'salary_in_usd', employee_grade)
        frappe.db.set_value('Salary Structure Assignment', {'name': get_salary_structure_ass[0].name}, 'staus', 'Salary Updated')
        frappe.db.commit()

@frappe.whitelist()
def set_conversion_rate(employee):
    employee_list = frappe.db.get_all('Payroll Employee Detail', {'employee': employee}, ['parent'], order_by='creation desc', limit=1, as_list=1)
    if employee_list:
        get_conversion_rate = frappe.db.get_value('Payroll Entry', employee_list[0][0], 'conversion_rate')
        return get_conversion_rate
        
@frappe.whitelist()
def assign_salary_structure(doc, company=None, grade=None, department=None, designation=None,employee=None,
        from_date=None, base=None, variable=None, income_tax_slab=None):
    employees = get_employees(doc, company= company, grade= grade,department= department,designation= designation,name=employee)

    if employees:
        if len(employees) > 20:
            frappe.enqueue(assign_salary_structure_for_employees, timeout=600,
                employees=employees, salary_structure=doc,from_date=from_date,
                base=base, variable=variable, income_tax_slab=income_tax_slab)
        else:
            assign_salary_structure_for_employees(employees, doc, from_date=from_date,
                base=base, variable=variable, income_tax_slab=income_tax_slab)
    else:
        frappe.msgprint(frappe._("No Employee Found"))

def assign_salary_structure_for_employees(employees, salary_structure, from_date=None, base=None, variable=None, income_tax_slab=None):
	salary_structures_assignments = []
	existing_assignments_for = get_existing_assignments(employees, salary_structure, from_date)
	count=0
	for employee in employees:
		if employee in existing_assignments_for:
			continue
		count +=1

		salary_structures_assignment = create_salary_structures_assignment(employee,
			salary_structure, from_date, base, variable, income_tax_slab)
		salary_structures_assignments.append(salary_structures_assignment)
		frappe.publish_progress(count*100/len(set(employees) - set(existing_assignments_for)), title = frappe._("Assigning Structures..."))

	if salary_structures_assignments:
		frappe.msgprint(frappe._("Structures have been assigned successfully"))


def create_salary_structures_assignment(employee, salary_structure, from_date, base, variable, income_tax_slab=None):
    salary_structure = ast.literal_eval(salary_structure)
    assignment = frappe.new_doc("Salary Structure Assignment")
    assignment.employee = employee
    assignment.salary_structure = salary_structure['name']
    assignment.company = salary_structure['company']
    assignment.from_date = from_date
    assignment.base = base
    assignment.variable = variable
    assignment.income_tax_slab = income_tax_slab
    assignment.save(ignore_permissions = True)
    assignment.submit()
    return assignment.name


def get_existing_assignments(employees, salary_structure, from_date):
    salary_structure = ast.literal_eval(salary_structure)
    salary_structures_assignments = frappe.db.sql_list("""
        select distinct employee from `tabSalary Structure Assignment`
        where salary_structure=%s and employee in (%s)
        and company= %s and docstatus=1
    """ % ('%s', ', '.join(['%s']*len(employees)),'%s'), [salary_structure['name']] + employees+[salary_structure['company']])
    if salary_structures_assignments:
        frappe.msgprint(frappe._("Skipping Salary Structure Assignment for the following employees, as Salary Structure Assignment records already exists against them. {0}")
            .format("\n".join(salary_structures_assignments)))
    return salary_structures_assignments

@frappe.whitelist()
def make_salary_slip(source_name, target_doc = None, employee = None, as_print = False, print_format = None, for_preview=0, ignore_permissions=False):
	def postprocess(source, target):
		if employee:
			employee_details = frappe.db.get_value("Employee", employee,
				["employee_name", "branch", "designation", "department"], as_dict=1)
			target.employee = employee
			target.employee_name = employee_details.employee_name
			target.branch = employee_details.branch
			target.designation = employee_details.designation
			target.department = employee_details.department
		target.run_method('process_salary_structure', for_preview=for_preview)

	doc = get_mapped_doc("Salary Structure", source_name, {
		"Salary Structure": {
			"doctype": "Salary Slip",
			"field_map": {
				"total_earning": "gross_pay",
				"name": "salary_structure"
			}
		}
	}, target_doc, postprocess, ignore_child_tables=True, ignore_permissions=ignore_permissions)

	if cint(as_print):
		doc.name = 'Preview for {0}'.format(employee)
		return frappe.get_print(doc.doctype, doc.name, doc = doc, print_format = print_format)
	else:
		return doc



def get_employees(doc, **kwargs):
		conditions, values = [], []
		for field, value in kwargs.items():
			if value:
				conditions.append("{0}=%s".format(field))
				values.append(value)

		condition_str = " and " + " and ".join(conditions) if conditions else ""

		employees = frappe.db.sql_list("select name from tabEmployee where status='Active' {condition}"
			.format(condition=condition_str), tuple(values))

		return employees

@frappe.whitelist()
def existing_interview_rounds(job_applicant, job_opening):
    interview = frappe.get_list('Interview', filters={'job_applicant': job_applicant}, as_list = 1)
    if len(interview) > 0:
        rounds = frappe.get_list('Interview Round', filters={'interview': interview[0][0]}, order_by='round_number')
        print(len(rounds))
        if len(rounds) > 0:
            return True
        else:
            return False

@frappe.whitelist()
def get_interview_rounds(job_applicant, job_opening):
    interview = frappe.get_all('Interview', filters={'job_applicant': job_applicant, }, as_list = 1)
    rounds = frappe.get_all('Interview Round', filters={'interview': interview[0][0]}, fields=['*'], order_by='round_number')
    print(rounds)
    list2 = []
    for i in rounds:
        comment = []
        if i['_comments'] is not None:
            a = json.loads(i['_comments'])
            for j in a:
                comment.append(j['comment'])
            
        print(comment)
       
        interviewer = frappe.get_all('Interviewer', filters={'parent': i['name']}, fields=['employee', 'employee_name'] )
        l_ = []
        for row in interviewer:
                l_.append("{}-{}".format(row['employee'], row['employee_name']))    
        k =  [
                # {
                #     'label': i['round_number'],
                #     'fieldname': '',
                #     'fieldtype': 'Section Break'
                # },
                {
                    'label': 'Round Number',
                    'fieldname': 'round_number',
                    'fieldtype': 'Data',
                    'default': i['round_number'],
                    'read_only': 1
                },
                {
                    'label': 'Date',
                    'fieldname': 'date',
                    'fieldtype': 'Datetime',
                    'read_only': 1,
                    'default': i['date']
                },
                {
                    'label': '',
                    'fieldname': '',
                    'fieldtype': 'Column Break'
                },
                {
                    'label': 'Round Name',
                    'fieldname': 'round_name',
                    'fieldtype': 'Data',
                    'default': i['round'],
                    'read_only': 1
                },
                {
                    'label': 'Status',
                    'fieldname': 'status',
                    'fieldtype': 'Data',
                    'default': i['status'],
                    'read_only': 1
                },
                {
                    'label': '',
                    'fieldname': '',
                    'fieldtype': 'Column Break'
                },
                {
                    "label": "Interviewer's",
                    'fieldname': "interviewers",
                    "fieldtype": "Small Text",
                    "options": "Interviewer",
                    '_link_field':'employee',
                    'default': '\n'.join(l_),
                    'read_only': 1
                },
                {
                    "label": "Overall Recommendation",
                    'fieldname': "overall_recommendation",
                    "fieldtype": "Data",
                    'read_only': 1,
                    'default': i['overall_recommendation']
                },
                {
                    'label': '',
                    'fieldname': '',
                    'fieldtype': 'Section Break'

                }
            ]  
        list2.append(k)
        
        rounds_feedback = frappe.get_all('Interview Round Feedback', filters={'parent': i['name']}, fields=['*'])
        print(rounds_feedback, 'rounds feedback')
        if len(rounds_feedback) > 0:
            for i in rounds_feedback:
                l = [
                    {
                        'label': 'Skill',
                        'fieldname': 'skill',
                        'fieldtype': 'Link',
                        'read_only': 1,
                        'default': i['skill']
                    },
                    {
                        'label': '',
                        'fieldname': '',
                        'fieldtype': 'Column Break'
                    },
                    {
                        'label': 'Remark',
                        'fieldname': 'remark',
                        'fieldtype': 'Small Text',
                        'read_only': 1,
                        'default': i['remark']
                    },
                    {
                        'label': '',
                        'fieldname': '',
                        'fieldtype': 'Column Break'
                    },
                    {
                        'label': 'Rating',
                        'fieldname': 'rating',
                        'fieldtype': 'Int',
                        'read_only': 1,
                        'default': i['rating1']
                    },
                     
                    {
                        'label': '',
                        'fieldname': '',
                        'fieldtype': 'Section Break'
                    }

                ]
                list2.append(l)
        c = [
                {
                    'label': 'Comment',
                    'fieldname': 'comment',
                    'fieldtype': 'HTML Editor',
                    'read_only': 1,
                    'default': comment,
                    'Bold': 1
                    # 'default': a[0]['comment']
                },
                {
                    'label': '',
                    'fieldname': '',
                    'fieldtype': 'Section Break'
                }
            ]    
        list2.append(c)   
    interview_rounds = [val for sublist in list2 for val in sublist] 
    interviewer = frappe.get_doc('DocType', 'Interviewer')
    return {'interview_rounds': interview_rounds, 'interviewer': interviewer}

@frappe.whitelist()
def get_interview_and_interview_rounds(job_applicant, job_opening):
    interview = frappe.get_list("Interview", filters={'job_applicant': job_applicant}, fields=['*'])
    designation = frappe.get_list("Job Opening", filters={'name': job_opening}, fields=['designation'], as_list=1)
    print(designation)
    configuration = frappe.get_all('Interview Configuration', filters={'designation': designation[0][0]})
    print(len(configuration))
    if len(configuration) == 0:
        return False
    if len(interview) == 0:
        print("In if condition")
        rounds =  [
            {
                'label': 'Round 1',
                'fieldname': '',
                'fieldtype': 'Section Break'
            },

            {
                'label': 'Date',
                'fieldname': 'date',
                'fieldtype': 'Datetime'
            },
            {
                'label': '',
                'fieldname': '',
                'fieldtype': 'Column Break'
            },
            {
                    "label": "Interviewers",
                    'fieldname': "interviewers",
                    "fieldtype": "Table MultiSelect",
                    "options": "Interviewer",
                    '_link_field':'employee'
            }
        ] 
        interviewer = frappe.get_doc('DocType', 'Interviewer')
        return {'rounds':rounds, 'interviewer': interviewer}  
    else:
        print("in else condition")
        # created interview section
        list1 = []
        k = [
                {
                    'label': 'Interview',
                    'fieldname': 'interview',
                    'fieldtype': 'Link',
                    'options': 'Interview',
                    'default': interview[0]['name'],
                    'read_only': 1
                },
                {
                    'label': 'Job Opening',
                    'fieldname': 'job_opening',
                    'fieldtype': 'Link',
                    'options': 'Job Opening',
                    'default': interview[0]['job_opening'],
                    'read_only': 1
                },
                {
                    'label': '',
                    'fieldname': '',
                    'fieldtype': 'Column Break'
                },
                {
                    'label': 'Job Applicant',
                    'fieldname': 'job_applicant',
                    'fieldtype': 'Link',
                    'options': 'Job Applicant',
                    'default': interview[0]['job_applicant_name'],
                    'read_only': 1
                },
                {
                    'label': 'Designation',
                    'fieldname': 'designation',
                    'fieldtype': 'Link',
                    'options': 'Designation',
                    'default': interview[0]['designation'],
                    'read_only': 1
                }
        ]
        list1.append(k)
        interview_round = frappe.get_list('Interview Round', filters={'interview': interview[0]['name']}, fields=['*'], order_by = 'round_number')
        print(interview_round)
        for l in interview_round:
            
            interviewer = frappe.get_all('Interviewer', filters={'parent': l['name']}, fields=['employee', 'employee_name'] )
            l_ = []
            for row in interviewer:
                l_.append("{}-{}".format(row['employee'], row['employee_name']))
            #   created rounds section
            m =  [
                {
                    'label': 'Round' + ' ' + str(l['round_number']) + '-' + l['round'],
                    'fieldname': '',
                    'fieldtype': 'Section Break'
                },
                {
                    'label': 'Date',
                    'fieldname': 'date_',
                    'fieldtype': 'Datetime',
                    'default': l['date'],
                    'read_only': 1

                },
                {
                    'label': '',
                    'fieldname': '',
                    'fieldtype': 'Column Break'
                },
                {
                    "label": "Interviewers",
                    'fieldname': "interviewers",
                    "fieldtype": "Small Text",
                    "options": "Interviewer",
                    '_link_field':'employee',
                    'default': '\n'.join(l_),
                    'read_only': 1
                }
                
                ]
            list1.append(m)
        existing_rounds_ = frappe.get_list("Interview Round", fields=["round"], filters={
                                'interview': interview[0]['name']}, as_list=1)
        existing_rounds = [i[0] for i in existing_rounds_]
        # print(designation[0][0])
        rounds = frappe.get_list("Interview Round Configuration", fields=['*'], filters={'parent': interview[0]['designation'], 'round_name': ['not in', existing_rounds]}, order_by='round_number')
        if len(rounds) > 0:
            # new rounds section
            y =  [
                {
                    'label': 'Round' + ' ' + str(rounds[0]['round_number']) + '-' + rounds[0]['round_name'],
                    'fieldname': '',
                    'fieldtype': 'Section Break'
                },
                {
                    'label': 'Date',
                    'fieldname': 'date',
                    'fieldtype': 'Datetime',
                    # 'default': z['date']

                },
                {
                    'label': '',
                    'fieldname': '',
                    'fieldtype': 'Column Break'
                }, 
                {
                    "label": "Interviewers",
                    'fieldname': "interviewers",
                    "fieldtype": "Table MultiSelect",
                    "options": "Interviewer",
                    '_link_field':'employee'
                }
            ]
            list1.append(y)
        rounds_ = [val for sublist in list1 for val in sublist] 
        interviewer = frappe.get_doc('DocType', 'Interviewer')
        return {'rounds':rounds_, 'interviewer': interviewer} 

@frappe.whitelist()
def save_interview_round(formdata, job_applicant):
    data = json.loads(formdata)
  
    job_applicant_doc = frappe.get_doc("Job Applicant", job_applicant)

    job_opening_doc = frappe.get_doc("Job Opening", job_applicant_doc.job_title)

    get_interview = frappe.get_list('Interview', filters={'job_applicant': job_applicant}, as_list=1)

    job_opening = frappe.get_list('Job Opening', filters={'name' : job_opening_doc.name}, fields=['designation'], as_list =1)

    interview_configuration = frappe.get_list('Interview Round Configuration', filters={'parent': job_opening[0][0]}, fields=['round_number', 'round_name'], order_by='round_number')
    interview1 = frappe.get_list('Interview', filters={'job_applicant': job_applicant}, as_list=1)
    print(interview_configuration, len(interview_configuration))
    # configuration = frappe.get_all('Interview Configuration', filters={'designation': job_opening[0][0]})
    # print(len(configuration))
    # if len(configuration) == 0:
    #     return False

    if len(get_interview) == 0:
        interview = frappe.new_doc("Interview")
        interview.job_applicant = job_applicant
        interview.job_opening = job_opening_doc.name
        interview.designation = job_opening_doc.designation
        interview.current_round = interview_configuration[0]['round_name']
        interview.current_round_status = "Scheduled"
        interview.insert(ignore_permissions=True)
    
        interview1 = frappe.get_list('Interview', filters={'job_applicant': job_applicant}, as_list=1)
        interview_round = frappe.new_doc('Interview Round')
        interview_round.interview = interview1[0][0]
        interview_round.job_applicant = job_applicant
        interview_round.job_opening = job_opening_doc.name
        interview_round.designation = job_opening_doc.designation
        interview_round.attached_resume = job_applicant_doc.resume_attachment
        interview_round.round = interview_configuration[0]['round_name']
        interview_round.date = data['date']
        interview_round.round_number = interview_configuration[0]['round_number']
        # interview_round.interviewers = data['interviewers']
        for row in data['interviewers']:
            interview_round.append('interviewers', {
                'employee': row['employee']
            })
        interview_round.insert(ignore_permissions=True)

        job_applicant = frappe.get_doc('Job Applicant', job_applicant)
        job_applicant.current_round = 'Round' + " " + interview_configuration[0]['round_number']
        job_applicant.status = 'Round' + " " + interview_configuration[0]['round_number'] + " " + 'Scheduled'    
        job_applicant.save(ignore_permissions=True)
       
        print("Save interview round")

    else:
        existing_rounds_ = frappe.get_list("Interview Round", fields=["round"], filters={
                                'interview': interview1[0][0]}, as_list=1)
        existing_rounds = [i[0] for i in existing_rounds_]
        rounds = frappe.get_list("Interview Round Configuration", fields=['*'], filters={'parent': job_opening_doc.designation, 'round_name': ['not in', existing_rounds]}, order_by='round_number')
       
       
        interview = frappe.get_doc("Interview", get_interview[0][0])
        interview.current_round = rounds[0]['round_name']
        interview.current_round_status = "Scheduled"
        interview.save(ignore_permissions=True)

        interview_round = frappe.new_doc('Interview Round')
        interview_round.interview = get_interview[0][0]
        interview_round.job_applicant = job_applicant
        interview_round.job_opening = job_opening_doc.name
        interview_round.designation = job_opening_doc.designation
        interview_round.attached_resume = job_applicant_doc.resume_attachment
        interview_round.round = rounds[0]['round_name']
        interview_round.date = data['date']
        interview_round.round_number = rounds[0]['round_number']
        # interview_round.interviewers = data['interviewers']
        # interview_round.comments = 
        for row in data['interviewers']:
            interview_round.append('interviewers', {
                'employee': row['employee']
            })
        interview_round.insert(ignore_permissions=True)

        job_applicant = frappe.get_doc('Job Applicant', job_applicant)
        job_applicant.current_round = 'Round' + " " + rounds[0]['round_number']
        job_applicant.status = 'Round' + " " + rounds[0]['round_number'] + " " + 'Scheduled'    
        job_applicant.save(ignore_permissions=True)

@frappe.whitelist()
def before_insert_payment_entry(doc, method):
    if doc.naming_series.startswith('CPV') and doc.mode_of_payment == 'Cheque':
        payment_entries = frappe.db.get_value('Payment Entry', {'reference_no': doc.reference_no, 'docstatus': ['!=', '2']}, ['name'])
        if payment_entries == None:
            return
        elif payment_entries != doc.name:    
            frappe.throw('Cheque/Reference no must be unique')   

def before_insert_sales_invoice(doc, method):
    if doc.naming_series.startswith('ACSI-TU'):
        sales_invoice = frappe.db.get_value('Sales Invoice', {'fs_number': doc.fs_number, 'naming_series': ['like', '%ACSI-TU-%'], 'docstatus': ['!=', '2']}, ['name'])
        if sales_invoice == None:
            return
        elif sales_invoice != doc.name:    
            frappe.throw('FS Numer must be unique')   
    elif doc.naming_series.startswith('ACSI-DB'):  
        sales_invoice = frappe.db.get_value('Sales Invoice', {'fs_number': doc.fs_number, 'naming_series': ['like', '%ACSI-DB-%'], 'docstatus': ['!=', '2']}, ['name'])
        if sales_invoice == None:
            return
        elif sales_invoice != doc.name:    
            frappe.throw('FS Numer must be unique')   