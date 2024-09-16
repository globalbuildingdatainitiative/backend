import json
import time
from pathlib import Path
import httpx
from lcax import Country
from iso3166 import countries

def write_country_cache():
    location_data = {}
    out_path = Path(__file__).parent / "country_cache.json"

    for country in Country:
        name = country.value
        loaded_data = json.loads(out_path.read_text())
        if loaded_data.get(name) or name == "unknown":
            continue
        country_name = countries.get(name).name.lower()
        print(f"Getting location data for {name} - {country_name}")
        response = httpx.get(f"https://nominatim.openstreetmap.org/search?q={country_name}&format=json")
        data = response.json()
        if not data:
            print(f"Could not get location data for {country_name}({name}) - {data}")
            continue
        data = data[0]
        location_data[name] = {"latitude": float(data["lat"]), "longitude": float(data["lon"])}
        out_path.write_text(json.dumps(location_data, indent=2))
        time.sleep(0.02)





if __name__ == "__main__":
    write_country_cache()