from imap_tools import MailBox, AND, OR
from dotenv import load_dotenv
from read_email import get_account_credentials
import os


load_dotenv()

def delete_email_inbox(account_name, uid):
    email, password = get_account_credentials(account_name)

    with MailBox('imap.mail.yahoo.com').login(email, password) as mailbox:
        mailbox.delete([uid])
    return {"uid": uid, "status": "deleted"}  


