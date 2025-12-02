from dataclasses import dataclass


@dataclass
class ThreatLevel:
    level: int
    colour: str
    description: str


ThreatLevel.LEVEL_0 = ThreatLevel(level=0, colour="white", description="")
ThreatLevel.LEVEL_1 = ThreatLevel(
    level=1, colour="yellow", description="watch"
)
ThreatLevel.LEVEL_2 = ThreatLevel(
    level=2, colour="orange", description="alert"
)
ThreatLevel.LEVEL_3 = ThreatLevel(
    level=3, colour="red", description="evaluate"
)
