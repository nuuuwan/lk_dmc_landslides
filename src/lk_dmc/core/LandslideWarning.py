import os
from dataclasses import dataclass
from urllib.request import urlretrieve

from utils import File, Log, TSVFile

log = Log("LandslideWarning")


@dataclass
class LandslideWarning:
    time_ut_start: int
    time_ut_end: int
    dsd_id_to_threat_level: dict[str, int]

    DIR_DATA = "data"
    DIR_DATA_PDFS = os.path.join(DIR_DATA, "pdfs")
    URL_BASE = (
        "https://raw.githubusercontent.com"
        + "/nuuuwan/lk_dmc/refs/heads/data_lk_dmc_landslide_warnings"
        + "/data/lk_dmc_landslide_warnings"
    )
    N_METADATA_ITEMS = 10

    @classmethod
    def get_metadata_list(cls) -> list[dict]:
        url_remote_metadata_list = cls.URL_BASE + "/docs_last100.tsv"
        local_metadata_tsv_path = os.path.join(
            cls.DIR_DATA, "docs_last100.tsv"
        )

        os.makedirs(cls.DIR_DATA, exist_ok=True)
        urlretrieve(url_remote_metadata_list, local_metadata_tsv_path)

        metadata_tsv_file = TSVFile(local_metadata_tsv_path)
        metadata_list = metadata_tsv_file.read()
        log.info(f"Wrote {len(metadata_list)} items to {metadata_tsv_file}")
        return metadata_list

    @classmethod
    def from_pdf(cls, pdf_path):
        return cls(
            time_ut_start=0,
            time_ut_end=0,
            dsd_id_to_threat_level={},
        )

    @classmethod
    def from_metadata(cls, metadata: dict) -> "LandslideWarning":
        doc_id = metadata["doc_id"]
        date_str = metadata["date_str"]
        year = date_str[0:4]
        decade = date_str[0:3] + "0s"

        url_remote_pdf = cls.URL_BASE + f"/{decade}/{year}/{doc_id}/doc.pdf"
        year_and_month = date_str[0:7]
        dir_pdf = os.path.join(
            cls.DIR_DATA_PDFS, decade, year, year_and_month
        )
        os.makedirs(dir_pdf, exist_ok=True)
        pdf_path = os.path.join(dir_pdf, f"{date_str}.pdf")
        if not os.path.exists(pdf_path):
            urlretrieve(url_remote_pdf, pdf_path)
            log.debug(f"Downloaded {File(pdf_path)}")
        return cls.from_pdf(pdf_path)

    @classmethod
    def list_from_remote(cls):
        metadata_list = cls.get_metadata_list()[: cls.N_METADATA_ITEMS]
        return [cls.from_metadata(metadata) for metadata in metadata_list]
