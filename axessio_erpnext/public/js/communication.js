frappe.ui.form.on("Communication",{

    refresh: function(frm) {
        //add axession actions doctype
        
        cur_frm.remove_custom_button("Relink")
        cur_frm.remove_custom_button("Contact","Create")
		cur_frm.remove_custom_button("Lead","Create")
		cur_frm.remove_custom_button("Opportunity","Create")

        cur_frm.add_custom_button(__("Create Issue"), function(){
            frm.trigger("show_create_issue_dialog")
        },"Axessio Actions")

        cur_frm.add_custom_button(__("Link to Existing Issue"), function(){
            frm.trigger("show_issue_relink_dialog")
        },"Axessio Actions")

        cur_frm.add_custom_button(__("Create Opportunity"), function(){
            frm.trigger("make_opportunity_from_communication");
        },"Axessio Actions")
    },

    show_create_issue_dialog: function (frm) {
		var d = new frappe.ui.Dialog({
			title: __("Create Issue"),
			fields: [
				{
					fieldtype: "Data",
					label: __("Subject"),
					fieldname: "subject",
                    default : __(frm.doc.subject),
					
				},
				{
					fieldtype: "Link",
					options: "Issue Type",
					label: __("Issue Type"),
					fieldname: "issue_type",
				},
                {
					fieldtype: "Link",
					options: "Issue Priority",
					label: __("Priority"),
					fieldname: "priority",
				},
                {
					fieldtype: "Link",
					options: "Property",
					label: __("Property Unit"),
					fieldname: "property_unit",
				},
                {
					fieldtype: "Link",
					options: "Employee",
					label: __("Employee in Charge"),
					fieldname: "employee_in_charge",
				},
                {
					fieldtype: "Select",
					options: [" ","nicht begonnen","beauftragt","erledigt","angefangen","wiederkehrend"],
					label: __("Status"),
					fieldname: "status",
                    reqd : 1
				},
			],
		});
		d.set_primary_action(__("Create Issue"), function () {
			var values = d.get_values();
			if (values) {
				frappe.confirm(
					__("Are you sure you want to create an isssue from this communication?",),
					function () {
						d.hide();
						frappe.call({
							method: "axessio_erpnext.utils.create_issue",
							args: {
								"dialog_values": values,
								"description" : frm.doc.content,
                                "docname" : frm.doc.name
							},
							callback: function () {
								frappe.show_alert({
									message: __("Issue Created"),
									indicator: "info",
								});
                                cur_frm.reload_doc()
								

							},
						});
					},
					function () {
						frappe.show_alert({
							message: __("Issue not Created"),
							indicator: "info",
						});
                        d.hide()
					}
				);
			}
		});
		d.show();
	},

    show_issue_relink_dialog: function (frm) {
		var d = new frappe.ui.Dialog({
			title: __("Link Communication to Existing Issue"),
			fields: [
				
				{
					fieldtype: "Link",
					options: "Issue",
					label: __("Issue"),
					fieldname: "reference_name",
				},
			],
		});
		
		d.set_primary_action(__("link"), function () {
			var values = d.get_values();
			if (values) {
				frappe.confirm(
					__("Are you sure you want to relink this communication to {0}?", [
						values["reference_name"],
					]),
					function () {
						d.hide();
						frappe.call({
							method: "frappe.email.relink",
							args: {
								name: frm.doc.name,
								reference_doctype: "Issue",
								reference_name: values["reference_name"],
							},
							callback: function () {
								frm.refresh();
                                cur_frm.reload_doc()
							},
						});
					},
					function () {
						
					}
				);
			}
		});
		d.show();
	},
})