import requests
from bs4 import BeautifulSoup
import json

url = "https://www.salaahtimes.co.uk/Timetable/TodaysTimes"
headers = {'User-Agent': 'Mozilla/5.0'}

def clean_time(t):
    # Remove any extra text like ' (S)' or ' (H)'
    return t.split(' ')[0].strip()

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    data_map = {}
    
    # We look for ALL tables. Usually, Jamaat is the first big table.
    tables = soup.find_all('table')
    
    for table in tables:
        # Check if this table is the 'Beginning Times' table by looking at headers
        header_text = table.get_text().lower()
        if "beginning" in header_text or "sunrise" in header_text:
            continue # Skip this table entirely!
            
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 6:
                continue
                
            name = cols[0].get_text(strip=True)
            if not name or any(word in name.lower() for word in ["masjid", "fajr", "zohar", "asr"]):
                if name.lower() != "masjid aisha": # Keep Aisha if it's there
                    continue

            # Logic to extract the 5 core times based on column count
            # Normal = [Name, F, Z, A, M, I] (6 cols)
            # Expanded = [Name, F, Sunrise, Z, Shafi, A, M, I] (8 cols)
            raw_times = [c.get_text(strip=True) for c in cols[1:]]
            
            if len(cols) == 6: # Standard Jamaat Row
                times = raw_times
            elif len(cols) == 8: # Aisha/Special Row with Sunrise & Shafi
                # We skip index 1 (Sunrise) and index 3 (Shafi Asr)
                times = [raw_times[0], raw_times[2], raw_times[4], raw_times[5], raw_times[6]]
            elif len(cols) == 7: # Special Row with Sunrise only
                times = [raw_times[0], raw_times[2], raw_times[3], raw_times[4], raw_times[5]]
            else:
                continue

            # Validate they look like times (HH:MM)
            if all(":" in t for t in times[:5]):
                data_map[name] = {
                    "name": name,
                    "fajr": clean_time(times[0]),
                    "zohar": clean_time(times[1]),
                    "asr": clean_time(times[2]),
                    "maghrib": clean_time(times[3]),
                    "eisha": clean_time(times[4])
                }

    # Convert to list and save
    final_data = list(data_map.values())
    with open('prayer_times.json', 'w') as f:
        json.dump(final_data, f, indent=2)
    
    print(f"Successfully synced {len(final_data)} Masaajid. Masjid Aisha fixed.")

except Exception as e:
    print(f"Error: {e}")
    exit(1)
