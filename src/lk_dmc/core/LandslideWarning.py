from dataclasses import dataclass


@dataclass
class LandslideWarning:
    time_ut_start: int
    time_ut_end: int
    dsd_id_to_threat_level: dict[str, int]
