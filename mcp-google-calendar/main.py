"""
Salesforce Basic MCP Server to fetch Salesforce data
"""
import os
from pathlib import Path
from turtle import title
from mcp.server.fastmcp import FastMCP
from simple_salesforce.api import Salesforce
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.absolute()

#Load environment variables from .env file
load_dotenv(SCRIPT_DIR / ".env")

#Initialize MCP server
mcp = FastMCP("salesforce-basic")

def get_salesforce_connection():
    return Salesforce(username=os.getenv("SF_USERNAME"),
                      password=os.getenv("SF_PASSWORD"),
                      security_token=os.getenv("SF_SECURITY_TOKEN"),
                      domain=os.getenv("SF_DOMAIN", "login")
    )

def get_calendar_service():
    SCOPES = ['https://www.googleapis.com/auth/calendar']

    creds_file = os.getenv("GOOGLE_CALENDAR_CREDENTIALS", "calendar_credentials.json")
    # Make path absolute if it's relative
    if not os.path.isabs(creds_file):
        creds_file = str(SCRIPT_DIR / creds_file)

    try:
        creds = service_account.Credentials.from_service_account_file(creds_file, scopes=SCOPES)

        delegated_email = os.getenv("GOOGLE_CALENDAR_USER_EMAIL")
        if delegated_email:
            creds = creds.with_subject(delegated_email)

        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"Error creating Google Calendar service: {e}")
        return None

#Tool 1: Get Accounts
@mcp.tool()
def get_account(account_id: str) -> dict:
    sf = get_salesforce_connection()
    try:
        account = sf.Account.get(account_id)
        return {
            "success": True,
            "account": account
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

#Tool 2: Search Accts by Name
@mcp.tool()
def search_accounts(name: str) -> dict:
    sf = get_salesforce_connection()
    try:
        query = f"SELECT Id, Name, BillingAddress, Phone, Type, Industry FROM Account WHERE Name LIKE '%{name}%' LIMIT 10"
        result = sf.query(query)
        return {
            "success": True,
            "accounts": result['records'],
            "count": result['totalSize']
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

#Tool 3: Get recent Opportunities
@mcp.tool()
def get_recent_opportunities(limit: int = 5) -> dict:
    sf = get_salesforce_connection()
    try:
        query = f"SELECT Id, Name, StageName, Amount, CloseDate FROM Opportunity ORDER BY CreatedDate DESC LIMIT {limit}"
        result = sf.query(query)
        return {
            "success": True,
            "count": result["totalSize"],
            "opportunities": result['records']
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    
#Tool 4: Get Closed Won Opportunities
@mcp.tool()
def get_closed_won_opportunities(limit: int = 5) -> dict:
    sf = get_salesforce_connection()
    try:
        query = f"SELECT Id, Name, StageName, Amount, CloseDate FROM Opportunity WHERE StageName = 'Closed Won' ORDER BY Name ASC LIMIT {limit}"
        result = sf.query(query)
        return {
            "success": True,
            "count": result["totalSize"],
            "opportunities": result['records']
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# =========================================================
# GOOGLE CALENDAR INTEGRATION
# =========================================================

#Tool 5: Schedule follow ups for Salesforce Account in Gmail
@mcp.tool()
def schedule_accounts_follow_ups(account_id: str, 
                                 days_from_now: int = 7, 
                                 duration_min: int = 30,
                                 event_hour: int = 8,
                                 event_minute: int = 0, 
                                 title: str = 'None') -> dict:
    sf = get_salesforce_connection()
    calendar_service = get_calendar_service()

    if not calendar_service:
        return {
            "success": False,
            "error": "Failed to create Google Calendar service. Check credentials."
        }
    try:
        # Get SF Accounts
        acc = sf.Account.get(account_id)
        account_name = acc.get("Name", "Unknown Account")

        # Get SF Opp
        opp_query = f"SELECT Id, Name, CloseDate, Amount, StageName FROM Opportunity WHERE AccountId = '{account_id}' AND IsClosed = false LIMIT 5"
        opps = sf.query(opp_query)

        # Build events
        event_title = title or f"Follow up with {account_name}"
        event_description = f"Follow up with account: {account_name}\n\nOpen Opportunities"

        tz = pytz.timezone('America/Phoenix')
        start_time = datetime.now(tz) + timedelta(days=days_from_now)
        start_time = start_time.replace(hour=event_hour, minute=event_minute, second=0, microsecond=0)
        end_time = start_time + timedelta(minutes=duration_min)

        description = f"Follow-up meeting with {account_name}\n\n"
        description += F"Account ID: {account_id}\n\n"
        description += f"Type: {acc.get('Type', 'N/A')}\n"
        description += f"Industry: {acc.get('Industry', 'N/A')}\n"

        if acc.get('Phone'):
            description += f"Phone: {acc['Phone']}\n"

        if opps['totalSize'] > 0:
            description += "\nOpen Opportunities:\n"
            for opp in opps['records']:
                amount = opp.get('Amount', '0') or 0
                description += f" - {opp['Name']} | Amount: ${amount:,.2f} | Stage: {opp.get('StageName')}\n"

        description += "\nPlease prepare accordingly."

        event = {
            'summary': event_title,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'America/Phoenix',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'America/Phoenix',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                    {'method': 'popup', 'minutes': 10},       # 10 minutes before
                ],
            },
        }

        calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")

        created_event = calendar_service.events().insert(calendarId=calendar_id, body=event).execute()

        return {
            "success": True,
            "account": {
                "Id": account_id,
                "Name": account_name,
                "Type": acc.get("Type"),
                "Industry": acc.get("Industry")
            },
            "calendar_event": {
                "Id": created_event['id'],
                "title": event_title,
                "start": start_time.isoformat(),
                "duration": duration_min,
                "link": created_event.get('htmlLink')
            },
            "opportunities_found": opps['totalSize']
        }
    
    except HttpError as e:
        return {
            "success": False,
            "error": f"Google Calendar API error: {e}"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

#Run server
if __name__ == "__main__":
    mcp.run()
    