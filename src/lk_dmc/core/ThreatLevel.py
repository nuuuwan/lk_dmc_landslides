from dataclasses import dataclass


@dataclass
class ThreatLevel:
    level: int
    colour: str
    description: str
    emoji: str = ""

    @classmethod
    def from_level(cls, level: int):
        for threat_level in cls.list_all():
            if threat_level.level == int(level):
                return threat_level
        raise ValueError(f"Invalid threat level: {level}")


ThreatLevel.LEVEL_0 = ThreatLevel(level=0, colour="white", description="🟩")
ThreatLevel.LEVEL_1 = ThreatLevel(
    level=1, colour="yellow", description="watch", emoji="🟡"
)
ThreatLevel.LEVEL_2 = ThreatLevel(
    level=2, colour="orange", description="alert", emoji="🟠"
)
ThreatLevel.LEVEL_3 = ThreatLevel(
    level=3, colour="red", description="evacuate", emoji="🛑"
)


ThreatLevel.list_all = lambda: [
    ThreatLevel.LEVEL_0,
    ThreatLevel.LEVEL_1,
    ThreatLevel.LEVEL_2,
    ThreatLevel.LEVEL_3,
]
