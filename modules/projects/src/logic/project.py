import requests
from motor.motor_asyncio import AsyncIOMotorCollection

from models import DBProject, ProjectFilters, ProjectSortOptions, GraphQLProject


# Function to get coordinates from country name
async def get_coordinates(country_name: str) -> dict:
    variations = [
        country_name,
        country_name.lower(),
        country_name.upper()
    ]

    for variation in variations:
        response = requests.get(f'https://nominatim.openstreetmap.org/search?q={variation}&format=json')
        if response.status_code == 200 and response.json():
            return {
                'latitude': float(response.json()[0]['lat']),
                'longitude': float(response.json()[0]['lon'])
            }
    return {}


async def get_projects_counts_by_country() -> list[dict]:
    #import pydevd_pycharm
    #pydevd_pycharm.settrace('host.minikube.internal', port=7891, stdoutToServer=True, stderrToServer=True)

    collection: AsyncIOMotorCollection = DBProject.get_motor_collection()
    pipeline = [
        {"$group": {
            "_id": "$location.country",
            "count": {"$sum": 1}
        }}
    ]
    print("pipeline: ", pipeline)

    distinct_countries = await collection.distinct("location.country")
    print("Distinct Country: ", distinct_countries)

    cursor = collection.find({}, {"location.country": 1, "_id": 0})
    all_countries = [doc["location"]["country"] for doc in await cursor.to_list(length=None)]
    print("All Countries: ", all_countries)
    results = await collection.aggregate(pipeline).to_list(None)

    print("Results:", results)
    country_data = []
    # Fetch coordinates for each country and add to results
    for result in results:
        country = result["_id"]
        print("Country: ", country)
        count = result["count"]
        if country:
            coordinates = await get_coordinates(country)
            if coordinates:
                country_data.append({
                    "country": country,
                    "count": count,
                    "latitude": coordinates["latitude"],
                    "longitude": coordinates["longitude"]
                })
    print("Country Data: ", country_data)
    return country_data


async def get_projects(filters: ProjectFilters = None, sort: ProjectSortOptions = None) -> list[GraphQLProject]:
    collection: AsyncIOMotorCollection = DBProject.get_motor_collection()

    query = {}
    if filters:
        if filters.country:
            query['location.country'] = filters.country
        if filters.city:
            query['location.city'] = filters.city
        if filters.classification_system:
            query['classificationSystem'] = filters.classification_system
        if filters.project_phase:
            query['projectPhase'] = filters.project_phase

    cursor = collection.find(query)

    if sort:
        sort_order = 1 if sort.order == 'asc' else -1
        cursor = cursor.sort(sort.field, sort_order)

    projects = [GraphQLProject(**doc) for doc in await cursor.to_list(length=None)]
    return projects
