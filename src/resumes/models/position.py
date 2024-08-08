from typing import NamedTuple

class Position(NamedTuple):
    id: int
    parent_id: int
    level: int
    title: str
    prof_area: str
    other_names: str