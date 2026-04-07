from dataclasses import dataclass
@dataclass
class HorseResult:
    placement: int
    name: str
    trainer: str
    jockey: str
    owner: str
    breeder: str
    sex: str
    weight: float = 0.0
    odds: float = 0.0
    age: int = 0
