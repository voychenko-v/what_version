import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials
import requests
import re
from datetime import datetime

# ============ Enter data ============
START_READ = ''
FINISH_READ = ''
START_UPDATE = ''
FINISH_UPDATE = ''
TIME_UPDATE_CELL = ''
# File get in Google Developer Console
CREDENTIALS_DICT = {}
# ID Google Sheets(take from URL)
spreadsheet_id = ''
# ====================================

PATTERN = r'Version: \d+.\d+.\d+'
UPDATE_TIME = f'Update: {datetime.now().strftime("%H:%M-%d.%m")}'

# We authorize and get service - an instance of access to the API
credentials = ServiceAccountCredentials.from_json_keyfile_dict(  # you can also read from a file
    CREDENTIALS_DICT,
    ['https://www.googleapis.com/auth/spreadsheets',
     'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)

def read_spreadsheets(start_read, finish_read, dimension='COLUMNS'):
    """
    Read a single range of data out of a spreadsheet
    :return: list -> [[value],[value],[value], ....]
    """
    values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f'{start_read}:{finish_read}',
        majorDimension=dimension,
    ).execute()
    return values['values'][0]

def write_spreadsheets(start_update, finish_update, version_values: list, value_input_option='RAW'):
    """
    Write data to a single range
    :return: None
    """
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        valueInputOption=value_input_option,
        range=f'{start_update}:{finish_update}',
        body={
        'values': version_values
    }
    ).execute()

def get_version(ip: str):
    """
    Gets a version from a page by searching for a substring in the content.
    :return: version, status code if it is not 200 or '' if argument ip False
    """
    if ip:
        try:
            ip = f'http://{ip}'
            response = requests.get(ip, verify=False, timeout=.5)
            if response.status_code == 200:
                version = re.search(PATTERN, response.text)
                return version[0].strip('Version: ') if version else 'Not found pattern'
            else:
                return response.status_code
        except Exception as err:
            print(f'Other error occurred: {err}')
            return 'Error'
    else:
        return ''


def main():

    list_ip = read_spreadsheets(START_READ, FINISH_READ)
    list_version = []
    for ip in list_ip:
        list_version.append([get_version(ip)])
    assert len(list_ip) == len(list_version)
    # the format of the entry in the table is as follows [[value],[value],[value], ....]
    write_spreadsheets(START_UPDATE, FINISH_UPDATE, list_version)
    write_spreadsheets(TIME_UPDATE_CELL, TIME_UPDATE_CELL, [[UPDATE_TIME]])

if __name__ == '__main__':
    main()