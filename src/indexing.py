import os
import csv
import json
from datetime import datetime
from tkinter import Tk, Label, Button, filedialog, messagebox, Toplevel, Text, Scrollbar, Menu, Frame
import webbrowser
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
from ttkbootstrap import Style, Button  # Import Button from ttkbootstrap

class IndexingApp(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.parent.title("Google Indexing API GUI")
        self.pack(fill="both", expand=True)

        # Create a style
        style = Style(theme='flatly')  # Choose a friendly theme

        # Create a menu bar
        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)

        # Create an Info menu
        info_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=info_menu)
        info_menu.add_command(label="About", command=self.show_info)
        info_menu.add_command(label="More Information", command=self.open_info_url)

        # Initialize the main UI
        self.initMainUI()

    def initMainUI(self):
        # Labels and Buttons for file selection and indexing
        self.json_label = Label(self, text="No JSON Key File Selected", font=("Helvetica", 12), bg="#34495E", fg="white")
        self.json_label.pack(pady=10)
        
        # Use ttkbootstrap Button for better styling
        self.json_button = Button(self, text="Select JSON Key File", command=self.select_json_file, style='primary.TButton')
        self.json_button.pack(pady=5)

        self.csv_label = Label(self, text="No CSV File Selected", font=("Helvetica", 12), bg="#34495E", fg="white")
        self.csv_label.pack(pady=10)
        
        # Use ttkbootstrap Button for better styling
        self.csv_button = Button(self, text="Select CSV File", command=self.select_csv_file, style='primary.TButton')
        self.csv_button.pack(pady=5)

        # Use ttkbootstrap Button for better styling
        self.run_button = Button(self, text="Run Indexing", command=self.run_indexing, style='success.TButton')
        self.run_button.pack(pady=20)

        self.json_file = None
        self.csv_file = None
        
    def open_info_url(self):
        webbrowser.open("https://github.com/koutsosg/google-indexAPI-python/releases")  # Replace with your actual URL

    def show_info(self):
        info_window = Toplevel(self.parent)
        info_window.title("About This Application")

        info_text = (
            "This application allows you to use the Google Indexing API.\n\n"
            "Instructions:\n"
            "1. Select your JSON key file for authentication.\n"
            "2. Select a CSV file containing URLs to be indexed (must have 'URL' column).\n"
            "3. Click 'Run Indexing' to start the process.\n\n"
            "For more information, visit: "
            "https://github.com/koutsosg/google-indexAPI-python/releases"  # Replace with your actual URL
        )

        label = Label(info_window, text="Information", font=("Helvetica", 16))
        label.pack(pady=10)

        text_area = Text(info_window, wrap='word', width=50, height=15)
        text_area.insert('1.0', info_text)
        text_area.config(state='disabled')  # Make text read-only
        text_area.pack(pady=5)
    



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
    root.geometry("400x300")
    root.mainloop()

if __name__ == "__main__":
    main()
