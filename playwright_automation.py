from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import time
import csv
import os

def automate_childcare_website():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)  # Set headless=True if you don't want to see the browser
        page = browser.new_page()
        
        try:
            # Navigate to the website
            print("Opening the website...")
            page.goto("https://central.childcare.go.kr/ccef/job/JobOfferSlPL.jsp?flag=SlPL")
            
            # Wait for the page to load
            page.wait_for_load_state("networkidle")
            print("Website loaded successfully")
            
            # Change the "Deadline" filter to "Hiring" (구인중)
            print("Changing deadline filter to 'Hiring'...")
            page.select_option('#endYn', value='N')
            print("Filter changed successfully")
            
            # Wait a moment for the filter to apply
            time.sleep(1)
            
            # Click the search button
            print("Clicking search button...")
            page.click('a[href="#fnSearch"][onclick*="fnSearch"]')
            print("Search button clicked")
            
            # Wait for search results to load
            page.wait_for_load_state("networkidle")
            print("Search completed successfully")
            
            # Wait for the table to be visible
            page.wait_for_selector('table tbody tr', timeout=10000)
            print("Search results table loaded")
            
            # Get the total number of job listings first
            initial_title_links = page.query_selector_all('table tbody tr td:nth-child(3) a[onclick*="fnGoBoardSl"]')
            total_listings = len(initial_title_links)
            print(f"Found {total_listings} job listings to process")
            
            # Create CSV file and write headers
            csv_filename = "job_listings_data.csv"
            csv_headers = ["Job Title", "Name", "Region", "Email", "Facility Type"]
            
            # Check if file exists to determine if we need to write headers
            file_exists = os.path.exists(csv_filename)
            
            with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write headers only if file doesn't exist
                if not file_exists:
                    writer.writerow(csv_headers)
                    print(f"Created new CSV file: {csv_filename}")
                else:
                    print(f"Appending to existing CSV file: {csv_filename}")
            
            # Process each job listing by index
            for i in range(total_listings):
                try:
                    print(f"\n--- Processing job listing {i+1}/{total_listings} ---")
                    
                    # Re-find the title links after each navigation
                    title_links = page.query_selector_all('table tbody tr td:nth-child(3) a[onclick*="fnGoBoardSl"]')
                    
                    if i >= len(title_links):
                        print(f"No more links found. Stopping at {i+1}")
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
                        # Find the table on the detail page
                        table_element = page.query_selector('table')
                        if table_element:
                            html_content = page.content()
                            print(f"Captured table content for job: {job_title}")
                            print(f"Table HTML length: {len(html_content)} characters")
                            # print(html_content)

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
                            
                            # You can save this to a file or process it further
                            # with open(f"job_{i+1}_table.html", "w", encoding="utf-8") as f:
                            #     f.write(html_content)
                        else:
                            print("No table found on detail page")
                            html_content = ""
                    except Exception as e:
                        print(f"Error extracting table content: {e}")
                        html_content = ""

                    # DRIVE BACK TO THE PAGE
                    # Go back to the previous page
                    print("Going back to search results...")
                    page.go_back()

                    # Re-find the title links after each navigation
                    title_links = page.query_selector_all('table tbody tr td:nth-child(3) a[onclick*="fnGoBoardSl"]')

                    # Wait a moment before processing next item
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error processing job listing {i+1}: {e}")
                    # Try to go back if we're on a detail page
                    try:
                        page.go_back()
                        page.wait_for_load_state("networkidle")
                    except:
                        pass
                    continue
            
            print(f"\nCompleted processing {total_listings} job listings")
            
            # Keep the browser open for a few seconds to see the final results
            time.sleep(5)
            
        except Exception as e:
            print(f"An error occurred: {e}")
        
        finally:
            # Close the browser
            browser.close()
            print("Browser closed")

if __name__ == "__main__":
    automate_childcare_website() 