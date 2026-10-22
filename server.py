from read_email import list_emails, get_account_credentials, search_inbox
from mail_delete import delete_email_inbox
from mcp.server import MCPServer
from mail_send import send_email_outbox

mcp = MCPServer("YAHOO-MCP-SERVER")

@mcp.tool()
def fetch_emails(account_name: str, limit: int = 10):
    """Fetch a list of emails from the specified account."""
    return list_emails(account_name, limit=limit)

@mcp.tool()
def search_emails(account_name: str, sender: str = "", subject: str = "", body: str = ""):
    """Search emails in the inbox based on sender, subject, and body content."""
    return search_inbox(account_name, sender, subject)

@mcp.tool()
def delete_email(account_name: str, uid: str):
    """Delete a specific email by its UID."""
    delete_email_inbox(account_name,uid)
    return {"account_name": account_name, "uid": uid, "status": "deleted"}

@mcp.tool()
def send_email(
    account_name: str,
    recipient: str,
    subject: str,
    body: str,
) -> dict[str, str]:
    """Send an email to the specified recipient."""
    return send_email_outbox(account_name, recipient, subject, body)


if __name__ == "__main__":
    mcp.run()