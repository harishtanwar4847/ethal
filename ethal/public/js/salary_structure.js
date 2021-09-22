frappe.ui.form.on('Salary Structure', {
    refresh(frm) {
        // your code here
        frm.remove_custom_button('Assign to Employees')
        frm.add_custom_button('Assign Employees', () => {
            var d = new frappe.ui.Dialog({

                title: __("Assign to Employees"),
                fields: [
                    { fieldname: "sec_break", fieldtype: "Section Break", label: __("Filter Employees By (Optional)") },
                    { fieldname: "company", fieldtype: "Link", options: "Company", label: __("Company"), default: frm.doc.company, read_only: 1 },
                    {
                        fieldname: "grade", fieldtype: "Link", options: "Employee Grade", label: __("Employee Grade"), change: () => {

                            frappe.db.get_value('Employee Grade', d.get_value('grade'), 'base_amount')
                                .then(r => {
                                    console.log(r.message) // Open
                                    d.set_value('base', r.message.base_amount)
                                })

                        }
                    },
                    { fieldname: 'department', fieldtype: 'Link', options: 'Department', label: __('Department') },
                    { fieldname: 'designation', fieldtype: 'Link', options: 'Designation', label: __('Designation') },
                    { fieldname: "employee", fieldtype: "Link", options: "Employee", label: __("Employee") },
                    { fieldname: 'base_variable', fieldtype: 'Section Break' },
                    { fieldname: 'from_date', fieldtype: 'Date', label: __('From Date'), "reqd": 1 },
                    { fieldname: 'income_tax_slab', fieldtype: 'Link', label: __('Income Tax Slab'), options: 'Income Tax Slab' },
                    { fieldname: 'base_col_br', fieldtype: 'Column Break' },
                    { fieldname: 'base', fieldtype: 'Currency', label: __('Base'), read_only: 1 }
                ],
                primary_action: function () {
                    console.log(d.get_value('grade'))
                    var data = d.get_values();
                    data['doc'] = frm.doc
                    console.log(data)
                    frappe.call({

                        method: "ethal.hr.assign_salary_structure",
                        args: data,
                        callback: function (r) {
                            if (!r.exc) {
                                d.hide();
                                frm.reload_doc();
                            }
                        }
                    });
                },
                primary_action_label: __('Assign')
            });


            d.show();
        })
    }
})