frappe.ui.form.on('HD Ticket', {

    custom_lease : function(frm){
        // get value of property,customer and customer email if existing
        frappe.call({
            method:"axessio_erpnext.overrides.get_lease_details",
            args:{
                "lease" : frm.doc.custom_lease,

            },
            callback:function(r){
                var data = r["message"]
                //set values
                frm.set_value("custom_property_unit",data["property"])
                frm.set_value("customer",data["lease_customer"])
                frm.set_value("custom_customer_contact_email",data["contact_email"])
                frm.set_value("custom_customer_contact_phone",data["email_id"])
                frm.set_value("custom_person_in_charge",data["employee"])

            }
        })
    }
    
})