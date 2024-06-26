import requests
from motor.motor_asyncio import AsyncIOMotorCollection

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
    collection: AsyncIOMotorCollection = DBProject.get_motor_collection()
    pipeline = [
        {"$group": {
            "_id": "$location_country",
            "count": {"$sum": 1}
        }}
    ]

    results = await collection.aggregate(pipeline).to_list(None)

    print(results)
    country_data = []
    # Fetch coordinates for each country and add to results
    for result in results:
        country = result["_id"]
        count = result["count"]
        coordinates = await get_coordinates(country)
        if coordinates:
            country_data.append({
                "country": country,
                "count": count,
                "latitude": coordinates["latitude"],
                "longitude": coordinates["longitude"]
            })

    return country_data
