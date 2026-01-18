# Salesforce Basic MCP Server

A simple Model Context Protocol (MCP) server that provides AI assistants with tools to query Salesforce data.

## Features

- ✅ Get Account by ID
- ✅ Search Accounts by name
- ✅ Get recent Opportunities
- ✅ Schedule events in Google Calendar

## Setup

### 1. Install Dependencies

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install. sh | sh

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # Mac/Linux
# OR
. venv\Scripts\activate     # Windows

# Install dependencies
uv add "mcp[cli]" simple-salesforce python-dotenv
```

### 2. Configure Salesforce Credentials

Create a `.env` file in the project root: 

```env
SF_USERNAME=your@salesforce.email.com
SF_PASSWORD=yourpassword
SF_SECURITY_TOKEN=yoursecuritytoken
SF_DOMAIN=login  # or 'test' for sandbox
```

**How to get your Security Token:**
1. Log into Salesforce
2. Click your profile icon → Settings
3. On the left sidebar:  Personal → Reset My Security Token
4. Check your email for the token

### 3. Run the Server

```bash
python main.py
```

### 4. Test with MCP Inspector

```bash
npx @modelcontextprotocol/inspector python main.py
```

## Available Tools

### `get_account`
Get a Salesforce Account by ID. 

**Parameters:**
- `account_id` (string): The Salesforce Account ID

**Example:**
```json
{
  "account_id": "001XXXXXXXXXXXXXXX"
}
```

### `search_accounts`
Search for Accounts by name.

**Parameters:**
- `name` (string): The account name to search for

**Example:**
```json
{
  "name": "Acme"
}
```

### `get_recent_opportunities`
Get the most recent Opportunities.

**Parameters:**
- `limit` (integer, optional): Number to return (default: 5, max: 20)

**Example:**
```json
{
  "limit": 10
}
```

## Connect to Claude Desktop

Add to your Claude Desktop config file:

**Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config. json`

```json
{
  "mcpServers": {
    "salesforce-basic": {
      "command": "python",
      "args": ["/absolute/path/to/salesforce-mcp-basic/server.py"],
      "env": {
        "SF_USERNAME": "your@email.com",
        "SF_PASSWORD": "yourpassword",
        "SF_SECURITY_TOKEN": "yourtoken",
        "SF_DOMAIN": "login"
      }
    }
  }
}
```

## Security Notes

⚠️ **Never commit `.env` to git!**
- The `.gitignore` file is configured to exclude it
- Use environment variables in production

## Troubleshooting

### "Authentication Failed"
- Double-check username, password, and security token
- Verify your IP is not blocked in Salesforce
- For sandboxes, use `SF_DOMAIN=test`

### "Module not found"
- Make sure virtual environment is activated
- Run `uv add "mcp[cli]" simple-salesforce python-dotenv`

## Next Steps

- Add more Salesforce objects (Contacts, Cases, etc.)
- Implement create/update operations
- Add error logging
- Add data validation
