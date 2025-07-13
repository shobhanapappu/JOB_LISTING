# Job Automation GUI

A graphical user interface for the job listing automation tool that scrapes job data from childcare websites.

## Features

- **Real-time Statistics**: Shows total saved entries, current page, and progress
- **Live Data Display**: Shows current job being processed (title, name, region, email, facility type)
- **Log Window**: Real-time logging of automation progress
- **Start/Stop Controls**: Easy control over the automation process
- **Threading**: GUI remains responsive during automation

## Installation

1. Make sure you have Python 3.7+ installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Playwright browsers:
   ```bash
   playwright install
   ```

## Usage

### Running the GUI

1. **Option 1**: Run the launcher script
   ```bash
   python run_ctk_gui.py
   ```

2. **Option 2**: Run directly
   ```bash
   python job_automation_gui.py
   ```

### Using the GUI

1. **Start Automation**: Click the "Start Automation" button to begin the scraping process
2. **Monitor Progress**: Watch the statistics panel for real-time updates:
   - Total Saved: Number of job entries saved to CSV
   - Current Page: Current page being processed
   - Progress: Current job number / total jobs on page
3. **View Current Job**: The "Current Job Data" panel shows the details of the job being processed
4. **Check Logs**: The log window shows detailed progress and any errors
5. **Stop Process**: Click "Stop" to halt the automation at any time

### Output

The automation saves data to `job_listings.csv` with the following columns:
- Job Title
- Name (담당자명)
- Region (소재지)
- Email (담당자 이메일)
- Facility Type (시설유형)

## GUI Components

### Statistics Panel
- **Total Saved**: Count of successfully saved job entries
- **Current Page**: Current page number being processed
- **Progress**: Current job index / total jobs on current page

### Current Job Data Panel
- **Job Title**: Title of the job being processed
- **Name**: Contact person name
- **Region**: Location/region of the job
- **Email**: Contact email address
- **Facility Type**: Type of childcare facility

### Log Panel
- Real-time logging of all automation activities
- Timestamps for all log entries
- Error messages and status updates

## Technical Details

- **Threading**: Automation runs in a separate thread to keep GUI responsive
- **Message Queue**: Thread-safe communication between automation and GUI
- **Error Handling**: Robust error handling with user-friendly error messages
- **Headless Browser**: Uses headless browser mode for better performance

## Troubleshooting

1. **Import Errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`
2. **Browser Issues**: Run `playwright install` to install required browsers
3. **Network Issues**: Check internet connection and website availability
4. **Permission Errors**: Ensure write permissions in the current directory for CSV file creation

## Files

- `job_automation_gui.py`: Main GUI application
- `run_gui.py`: Simple launcher script
- `requirements.txt`: Python dependencies
- `README_GUI.md`: This documentation file 
