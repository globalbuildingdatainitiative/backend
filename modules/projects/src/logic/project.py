import requests
from models import DBProject


# Function to get coordinates from country name
async def get_coordinates(country_name: str) -> dict:
    response = requests.get(f'https://nominatim.openstreetmap.org/search?q={country_name}&format=json')
    if response.status_code == 200 and response.json():
        return {
            'latitude': float(response.json()[0]['lat']),
            'longitude': float(response.json()[0]['lon'])
        }
    return {}


async def get_projects_counts_by_country() -> list[dict]:
    pipeline = [
        {"$group": {
            "_id": "$stock_region_code",
            "count": {"$sum": 1}
        }}
    ]

    results = await DBProject.get_motor_collection().aggregate(pipeline).to_list(None)

    # Fetch coordinates for each country and add to results
    for result in results:
        coordinates = await get_coordinates(result["_id"])
        result.update(coordinates)

    return results

