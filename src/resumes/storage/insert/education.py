import logging

from storage import connect
from storage.config import TABLE_EDUCATION, TABLE_ADDITIONAL
from models import Education

def add_education(education_list: list[Education], table: str = TABLE_EDUCATION):
    connection = connect()
    try:
        for education in education_list:
            cursor = connection.cursor()
            query = f"""INSERT INTO {table} (resume_id, title, direction, year_grade)
                        VALUES (%s, %s, %s, %s)""",
            data = (education.resume_id, education.title, education.direction if education.direction is not None else "null", education.year_of_release if education.year_of_release is not None else "null")
            cursor.execute(query, data)
            connection.commit()
            logging.info(f"Successfully added education: {education.resume_id}")
    except Exception as err:
        logging.error(f"Failed to save education: {err}")
    finally:
        connection.close()

def add_additional(additional: Education):
    add_education(education_list=[additional], table=TABLE_ADDITIONAL)
