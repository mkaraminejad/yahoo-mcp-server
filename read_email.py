from imap_tools import MailBox, AND
from dotenv import load_dotenv
import os

a=load_dotenv()

ACCOUNTS = {
    "personal": ("YAHOO_PERSONAL_EMAIL", "YAHOO_PERSONAL_APP_PASSWORD"),
    "business": ("YAHOO_BS_EMAIL", "YAHOO_BS_APP_PASSWORD"),
}

#################################################
############### Credentials Function #####################
def get_account_credentials(account_name):
    email_env, password_env = ACCOUNTS[account_name]
    
    email = os.environ.get(email_env)
    password = os.environ.get(password_env)
    return email, password
#################################################################
##################### List Emails Function ######################
def list_emails(account_name, limit=10):
    email, password = get_account_credentials(account_name)
    results = []
# Get date, subject and body len of all emails from INBOX folder
    with MailBox('imap.mail.yahoo.com').login(email, password) as mailbox:
        for msg in mailbox.fetch(AND(seen=False), mark_seen=False, limit=limit, reverse=True, headers_only=True):
         #print(msg.date, msg.subject, len(msg.text or msg.html))
         results.append((msg.uid,msg.from_, msg.date_str, msg.subject, len(msg.text or msg.html)))
    return results
###################################################################
def search_inbox(account_name, sender="", subject="",body=""):
    email, password = get_account_credentials(account_name)
    sender = sender.strip()
    subject = subject.strip()
    body = body.strip()

    if sender and subject: 
        search_criteria = AND(from_=sender, subject=subject)
    elif sender:
        search_criteria = AND(from_=sender)
    elif subject:
        search_criteria = AND(subject=subject)  
    else:
        search_criteria = AND()  # No specific criteria, fetch all emails
    #####################################################################
    results = []
    with MailBox("imap.mail.yahoo.com").login(email, password) as mailbox:
        for msg in mailbox.fetch(
            search_criteria,
            reverse=True,
            mark_seen=False,
            headers_only=True,
        ):
            results.append({
                "uid": msg.uid,
                "from": msg.from_,
                "subject": msg.subject,
                "date": msg.date_str,
                "is_read": "\\Seen" in msg.flags,
            })

    return results
#####################################################################

                
    
    
    
    
    
    
        


    
    


###################################################################
if __name__ == "__main__":
    account_name=input("Enter account name (personal/business): ").strip().lower()
    limits=int(input("Enter the number of emails to fetch: ").strip())
    emails = list_emails(account_name, limit=limits)
    for email in emails:
        print(email)
    
    