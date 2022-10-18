import json
from urllib.request import urlopen

import yaml
from django.conf import settings

from ...utils.logger import ApplicationLogger


class DataPull:
    def __init__(self):
        self.logger = ApplicationLogger()

    def pull_indices_market_cap(self, record: dict) -> dict | None:
        temp_folder = settings.TEMP_DIR  # temp folder to store files

        if "url" not in record:
            self.logger.log_debug("No url exists for '%s'." % record["name"])
            return None

        # get indices details
        index_url = record["url"]
        index_name = str(record["name"])
        sector_name_file_name = index_name.replace(" ", "_")

        self.logger.log_debug(f"Started with {index_name}, {index_url}.")
        with urlopen(index_url) as webpage:
            content = (
                webpage.read()
                .decode()
                .replace("'", "||||")
                .replace("modelDataAvailable(", "[")
                .replace(");", "]")
                .replace("label:", '"label":')
                .replace("label:", '"label":')
                .replace("file:", '"file":')
            )

            url_temp = f"{temp_folder}/{sector_name_file_name}_temp.json"

            with open(url_temp, "w") as file_intermediate:
                # Writing the replaced data in our
                # text file
                file_intermediate.write(
                    json.dumps(content, ensure_ascii=True, indent=4).replace(
                        '\\"', '"'
                    )[1:-1]
                )

            with open(url_temp) as file_intermediate2:
                # Writing the replaced data in our
                # text file
                data = yaml.safe_load(file_intermediate2)

            with open(url_temp, "w") as file_final:
                # Writing the replaced data in our
                # text file
                file_final.write(str(data).replace("'", '"').replace("||||", "'"))

            with open(url_temp) as file_final2:
                # Writing the replaced data in our
                # text file
                return json.load(file_final2)

    # def parse_indices_market_cap(self, records:dict):
    #     for record in records:
    #         pass

    # try:
    #     df = pd.json_normalize(
    #         data_updated[0]["groups"],
    #         "groups",
    #         ["label", "weight", "id"],
    #         record_prefix="_",
    #     )
    #     df["label"] = df["label"].str.rsplit(" ", n=1).str.get(0)
    #     df["_label"] = df["_label"].str.rsplit(" ", n=1).str.get(0)
    #     df = df.assign(name=indice_name)
    #     df = df.assign(indice_symbol=indice_symbol)
    #     df = df.assign(is_sector=indice_is_sectoral)
    #     df.rename(
    #         columns={
    #             "_label": "symbol",
    #             "_weight": "equity_weightage",
    #             "label": "sector_name",
    #             "weight": "sector_weightage",
    #         },
    #         inplace=True,
    #     )  # rename the column name
    # except Exception:
    #     # exception will be thrown if there is no nested records
    #     df = pd.DataFrame(data_updated[0]["groups"])
    #     df["label"] = df["label"].str.rsplit(" ", n=1).str.get(0)
    #     df = df.assign(sector_name=indice_name.replace("_", " "))
    #     df = df.assign(name=indice_name)
    #     df = df.assign(indice_symbol=indice_symbol)
    #     df = df.assign(sector_weightage=100)
    #     df = df.assign(is_sector=indice_is_sectoral)
    #     df.rename(
    #         columns={"label": "symbol", "weight": "equity_weightage"},
    #         inplace=True,
    #     )  # rename the column name

    # self.logger.log_debug(f"{df.count}")
    # return df
