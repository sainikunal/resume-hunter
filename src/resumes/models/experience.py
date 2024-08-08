from typing import NamedTuple

class ExperienceStep(NamedTuple):
    resume_id: int
    post: str
    duration: int
    interval: str
    branch: str
    subbranch: str