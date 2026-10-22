import smtplib
import ssl
from email.message import EmailMessage
from read_email import get_account_credentials


def send_email_outbox(
    account_name: str,
    recipient: str,
    subject: str,
    body: str,
) -> dict[str, str]:
    email, password = get_account_credentials(account_name)

    message = EmailMessage()
    message["From"] = email
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP_SSL(
        "smtp.mail.yahoo.com",
        465,
        context=ssl.create_default_context(),
        timeout=30,
    ) as smtp:
        smtp.login(email, password)
        smtp.send_message(message)

    return {
        "account": account_name,
        "recipient": recipient,
        "status": "sent",
    }