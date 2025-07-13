import time
import csv
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# Define CSV filename
csv_filename = 'job_listings.csv'

# Initialize CSV with headers
with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Job Title', 'Name', 'Region', 'Email', 'Facility Type'])


# Function to process job listings on the current page
def process_page(page, total_listings_per_page):
    title_links = page.query_selector_all('table tbody tr td:nth-child(3) a[onclick*="fnGoBoardSl"]')
    for i in range(len(title_links)):
        try:
            print(f"\n--- Processing job listing {i + 1}/{len(title_links)} on current page ---")

            # Re-find title links to avoid stale elements
            title_links = page.query_selector_all('table tbody tr td:nth-child(3) a[onclick*="fnGoBoardSl"]')

            if i >= len(title_links):
                print(f"No more links found. Stopping at {i + 1}")
                break

            # Get the current link
            current_link = title_links[i]

            # Get the job title text
            job_title = current_link.inner_text().strip()
            print(f"Job title: {job_title}")

            # Click on the title link
            print("Clicking on job title...")
            current_link.click()

            # Wait for the detail page to load
            page.wait_for_load_state("networkidle")
            print("Detail page loaded")

            # Wait a moment to see the detail page
            time.sleep(2)

            # Extract the entire table content from the detail page
            try:
                table_element = page.query_selector('table')
                if table_element:
                    html_content = page.content()
                    print(f"Captured table content for job: {job_title}")
                    print(f"Table HTML length: {len(html_content)} characters")

                    time.sleep(2)

                    # Parse the HTML content with BeautifulSoup
                    soup = BeautifulSoup(html_content, 'html.parser')

                    # Find the table
                    table = soup.find('table')

                    # Get all rows from the table body
                    rows = table.find('tbody').find_all('tr')

                    # Initialize variables to store the required data
                    name = ""
                    region = ""
                    email = ""
                    facility_type = ""

                    # Extract data based on row positions
                    # 3rd row: Type (시설유형, only TD text, ignoring span)
                    type_row = rows[2]  # 3rd row (index 2)
                    facility_type = type_row.find('td').contents[0].strip()  # Get only the text before the span

                    # 5th row: Region (소재지)
                    region_row = rows[4]  # 5th row (index 4)
                    region = region_row.find('td').text.strip()

                    # 6th row: Name (담당자명)
                    name_row = rows[5]  # 6th row (index 5)
                    name = name_row.find_all('td')[0].text.strip()  # First TD for 담당자명

                    # 7th row: Email (담당자 이메일)
                    email_row = rows[6]  # 7th row (index 6)
                    email = email_row.find_all('td')[1].text.strip()  # Second TD for 담당자 이메일

                    # Print the extracted data
                    print(f"Name: {name}")
                    print(f"Region: {region}")
                    print(f"Email: {email}")
                    print(f"Type: {facility_type}")

                    # Save data to CSV
                    with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([job_title, name, region, email, facility_type])
                        print(f"Saved data to CSV for job: {job_title}")
                else:
                    print("No table found on detail page")
                    html_content = ""
            except Exception as e:
                print(f"Error extracting table content: {e}")
                html_content = ""

            # Go back to the search results
            print("Going back to search results...")
            page.go_back()
            page.wait_for_load_state("networkidle")

            # Wait a moment before processing the next item
            time.sleep(1)

        except Exception as e:
            print(f"Error processing job listing {i + 1}: {e}")
            try:
                page.go_back()
                page.wait_for_load_state("networkidle")
            except:
                pass
            continue


# Main script with pagination
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Set to True for headless mode
    page = browser.new_page()

    # Navigate to the initial page (replace with your URL)
    page.goto('https://central.childcare.go.kr/ccef/job/JobOfferSlPL.jsp?flag=SlPL')  # Replace with the actual URL
    page.wait_for_load_state("networkidle")

    while True:
        print("\n=== Processing new page ===")

        # Process all job listings on the current page
        title_links = page.query_selector_all('table tbody tr td:nth-child(3) a[onclick*="fnGoBoardSl"]')
        total_listings_per_page = len(title_links)
        process_page(page, total_listings_per_page)

        # Check for the "next" page link
        next_page_link = page.query_selector('a[href="#page_next"][class="next"]')
        if not next_page_link:
            print("No 'Next' button found. Stopping pagination.")
            break

        try:
            # Click the "Next" button
            print("Moving to the next page...")
            next_page_link.click()
            page.wait_for_load_state("networkidle")
            time.sleep(2)  # Allow page to stabilize
        except Exception as e:
            print(f"Error navigating to next page: {e}")
            break

    # Close the browser
    browser.close()