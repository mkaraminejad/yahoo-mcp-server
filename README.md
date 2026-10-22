# Yahoo Mail MCP Server

**Connect an MCP-compatible AI assistant to Yahoo Mail with Python.**

A hands-on BE-DevOps project that exposes Yahoo Mail operations through the **Model Context Protocol (MCP)**. Fetch unread email headers, search your inbox, send plain-text messages, and delete messages by UID using separate personal and business account configurations.

This project uses IMAP for inbox operations and SMTP over SSL for sending mail. It is intended for local learning and experimentation.

## Features

- Fetch the newest unread email headers without marking messages as read.
- Search inbox messages by sender, subject, or both.
- Send plain-text emails.
- Delete inbox messages by UID.
- Select a `personal` or `business` Yahoo account for each tool call.
- Load credentials from environment variables or a local `.env` file.

**Current scope:** email bodies and attachments are not returned by the tools. Body-content search is not implemented, even though a `body` parameter appears in the search function signatures.

## Project files

| File | Purpose |
| --- | --- |
| `server.py` | Registers the four MCP tools and starts the server. |
| `read_email.py` | Loads account credentials, lists unread messages, and searches inbox headers. |
| `mail_send.py` | Sends plain-text email through Yahoo SMTP. |
| `mail_delete.py` | Deletes messages by IMAP UID. |
| `main.py` | Placeholder script; this does not start the MCP server. |
| `pyproject.toml` | Project metadata and dependency declarations. |
| `.python-version` | Selects Python 3.14. |
| `.gitignore` | Excludes virtual environments and Python-generated files. |

## Requirements

