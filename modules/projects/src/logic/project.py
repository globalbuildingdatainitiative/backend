from models import DBProject


async def get_projects() -> list[DBProject]:
    return await DBProject.find_all(fetch_links=True).to_list()
