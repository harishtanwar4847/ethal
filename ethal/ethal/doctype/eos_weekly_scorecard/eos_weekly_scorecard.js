// Copyright (c) 2021, Atrina Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('EOS Weekly Scorecard', {
	refresh: function(frm) {
		if (frm.doc.eos_details == undefined) {
			frappe.call({
				'method': 'ethal.ethal.doctype.eos_weekly_scorecard.eos_weekly_scorecard.get_previous_record',
				'args': {
					doc: frm.doc
				}
			})
			.success(success => {
				console.log(success.message[0])
				var data = success.message
				for (var i = 0; i < data.length; i++) {
					var childTable = cur_frm.add_child("eos_details");
					childTable.division = data[i].division
					childTable.responsibility = data[i].responsibility
					childTable.parameter = data[i].parameter
					childTable.uom = data[i].uom
					childTable.target = data[i].target
					childTable.actual = data[i].actual
					childTable.remarks = data[i].remarks
					// childTable.items = l[i]
				}
				cur_frm.refresh_fields("eos_details");
			})
		}
	},
	
});

frappe.ui.form.on('EOS Weekly Scorecard Details', {
	target: function(frm, cdt, cdn) {
		var a = frm.doc.eos_details.length - 1
		var b = frm.doc.eos_details[a]
		if (b.parameter == 'Advance') {
			var c = frm.doc.eos_details.length - 2
			var d = (frm.doc.eos_details[c].actual / frm.doc.eos_details[c].target)
			var grid_row = locals[cdt][cdn];
			$("input[data-fieldname='actual']").css('pointer-events','none');
			console.log(b)
			b.actual = d
			frm.set_df_property(b.actual, 'read_only', 1)
			cur_frm.refresh_fields("eos_details");
		}
	},
	form_render: function(frm){
		var a = frm.doc.eos_details.length - 1
		var b = frm.doc.eos_details[a]
		if (b.parameter == 'Advance') {
			$("input[data-fieldname='actual']").css('pointer-events','none');
		}
	}	
});