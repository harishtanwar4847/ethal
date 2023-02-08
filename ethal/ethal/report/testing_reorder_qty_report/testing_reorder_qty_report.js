frappe.query_reports["Testing Reorder qty report"] = {
    "filters": [
        {
            "fieldname":"from_date",
            "label":("From Date"),
            "fieldtype":"Date",
            "default":frappe.datetime.get_today()
        },
        {
            "fieldname":"to_date",
            "label":("To Date"),
            "fieldtype":"Date",
            "default":frappe.datetime.get_today()
        },
]
}