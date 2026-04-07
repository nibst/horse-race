from typing import List
from dataclasses import dataclass
from domain.match import Match
@dataclass
class Race:
    date: str
    matches: List[Match]
