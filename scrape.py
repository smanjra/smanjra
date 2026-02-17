import requests
from bs4 import BeautifulSoup
import json
import os

# 1. Fetch the page
url = "https://www.salaahtimes.co.uk/Timetable/NextPrayerTime"
headers = {'User-Agent': 'Mozilla/5.0'} # Pretend to be a browser
try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    # 2. Parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the table rows. 
    # Based on the website structure, we look for the main table rows
    data = []
    
    # The site often uses a table structure. We target the specific rows.
    # Note: Selectors might need adjustment if the site changes.
    rows = soup.select('tr') 
    
    for row in rows:
        cols = row.find_all('td')
        # We need rows that have at least 2 columns (Mosque Name + Time)
        if len(cols) >= 2:
            name = cols[0].get_text(strip=True)
            time = cols[1].get_text(strip=True)
            
            # Simple filter to ensure it's a valid row (contains a time format like : )
            if ":" in time and len(time) <= 6:
                data.append({
                    "name": name,
                    "time": time
                })

    # 3. Save to JSON
    with open('prayer_times.json', 'w') as f:
        json.dump(data, f, indent=2)
        
    print(f"Successfully scraped {len(data)} mosques.")

except Exception as e:
    print(f"Error scraping data: {e}")
    exit(1)
