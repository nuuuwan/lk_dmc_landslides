import os
from urllib.request import urlretrieve

from utils import File, Log, TSVFile

log = Log("LandslideWarning")


class LandSlideWarningRemoteMixin:
    DIR_DATA = "data"
    DIR_DATA_PDFS = os.path.join(DIR_DATA, "pdfs")
    DIR_DATA_JSONS = os.path.join(DIR_DATA, "jsons")
    URL_BASE = (
        "https://raw.githubusercontent.com"
        + "/nuuuwan/lk_dmc/refs/heads/data_lk_dmc_landslide_warnings"
        + "/data/lk_dmc_landslide_warnings"
    )
    N_METADATA_ITEMS = 10

    @classmethod
    def get_metadata_list(cls) -> list[dict]:
        url_remote_metadata_list = cls.URL_BASE + "/docs_all.tsv"
        local_metadata_tsv_path = os.path.join(cls.DIR_DATA, "docs_all.tsv")

        os.makedirs(cls.DIR_DATA, exist_ok=True)
        urlretrieve(url_remote_metadata_list, local_metadata_tsv_path)

        metadata_tsv_file = TSVFile(local_metadata_tsv_path)
        metadata_list = metadata_tsv_file.read()
        log.info(f"Wrote {len(metadata_list):,} items to {metadata_tsv_file}")
        return metadata_list

    @classmethod
    def from_metadata(cls, metadata: dict):
        doc_id = metadata["doc_id"]
        date_str = metadata["date_str"]
        year = date_str[0:4]
        decade = date_str[0:3] + "0s"

        url_remote_pdf = cls.URL_BASE + f"/{decade}/{year}/{doc_id}/doc.pdf"
        year_and_month = date_str[0:7]
        dir_pdf = os.path.join(cls.DIR_DATA_PDFS, decade, year, year_and_month)
        os.makedirs(dir_pdf, exist_ok=True)
        pdf_path = os.path.join(dir_pdf, f"{date_str}.pdf")
        if not os.path.exists(pdf_path):
            urlretrieve(url_remote_pdf, pdf_path)
            log.debug(f"Wrote {File(pdf_path)}")
        try:
            return cls.from_pdf(pdf_path)
        except Exception as e:
            log.error(
                f"Failed to parse LandslideWarning from {File(pdf_path)}: {e}"
            )
            return None

    @classmethod
    def list_from_remote(cls, n_limit: int):
        metadata_list = cls.get_metadata_list()
        if n_limit is not None and len(metadata_list) > n_limit:
            metadata_list = metadata_list[:n_limit]

        lw_list = [cls.from_metadata(metadata) for metadata in metadata_list]
        lw_list = [lw for lw in lw_list if lw is not None]
        return lw_list
