import os
import csv
import json
from datetime import datetime
from tkinter import Tk, Label, Button, filedialog, messagebox
from tkinter.ttk import Frame
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import httplib2

class IndexingApp(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.parent.title("Google Indexing API GUI")
        self.pack(fill="both", expand=True)

        # Labels and Buttons
        self.json_label = Label(self, text="No JSON Key File Selected")
        self.json_label.pack(pady=5)
        self.json_button = Button(self, text="Select JSON Key File", command=self.select_json_file)
        self.json_button.pack(pady=5)

        self.csv_label = Label(self, text="No CSV File Selected")
        self.csv_label.pack(pady=5)
        self.csv_button = Button(self, text="Select CSV File", command=self.select_csv_file)
        self.csv_button.pack(pady=5)

        self.run_button = Button(self, text="Run Indexing", command=self.run_indexing)
        self.run_button.pack(pady=20)

        self.json_file = None
        self.csv_file = None

    def select_json_file(self):
        self.json_file = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if self.json_file:
            self.json_label.config(text=os.path.basename(self.json_file))

    def select_csv_file(self):
        self.csv_file = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if self.csv_file:
            self.csv_label.config(text=os.path.basename(self.csv_file))

    def run_indexing(self):
        if not self.json_file or not self.csv_file:
            messagebox.showerror("Error", "Please select both a JSON key file and a CSV file.")
            return

        # Run the indexing process
        try:
            self.index_urls()
            messagebox.showinfo("Success", "Indexing process completed.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def index_urls(self):
        # Create logs directory and timestamped folder
        MAIN_LOGS_DIR = 'logs'
        os.makedirs(MAIN_LOGS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        folder_name = f'indexing_logs_{timestamp}'
        timestamped_folder = os.path.join(MAIN_LOGS_DIR, folder_name)
        os.makedirs(timestamped_folder, exist_ok=True)

        # Define log file paths
        LOG_FILE_UPDATED = os.path.join(timestamped_folder, 'updated.csv')
        LOG_FILE_OTHER = os.path.join(timestamped_folder, 'failed.csv')

        # Initialize log files with headers
        with open(LOG_FILE_UPDATED, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['url', 'latest_update_url', 'latest_update_type', 'notify_time'])

        with open(LOG_FILE_OTHER, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['url', 'error_code', 'error_status', 'error_message'])

        SCOPES = ["https://www.googleapis.com/auth/indexing"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.json_file, scopes=SCOPES)
        http = credentials.authorize(httplib2.Http())

        def indexURL(urls):
            ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
            
            for u in urls:
                content = {'url': u.strip(), 'type': "URL_UPDATED"}
                json_ctn = json.dumps(content)
            
                try:
                    response, raw_content = http.request(ENDPOINT, method="POST", body=json_ctn)
                    result = json.loads(raw_content.decode('utf-8'))
                except httplib2.HttpLib2Error as e:
                    with open(LOG_FILE_OTHER, mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow([content['url'], 'HttpLib2Error', '', str(e)])
                    continue
                except json.JSONDecodeError as e:
                    with open(LOG_FILE_OTHER, mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow([content['url'], 'JSONDecodeError', '', str(e)])
                    continue

                if "error" in result:
                    error_code = result['error'].get('code', '')
                    error_status = result['error'].get('status', '')
                    error_message = result['error'].get('message', '')
                    with open(LOG_FILE_OTHER, mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow([content['url'], error_code, error_status, error_message])
                else:
                    latest_update_url = result['urlNotificationMetadata']['latestUpdate'].get('url', '')
                    latest_update_type = result['urlNotificationMetadata']['latestUpdate'].get('type', '')
                    notify_time = result['urlNotificationMetadata']['latestUpdate'].get('notifyTime', '')

                    with open(LOG_FILE_UPDATED, mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow([content['url'], latest_update_url, latest_update_type, notify_time])

        # Read URLs from CSV and process them
        csv_data = pd.read_csv(self.csv_file)
        if "URL" in csv_data.columns:
            indexURL(csv_data["URL"].tolist())
        else:
            raise ValueError("The selected CSV file does not contain a 'URL' column.")

def main():
    root = Tk()
    app = IndexingApp(root)
    root.geometry("400x200")
    root.mainloop()

if __name__ == "__main__":
    main()
