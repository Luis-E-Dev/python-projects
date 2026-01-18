# How to use MCP server

This MCP (Model Context Protocol) client connects to an MCP server to fetch account data and writes it to Google Sheets.

## Prerequisites

- Python 3.10 or higher
- A Google Cloud project with Google Sheets API enabled
- A Google Service Account with credentials
- An MCP server running (with a `search_accounts` tool)

## Setup

### 1. Install Dependencies

Install the required Python packages:

```bash
pip install mcp python-dotenv gspread google-auth
```

### 2. Google Sheets API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API
4. Create a Service Account:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Give it a name and click "Create"
   - Grant it the "Editor" role (or appropriate permissions)
   - Click "Done"
5. Create credentials:
   - Click on the service account you just created
   - Go to the "Keys" tab
   - Click "Add Key" > "Create New Key"
   - Choose JSON format
   - Save the file as `creds.json` in this project directory

### 3. Configure Google Sheets

1. Create a new Google Sheet or use an existing one
2. Copy the Spreadsheet ID from the URL (the long string between `/d/` and `/edit`)
   - Example: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
3. Share the Google Sheet with the service account email (found in `creds.json`)
   - Give it "Editor" permissions

### 4. Update Configuration

Edit `client.py` and update the following variables:

- `SPREADSHEET_ID`: Your Google Sheets ID
- `CREDENTIALS_FILE`: Path to your credentials file (default: `creds.json`)
- MCP server path in `server_params` (line 26): Update the path to your MCP server

```python
server_params = StdioServerParameters(
    command="python3",
    args=["/path/to/your/mcp-server/main.py"],
    env=None
)
```

## Usage

### Basic Usage

Run the client to fetch accounts and write to Google Sheets:

```bash
python client.py
```

By default, this searches for accounts with the name "United" and writes the results to a worksheet called "Accounts for United".

### Customizing the Search

To search for different accounts, modify the `main()` function in `client.py`:

```python
async def main():
    client = MCPToGoogleSheets(SPREADSHEET_ID)
    await client.fetch_and_write_accounts("Your Search Term")
```

## What It Does

1. **Connects to MCP Server**: Establishes a connection to your MCP server via stdio
2. **Searches Accounts**: Calls the `search_accounts` tool with the provided name
3. **Processes Results**: Parses the account data including:
   - Account ID
   - Name
   - Billing Address
   - Type
   - Industry
4. **Writes to Google Sheets**: Creates or updates a worksheet with the fetched data

## Troubleshooting

### Permission Denied Errors
- Ensure the Google Sheet is shared with your service account email
- Verify your service account has the correct permissions

### MCP Server Connection Issues
- Check that the MCP server path is correct
- Ensure the MCP server is executable and has the `search_accounts` tool

### Credentials Not Found
- Verify `creds.json` exists in the project directory
- Ensure the file is valid JSON with proper service account credentials

## Output Format

The script creates a worksheet with the following columns:

| Account ID | Name | BillingAddress | Type | Industry |
|------------|------|----------------|------|----------|
| ...        | ...  | ...            | ...  | ...      |
