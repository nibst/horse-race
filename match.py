from typing import List
from horse_result import HorseResult
from dataclasses import dataclass
"""Data class for a Horse Match"""
@dataclass
class Match:
    id: int
    sequence_number: int
    results: List[HorseResult]    
        