- Python **3.14 or newer**, as required by this project's `pyproject.toml`.
- [uv](https://docs.astral.sh/uv/) for dependency and environment management.
- A Yahoo Mail account and a Yahoo **app password** for each configured account.
- An MCP client that supports local stdio servers.
- Network access to Yahoo IMAP and SMTP.

The source imports `MCPServer` from `mcp.server`, which follows the official **MCP Python SDK v2** API. The installation below selects that major version. Older v1 tutorials use `FastMCP` and are not a direct match for these files.

## Required preparation

### Exclude credentials from Git

Add these entries to `.gitignore` before creating your credentials file:

```gitignore
# Local credentials
.env
.env.*
!.env.example
```

The supplied `.gitignore` does not yet exclude `.env`. If credentials were already committed, ignoring the file will not remove them from Git history: revoke the exposed app passwords and remove the tracked secrets.

## Installation

Download or clone this repository, then open a terminal in the directory containing `server.py` and `pyproject.toml`.

```bash
uv python install 3.14
uv add "mcp[cli]>=2,<3" imap-tools python-dotenv
```

The supplied project declares `dependencies = []`. The `uv add` command records the required packages in `pyproject.toml`, creates or updates the environment, and generates a lockfile. Commit the updated `pyproject.toml` and `uv.lock` so other users can reproduce the dependency resolution.

After those files are committed, subsequent installations can use:

```bash
uv sync --locked
```

## Configure Yahoo accounts

Generate an app password from your [Yahoo Account Security](https://login.yahoo.com/account/security) settings. Use that app password rather than your normal Yahoo account password. See [Yahoo's app-password instructions](https://help.yahoo.com/kb/SLN15241.html).

Create a file named `.env` beside `server.py`:

```dotenv
YAHOO_PERSONAL_EMAIL=your-personal-address@yahoo.com
YAHOO_PERSONAL_APP_PASSWORD=replace-with-your-personal-app-password

YAHOO_BS_EMAIL=your-business-address@yahoo.com
YAHOO_BS_APP_PASSWORD=replace-with-your-business-app-password
```

Only configure the account pairs you plan to use. `business` is a local account alias; it does not require a different Yahoo subscription. The `YAHOO_BS_*` spelling is intentional and matches the source code.

| Tool account name | Email variable | Password variable |
| --- | --- | --- |
| `personal` | `YAHOO_PERSONAL_EMAIL` | `YAHOO_PERSONAL_APP_PASSWORD` |
| `business` | `YAHOO_BS_EMAIL` | `YAHOO_BS_APP_PASSWORD` |

Use the account names exactly as shown, in lowercase. The current implementation does not validate missing credentials or unknown account names before connecting.

## Start the server

After completing the preparation and configuration steps:

```bash
uv run server.py
```

The server uses **stdio** by default. It waits for an MCP client to communicate over standard input and output; it does not provide a web page or a REST endpoint. A quiet terminal is therefore expected. Stop a manually launched process with `Ctrl+C`.

To inspect and call tools interactively:

```bash
uv run mcp dev server.py
```

The development Inspector requires Node.js with `npx` available. Start with `fetch_emails`; sending and deleting perform real mailbox operations.

## Connect an MCP client

For a client that uses an `mcpServers` configuration, use the following example. Replace the paths with your own absolute paths:

```json
{
  "mcpServers": {
    "yahoo-mail": {
      "command": "/absolute/path/to/uv",
      "args": [
        "--directory",
        "/absolute/path/to/yahoo-mcp-server",
        "run",
        "server.py"
      ]
    }
  }
}
```

This configuration lets the client launch the server itself. The `--directory` option sets the project working directory. Clients with different configuration formats need the same executable and arguments expressed in their own format.

On Windows, locate `uv` with `where.exe uv` and use paths such as `C:/Users/YourName/.local/bin/uv.exe` and `C:/Projects/yahoo-mcp-server`. On macOS or Linux, locate it with `command -v uv`. Forward slashes in Windows JSON paths avoid backslash-escaping mistakes.

## Available tools

| Tool | Parameters | Behavior |
| --- | --- | --- |
| `fetch_emails` | `account_name`, `limit=10` | Returns unread INBOX headers, newest first, without marking messages as read. |
| `search_emails` | `account_name`, `sender=""`, `subject=""`, `body=""` | Searches inbox headers using sender and/or subject; the body argument is currently ignored. |
| `send_email` | `account_name`, `recipient`, `subject`, `body` | Sends a plain-text email through Yahoo SMTP over SSL. |
| `delete_email` | `account_name`, `uid` | Deletes the specified inbox message using its IMAP UID. |

Starting the server does not delete messages automatically. The deletion tool runs only when explicitly called by an MCP client.

### Fetch unread messages

Tool: `fetch_emails`

```json
{"account_name": "personal", "limit": 5}
```

The underlying function returns rows containing UID, sender, date string, subject, and body-length calculation. Because the fetch uses `headers_only=True`, the length value should not be treated as the actual email body size. Messages remain unread.

### Search the inbox

Tool: `search_emails`

```json
{"account_name": "business", "sender": "alerts@example.com", "subject": "deployment"}
```

When both filters are supplied, **both must match**. Search includes read and unread inbox messages and returns `uid`, `from`, `subject`, `date`, and `is_read`. With no filters, it retrieves all inbox headers. There is currently no result limit or pagination for search.

### Send a message

Tool: `send_email`

```json
{
  "account_name": "personal",
  "recipient": "recipient@example.com",
  "subject": "Hello from my Yahoo MCP server",
  "body": "This is a test message sent through my Python MCP server."
}
```

This sends immediately when the tool executes. The server does not include a draft or approval step.

### Delete a message

Tool: `delete_email`

```json
{"account_name": "personal", "uid": "12345"}
```

The UID above is an example. Get the actual UID from a fetch or search in the **same account**. Treat this as destructive deletion, not a move-to-Trash feature. The tool reports completion but does not independently check whether the supplied UID existed.

## Example assistant requests

- “Show my five newest unread emails from my personal account.”
- “Search my business inbox for messages from alerts@example.com with deployment in the subject.”
- “Send a plain-text email from my personal account to recipient@example.com.”

Your client must be connected to the server and allow the requested tool. Review recipients and message content before authorizing sends, and verify the account and UID before authorizing deletion.

## Limitations and handling private data

- The `body` search argument is not forwarded by `server.py`, and `search_inbox` does not use it in its IMAP criteria.
- No full-message reading, attachments, folder selection, drafts, or move-to-Trash tool is implemented.
- Search can return a large response because it has no limit.
- Sending and deletion have no server-side confirmation mechanism.
- Input validation, friendly error handling, and retry logic are not implemented.
- This is a local prototype; do not expose it as a shared service without adding appropriate access controls.
- Email metadata returned by tools becomes available to the connected AI client. Use accounts appropriate for that client and its data-handling settings.
- Treat email text as untrusted data, and keep credentials out of prompts, logs, screenshots, and Git commits.

## Troubleshooting

| Problem | What to check |
| --- | --- |
| `ModuleNotFoundError` | Run the `uv add` installation command from this project's directory, then use `uv run`. |
| Cannot import `MCPServer` | Check the installed `mcp` version. These files target SDK v2; install the v2 dependency range shown above. |
| Yahoo authentication fails | Check the configured address and app password for the selected account. Regenerate the app password if necessary. |
| `KeyError` for an account | Use exactly `personal` or `business`. |
| Fetch returns no messages | `fetch_emails` only lists unread messages; a read-only inbox can return an empty list. |
| Body search has no effect | It is not implemented. Use sender and subject filters. |
| Client cannot launch `uv` | Use its absolute executable path and verify the project directory. |
| `main.py` only prints a greeting | Start `server.py`, which contains the MCP server. |

## References

- [Official MCP Python SDK](https://py.sdk.modelcontextprotocol.io/)
- [Running an MCP Python server](https://py.sdk.modelcontextprotocol.io/run/)
- [Yahoo app-password instructions](https://help.yahoo.com/kb/SLN15241.html)
- [imap-tools](https://github.com/ikvk/imap_tools)
- [uv documentation](https://docs.astral.sh/uv/)

## About

Created for **BE-DevOps** to explore Python, email automation, and MCP through a practical project.

## License

No license file was included in the supplied project. Add a `LICENSE` file with your chosen terms before presenting this repository as licensed open-source software.
