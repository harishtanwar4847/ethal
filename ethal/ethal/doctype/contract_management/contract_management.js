// Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Contract Management', {
	setup: function(frm) {
		frm.set_query('payments_details', () => {
			return {
				filters: {
					naming_series: ['like', 'CPV%']
				}
			}
		})
	},
	contract_type: function(frm) {
		if (frm.doc.contract_type == 'Insurance') {
			frm.set_df_property('contract_for', 'options', ['Motor Vehicle - Full', 'Motor Vehicle - 3rd Party', 'Fixed Asset', 'Current Asset', 'Goods in Transit', 'Fidelity', 'Workmens', 'Others'])
		}
		else if (frm.doc.contract_type == 'Licenses') {
			frm.set_df_property('contract_for', 'options', ['Business Licence', 'Investment Permit', 'TIN no', 'VAT', 'ESIA'])
		}
		else if (frm.doc.contract_type == 'Employee Permits') {
			frm.set_df_property('contract_for', 'options', ['Passport', 'WorkPermit', 'Temporary Residence ID', 'Visa', 'Yellow Fever Vaccination Certificate', 'Oral Polio vaccination Certificate'])
		}
	}
});
