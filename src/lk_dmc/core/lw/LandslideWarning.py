import os
from dataclasses import asdict, dataclass

from utils import JSONFile, Log

from .LandSlideWarningPDFMixin import LandSlideWarningPDFMixin
from .LandSlideWarningRemoteMixin import LandSlideWarningRemoteMixin

log = Log("LandslideWarning")


@dataclass
class LandslideWarning(LandSlideWarningPDFMixin, LandSlideWarningRemoteMixin):
    date_id: str
    level_to_district_to_dsds: dict[int, dict[str, list[str]]]

    def get_level_to_n_warnings(self) -> dict[int, int]:
        return {
            threat_level: sum(
                len(dsd_id_list) for dsd_id_list in district_to_dsds.values()
            )
            for threat_level, district_to_dsds in self.level_to_district_to_dsds.items()  # noqa: E501
        }

    def len(self) -> int:
        return sum(self.get_level_to_n_warnings().values())

    @classmethod
    def get_json_path(cls, date_id) -> str:
        decade = date_id[0:3] + "0s"
        year = date_id[0:4]
        year_and_month = date_id[0:7]
        return os.path.join(
            cls.DIR_DATA_JSONS,
            decade,
            year,
            year_and_month,
            f"{date_id}.json",
        )

    @property
    def json_path(self) -> str:
        return self.get_json_path(self.date_id)

    @classmethod
    def from_json(cls, json_path) -> "LandslideWarning":
        d = JSONFile(json_path).read()
        return cls(**d)

    @classmethod
    def __get_all_json_paths__(cls):
        json_paths = []
        for dirpath, _, filenames in os.walk(cls.DIR_DATA_JSONS):
            for filename in filenames:
                if filename.endswith(".json"):
                    json_paths.append(os.path.join(dirpath, filename))
        return sorted(json_paths)

    @classmethod
    def list_all(cls):
        json_paths = cls.__get_all_json_paths__()
        lw_list = [cls.from_json(json_path) for json_path in json_paths]
        lw_list.sort(key=lambda lw: lw.date_id, reverse=True)
        return lw_list

    @classmethod
    def aggregate(cls):
        lw_list = cls.list_all()
        json_path = os.path.join(cls.DIR_DATA, "all.json")
        json_file = JSONFile(json_path)
        json_file.write([asdict(lw) for lw in lw_list])
        log.info(f"Wrote  {json_file}")

        latest = lw_list[0]
        json_path_latest = os.path.join(cls.DIR_DATA, "latest.json")
        json_file_latest = JSONFile(json_path_latest)
        json_file_latest.write(asdict(latest))
        log.info(f"Wrote {json_file_latest}")
