import requests
from bs4 import BeautifulSoup
import json

url = "https://www.salaahtimes.co.uk/Timetable/TodaysTimes"
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    data_map = {} # Using a map to handle duplicates
    rows = soup.select('tr') 
    
    # Expanded list of keywords that indicate a non-jamaat row
    blacklist = [
        "beginning", "sunrise", "start", "sehri", "sunset", 
        "zawal", "imsak", "subah", "sadiq", "timetable", "jamaat"
    ]
    
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 6:
            # Clean up the mosque name
            name = cols[0].get_text(" ", strip=True)
            
            # 1. Skip if the name contains a blacklist word
            if any(word in name.lower() for word in blacklist):
                continue
            
            # 2. Extract times
            times = [c.get_text(strip=True) for c in cols[1:6]]
            
            # 3. Validation: All 5 slots must look like HH:MM
            if all(":" in t and len(t) <= 5 for t in times):
                # If we already have this masjid, we check if the new row 
                # looks 'more' like jamaat times (website specific quirk)
                # Usually, the jamaat times appear later in the HTML.
                data_map[name] = {
                    "name": name,
                    "fajr": times[0],
                    "zohar": times[1],
                    "asr": times[2],
                    "maghrib": times[3],
                    "eisha": times[4]
                }

    # Convert map back to list
    final_data = list(data_map.values())

    with open('prayer_times.json', 'w') as f:
        json.dump(final_data, f, indent=2)
        
    print(f"Successfully cleaned and scraped {len(final_data)} mosques.")

except Exception as e:
    print(f"Error: {e}")
    exit(1)
