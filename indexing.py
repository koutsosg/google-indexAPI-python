from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import json
import pandas as pd
import csv
import os
from datetime import datetime

# Define main logs directory
MAIN_LOGS_DIR = 'logs'

# Ensure the main logs directory exists
os.makedirs(MAIN_LOGS_DIR, exist_ok=True)

# Generate a timestamped subfolder inside the main logs directory
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
folder_name = f'indexing_logs_{timestamp}'
timestamped_folder = os.path.join(MAIN_LOGS_DIR, folder_name)

# Create the timestamped subfolder
os.makedirs(timestamped_folder, exist_ok=True)

# Generate timestamped filenames for log files inside the timestamped folder
LOG_FILE_UPDATED = os.path.join(timestamped_folder, f'updated.csv')
LOG_FILE_OTHER = os.path.join(timestamped_folder, f'failed.csv')

# Initialize CSV files with headers
with open(LOG_FILE_UPDATED, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['url', 'latest_update_url', 'latest_update_type', 'notify_time'])

with open(LOG_FILE_OTHER, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['url', 'error_code', 'error_status', 'error_message'])

JSON_KEY_FILE = "apidetails.json"
SCOPES = ["https://www.googleapis.com/auth/indexing"]

credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEY_FILE, scopes=SCOPES)
http = credentials.authorize(httplib2.Http())

def indexURL(urls, http):
    ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
    
    for u in urls:
        content = {'url': u.strip(), 'type': "URL_UPDATED"}
        json_ctn = json.dumps(content)
    
        response, raw_content = http.request(ENDPOINT, method="POST", body=json_ctn)
        
        try:
            result = json.loads(raw_content.decode('utf-8'))
        except json.JSONDecodeError as e:
            # Log error if JSON decoding fails
            with open(LOG_FILE_OTHER, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([content['url'], 'JSONDecodeError', '', str(e)])
            continue

        if "error" in result:
            error_code = result['error'].get('code', '')
            error_status = result['error'].get('status', '')
            error_message = result['error'].get('message', '')
            # Log errors in the 'other' log file
            with open(LOG_FILE_OTHER, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([content['url'], error_code, error_status, error_message])
        else:
            # Log URL_UPDATED details in the 'updated' log file
            latest_update_url = result['urlNotificationMetadata']['latestUpdate'].get('url', '')
            latest_update_type = result['urlNotificationMetadata']['latestUpdate'].get('type', '')
            notify_time = result['urlNotificationMetadata']['latestUpdate'].get('notifyTime', '')

            with open(LOG_FILE_UPDATED, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([content['url'], latest_update_url, latest_update_type, notify_time])

# Read URLs from CSV and process them
csv_data = pd.read_csv("my_data.csv")
for url in csv_data["URL"]:
    indexURL([url], http)