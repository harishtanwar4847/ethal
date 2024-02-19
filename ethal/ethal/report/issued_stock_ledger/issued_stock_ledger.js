frappe.query_reports["Issued Stock Ledger"] = {
    "filters": [
        {
            "fieldname":"from_date",
            "label":("From Date"),
            "fieldtype":"Date",
            "default":frappe.datetime.month_start()
        },
        {
            "fieldname":"to_date",
            "label":("To Date"),
            "fieldtype":"Date",
            "default":frappe.datetime.month_end()
        },
        {
            "fieldname":"company",
            "label":("Company"),
            "fieldtype":"Link",
            "options":"Company",
            "default":"Ethal 2021"
        }
]
}