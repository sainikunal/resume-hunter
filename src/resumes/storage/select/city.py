import os

from storage.config import connect, TABLE_CITY
from models import City

limit = os.getenv("CITY_LIMIT")
if limit:
    print(f"Limit on the number of cities: {limit}")
else:
    print(f"No limit on the number of cities")

def get_cities() -> list[City]:
    cities: list[City] = []
    connection = connect()
    cursor = connection.cursor()
    query = f"SELECT * FROM {TABLE_CITY} WHERE id_hh != 0 ORDER BY id_hh LIMIT {limit} "
    try:
        cursor.execute(query)
        cities = [City(*i) for i in cursor.fetchall()]
    except BaseException as err:
        print(f"Error fetching cities: {err}")
    finally:
        connection.close()
    return cities