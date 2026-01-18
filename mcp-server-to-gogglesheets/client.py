import asyncio
from dotenv import load_dotenv
from typing import Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json
from mcp.types import TextContent

#GOOGLE Sheets SETUP
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'creds.json'
SPREADSHEET_ID = '1lMDc0azA2zJ2dWShWxJ49cqAXw8zsZsw6bAJvW56Veg'

load_dotenv()

class MCPToGoogleSheets:
    def __init__(self, spreadsheet_id):
        #Initialize Google Sheets client
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        self.gc = gspread.authorize(creds)
        self.spreadsheet = self.gc.open_by_key(spreadsheet_id)

    async def fetch_and_write_accounts(self, search_name: str) -> int:
        server_params = StdioServerParameters(
            command="python3",
            args=["/Users/luisescalante/Desktop/my-new-mcp-server/main.py"],
            env=None
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Call the search accounts tool (INSIDE the session context)
                result = await session.call_tool("search_accounts", arguments={"name": search_name})

                if not result.content:
                    print("No content returned from MCP server.")
                    return 0

                content_item = result.content[0]

                if not isinstance(content_item, TextContent):
                    print(f"Unexpected content format: {type(content_item)}")
                    return 0

                # Parse the result
                data = json.loads(content_item.text)
                accounts = data.get('accounts', [])

        # Get or Create worksheet
        try:
            worksheet = self.spreadsheet.worksheet("Accounts for United")
        except gspread.exceptions.WorksheetNotFound:
            worksheet = self.spreadsheet.add_worksheet(title="Accounts for United", rows=100, cols=5)

        # Headers
        headers = ["Account ID", "Name", "BillingAddress", "Type", "Industry"]
        worksheet.update([headers], 'A1:E1')

        # Data rows
        rows = []
        for account in accounts:
            billing_address = account.get("BillingAddress")
            if billing_address and isinstance(billing_address, dict):
                address_parts = []
                if billing_address.get("street"):
                    address_parts.append(billing_address["street"])
                if billing_address.get("city"):
                    address_parts.append(billing_address["city"])
                if billing_address.get("state"):
                    address_parts.append(billing_address["state"])
                if billing_address.get("postalCode"):
                    address_parts.append(billing_address["postalCode"])
                if billing_address.get("country"):
                    address_parts.append(billing_address["country"])
                billing_address = ", ".join(address_parts)
            else:
                billing_address = ""

            rows.append([
                account.get("Id", ""),
                account.get("Name", ""),
                billing_address,
                account.get("Type", ""),
                account.get("Industry", "")
            ])

        if rows:
            worksheet.update(rows, f'A2:E{len(rows)+1}')
            
        print(f"Written {len(rows)} accounts to Google Sheets.")
        return len(rows)
        
# Usage
async def main():
    client = MCPToGoogleSheets(SPREADSHEET_ID)

    await client.fetch_and_write_accounts("United")

if __name__ == "__main__":
    asyncio.run(main())