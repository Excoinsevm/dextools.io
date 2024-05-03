import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

class GoogleSheetDownloader:
    def __init__(self, credentials_path):
        self.credentials_path = credentials_path
        self.scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    def download_sheet(self, sheetname, worksheetname):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_path, self.scope)
        gc = gspread.authorize(credentials)
        wks_read = gc.open(sheetname).worksheet(worksheetname)
        data = wks_read.get_all_values()
        headers = data.pop(0)
        df_down_gsheet = pd.DataFrame(data, columns=headers)
        return df_down_gsheet.chain.to_list()

# Example usage
# if __name__ == "__main__":
#     gsheet_credentials_path = 'datahive-1-e22139a5c759.json'
#     sheetname = 'dex_params'
#     worksheetname = 'Sheet1'

#     downloader = GoogleSheetDownloader(gsheet_credentials_path)
#     downloaded_data = downloader.download_sheet(sheetname, worksheetname)
#     print(downloaded_data)
