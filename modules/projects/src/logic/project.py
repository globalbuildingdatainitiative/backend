import requests

from models import DBProject, ProjectFilters, ProjectSort, filter_model_query, sort_model_query


async def get_projects(filter_by: ProjectFilters, sort_by: ProjectSort, limit: int, offset: int):

    project_query = filter_model_query(DBProject, filter_by)
    project_query = sort_model_query(DBProject, sort_by, project_query)
    project_query = project_query.limit(limit)

    if offset:
        project_query = project_query.skip(offset)

    return await project_query.to_list()



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


# async def get_projects_counts_by_country() -> list[dict]:
#     #import pydevd_pycharm
#     #pydevd_pycharm.settrace('host.minikube.internal', port=7891, stdoutToServer=True, stderrToServer=True)
#
#     collection: AsyncIOMotorCollection = DBProject.get_motor_collection()
#     pipeline = [
#         {"$group": {
#             "_id": "$location.country",
#             "count": {"$sum": 1}
#         }}
#     ]
#     print("pipeline: ", pipeline)
#
#     distinct_countries = await collection.distinct("location.country")
#     print("Distinct Country: ", distinct_countries)
#
#     cursor = collection.find({}, {"location.country": 1, "_id": 0})
#     all_countries = [doc["location"]["country"] for doc in await cursor.to_list(length=None)]
#     print("All Countries: ", all_countries)
#     results = await collection.aggregate(pipeline).to_list(None)
#
#     print("Results:", results)
#     country_data = []
#     # Fetch coordinates for each country and add to results
#     for result in results:
#         country = result["_id"]
#         print("Country: ", country)
#         count = result["count"]
#         if country:
#             coordinates = await get_coordinates(country)
#             if coordinates:
#                 country_data.append({
#                     "country": country,
#                     "count": count,
#                     "latitude": coordinates["latitude"],
#                     "longitude": coordinates["longitude"]
#                 })
#     print("Country Data: ", country_data)
#     return country_data
