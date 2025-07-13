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
import math

class ModernButton(tk.Canvas):
    """Custom modern button with hover effects and gradients"""
    def __init__(self, parent, text, command=None, bg="#4CAF50", fg="white", 
                 hover_bg="#45a049", width=120, height=35, font_size=12):
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, relief="flat")
        
        self.command = command
        self.bg = bg
        self.hover_bg = hover_bg
        self.fg = fg
        self.font_size = font_size
        
        # Create gradient background
        self.create_gradient_rect(0, 0, width, height, bg)
        
        # Create text
        self.text_id = self.create_text(width//2, height//2, text=text, 
                                       fill=fg, font=("Segoe UI", font_size, "bold"))
        
        # Bind events
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)
        
        # State tracking
        self.pressed = False
    
    def create_gradient_rect(self, x1, y1, x2, y2, color):
        """Create a gradient rectangle"""
        steps = 20
        for i in range(steps):
            # Create gradient effect
            alpha = 0.8 + (i / steps) * 0.2
            r, g, b = self.hex_to_rgb(color)
            r = int(r * alpha)
            g = int(g * alpha)
            b = int(b * alpha)
            grad_color = f'#{r:02x}{g:02x}{b:02x}'
            
            y_start = y1 + (y2 - y1) * i / steps
            y_end = y1 + (y2 - y1) * (i + 1) / steps
            
            self.create_rectangle(x1, y_start, x2, y_end, 
                                fill=grad_color, outline="", width=0)
    
    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def on_enter(self, event):
        """Mouse enter event"""
        self.delete("all")
        self.create_gradient_rect(0, 0, self.winfo_reqwidth(), self.winfo_reqheight(), self.hover_bg)
        self.text_id = self.create_text(self.winfo_reqwidth()//2, self.winfo_reqheight()//2, 
                                       text=self.itemcget(self.text_id, 'text'), 
                                       fill=self.fg, font=("Segoe UI", self.font_size, "bold"))
    
    def on_leave(self, event):
        """Mouse leave event"""
        self.delete("all")
        self.create_gradient_rect(0, 0, self.winfo_reqwidth(), self.winfo_reqheight(), self.bg)
        self.text_id = self.create_text(self.winfo_reqwidth()//2, self.winfo_reqheight()//2, 
                                       text=self.itemcget(self.text_id, 'text'), 
                                       fill=self.fg, font=("Segoe UI", self.font_size, "bold"))
    
    def on_click(self, event):
        """Mouse click event"""
        self.pressed = True
        self.configure(cursor="hand2")
    
    def on_release(self, event):
        """Mouse release event"""
        self.pressed = False
        self.configure(cursor="")
        if self.command:
            self.command()

class ProgressBar(tk.Canvas):
    """Custom animated progress bar"""
    def __init__(self, parent, width=300, height=20, bg="#f0f0f0", fg="#4CAF50"):
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, relief="flat")
        
        self.width = width
        self.height = height
        self.fg = fg
        self.progress = 0
        self.target_progress = 0
        
        # Create background
        self.create_rounded_rect(0, 0, width, height, 10, bg)
        
        # Create progress bar
        self.progress_rect = self.create_rounded_rect(2, 2, 2, height-2, 8, fg)
        
        # Create text
        self.text_id = self.create_text(width//2, height//2, text="0%", 
                                       fill="white", font=("Segoe UI", 10, "bold"))
        
        self.animate_progress()
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, color):
        """Create a rounded rectangle"""
        # Create rounded rectangle using arcs and lines
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, fill=color, smooth=True)
    
    def set_progress(self, progress):
        """Set progress (0-100)"""
        self.target_progress = max(0, min(100, progress))
    
    def animate_progress(self):
        """Animate progress bar"""
        if abs(self.progress - self.target_progress) > 0.5:
            self.progress += (self.target_progress - self.progress) * 0.1
        else:
            self.progress = self.target_progress
        
        # Update progress bar
        progress_width = (self.width - 4) * (self.progress / 100)
        self.coords(self.progress_rect, 2, 2, 2 + progress_width, self.height - 2)
        
        # Update text
        self.itemconfig(self.text_id, text=f"{int(self.progress)}%")
        
        self.after(16, self.animate_progress)  # ~60 FPS

