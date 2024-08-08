from typing import NamedTuple

class Resume(NamedTuple):
    id: int
    city_id: int
    city: str
    position_id: int
    title: str
    salary: int
    currency: str
    specialization: list[str]
    experience_duration: str
    languages: list[str]
    skills: list[str]
    date_update: str
    url: str