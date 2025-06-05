frappe.ui.form.on('Purchase Order', {

   company(frm){
    //set default billing address
    console.log("compant")
    frappe.call({
        "method" : "axessio_erpnext.utils.get_company_default_billing_address",
        "args" : {
            "company" : frm.doc.company
        },
        callback:function(r) {
            if(r.message) {
                frm.set_value("billing_address",r.message)
            }
        }
    })
   }
    
})