class AnimatedLabel(tk.Label):
    """Label with fade-in animation"""
    def __init__(self, parent, text="", **kwargs):
        super().__init__(parent, text=text, **kwargs)
        self.alpha = 0
        self.target_alpha = 1
        self.animate()
    
    def animate(self):
        """Animate opacity"""
        if abs(self.alpha - self.target_alpha) > 0.01:
            self.alpha += (self.target_alpha - self.alpha) * 0.1
            # Apply alpha effect (simplified)
            self.configure(fg=self.get_fade_color())
        self.after(16, self.animate)
    
    def get_fade_color(self):
        """Get faded color based on alpha"""
        # Simplified fade effect
        return f"#{int(255 * self.alpha):02x}{int(255 * self.alpha):02x}{int(255 * self.alpha):02x}"
    
    def set_text(self, text):
        """Set text with animation"""
        self.configure(text=text)
        self.alpha = 0
        self.target_alpha = 1

class JobAutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Job Listing Automation Tool - Advanced")
        self.root.geometry("1000x700")
        # Configure root window
        self.root.configure(background="#f8f9fa")
        
        # Set window icon and style
        self.setup_styles()
        
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
        
        # Create main container with gradient background
        self.create_main_container()
        self.setup_gui()
        self.update_gui()
    
    def setup_styles(self):
        """Setup custom styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Title.TLabel', font=('Segoe UI', 24, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Segoe UI', 12), foreground='#7f8c8d')
        style.configure('Stats.TLabel', font=('Segoe UI', 11, 'bold'), foreground='#34495e')
        style.configure('Data.TLabel', font=('Segoe UI', 10), foreground='#2c3e50')
        style.configure('Card.TFrame', background='white', relief='flat')
    
    def create_main_container(self):
        """Create main container with gradient background"""
        self.main_canvas = tk.Canvas(self.root, highlightthickness=0)
        self.main_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create gradient background
        self.create_gradient_background()
        
        # Create scrollable frame
        self.scrollable_frame = ttk.Frame(self.main_canvas)
        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configure scrolling
        self.scrollable_frame.bind("<Configure>", lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))
        self.root.bind("<MouseWheel>", self.on_mousewheel)
    
    def create_gradient_background(self):
        """Create gradient background"""
        width = 1000
        height = 700
        
        for i in range(height):
            # Create gradient from top to bottom
            ratio = i / height
            r = int(248 + (245 - 248) * ratio)  # #f8f9fa to #f5f5f5
            g = int(249 + (245 - 249) * ratio)
            b = int(250 + (245 - 250) * ratio)
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.main_canvas.create_line(0, i, width, i, fill=color, width=1)
    
    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def setup_gui(self):
        """Setup the GUI components"""
        # Main container
        main_frame = ttk.Frame(self.scrollable_frame, style='Card.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header section with gradient
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
        self.start_button = ModernButton(buttons_frame, "🚀 Start Automation", 
                                       command=self.start_automation, 
                                       bg="#27ae60", hover_bg="#229954", width=180, height=45)
        self.start_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # Stop button
        self.stop_button = ModernButton(buttons_frame, "⏹️ Stop", 
                                      command=self.stop_automation, 
                                      bg="#e74c3c", hover_bg="#c0392b", width=120, height=45)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # Status indicator
        self.status_label = AnimatedLabel(buttons_frame, text="⏸️ Ready", 
                                        font=('Segoe UI', 12, 'bold'), fg='#7f8c8d')
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))
    
    def create_statistics_section(self, parent):
        """Create statistics section with cards"""
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Statistics title
        stats_title = ttk.Label(stats_frame, text="📊 Real-time Statistics", 
                               font=('Segoe UI', 16, 'bold'), foreground='#2c3e50')
        stats_title.pack(anchor=tk.W, pady=(0, 15))
        
        # Statistics cards container
        cards_frame = ttk.Frame(stats_frame)
        cards_frame.pack(fill=tk.X)
        
        # Card 1: Total Saved
        self.create_stat_card(cards_frame, "Total Saved", "0", "📈", "#3498db", 0)
        
        # Card 2: Current Page
        self.create_stat_card(cards_frame, "Current Page", "1", "📄", "#e67e22", 1)
        
        # Card 3: Progress
        self.create_stat_card(cards_frame, "Progress", "0/0", "⚡", "#9b59b6", 2)
        
        # Progress bar
        progress_frame = ttk.Frame(stats_frame)
        progress_frame.pack(fill=tk.X, pady=(20, 0))
        
        progress_label = ttk.Label(progress_frame, text="Overall Progress", 
                                  font=('Segoe UI', 12, 'bold'), foreground='#2c3e50')
        progress_label.pack(anchor=tk.W, pady=(0, 10))
        
        self.progress_bar = ProgressBar(progress_frame, width=400, height=25)
        self.progress_bar.pack(anchor=tk.W)
    
    def create_stat_card(self, parent, title, initial_value, icon, color, column):
        """Create a statistics card"""
        card_frame = ttk.Frame(parent, style='Card.TFrame')
        card_frame.grid(row=0, column=column, padx=(0, 15), sticky=(tk.W, tk.E))
        
        # Card content
        icon_label = ttk.Label(card_frame, text=icon, font=('Segoe UI', 24))
        icon_label.pack(pady=(15, 5))
        
        value_label = ttk.Label(card_frame, text=initial_value, 
                               font=('Segoe UI', 20, 'bold'), foreground=color)
        value_label.pack()
        
        title_label = ttk.Label(card_frame, text=title, 
                               font=('Segoe UI', 11), foreground='#7f8c8d')
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
                             font=('Segoe UI', 16, 'bold'), foreground='#2c3e50')
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
                                font=('Segoe UI', 11, 'bold'), foreground='#34495e')
        label_widget.pack(side=tk.LEFT)
        
        value_widget = ttk.Label(row_frame, text=value, 
                                font=('Segoe UI', 11), foreground='#2c3e50')
        value_widget.pack(side=tk.LEFT, padx=(10, 0))
        
        return value_widget
    
    def create_log_section(self, parent):
        """Create log section"""
        log_frame = ttk.Frame(parent)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Log title
        log_title = ttk.Label(log_frame, text="📝 Activity Log", 
                             font=('Segoe UI', 16, 'bold'), foreground='#2c3e50')
        log_title.pack(anchor=tk.W, pady=(0, 15))
        
        # Log container
        log_container = ttk.Frame(log_frame, style='Card.TFrame')
        log_container.pack(fill=tk.BOTH, expand=True)
        
        # Log text area with custom styling
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
            color = "#e74c3c"
        elif "Saved" in message:
            color = "#27ae60"
        elif "Processing" in message:
            color = "#3498db"
        else:
            color = "#ecf0f1"
        
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # Apply color to the last line
        last_line_start = self.log_text.index("end-2c linestart")
        last_line_end = self.log_text.index("end-1c")
        self.log_text.tag_add("colored", last_line_start, last_line_end)
        self.log_text.tag_config("colored", foreground=color)
    
    def update_statistics(self):
        """Update statistics display with animations"""
        self.total_saved_card.configure(text=str(self.total_saved))
        self.current_page_card.configure(text=str(self.current_page))
        self.progress_card.configure(text=f"{self.current_job_index}/{self.total_jobs_on_page}")
        
        # Update progress bar
        if self.total_jobs_on_page > 0:
            progress_percent = (self.current_job_index / self.total_jobs_on_page) * 100
            self.progress_bar.set_progress(progress_percent)
    
    def update_current_job_display(self):
        """Update current job data display with animations"""
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
            self.status_label.set_text("✅ Complete")
            self.stop_automation()
    
    def start_automation(self):
        """Start the automation process in a separate thread"""
        if not self.is_running:
            self.is_running = True
            self.stop_requested = False
            self.start_button.configure(state=tk.DISABLED)
            self.stop_button.configure(state=tk.NORMAL)
            self.status_label.set_text("🔄 Running")
            
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
            self.status_label.set_text("⏸️ Stopped")
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