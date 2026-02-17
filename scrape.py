import requests
from bs4 import BeautifulSoup
import json

# We use the "TodaysTimes" page which lists the full grid
url = "https://www.salaahtimes.co.uk/Timetable/TodaysTimes"
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    data = []
    
    # The table usually has rows with: Name | Fajr | Zohar | Asr | Maghrib | Eisha
    rows = soup.select('tr') 
    
    for row in rows:
        cols = row.find_all('td')
        # We need rows with enough columns (Masjid Name + 5 prayers)
        if len(cols) >= 6:
            name = cols[0].get_text(strip=True)
            fajr = cols[1].get_text(strip=True)
            zohar = cols[2].get_text(strip=True)
            asr = cols[3].get_text(strip=True)
            maghrib = cols[4].get_text(strip=True)
            eisha = cols[5].get_text(strip=True)
            
            # Basic validation: ensure the "time" looks like a time (contains :)
            if ":" in fajr:
                data.append({
                    "name": name,
                    "fajr": fajr,
                    "zohar": zohar,
                    "asr": asr,
                    "maghrib": maghrib,
                    "eisha": eisha
                })

    with open('prayer_times.json', 'w') as f:
        json.dump(data, f, indent=2)
        
    print(f"Successfully scraped {len(data)} mosques.")

except Exception as e:
    print(f"Error: {e}")
    exit(1)
