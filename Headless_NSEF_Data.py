import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
import smtplib
import random
import sys
import json
import datetime
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date
import requests
import time
from selenium.webdriver import FirefoxOptions
import pandas as pd
import gspread
import pandas as pd
from gspread_dataframe import get_as_dataframe, set_with_dataframe

bot_token = '6205352350:AAHBWNZMahHftYhdyn3nqOGj1UHCP4RlBN4'
bot_chatID = '-1001805182915'

url = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&text=NSE_FII script "started" @13.126.78.253- /var/www/scrapping/Headless_NSEF_Data.py '
res = requests.get(url)

def update_fii_gsheet(service_account,sheet_title,worksheet_name):
    df = pd.read_json("FII_data.json")
    # df=df.iloc[0].values
    #print(df)

    gc = gspread.service_account(filename=service_account)
    doc = gc.open(sheet_title)
    worksheet = doc.worksheet(worksheet_name)
    existing_data = get_as_dataframe(worksheet)
    
# Append the new data (df) to the existing data
    combined_data = pd.concat([df, existing_data], ignore_index=True)

# Clear the existing worksheet
    worksheet.clear()

    worksheet.resize(rows=combined_data.shape[0], cols=combined_data.shape[1])
    set_with_dataframe(worksheet, combined_data, include_index=False)

url = 'http://13.126.78.253/sofr/nse_data_email_ids.json'

def get_first_value_from_json(url):
    response = requests.get(url)
    data = json.loads(response.text)
    email_id = next(iter(data.values()))  # Retrieve the first value
    return email_id

# Example usage
json_url = 'http://13.126.78.253/sofr/nse_data_email_ids.json'  # Replace with your JSON file URL
email_id = get_first_value_from_json(json_url)
#print("First value:", email_id)


todaydtformat = date.today().strftime("%d/%m/%Y")

# Open the JSON file in read mode
with open('FII_data.json', 'r') as f:
    # Load the JSON data into a Python dictionary
    data = json.load(f)

# Extract the date information from the dictionary
date_str = data[0]['Date']

#print(date_str)
# Convert the date string to a datetime object
# date_conv = datetime.datetime.strptime(date_str, '%d/%m/%Y').date()

# Get the current date
current_date = datetime.date.today()

# Format the date in the desired format
formatted_date = current_date.strftime("%d-%b-%Y")
# date_conv="07/09/2023"
# Compare the json file date with the current date
if date_str == formatted_date:
    #print("Date mached, skipping script...")
    sys.exit()
