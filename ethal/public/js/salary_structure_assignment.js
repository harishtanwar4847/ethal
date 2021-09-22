frappe.ui.form.on('Salary Structure Assignment', {
	refresh(frm) {
		// your code here
	},
	employee(frm){
	  frappe.db.get_value('Employee', frm.doc.employee, 'grade')
        .then(r => {
        console.log(r.message.grade)
        if (r.message.grade){
            console.log('hello')
            frappe.db.get_value('Employee Grade', r.message.grade, 'base_amount')
            .then(r => {
                console.log(r.message.base_amount)
                frm.set_value('base', r.message.base_amount)
             })
            frappe.db.get_value('Employee Grade', r.message.grade, 'default_salary_structure')
            .then(r => {
                frm.set_value('salary_structure', r.message.default_salary_structure)
             }) 
             

        }
    })
  
	},
	base(frm){
        frm.set_value('salary_in_usd', frm.doc.base)
        frappe.call({
            "method": "ethal.hr.set_conversion_rate",
            "args": {
                employee: frm.doc.employee
            }
        })
        .success(success => {
            console.log(success)
            frm.set_value('salary_in_birr', success.message*frm.doc.base)
        })
	}
})