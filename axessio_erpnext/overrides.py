import frappe


def custom_create_reference_document(self, doctype):
    """Create reference document if it does not exist in the system."""
    try:
        parent = frappe.new_doc(doctype)
        email_fields = self.get_email_fields(doctype)
        if email_fields.subject_field:
            parent.set(email_fields.subject_field, frappe.as_unicode(self.subject)[:140])

        if email_fields.sender_field:
            parent.set(email_fields.sender_field, frappe.as_unicode(self.from_email))
            #get property from recipient name
            #find if an existing employee exists under this email
            #do this only if on issue
            property_unit,property_manager = get_linked_property(frappe.as_unicode(self.from_email),self.email_account.email_id)
            parent.set("property_name",property_unit)
            parent.set("person_in_charge",property_manager)
                
                    
        if email_fields.sender_name_field:
            parent.set(email_fields.sender_name_field, frappe.as_unicode(self.from_real_name))

        parent.flags.ignore_mandatory = True

        try:
            parent.insert(ignore_permissions=True)
            return parent.name
        except frappe.DuplicateEntryError:
            # try and find matching parent
            return frappe.db.get_value(doctype, {email_fields.sender_field: self.from_email})
    except:
        frappe.log_error("create_documents",frappe.get_traceback())

def issue_after_insert(doc,event):
    #update issues table in Property Unit.
    if doc.property_name:
        issue = frappe.get_doc({
            "doctype" : "Issues Table",
            "issue" : doc.name,
            "issue_type" : doc.issue_type,
            "issue_status" : doc.status,
            "parent": doc.property_name,
            "parentfield": "custom_tickets",
            "parenttype": "Property"
        })
        issue.insert()
        


def get_linked_property(sender_email,recipient_email):
    """Get linked property from either the sender email or recipient email
        property can be found in the linked lease for a customer(/property unit
        property can be found using the property_manager assigned to a property

    Args:
        sender_email (str): _description_
    """
    #find customer with same sender email
    property_unit = ""
    employee = ""
    if frappe.db.exists("Contact",{"email_id":sender_email}):
        contact = frappe.db.get_value("Contact",{"email_id":sender_email},"name")
        #get linked customer if existing
        customer = frappe.db.get_value("Dynamic Link",{"parenttype":"Contact","parent":contact,"link_doctype":"Customer"},"link_name")
        print(customer)
        if customer:
            #get property unit from customer lease
            property_unit = frappe.db.get_value("Lease",{"lease_customer":customer},"property")
            if property_unit:
                employee = frappe.db.get_value("Property", property_unit,"custom_property_manager")

    if not property_unit:
        #try to get the property unit using the property unit manager email
        if frappe.db.exists("Employee",{"personal_email":recipient_email}):
            employee = frappe.db.get_value("Employee",{"personal_email":recipient_email},"name")
            property_unit = frappe.db.get_value("Property",{"custom_property_manager":employee},"name")
    return property_unit,employee