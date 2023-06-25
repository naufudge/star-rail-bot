import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SPREADSHEET_ID = "1cdqyFfc7GgK8905sWQqyADmkNpZ15nzqflPAGjfSMlw"

def timers():
    credentials = None
    if os.path.exists('hsr_timer/token.json'):
        credentials = Credentials.from_authorized_user_file('hsr_timer/token.json', SCOPES)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("hsr_timer/credentials.json", SCOPES)
            credentials = flow.run_local_server(port=0)

        with open('hsr_timer/token.json', 'w') as token:
            token.write(credentials.to_json())

    try:
        service = build('sheets', 'v4', credentials=credentials)
        sheets = service.spreadsheets()

        result1 = sheets.values().get(spreadsheetId=SPREADSHEET_ID, range="Sheet1!A2:C2").execute()
        result2 = sheets.values().get(spreadsheetId=SPREADSHEET_ID, range="Sheet1!B5:C8").execute()

        titleDesc = result1.get('values', [])
        fields = result2.get('values', [])

        # for row in fields:
        #     print(row)
        return titleDesc[0], fields

    except HttpError as error:
        print(error)


# if __name__ == '__main__':
#     one, two = main()
#     print(one)
