import requests
from bs4 import BeautifulSoup
import json

url = "https://www.salaahtimes.co.uk/Timetable/TodaysTimes"
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    data = []
    rows = soup.select('tr') 
    
    # Keywords to ignore to ensure we only get Jamaat times
    ignore_keywords = ["beginning", "sunrise", "start", "sehri", "sunset"]
    
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 6:
            name = cols[0].get_text(strip=True)
            
            # Skip rows that are clearly not mosque Jamaat times
            if any(key in name.lower() for key in ignore_keywords):
                continue

            times = [c.get_text(strip=True) for c in cols[1:6]]
            
            # Ensure the row actually contains valid looking times
            if all(":" in t for t in times):
                data.append({
                    "name": name,
                    "fajr": times[0],
                    "zohar": times[1],
                    "asr": times[2],
                    "maghrib": times[3],
                    "eisha": times[4]
                })

    with open('prayer_times.json', 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Scraped {len(data)} mosques.")

except Exception as e:
    print(f"Error: {e}")
    exit(1)
