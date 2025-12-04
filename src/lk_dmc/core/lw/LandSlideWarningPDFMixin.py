import os
from dataclasses import asdict

import camelot
from gig import Ent, EntType
from utils import JSONFile, Log

log = Log("LandslideWarning")


class LandSlideWarningPDFMixin:
    @staticmethod
    def __parse_district_name__(x) -> str:
        return x[0].replace("\n", "").strip()

    @staticmethod
    def __get_extra_dsd_names__(dsd_names_all: list[str]) -> list[str]:
        # Hack
        extra_dsd_names = []

        before_to_after = {
            "Kotmale": "Kotmale",
            "Mathurata": "Hanguranketha",
            "Thalawakele": "Nuwara Eliya",
            "Nildandahinna": "Walapane",
            "Gangawata Korale": "Kandy Four Gravets & Gangawata Korale",
        }

        for dsd_name in dsd_names_all:
            for before, after in before_to_after.items():
                if before in dsd_name:
                    extra_dsd_names.append(after)
        return extra_dsd_names

    @staticmethod
    def __parse_dsd_name_list__(x) -> str:
        dsd_names_all = []
        for line in x.split("\n"):
            line = line.replace("↓", "")
            line = line.strip()
            if line.endswith(" and"):
                line = line[:-4]
            line = line.replace(" and ", ",")
            dsd_names = line.split(",")
            dsd_names = [name.strip() for name in dsd_names if name.strip()]
            dsd_names_all.extend(dsd_names)

        extra_dsd_names = LandSlideWarningPDFMixin.__get_extra_dsd_names__(
            dsd_names_all
        )
        return list(set(dsd_names_all + extra_dsd_names))

    @staticmethod
    def __get_district_entity__(
        district_name: str, prev_ent_district
    ) -> tuple:
        cand_ent_districts = Ent.list_from_name_fuzzy(
            name_fuzzy=district_name,
            filter_ent_type=EntType.DISTRICT,
        )
        if len(cand_ent_districts) != 1:
            if not prev_ent_district:
                return None, prev_ent_district
            return prev_ent_district, prev_ent_district
        return cand_ent_districts[0], cand_ent_districts[0]

    @staticmethod
    def __get_dsd_entities__(
        dsd_names: list[str], district_id: str
    ) -> list[Ent]:
        ent_dsds = []
        for dsd_name in dsd_names:
            cand_ent_dsds = Ent.list_from_name_fuzzy(
                name_fuzzy=dsd_name,
                filter_ent_type=EntType.DSD,
                filter_parent_id=district_id,
            )
            if len(cand_ent_dsds) >= 1:
                ent_dsds.append(cand_ent_dsds[0])
        return ent_dsds

    @classmethod
    def __process_threat_level__(
        cls,
        row_values: list,
        threat_level: int,
        district_id: str,
        level_to_district_to_dsds: dict,
    ) -> None:
        if threat_level not in level_to_district_to_dsds:
            level_to_district_to_dsds[threat_level] = {}

        dsd_names = cls.__parse_dsd_name_list__(row_values[threat_level])
        ent_dsds = cls.__get_dsd_entities__(dsd_names, district_id)
        dsd_ids = [ent_dsd.id for ent_dsd in ent_dsds]
        if not dsd_ids:
            return

        if district_id not in level_to_district_to_dsds[threat_level]:
            level_to_district_to_dsds[threat_level][district_id] = []
        level_to_district_to_dsds[threat_level][district_id].extend(dsd_ids)

    @classmethod
    def __process_table_row__(
        cls,
        row_values: list,
        prev_ent_district,
        level_to_district_to_dsds: dict,
    ) -> tuple:
        if len(row_values) != 4:
            return prev_ent_district

        district_name = cls.__parse_district_name__(row_values)
        ent_district, prev_ent_district = cls.__get_district_entity__(
            district_name, prev_ent_district
        )

        if not ent_district:
            return prev_ent_district

        district_id = ent_district.id
        for i_col in [1, 2, 3]:
            cls.__process_threat_level__(
                row_values,
                i_col,
                district_id,
                level_to_district_to_dsds,
            )

        return prev_ent_district

    @staticmethod
    def __read_pdf_tables__(pdf_path: str):
        """Read tables from PDF file using Camelot."""
        tables = camelot.read_pdf(pdf_path, pages="all", flavor="lattice")
        if not tables:
            log.error(f"No tables found in {pdf_path}")
            return None
        return tables

    @classmethod
    def __process_all_tables__(
        cls, tables
    ) -> dict[int, dict[str, list[str]]]:
        """Process all tables and build the district to DSDs mapping."""
        level_to_district_to_dsds = {}
        prev_ent_district = None

        for table in tables:
            df = table.df
            for _, row in df.iterrows():
                row_values = row.tolist()
                prev_ent_district = cls.__process_table_row__(
                    row_values, prev_ent_district, level_to_district_to_dsds
                )

        return level_to_district_to_dsds

    @staticmethod
    def __sort_dsd_lists__(level_to_district_to_dsds: dict) -> None:
        """Sort all DSD lists in place."""
        for level, district_dict in level_to_district_to_dsds.items():
            for district_id, dsd_list in district_dict.items():
                dsd_list = list(set(dsd_list))
                level_to_district_to_dsds[level][district_id] = sorted(
                    dsd_list
                )

    @classmethod
    def __extract_tables_from_pdf__(
        cls, pdf_path: str
    ) -> dict[int, dict[str, list[str]]]:
        """Extract and process all tables from PDF."""
        tables = cls.__read_pdf_tables__(pdf_path)
        if not tables:
            return None

        level_to_district_to_dsds = cls.__process_all_tables__(tables)
        cls.__sort_dsd_lists__(level_to_district_to_dsds)

        return level_to_district_to_dsds

    @classmethod
    def __save_to_json__(cls, lw, json_path: str) -> None:
        dir_json_path = os.path.dirname(json_path)
        os.makedirs(dir_json_path, exist_ok=True)
        json_file = JSONFile(json_path)
        json_file.write(asdict(lw))
        log.info(f"Wrote {json_file}")

    @classmethod
    def from_pdf(cls, pdf_path, force_parse_pdf=False):
        date_id = os.path.basename(pdf_path)[:-4]
        json_path = cls.get_json_path(date_id)

        if not force_parse_pdf and os.path.exists(json_path):
            return cls.from_json(json_path)

        level_to_district_to_dsds = cls.__extract_tables_from_pdf__(pdf_path)

        if level_to_district_to_dsds is None:
            return None

        lw = cls(
            date_id=date_id,
            level_to_district_to_dsds=level_to_district_to_dsds,
        )
        cls.__save_to_json__(lw, json_path)
        return lw