else:
    #print("Executing script...")
    wait=random.randint(20,40)

    # This is for setting firefox for Headless
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    with webdriver.Firefox(
        options=opts
    ) as browser:
    #print("Executing script...")
        browser.get("https://www.moneycontrol.com/stocks/marketstats/fii_dii_activity/index.php")
        time.sleep(10)

        table_element = WebDriverWait(browser, wait).until(
        EC.presence_of_element_located((By.XPATH,('//*[@id="fidicash"]/div/div')))
        )

        time.sleep(10)

        # Find all the rows in the table
        rows = table_element.find_elements(By.TAG_NAME, 'tr')

        # Extract data from the first row (skip the header row if necessary)
        first_row_data = []
        for cell in rows[0].find_elements(By.XPATH, '//*[@id="fidicash"]/div/div/table/tbody/tr[1]'):
            first_row_data.append(cell.text)

        # Now 'first_row_data' contains the data from the first row of the table
        # print(first_row_data)
        browser.close()
        data=[]
        data_fii=[]
        data_dii=[]
        for data_str in first_row_data:
            data_parts = data_str.split()  # Split the string by whitespace

            # Extract data and format as needed
            date_str = (data_parts[0].replace('""',''))
            buy_value = (data_parts[1].replace('""',''))
            sell_value = (data_parts[2].replace('""',''))
            net_value = (data_parts[3].replace('""',''))
            buy_value_dii = (data_parts[4].replace('""',''))
            sell_value_dii = (data_parts[5].replace('""',''))
            net_value_dii = (data_parts[6].replace('""',''))
        

            #appending fii and dii in data is only for  
            data.append( {
                "Category": "FII/FPI**",
                "Date": date_str,
                "Buy Value": buy_value,
                "Sell Value": sell_value,
                "Net Value": net_value,
            }
            )
            
            data.append(
            {
            "Category": "DII**",
            "Date": date_str,
            "Buy Value": buy_value_dii,
            "Sell Value": sell_value_dii,
            "Net Value": net_value_dii,

            }
            )

            # appending in data_fii is for updating fii data in gsehet
            data_fii.append( {
                "Category": "FII/FPI",
                "Date": date_str,
                "Buy Value": buy_value,
                "Sell Value": sell_value,
                "Net Value": net_value,
            }
            )

            # appending in data_iii is for updating dii data in gsehet
            data_dii.append(
                {
                "Category": "DII**",
                "Date": date_str,
                "Buy Value": buy_value_dii,
                "Sell Value": sell_value_dii,
                "Net Value": net_value_dii              
                }
            )

            
        with open('FII_data.json', 'w') as file:
            json.dump(data_fii, file)

        with open('DII_data.json', 'w') as file:
            json.dump(data_dii, file)

        # Print the JSON
        # print(json_data)


        html_body = ''
        if len(data) >=2:
            html_body = '''<html>
            <body>
            <table border=1 cellpadding=2 cellspacing=2>
            <thead>
            <td>Category</td>
            <td>Date</td>
            <td>Buy Value </td>
            <td>Sell Value </td>
            <td>Net Value </td>
            </thead>
            <tr>
                <td>{0}</td>
                <td>{1}</td>
                <td>{2}</td>
                <td>{3}</td>
                <td>{4}</td>
            </tr>
            <tr>
                <td>{5}</td>
                <td>{6}</td>
                <td>{7}</td>
                <td>{8}</td>
                <td>{9}</td>
            </tr>
            </table>
            </body>
            </html>'''.format(data[0]['Category'],data[0]['Date'],data[0]['Buy Value'],data[0]['Sell Value'],data[0]['Net Value'],data[1]['Category'],data[1]['Date'],data[1]['Buy Value'],data[1]['Sell Value'],data[1]['Net Value'])

        # print(html_body)
email_id=' ' # Enter mail whom you want send mail      
# message to be sent
message = html_body
subject = "NSE_Data"
to_addr = email_id
from_addr = " " # Enter your mail id

message = MIMEMultipart('alternative')
message['subject'] = subject
message['To'] = to_addr
message['From'] = from_addr

html_body = MIMEText(html_body, 'html')
message.attach(html_body)

# terminating the session
s = smtplib.SMTP('smtp.gmail.com', 587)

# start TLS for security
s.starttls()
s.login("ankush@greenbackforex.com", " ") # Enter passkey
to_arr2 = to_addr.split(",")
s.sendmail(from_addr, to_arr2, message.as_string())

s.quit()

#print("Mail has deleverd!")

bot_token = '6205352350:AAHBWNZMahHftYhdyn3nqOGj1UHCP4RlBN4'
bot_chatID = '-1001805182915'

url = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&text=NSE_FII script run "completed" successfully @github ankush account '
res = requests.get(url)



# close the driver
# browser.quit()
service_account_file = "gb.json"
sheet_title = "DCM IMAGE EXCEL"
worksheet_name = "FII Rs. Crs."
update_fii_gsheet(service_account_file, sheet_title, worksheet_name)



def update_dii_gsheet(service_account,sheet_title,worksheet_name):
    df = pd.read_json("DII_data.json")
    # df=df.iloc[0].values
    #print(df)

    gc = gspread.service_account(filename=service_account)
    doc = gc.open(sheet_title)
    worksheet = doc.worksheet(worksheet_name)
    exi_data = get_as_dataframe(worksheet)
    
# Append the new data (df) to the existing data
    both_data = pd.concat([df, exi_data], ignore_index=True)

# Clear the existing worksheet
    worksheet.clear()

    worksheet.resize(rows=both_data.shape[0], cols=both_data.shape[1])
    set_with_dataframe(worksheet, both_data, include_index=False)

service_account_file = "gb.json"
sheet_title = "DCM IMAGE EXCEL"
worksheet_name = "DII Rs. Crs."
update_dii_gsheet(service_account_file, sheet_title, worksheet_name)



url = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&text=NSE_FII script  "ended" @13.126.78.253- /var/www/scrapping/Headless_NSEF_Data.py '
res = requests.get(url)

# Authenticate using the JSON key file

#print("Data has been written to Google Sheets.")