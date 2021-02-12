import frappe

@frappe.whitelist()
def before_submit_leave_allocation(doc, method):
    def calculate_years_of_experience(doj, till_date=None):
        from dateutil.relativedelta import relativedelta
        if not till_date:
            from datetime import datetime 
            till_date = datetime.today()

        try: 
            experience = relativedelta(till_date, doj).years
        except AttributeError:
            experience = 0
        
        return experience

    doj = frappe.db.get_value('Employee', doc.employee, 'date_of_joining')
    leave_date = frappe.db.get_value('Leave Allocation', doc.name, 'from_date')
    total_experience = calculate_years_of_experience(doj, leave_date)
    base_leave_count = 16
    get_total_leaves = base_leave_count+(float(total_experience)/2)
    frappe.db.set_value('Leave Allocation', doc.name, 'new_leaves_allocated', get_total_leaves)
    frappe.db.set_value('Leave Allocation', doc.name, 'total_leaves_allocated', get_total_leaves)