import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import csv
import os
from datetime import datetime
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import queue


class JobAutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Job Listing Automation Tool")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        # Data tracking variables
        self.total_saved = 0
        self.current_page = 1
        self.current_job_index = 0
        self.total_jobs_on_page = 0
        self.is_running = False
        self.stop_requested = False

        # Current job data
        self.current_job_data = {
            'title': '',
            'name': '',
            'region': '',
            'email': '',
            'facility_type': ''
        }

        # Message queue for thread communication
        self.message_queue = queue.Queue()

        # Set modern theme
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()

        self.setup_gui()
        self.update_gui()

    def configure_styles(self):
        """Configure modern ttk styles"""
        self.style.configure('TFrame', background='#f5f6f5')
        self.style.configure('TLabel', background='#f5f6f5', font=('Segoe UI', 10))
        self.style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'))
        self.style.configure('TButton', padding=8, font=('Segoe UI', 10))

        # Custom styles for buttons
        self.style.configure('Start.TButton', background='#4CAF50', foreground='white')
        self.style.map('Start.TButton',
                       background=[('active', '#45a049')],
                       foreground=[('active', 'white')])

        self.style.configure('Stop.TButton', background='#f44336', foreground='white')
        self.style.map('Stop.TButton',
                       background=[('active', '#da190b')],
                       foreground=[('active', 'white')])

        # Custom styles for labelframes
        self.style.configure('TLabelframe', background='#f5f6f5')
        self.style.configure('TLabelframe.Label',
                             font=('Segoe UI', 11, 'bold'),
                             background='#f5f6f5',
                             foreground='#333333')

    def setup_gui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="15", style='TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

        # Header
        title_label = ttk.Label(main_frame,
                                text="Job Listing Automation Tool",
                                style='Header.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 20))

        # Control buttons frame
        control_frame = ttk.Frame(main_frame, style='TFrame')
        control_frame.grid(row=1, column=0, pady=(0, 20))

        # Start/Stop buttons
        self.start_button = ttk.Button(control_frame,
                                       text="Start Automation",
                                       command=self.start_automation,
                                       style='Start.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_button = ttk.Button(control_frame,
                                      text="Stop",
                                      command=self.stop_automation,
                                      style='Stop.TButton',
                                      state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)

        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame,
                                            orient='horizontal',
                                            mode='determinate',
                                            length=300)
        self.progress_bar.grid(row=2, column=0, pady=(0, 15), sticky=tk.EW)

        # Statistics frame
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="10")
        stats_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Statistics labels
        stats_container = ttk.Frame(stats_frame, style='TFrame')
        stats_container.grid(row=0, column=0, sticky=(tk.W, tk.E))

        self.total_saved_label = ttk.Label(stats_container,
                                           text="Total Saved: 0")
        self.total_saved_label.grid(row=0, column=0, padx=(0, 20), pady=5)

        self.current_page_label = ttk.Label(stats_container,
                                            text="Current Page: 1")
        self.current_page_label.grid(row=0, column=1, padx=(0, 20), pady=5)

        self.progress_label = ttk.Label(stats_container,
                                        text="Progress: 0/0")
        self.progress_label.grid(row=0, column=2, padx=(0, 20), pady=5)

        # Current job data frame
        current_job_frame = ttk.LabelFrame(main_frame,
                                           text="Current Job Data",
                                           padding="10")
        current_job_frame.grid(row=4, column=0,
                               sticky=(tk.W, tk.E, tk.N),
                               pady=(0, 15))

        # Current job data labels with better formatting
        fields = [
            ('job_title_label', "Job Title"),
            ('name_label', "Name"),
            ('region_label', "Region"),
            ('email_label', "Email"),
            ('facility_type_label', "Facility Type")
        ]

        for idx, (attr, label) in enumerate(fields):
            frame = ttk.Frame(current_job_frame, style='TFrame')
            frame.grid(row=idx, column=0, sticky=tk.W, pady=5)

            ttk.Label(frame, text=f"{label}:", width=15).pack(side=tk.LEFT)
            setattr(self, attr, ttk.Label(frame, text="-", wraplength=600))
            getattr(self, attr).pack(side=tk.LEFT, padx=(10, 0))

        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Log text area with better styling
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=12,
            width=80,
            font=('Consolas', 9),
            wrap=tk.WORD,
            borderwidth=0,
            highlightthickness=0
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure log frame grid weights
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        # Configure root window background
        self.root.configure(background='#f5f6f5')

    def log_message(self, message):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)

    def update_statistics(self):
        """Update statistics display and progress bar"""
        self.total_saved_label.config(text=f"Total Saved: {self.total_saved}")
        self.current_page_label.config(text=f"Current Page: {self.current_page}")
        self.progress_label.config(text=f"Progress: {self.current_job_index}/{self.total_jobs_on_page}")

        # Update progress bar
        if self.total_jobs_on_page > 0:
            progress = (self.current_job_index / self.total_jobs_on_page) * 100
            self.progress_bar['value'] = progress

    def update_current_job_display(self):
        """Update current job data display"""
        self.job_title_label.config(text=self.current_job_data['title'] or "-")
        self.name_label.config(text=self.current_job_data['name'] or "-")
        self.region_label.config(text=self.current_job_data['region'] or "-")
        self.email_label.config(text=self.current_job_data['email'] or "-")
        self.facility_type_label.config(text=self.current_job_data['facility_type'] or "-")

    def update_gui(self):
        """Update GUI elements and check for messages from automation thread"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                self.handle_message(message)
        except queue.Empty:
            pass

        # Update displays
        self.update_statistics()
        self.update_current_job_display()

        # Schedule next update
        self.root.after(100, self.update_gui)

    def handle_message(self, message):
        """Handle messages from automation thread"""
        msg_type = message.get('type')

        if msg_type == 'log':
            self.log_message(message['text'])
        elif msg_type == 'stats_update':
            self.total_saved = message.get('total_saved', self.total_saved)
            self.current_page = message.get('current_page', self.current_page)
            self.current_job_index = message.get('current_job_index', self.current_job_index)
            self.total_jobs_on_page = message.get('total_jobs_on_page', self.total_jobs_on_page)
        elif msg_type == 'current_job':
            self.current_job_data = message.get('data', self.current_job_data)
        elif msg_type == 'error':
            messagebox.showerror("Error", message['text'], parent=self.root)
        elif msg_type == 'complete':
            self.log_message("Automation completed successfully!")
            messagebox.showinfo("Complete", "Automation process has finished!",
                                parent=self.root)
            self.stop_automation()

    def start_automation(self):
        """Start the automation process in a separate thread"""
        if not self.is_running:
            self.is_running = True
            self.stop_requested = False
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

            # Reset counters and progress bar
            self.total_saved = 0
            self.current_page = 1
            self.current_job_index = 0
            self.total_jobs_on_page = 0
            self.progress_bar['value'] = 0

            # Start automation thread
            self.automation_thread = threading.Thread(target=self.run_automation)
            self.automation_thread.daemon = True
            self.automation_thread.start()

            self.log_message("Automation started!")

    def stop_automation(self):
        """Stop the automation process"""
        if self.is_running:
            self.stop_requested = True
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.log_message("Stopping automation...")

    def send_message(self, msg_type, **kwargs):
        """Send message to GUI thread"""
        message = {'type': msg_type, **kwargs}
        self.message_queue.put(message)

    def run_automation(self):
        """Main automation function"""
        try:
            # Initialize CSV
            csv_filename = f'job_listings_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Job Title', 'Name', 'Region', 'Email', 'Facility Type'])

            self.send_message('log', text=f"Created new CSV file: {csv_filename}")

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                self.send_message('log', text="Navigating to job listings page...")
                page.goto('https://central.childcare.go.kr/ccef/job/JobOfferSlPL.jsp?flag=SlPL')

                try:
                    page.wait_for_load_state("networkidle", timeout=30000)
                except Exception as e:
                    self.send_message('error', text=f"Failed to load page: {str(e)}")
                    browser.close()
                    return

                while not self.stop_requested:
                    self.send_message('log', text=f"=== Processing page {self.current_page} ===")

                    # Get job listings
                    try:
                        title_links = page.query_selector_all('table tbody tr td:nth-child(3) a[onclick*="fnGoBoardSl"]')
                        self.total_jobs_on_page = len(title_links)
                        self.send_message('stats_update',
                                          total_jobs_on_page=self.total_jobs_on_page)

                        if self.total_jobs_on_page == 0:
                            self.send_message('log', text="No job listings found on this page")
                            break

                        for i in range(self.total_jobs_on_page):
                            if self.stop_requested:
                                break

                            self.current_job_index = i + 1
                            self.send_message('stats_update',
                                              current_job_index=self.current_job_index)

                            try:
                                title_links = page.query_selector_all('table tbody tr td:nth-child(3) a[onclick*="fnGoBoardSl"]')
                                if i >= len(title_links):
                                    break

                                current_link = title_links[i]
                                job_title = current_link.inner_text().strip()

                                self.current_job_data['title'] = job_title
                                self.send_message('current_job', data=self.current_job_data)
                                self.send_message('log', text=f"Processing job {i + 1}/{self.total_jobs_on_page}: {job_title}")

                                current_link.click()
                                page.wait_for_load_state("networkidle", timeout=30000)
                                time.sleep(1)

                                # Extract data
                                table_element = page.query_selector('table')
                                if table_element:
                                    html_content = page.content()
                                    soup = BeautifulSoup(html_content, 'html.parser')
                                    table = soup.find('table')

                                    if table and table.find('tbody'):
                                        rows = table.find('tbody').find_all('tr')

                                        if len(rows) >= 7:
                                            facility_type = rows[2].find('td').contents[0].strip()
                                            region = rows[4].find('td').text.strip()
                                            name = rows[5].find_all('td')[0].text.strip()
                                            email = rows[6].find_all('td')[1].text.strip()

                                            self.current_job_data.update({
                                                'name': name,
                                                'region': region,
                                                'email': email,
                                                'facility_type': facility_type
                                            })
                                            self.send_message('current_job',
                                                              data=self.current_job_data)

                                            with open(csv_filename, 'a',
                                                      newline='',
                                                      encoding='utf-8') as csvfile:
                                                writer = csv.writer(csvfile)
                                                writer.writerow([job_title, name,
                                                                 region, email,
                                                                 facility_type])

                                            self.total_saved += 1
                                            self.send_message('stats_update',
                                                              total_saved=self.total_saved)
                                            self.send_message('log',
                                                              text=f"Saved job: {job_title}")

                                page.go_back()
                                page.wait_for_load_state("networkidle", timeout=30000)
                                time.sleep(1)

                            except Exception as e:
                                self.send_message('log',
                                                  text=f"Error processing job {i + 1}: {str(e)}")
                                try:
                                    page.go_back()
                                    page.wait_for_load_state("networkidle", timeout=30000)
                                except:
                                    pass
                                continue

                        if self.stop_requested:
                            break

                        # Check for next page
                        next_page_link = page.query_selector('a[href="#page_next"][class="next"]')
                        if not next_page_link:
                            self.send_message('log',
                                              text="No more pages found. Automation complete.")
                            break

                        self.send_message('log', text="Moving to next page...")
                        next_page_link.click()
                        page.wait_for_load_state("networkidle", timeout=30000)
                        time.sleep(1)

                        self.current_page += 1
                        self.send_message('stats_update',
                                          current_page=self.current_page)

                    except Exception as e:
                        self.send_message('error', text=f"Page processing error: {str(e)}")
                        break

                browser.close()

                if not self.stop_requested:
                    self.send_message('complete')
                else:
                    self.send_message('log', text="Automation stopped by user")

        except Exception as e:
            self.send_message('error', text=f"Automation error: {str(e)}")
            self.send_message('log', text=f"Error: {str(e)}")


def main():
    root = tk.Tk()
    # Set window icon (if available)
    try:
        root.iconbitmap('automation.ico')
    except:
        pass
    app = JobAutomationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
