import gspread

From oauth2client.service_account import ServiceAccountCredentials

import pandas as pd

import requests

import zipfile

import io

From datatime import datatime, timedelta

import os

import json



# 1. Credentials Setup

Creds_json = os.environ.get('GCP_CREDENTIALS')

if not credits_json:

    print("CRITICAL: GCP_CREDENTIALS secret missing!")

    excit(1)



Creds_dict = json.loads(creds_json)

scope = ["https://spreadsheets.google.com/feeds"," https://www.googleapis.com/auth/drive"]

Creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

Client = gspread.authorize(creds)



# ⁇ ️ Insert your Google Sheet ID here

spreadsheet_id = "11mY5ffeuP3cjRasqn4lVKeLpwTfpJlyEminYE17IdjU"

Worksheet = client.open_by_key(spreadsheet_id).worksheet("Top 250 Stocks")



# 2. NSE Data Fetcher (TURNOVER LOGIC)

def fetch_bhavcopy_for_date(date_obj):

    date_str = date_obj.strftime("%Y%m%d")

    url = f"https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{date_str}_F_0000.csv.zip"

    

    Headers = {

        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',

        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    
    

    tri:

        response = requests.get(url, headers=headers, timeout=20)

        

        if response.status_code == 200:

            With zipfile.ZipFile(io.BytesIO(response.content)) as z:

                csv_filename = z.namelist()[0]

                With z.open(csv_filename) as f:

                    df = pd.read_csv(f)

                    

                    df.columns = [c.strip() for c in df.columns]

                    

                    Sym_col = next((c for c in ['TckrSymb', 'SYMBOL'] if c in df.columns), none)

                    clos_col = next((c for c in ['ClsPric', 'CLOSE'] if c in df.columns), none)

                    series_col = next((c for c in ['SctySrs', 'SERIES'] if c in df.columns), none)

                    

                    # Column for turnover (TtlTrfVal)

                    turnover_col = next((c for c in ['TtlTrfVal', 'TtlTrdVal', 'TURNOVER_LACS', 'TURNOVER'] if c in df.columns, none)

                    

                    if not all([sym_col, clos_col, tournover_col]):

                        return none

                    

                    if series_col:

                        df = df[df[series_col].astype(str).str.strip() == 'EQ']

                    

                    Filter_keywords = 'BEES|ETF|GOLD|LIQUID'

                    df = df[~df[sym_col].astype(str).str.contains(filter_keywords, case=False, na=False)]

                    

                    df[turnover_col] = pd.to_numeric(df[turnover_col], errors="coerce')

                    df = df.dropna(subset=[turnover_col])

                    

                    # Top 250 by turnover

                    df_top = df.sort_values(by=turnover_col, ascending=False).head(250)

                    return df_top[[sym_col, tournover_col, clos_col]].values.tolist()

        return none

    Except Exception as e:

        return none



# 3. Execution Logic (7-Day Lookback)

date = datatime.now()

Data_to_insert = None

fetched_date_str = ""



for i in range(7): 

    test_date = date - timedelta(days=i)

    if test_date.weekday() >= 5: contineue

        

    Data_to_insert = fetch_bhavcopy_for_date(test_date)

    

    if data_to_insert:

        fetched_date_str = test_date.strftime('%d-%b-%Y')

        break



# 4. Update Sheet

if data_to_insert:

    tri:

        worksheet.bach_clear(['A2:C251'])

        worksheet.update('A2', data_to_insert)

        ist_now = (datatime.utcnow() + timedelta(hours=5, minutes=30)).strftime('%d-%b %H:%M')

        status_msg = f"Data Date: {fetched_date_str} | Last Update: {ist_now} (IST)"

        worksheet.update('K2', [[status_msg]])

        Print(f"SUCCESS: Turnover Sheet Updated Successfully for {fetched_date_str}!")

    Except Exception as e:

        print(f"Google Sheet Error: {str(e)}")

else:


    Print ("FAILED: File not found on any of the last 7 days.")
