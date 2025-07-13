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
        self.root.title("Job Listing Automation Tool - Modern")
        self.root.geometry("1000x700")
        
        # Configure colors
        self.colors = {
            'primary': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'dark': '#2c3e50',
            'light': '#ecf0f1',
            'gray': '#95a5a6',
            'white': '#ffffff'
        }
        
        # Configure root
        self.root.configure(background=self.colors['light'])
        
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
        
        self.setup_styles()
        self.setup_gui()
        self.update_gui()
    
    def setup_styles(self):
        """Setup custom styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 24, 'bold'), 
                       foreground=self.colors['dark'])
        style.configure('Subtitle.TLabel', 
                       font=('Segoe UI', 12), 
                       foreground=self.colors['gray'])
        style.configure('Stats.TLabel', 
                       font=('Segoe UI', 11, 'bold'), 
                       foreground=self.colors['dark'])
        style.configure('Data.TLabel', 
                       font=('Segoe UI', 10), 
                       foreground=self.colors['dark'])
        style.configure('Card.TFrame', 
                       background=self.colors['white'], 
                       relief='flat')
        style.configure('Success.TButton', 
                       background=self.colors['success'])
        style.configure('Danger.TButton', 
                       background=self.colors['danger'])
    
    def setup_gui(self):
        """Setup the GUI components"""
        # Main container
        main_frame = ttk.Frame(self.root, style='Card.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header section
        self.create_header_section(main_frame)
        
        # Control section
        self.create_control_section(main_frame)
        
        # Statistics section
        self.create_statistics_section(main_frame)
        
        # Current job section
        self.create_current_job_section(main_frame)
        
        # Log section
        self.create_log_section(main_frame)
    
    def create_header_section(self, parent):
        """Create header section with title and subtitle"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # Title with icon
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(fill=tk.X)
        
        # Create icon (simulated with text)
        icon_label = ttk.Label(title_frame, text="🤖", font=('Segoe UI', 32))
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Title and subtitle
        title_label = ttk.Label(title_frame, text="Job Listing Automation Tool", 
                               style='Title.TLabel')
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = ttk.Label(header_frame, text="Advanced Web Scraping with Real-time Monitoring", 
                                  style='Subtitle.TLabel')
        subtitle_label.pack(anchor=tk.W, pady=(5, 0))
    
    def create_control_section(self, parent):
        """Create control buttons section"""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Control buttons container
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.pack()
        
        # Start button
        self.start_button = ttk.Button(buttons_frame, text="🚀 Start Automation", 
                                      command=self.start_automation, 
                                      style='Success.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # Stop button
        self.stop_button = ttk.Button(buttons_frame, text="⏹️ Stop", 
                                     command=self.stop_automation, 
                                     style='Danger.TButton', 
                                     state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # Status indicator
        self.status_label = ttk.Label(buttons_frame, text="⏸️ Ready", 
                                     font=('Segoe UI', 12, 'bold'), 
                                     foreground=self.colors['gray'])
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))
    
    def create_statistics_section(self, parent):
        """Create statistics section with cards"""
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Statistics title
        stats_title = ttk.Label(stats_frame, text="📊 Real-time Statistics", 
                               font=('Segoe UI', 16, 'bold'), 
                               foreground=self.colors['dark'])
        stats_title.pack(anchor=tk.W, pady=(0, 15))
        
        # Statistics cards container
        cards_frame = ttk.Frame(stats_frame)
        cards_frame.pack(fill=tk.X)
        
        # Card 1: Total Saved
        self.create_stat_card(cards_frame, "Total Saved", "0", "📈", self.colors['primary'], 0)
        
        # Card 2: Current Page
        self.create_stat_card(cards_frame, "Current Page", "1", "📄", self.colors['warning'], 1)
        
        # Card 3: Progress
        self.create_stat_card(cards_frame, "Progress", "0/0", "⚡", self.colors['success'], 2)
        
        # Progress bar
        progress_frame = ttk.Frame(stats_frame)
        progress_frame.pack(fill=tk.X, pady=(20, 0))
        
        progress_label = ttk.Label(progress_frame, text="Overall Progress", 
                                  font=('Segoe UI', 12, 'bold'), 
                                  foreground=self.colors['dark'])
        progress_label.pack(anchor=tk.W, pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(progress_frame, length=400, mode='determinate')
        self.progress_bar.pack(anchor=tk.W)
    
    def create_stat_card(self, parent, title, initial_value, icon, color, column):
        """Create a statistics card"""
        card_frame = ttk.Frame(parent, style='Card.TFrame')
        card_frame.grid(row=0, column=column, padx=(0, 15), sticky=(tk.W, tk.E))
        
        # Card content
        icon_label = ttk.Label(card_frame, text=icon, font=('Segoe UI', 24))
        icon_label.pack(pady=(15, 5))
        
        value_label = ttk.Label(card_frame, text=initial_value, 
                               font=('Segoe UI', 20, 'bold'), 
                               foreground=color)
        value_label.pack()
        
        title_label = ttk.Label(card_frame, text=title, 
                               font=('Segoe UI', 11), 
                               foreground=self.colors['gray'])
        title_label.pack(pady=(0, 15))
        
        # Store reference
        if title == "Total Saved":
            self.total_saved_card = value_label
        elif title == "Current Page":
            self.current_page_card = value_label
        elif title == "Progress":
            self.progress_card = value_label
    
    def create_current_job_section(self, parent):
        """Create current job data section"""
        job_frame = ttk.Frame(parent)
        job_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Section title
        job_title = ttk.Label(job_frame, text="🎯 Current Job Data", 
                             font=('Segoe UI', 16, 'bold'), 
                             foreground=self.colors['dark'])
        job_title.pack(anchor=tk.W, pady=(0, 15))
        
        # Job data container
        job_data_frame = ttk.Frame(job_frame, style='Card.TFrame')
        job_data_frame.pack(fill=tk.X, pady=10)
        
        # Create job data rows
        self.job_title_label = self.create_data_row(job_data_frame, "Job Title", "-", 0)
        self.name_label = self.create_data_row(job_data_frame, "Name", "-", 1)
        self.region_label = self.create_data_row(job_data_frame, "Region", "-", 2)
        self.email_label = self.create_data_row(job_data_frame, "Email", "-", 3)
        self.facility_type_label = self.create_data_row(job_data_frame, "Facility Type", "-", 4)
    
    def create_data_row(self, parent, label, value, row):
        """Create a data row with label and value"""
        row_frame = ttk.Frame(parent)
        row_frame.pack(fill=tk.X, padx=20, pady=8)
        
        label_widget = ttk.Label(row_frame, text=f"{label}:", 
                                font=('Segoe UI', 11, 'bold'), 
                                foreground=self.colors['dark'])
        label_widget.pack(side=tk.LEFT)
        
        value_widget = ttk.Label(row_frame, text=value, 
                                font=('Segoe UI', 11), 
                                foreground=self.colors['dark'])
        value_widget.pack(side=tk.LEFT, padx=(10, 0))
        
        return value_widget
    
    def create_log_section(self, parent):
        """Create log section"""
        log_frame = ttk.Frame(parent)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Log title
        log_title = ttk.Label(log_frame, text="📝 Activity Log", 
                             font=('Segoe UI', 16, 'bold'), 
                             foreground=self.colors['dark'])
        log_title.pack(anchor=tk.W, pady=(0, 15))
        
        # Log container
        log_container = ttk.Frame(log_frame, style='Card.TFrame')
        log_container.pack(fill=tk.BOTH, expand=True)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            log_container, 
            height=12, 
            width=80,
            font=('Consolas', 10),
            relief='flat',
            borderwidth=0
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def log_message(self, message):
        """Add message to log with timestamp and styling"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color code different message types
        if "Error" in message:
            color = self.colors['danger']
        elif "Saved" in message:
            color = self.colors['success']
        elif "Processing" in message:
            color = self.colors['primary']
        else:
            color = self.colors['dark']
        
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # Apply color to the last line
        last_line_start = self.log_text.index("end-2c linestart")
        last_line_end = self.log_text.index("end-1c")
        self.log_text.tag_add("colored", last_line_start, last_line_end)
        self.log_text.tag_config("colored", foreground=color)
    
    def update_statistics(self):
        """Update statistics display"""
        self.total_saved_card.configure(text=str(self.total_saved))
        self.current_page_card.configure(text=str(self.current_page))
        self.progress_card.configure(text=f"{self.current_job_index}/{self.total_jobs_on_page}")
        
        # Update progress bar
        if self.total_jobs_on_page > 0:
            progress_percent = (self.current_job_index / self.total_jobs_on_page) * 100
            self.progress_bar['value'] = progress_percent
        else:
            self.progress_bar['value'] = 0
    
    def update_current_job_display(self):
        """Update current job data display"""
        self.job_title_label.configure(text=self.current_job_data['title'] or "-")
        self.name_label.configure(text=self.current_job_data['name'] or "-")
        self.region_label.configure(text=self.current_job_data['region'] or "-")
        self.email_label.configure(text=self.current_job_data['email'] or "-")
        self.facility_type_label.configure(text=self.current_job_data['facility_type'] or "-")
    
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
            messagebox.showerror("Error", message['text'])
        elif msg_type == 'complete':
            self.log_message("✅ Automation completed!")
            self.status_label.configure(text="✅ Complete")
            self.stop_automation()
    
    def start_automation(self):
        """Start the automation process in a separate thread"""
        if not self.is_running:
            self.is_running = True
            self.stop_requested = False
            self.start_button.configure(state=tk.DISABLED)
            self.stop_button.configure(state=tk.NORMAL)
            self.status_label.configure(text="🔄 Running")
            
            # Reset counters
            self.total_saved = 0
            self.current_page = 1
            self.current_job_index = 0
            self.total_jobs_on_page = 0
            
            # Start automation thread
            self.automation_thread = threading.Thread(target=self.run_automation)
            self.automation_thread.daemon = True
            self.automation_thread.start()
            
            self.log_message("🚀 Automation started!")
    
    def stop_automation(self):
        """Stop the automation process"""
        if self.is_running:
            self.stop_requested = True
            self.is_running = False
            self.start_button.configure(state=tk.NORMAL)
            self.stop_button.configure(state=tk.DISABLED)
            self.status_label.configure(text="⏸️ Stopped")
            self.log_message("⏹️ Automation stopped by user")
    
    def send_message(self, msg_type, **kwargs):
        """Send message to GUI thread"""
        message = {'type': msg_type, **kwargs}
        self.message_queue.put(message)
    
    def run_automation(self):
        """Main automation function"""
        try:
            # Initialize CSV
            csv_filename = 'job_listings.csv'
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Job Title', 'Name', 'Region', 'Email', 'Facility Type'])
            
            self.send_message('log', text="📄 CSV file initialized")
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Navigate to the initial page
                self.send_message('log', text="🌐 Navigating to job listings page...")
                page.goto('https://central.childcare.go.kr/ccef/job/JobOfferSlPL.jsp?flag=SlPL')
                page.wait_for_load_state("networkidle")
                
                while not self.stop_requested:
                    self.send_message('log', text=f"📄 Processing page {self.current_page}")
                    
                    # Get job listings on current page
                    title_links = page.query_selector_all('table tbody tr td:nth-child(3) a[onclick*="fnGoBoardSl"]')
                    self.total_jobs_on_page = len(title_links)
                    
                    if self.total_jobs_on_page == 0:
                        self.send_message('log', text="⚠️ No job listings found on this page")
                        break
                    
                    # Process each job listing
                    for i in range(self.total_jobs_on_page):
                        if self.stop_requested:
                            break
                        
                        self.current_job_index = i + 1
                        self.send_message('stats_update', current_job_index=self.current_job_index)
                        
                        try:
                            self.send_message('log', text=f"🔄 Processing job {i + 1}/{self.total_jobs_on_page}")
                            
                            # Re-find title links
                            title_links = page.query_selector_all('table tbody tr td:nth-child(3) a[onclick*="fnGoBoardSl"]')
                            
                            if i >= len(title_links):
                                break
                            
                            current_link = title_links[i]
                            job_title = current_link.inner_text().strip()
                            
                            # Update current job display
                            self.current_job_data['title'] = job_title
                            self.send_message('current_job', data=self.current_job_data)
                            
                            self.send_message('log', text=f"📋 Job title: {job_title}")
                            
                            # Click on job title
                            current_link.click()
                            page.wait_for_load_state("networkidle")
                            time.sleep(2)
                            
                            # Extract data from detail page
                            table_element = page.query_selector('table')
                            if table_element:
                                html_content = page.content()
                                soup = BeautifulSoup(html_content, 'html.parser')
                                table = soup.find('table')
                                
                                if table and table.find('tbody'):
                                    rows = table.find('tbody').find_all('tr')
                                    
                                    if len(rows) >= 7:
                                        # Extract data
                                        facility_type = rows[2].find('td').contents[0].strip()
                                        region = rows[4].find('td').text.strip()
                                        name = rows[5].find_all('td')[0].text.strip()
                                        email = rows[6].find_all('td')[1].text.strip()
                                        
                                        # Update current job data
                                        self.current_job_data.update({
                                            'name': name,
                                            'region': region,
                                            'email': email,
                                            'facility_type': facility_type
                                        })
                                        self.send_message('current_job', data=self.current_job_data)
                                        
                                        # Save to CSV
                                        with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
                                            writer = csv.writer(csvfile)
                                            writer.writerow([job_title, name, region, email, facility_type])
                                        
                                        self.total_saved += 1
                                        self.send_message('stats_update', total_saved=self.total_saved)
                                        self.send_message('log', text=f"✅ Saved: {job_title}")
                            
                            # Go back to search results
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
                    
                    # Check for next page
                    next_page_link = page.query_selector('a[href="#page_next"][class="next"]')
                    if not next_page_link:
                        self.send_message('log', text="🏁 No more pages found. Automation complete.")
                        break
                    
                    # Go to next page
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
    root = tk.Tk()
    app = JobAutomationGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 