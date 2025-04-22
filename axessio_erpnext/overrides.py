import frappe
from frappe.model.naming import make_autoname
from helpdesk.helpdesk.doctype.hd_ticket.hd_ticket import HDTicket

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
            parent.set("custom_property_unit",property_unit)
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

def ticket_after_insert(doc,event):
    #update issues table in Property Unit.
    if doc.custom_property_unit:
        hdticket = frappe.get_doc({
            "doctype" : "Ticket Table",
            "ticket" : doc.name,
            "ticket_type" : doc.ticket_type,
            "ticket_status" : doc.status,
            "parent": doc.custom_property_unit,
            "parentfield": "custom_tickets",
            "parenttype": "Property"
        })
        hdticket.insert()
        


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



def run_after_migrate():
    add_options_to_issue_type()
    add_options_to_hd_ticket()


def add_options_to_issue_type():
    if frappe.db.exists("Property Setter", "Issue-status-options"):
        frappe.db.delete("Property Setter", "Issue-status-options")
    issue_status =  frappe.get_meta("Issue").get_field("status")
    issue_status_options = issue_status.options
    
    issue_status_options = [] #issue_status_options.split("\n")
    new_options = ["nicht begonnen","beauftragt","erledigt","angefangen","wiederkehrend"]
    for status in new_options:
        if status not in issue_status_options:
            issue_status_options.append(status)
    
    issue_status_options = "\n".join(issue_status_options)
        
    issue_status.options = issue_status_options
    frappe.db.delete("Property Setter", "Issue-status-options")
    issue_status.save()
    frappe.db.commit()
    

def add_options_to_hd_ticket():
    
    issue_status =  frappe.get_meta("HD Ticket").get_field("status")
    issue_status_options = issue_status.options
    
    issue_status_options = issue_status_options.split("\n")
    new_options = ["Open","nicht begonnen","beauftragt","erledigt","angefangen",
                   "wiederkehrend","Replied","Resolved","Closed"]
    for status in new_options:
        if status not in issue_status_options:
            issue_status_options.append(status)
    
    issue_status_options = "\n".join(issue_status_options)
        
    issue_status.options = issue_status_options
    issue_status.save()
    frappe.db.commit()
    

class CustomHDTicket(HDTicket):
    
      
   
   def validate(self):
        return       
        if self.is_new():
            self.name = make_autoname("TI.YY.MM.DD.-.#####")
        
       
       