from storage.config import connect, TABLE_POSITION
from models import Position

def get_positions() -> list[Position]:
    connection = connect()
    cursor = connection.cursor()
    query = f"SELECT id, parent_id, level, title, prof_area, other_names FROM {TABLE_POSITION} WHERE parsed = FALSE"
    cursor.execute(query)
    positions = [Position(*i) for i in cursor.fetchall()]
    connection.close()
    return positions

def set_parsed_to_profession(profession_id: int) -> None:
    connection = connect()
    cursor = connection.cursor()
    query = f"UPDATE {TABLE_POSITION} SET parsed = TRUE WHERE id = {profession_id}"
    cursor.execute(query)
    connection.commit()
    connection.close()