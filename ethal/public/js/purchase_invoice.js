frappe.ui.form.on('Purchase Invoice', {
    bill_no: function (frm) {
        var a = frm.doc.bill_no;
        var mystr = a.replace(/\D/g, '');
        frm.set_value('bill_no', mystr);
        frm.refresh_field('bill_no')
    },
    withholding_receipt_no: function (frm) {
        var a = frm.doc.withholding_receipt_no;
        var mystr = a.replace(/\D/g, '');
        frm.set_value('withholding_receipt_no', mystr);
        frm.refresh_field('withholding_receipt_no')
    },
    refresh: function (frm) {
        console.log('refresh')
        frm.fields_dict['items'].grid.get_field("expense_account").get_query = function (doc, cdt, cdn) {
            return {
                filters: [
                    ['Account', 'is_group', '=', 'No'],
                    ['Account', 'company', '=', frm.doc.company]
                ]
            }
        }
    }
});