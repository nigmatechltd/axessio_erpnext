import frappe
from frappe.model.naming import make_autoname
from helpdesk.helpdesk.doctype.hd_ticket.hd_ticket import HDTicket
from frappe.desk.form.assign_to import add
import json
from frappe.email.receive import InboundMail


from frappe.utils import (
    sanitize_html
)

class CustomInboundMail(InboundMail):
    
    
    def _create_reference_document(self, doctype):
        """Create reference document if it does not exist in the system."""
        try:
            parent = frappe.new_doc(doctype)
            email_fields = self.get_email_fields(doctype)
            
            print(doctype)
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
                parent.set("description",frappe.as_unicode(self.content))
                parent.set("status","erledigt")
                    
                        
            if email_fields.sender_name_field:
                parent.set(email_fields.sender_name_field, frappe.as_unicode(self.from_real_name))

            parent.flags.ignore_mandatory = True
            try:
                parent.insert(ignore_permissions=True)
                assign_ticket_to_recipient(parent,self.email_account.email_id)
                
                return parent.name
            except frappe.DuplicateEntryError:
                # try and find matching parent
                return frappe.db.get_value(doctype, {email_fields.sender_field: self.from_email})
        except:
            frappe.log_error("create_documents",frappe.get_traceback())


    # def _build_communication_doc(self):
    #         data = self.as_dict()
    #         data["doctype"] = "Communication"
          
            
    #         if self.parent_communication():
    #             data["in_reply_to"] = self.parent_communication().name

    #         append_to = self.append_to if self.email_account.use_imap else self.email_account.append_to

    #         # if self.reference_document():
    #         # 	data["reference_doctype"] = self.reference_document().doctype
    #         # 	data["reference_name"] = self.reference_document().name

    #         if append_to and append_to != "Communication": #alway use the append _to , pop does not work for 
    #             print("ok")
    #             reference_name = create_reference_document(append_to)
    #             if reference_name:
    #                 data["reference_doctype"] = append_to
    #                 data["reference_name"] = reference_name

    #         if self.is_notification():
    #             # Disable notifications for notification.
    #             data["unread_notification_sent"] = 1

    #         if self.seen_status:
    #             data["_seen"] = json.dumps(self.get_users_linked_to_account(self.email_account))

    #         communication = frappe.get_doc(data)
    #         communication.flags.in_receive = True
    #         communication.insert(ignore_permissions=True)

    #         # Communication might have been modified by some hooks, reload before saving
    #         communication.reload()

    #         # save attachments
    #         communication._attachments = self.save_attachments_in_doc(communication)
    #         communication.content = sanitize_html(self.replace_inline_images(communication._attachments))
    #         communication.save()
    #         return communication




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
    

def assign_ticket_to_recipient(parent,recipient_email):
    
    
    add({
        "doctype": "HD Ticket", 
        "name": parent.get("name"),
        "assign_to": [recipient_email],
        "description": parent.get("description","HD Ticket assigned"),
        "date": frappe.utils.getdate()
    })
    frappe.db.commit()    


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
    #add_options_to_hd_ticket()
    add_docperm_to_comm()


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
    
    #set completion field in Maintenance Visit to unmandatory
    completion_status =  frappe.get_meta("Maintenance Visit").get_field("completion_status")
    completion_status.reqd = 0
    completion_status.save()
    #set completion field in Maintenance Visit to unmandatory
    
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
        if self.is_new():
            self.name = make_autoname("TI.YY.MM.DD.-.#####")
        


def send_email(doc):
    
    if isinstance(doc,str):
        doc = json.loads(doc)
    
@frappe.whitelist()
def get_lease_details(lease):
    
    if frappe.db.exists("Lease",lease):
        lease_doc = frappe.get_doc("Lease", lease)
        lease_customer = lease_doc.lease_customer
        lease_company = lease_doc.company
        property = lease_doc.property
        property_address= lease_doc.property_address
        employee = frappe.db.get_value("Property",property,"custom_property_manager")
        lease_data = {"lease_customer":lease_customer,"lease_company":lease_company,
                      "property":property,"property_address":property_address,
                      "employee" : employee
                      }
        if lease_customer:
            mobile_no = frappe.db.get_value("Customer",lease_customer,"mobile_no")
            email_id = frappe.db.get_value("Customer",lease_customer,"email_id")
            lease_data.update({"mobile_no":mobile_no,"email_id":email_id})
        
        return lease_data



@frappe.whitelist()
def add_docperm_to_comm():
    #add docperm to communications
    if frappe.db.exists("DocPerm",{"parent": "Communication","role": "Employee","parentfield": "permissions"}):
        return
        comm_perm = frappe.get_doc({
            "doctype": "DocPerm",
            "parent": "Communication",
            "role": "Employee",
            "if_owner": 0,
            "permlevel": 0,
            "select": 0,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 1,
            "import": 0,
            "share": 1,
            "print": 1,
            "email": 1,
            "parentfield": "permissions",
            "parenttype": "DocType"
        })
        comm_perm.insert(ignore_permissions=True)
    
    #delete Permission
    if frappe.db.exists("DocPerm",{"parent": "Communication","role": "All","parentfield": "permissions",}):
        frappe.db.delete("DocPerm",{"parent": "Communication","role": "All","parentfield": "permissions",})