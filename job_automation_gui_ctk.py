import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import time
import csv
from datetime import datetime
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import queue

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class JobAutomationGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Job Listing Automation Tool - Advanced")
        self.root.geometry("1100x800")
        self.root.minsize(900, 600)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Data tracking variables
        self.total_saved = 0
        self.current_page = 1
        self.current_job_index = 0
        self.total_jobs_on_page = 0
        self.is_running = False
        self.stop_requested = False
        self.current_job_data = {
            'title': '',
            'name': '',
            'region': '',
            'email': '',
            'facility_type': ''
        }
        self.message_queue = queue.Queue()

        # Main scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(self.root, orientation="vertical")
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.setup_gui()
        self.update_gui()

    def setup_gui(self):
        # Header
        self.create_header_section(self.scrollable_frame)
        # Controls
        self.create_control_section(self.scrollable_frame)
        # Stats
        self.create_statistics_section(self.scrollable_frame)
        # Current job
        self.create_current_job_section(self.scrollable_frame)
        # Log
        self.create_log_section(self.scrollable_frame)

    def create_header_section(self, parent):
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        title_label = ctk.CTkLabel(
            header_frame, text="🤖 Job Listing Automation Tool",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=(0, 20))
        theme_label = ctk.CTkLabel(header_frame, text="Theme:", font=ctk.CTkFont(size=14))
        theme_label.grid(row=0, column=1, sticky="e", padx=(0, 10))
        self.theme_switch = ctk.CTkSwitch(
            header_frame, text="Dark Mode", command=self.toggle_theme,
            onvalue="dark", offvalue="light"
        )
        self.theme_switch.grid(row=0, column=2, sticky="e")
        self.theme_switch.select()
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Advanced Web Scraping with Real-time Monitoring",
            font=ctk.CTkFont(size=16), text_color="gray"
        )
        subtitle_label.grid(row=1, column=0, columnspan=3, sticky="w", pady=(10, 0))

    def toggle_theme(self):
        current_mode = ctk.get_appearance_mode()
        new_mode = "Light" if current_mode == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)
        self.theme_switch.configure(text=f"{new_mode} Mode")

    def create_control_section(self, parent):
        control_frame = ctk.CTkFrame(parent, fg_color="transparent")
        control_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=20)
        buttons_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        buttons_frame.pack()
        self.start_button = ctk.CTkButton(
            buttons_frame, text="🚀 Start Automation", command=self.start_automation,
            font=ctk.CTkFont(size=16, weight="bold"), height=45,
            fg_color="green", hover_color="darkgreen"
        )
        self.start_button.pack(side="left", padx=(0, 15))
        self.stop_button = ctk.CTkButton(
            buttons_frame, text="⏹️ Stop", command=self.stop_automation,
            font=ctk.CTkFont(size=16, weight="bold"), height=45,
            fg_color="red", hover_color="darkred", state="disabled"
        )
        self.stop_button.pack(side="left", padx=(0, 15))
        self.status_label = ctk.CTkLabel(
            buttons_frame, text="⏸️ Ready", font=ctk.CTkFont(size=16, weight="bold"), text_color="gray"
        )
        self.status_label.pack(side="left", padx=(20, 0))

    def create_statistics_section(self, parent):
        stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
        stats_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        stats_title = ctk.CTkLabel(
            stats_frame, text="📊 Real-time Statistics", font=ctk.CTkFont(size=20, weight="bold")
        )
        stats_title.pack(anchor="w", pady=(0, 15))
        cards_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
        cards_frame.pack(fill="x")
        self.create_stat_card(cards_frame, "Total Saved", "0", "📈", 0)
        self.create_stat_card(cards_frame, "Current Page", "1", "📄", 1)
        self.create_stat_card(cards_frame, "Progress", "0/0", "⚡", 2)
        progress_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
        progress_frame.pack(fill="x", pady=(20, 0))
        progress_label = ctk.CTkLabel(
            progress_frame, text="Overall Progress", font=ctk.CTkFont(size=16, weight="bold")
        )
        progress_label.pack(anchor="w", pady=(0, 10))
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", pady=(0, 5))
        self.progress_bar.set(0)
        # Removed percentage label here

    def create_stat_card(self, parent, title, initial_value, icon, column):
        card_frame = ctk.CTkFrame(parent, corner_radius=15)
        card_frame.grid(row=0, column=column, padx=(0, 15), sticky="ew")
        parent.grid_columnconfigure(column, weight=1)
        icon_label = ctk.CTkLabel(
            card_frame, text=icon, font=ctk.CTkFont(size=32)
        )
        icon_label.pack(pady=(20, 10))
        value_label = ctk.CTkLabel(
            card_frame, text=initial_value, font=ctk.CTkFont(size=24, weight="bold")
        )
        value_label.pack()
        title_label = ctk.CTkLabel(
            card_frame, text=title, font=ctk.CTkFont(size=14), text_color="gray"
        )
        title_label.pack(pady=(5, 20))
        if title == "Total Saved":
            self.total_saved_card = value_label
        elif title == "Current Page":
            self.current_page_card = value_label
        elif title == "Progress":
            self.progress_card = value_label

    def create_current_job_section(self, parent):
        job_frame = ctk.CTkFrame(parent, fg_color="transparent")
        job_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        job_title = ctk.CTkLabel(
            job_frame, text="🎯 Current Job Data", font=ctk.CTkFont(size=20, weight="bold")
        )
        job_title.pack(anchor="w", pady=(0, 15))
        job_data_frame = ctk.CTkFrame(job_frame, corner_radius=15)
        job_data_frame.pack(fill="x", pady=10)
        self.job_title_label = self.create_data_row(job_data_frame, "Job Title", "-", 0)
        self.name_label = self.create_data_row(job_data_frame, "Name", "-", 1)
        self.region_label = self.create_data_row(job_data_frame, "Region", "-", 2)
        self.email_label = self.create_data_row(job_data_frame, "Email", "-", 3)
        self.facility_type_label = self.create_data_row(job_data_frame, "Facility Type", "-", 4)

    def create_data_row(self, parent, label, value, row):
        row_frame = ctk.CTkFrame(parent, fg_color="transparent")
        row_frame.pack(fill="x", padx=20, pady=8)
        label_widget = ctk.CTkLabel(
            row_frame, text=f"{label}:", font=ctk.CTkFont(size=14, weight="bold"), width=120
        )
        label_widget.pack(side="left")
        value_widget = ctk.CTkLabel(
            row_frame, text=value, font=ctk.CTkFont(size=14), wraplength=400
        )
        value_widget.pack(side="left", padx=(10, 0), fill="x", expand=True)
        return value_widget

    def create_log_section(self, parent):
        log_frame = ctk.CTkFrame(parent, fg_color="transparent")
        log_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=10)
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)
        log_title = ctk.CTkLabel(
            log_frame, text="📝 Activity Log", font=ctk.CTkFont(size=20, weight="bold")
        )
        log_title.grid(row=0, column=0, sticky="w", pady=(0, 15))
        log_container = ctk.CTkFrame(log_frame, corner_radius=15)
        log_container.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        log_container.grid_columnconfigure(0, weight=1)
        log_container.grid_rowconfigure(0, weight=1)
        self.log_text = ctk.CTkTextbox(
            log_container, font=ctk.CTkFont(size=12, family="Consolas"), wrap="word"
        )
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        if "Error" in message:
            color = "red"
        elif "Saved" in message:
            color = "green"
        elif "Processing" in message:
            color = "blue"
        else:
            color = "white"
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert("end", log_entry)
        self.log_text.see("end")
        last_line_start = self.log_text.index("end-2c linestart")
        last_line_end = self.log_text.index("end-1c")
        self.log_text.tag_add("colored", last_line_start, last_line_end)
        self.log_text.tag_config("colored", foreground=color)

    def update_statistics(self):
        self.total_saved_card.configure(text=str(self.total_saved))
        self.current_page_card.configure(text=str(self.current_page))
        self.progress_card.configure(text=f"{self.current_job_index}/{self.total_jobs_on_page}")
        if self.total_jobs_on_page > 0:
            progress_percent = (self.current_job_index / self.total_jobs_on_page)
            self.progress_bar.set(progress_percent)
        else:
            self.progress_bar.set(0)

    def update_current_job_display(self):
        self.job_title_label.configure(text=self.current_job_data['title'] or "-")
        self.name_label.configure(text=self.current_job_data['name'] or "-")
        self.region_label.configure(text=self.current_job_data['region'] or "-")
        self.email_label.configure(text=self.current_job_data['email'] or "-")
        self.facility_type_label.configure(text=self.current_job_data['facility_type'] or "-")

    def update_gui(self):
        try:
            while True:
                message = self.message_queue.get_nowait()
                self.handle_message(message)
        except queue.Empty:
            pass
        self.update_statistics()
        self.update_current_job_display()
        self.root.after(100, self.update_gui)

    def handle_message(self, message):
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
            messagebox.showerror("Error", message['text'])
        elif msg_type == 'complete':
            self.log_message("✅ Automation completed!")
            self.status_label.configure(text="✅ Complete")
            self.stop_automation()

    def start_automation(self):
        if not self.is_running:
            self.is_running = True
            self.stop_requested = False
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.status_label.configure(text="🔄 Running")
            self.total_saved = 0
            self.current_page = 1
            self.current_job_index = 0
            self.total_jobs_on_page = 0
            self.automation_thread = threading.Thread(target=self.run_automation)
            self.automation_thread.daemon = True
            self.automation_thread.start()
            self.log_message("🚀 Automation started!")

    def stop_automation(self):
        if self.is_running:
            self.stop_requested = True
            self.is_running = False
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.status_label.configure(text="⏸️ Stopped")
            self.log_message("⏹️ Automation stopped by user")

    def send_message(self, msg_type, **kwargs):
        message = {'type': msg_type, **kwargs}
        self.message_queue.put(message)

    def run_automation(self):
        try:
            csv_filename = f'job_listings_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Job Title', 'Name', 'Region', 'Email', 'Facility Type'])
            self.send_message('log', text="📄 CSV file initialized")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                self.send_message('log', text="🌐 Navigating to job listings page...")
                page.goto('https://central.childcare.go.kr/ccef/job/JobOfferSlPL.jsp?flag=SlPL')
                page.wait_for_load_state("networkidle")
                while not self.stop_requested:
                    self.send_message('log', text=f"📄 Processing page {self.current_page}")
                    title_links = page.query_selector_all('table tbody tr td:nth-child(3) a[onclick*="fnGoBoardSl"]')
                    self.total_jobs_on_page = len(title_links)
                    if self.total_jobs_on_page == 0:
                        self.send_message('log', text="⚠️ No job listings found on this page")
                        break
                    for i in range(self.total_jobs_on_page):
                        if self.stop_requested:
                            break
                        self.current_job_index = i + 1
                        self.send_message('stats_update', current_job_index=self.current_job_index)
                        try:
                            self.send_message('log', text=f"🔄 Processing job {i + 1}/{self.total_jobs_on_page}")
                            title_links = page.query_selector_all('table tbody tr td:nth-child(3) a[onclick*="fnGoBoardSl"]')
                            if i >= len(title_links):
                                break
                            current_link = title_links[i]
                            job_title = current_link.inner_text().strip()
                            self.current_job_data['title'] = job_title
                            self.send_message('current_job', data=self.current_job_data)
                            self.send_message('log', text=f"📋 Job title: {job_title}")
                            current_link.click()
                            page.wait_for_load_state("networkidle")
                            time.sleep(2)
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
                                        self.send_message('current_job', data=self.current_job_data)
                                        with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
                                            writer = csv.writer(csvfile)
                                            writer.writerow([job_title, name, region, email, facility_type])
                                        self.total_saved += 1
                                        self.send_message('stats_update', total_saved=self.total_saved)
                                        self.send_message('log', text=f"✅ Saved: {job_title}")
                            page.go_back()
                            page.wait_for_load_state("networkidle")
                            time.sleep(1)
                        except Exception as e:
                            self.send_message('log', text=f"❌ Error processing job {i + 1}: {str(e)}")
                            try:
                                page.go_back()
                                page.wait_for_load_state("networkidle")
                            except:
                                pass
                            continue
                    if self.stop_requested:
                        break
                    next_page_link = page.query_selector('a[href="#page_next"][class="next"]')
                    if not next_page_link:
                        self.send_message('log', text="🏁 No more pages found. Automation complete.")
                        break
                    self.send_message('log', text="➡️ Moving to next page...")
                    next_page_link.click()
                    page.wait_for_load_state("networkidle")
                    time.sleep(2)
                    self.current_page += 1
                    self.send_message('stats_update', current_page=self.current_page)
                browser.close()
                if not self.stop_requested:
                    self.send_message('complete')
                else:
                    self.send_message('log', text="⏹️ Automation stopped by user")
        except Exception as e:
            self.send_message('error', text=f"Automation error: {str(e)}")
            self.send_message('log', text=f"❌ Error: {str(e)}")

def main():
    app = JobAutomationGUI()
    app.root.mainloop()

if __name__ == "__main__":
    main() 