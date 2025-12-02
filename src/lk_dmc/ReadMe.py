"""README generator for landslide warnings."""

from gig import Ent
from utils import File, Log

from lk_dmc.core.lw.LandslideWarning import LandslideWarning
from lk_dmc.core.ThreatLevel import ThreatLevel

log = Log("ReadMe")


class ReadMe:
    PATH = "README.md"
    URL_LWS = (
        "https://www.dmc.gov.lk/index.php"
        + "?option=com_dmcreports&view=reports"
        + "&Itemid=276&report_type_id=5&lang=en"
    )

    def __init__(self):
        self.lw_list = LandslideWarning.list_all()

    def get_lines_for_header(self) -> list[str]:
        return [
            "# 🇱🇰 Sri Lanka: Landslide Warnings\n",
            "",
            f"From the [Disaster Management Centre]({self.URL_LWS}).",
            "",
        ]

    def get_lines_for_latest(self) -> list[str]:
        latest_lw = self.lw_list[-1]
        lines = [
            f"## Latest Warnings ({latest_lw.date_id})",
            "",
        ]

        for (
            level,
            district_to_dsds,
        ) in latest_lw.level_to_district_to_dsds.items():
            threat_level = ThreatLevel.from_level(level)
            lines.extend(
                [
                    f"### {threat_level.emoji}"
                    + f' Level {level} - "{threat_level.description}"',
                    "",
                ]
            )
            for district_id, dsd_id_list in district_to_dsds.items():
                ent_district = Ent.from_id(district_id)
                lines.extend(
                    [f"#### `{district_id}` {ent_district.name}", ""]
                )
                for dsd_id in dsd_id_list:
                    ent_dsd = Ent.from_id(dsd_id)
                    lines.append(f"- `{dsd_id}` {ent_dsd.name}")
                lines.append("")
        return lines

    def get_lines(self) -> str:
        return self.get_lines_for_header() + self.get_lines_for_latest()

    def build(self) -> None:
        lines = self.get_lines()
        readme_file = File(self.PATH)
        readme_file.write_lines(lines)
        log.info(f"Wrote {readme_file}")
