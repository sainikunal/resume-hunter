import logging

from storage import connect
from storage.config import TABLE_EXPERIENCE_STEP
from models import ExperienceStep


def add_experience(experience_steps: list[ExperienceStep]):
    connection = connect()
    try:
        for step in experience_steps:
            cursor = connection.cursor()
            query = f"""INSERT INTO {TABLE_EXPERIENCE_STEP} (resume_id, post, duration_in_months, interval, branch, subbranch)
                        VALUES (%s, %s, %s, %s, %s, %s)""",
            data = (step.resume_id, step.post, step.duration_in_months, step.interval, '|'.join(step.branch), '|'.join(step.subbranch))
            cursor.execute(query, data)
            connection.commit()
            logging.info(f"Successfully added experience: {step.resume_id}: {step.post}")
    except Exception as err:
        logging.error(f"Failed to save experience: {err}")
    finally:
        connection.close()

