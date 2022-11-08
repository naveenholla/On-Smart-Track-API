import codecs
import csv

import pandas as pd
import requests

from .logger import ApplicationLogger


class LogicHelper:
    logger = ApplicationLogger()

    @staticmethod
    def populate_create_update_records(data, database_entity):
        # Let's define two lists:
        # - one to hold the values that we want to insert,
        # - and one to hold the new values alongside existing primary keys to update
        records_to_create = []
        records_to_update = []

        # This is where we check if the records are pre-existing,
        # and add primary keys to the objects if they do
        records = [
            {
                "id": database_entity.backend.unique_search(record).first().id
                if database_entity.backend.unique_search(record).first() is not None
                else None,
                **record,
            }
            for record in data
        ]

        LogicHelper.logger.log_debug("Added the existing records ids.")

        # This is where we delegate our records to our split lists:
        # - if the record already exists in the DB (the 'id' primary key), add it to the update list.
        # - Otherwise, add it to the create list.
        [
            records_to_update.append(record)
            if record["id"] is not None
            else records_to_create.append(record)
            for record in records
        ]

        LogicHelper.logger.log_debug("Added the records to the lists.")

        # Remove the 'id' field, as these will all hold a value of None,
        # since these records do not already exist in the DB
        [record.pop("id") for record in records_to_create]

        LogicHelper.logger.log_debug("Removed the id from new records.")

        records_to_create = [database_entity(**values) for values in records_to_create]
        records_to_update = [database_entity(**values) for values in records_to_update]

        return records_to_create, records_to_update

    @staticmethod
    def pull_data_from_external_api(record, headers=None, url=None):
        try:
            data = None

            if url is None:
                url = record["url"]

            parent_website = (
                record["parent_website"] if "parent_website" in record else None
            )
            LogicHelper.logger.log_debug(f"Started with [{url}].")
            session = requests.Session()
            session.headers.update(headers)

            if parent_website is not None:
                session.get(parent_website)

            res = session.get(url)

            if res.status_code == 200:
                data = res.json()
                LogicHelper.logger.log_debug("Got the Data.")
        finally:
            session.close()

        return data

    @staticmethod
    def reading_csv_raw(url: str, timeout=100, skiprows=0):
        """This task is used to pull the data from the website"""

        LogicHelper.logger.log_debug(f"Started with {url}.")
        try:
            # fetch page source using requests.get()
            res = requests.get(url, stream=True, timeout=timeout)
            if res.status_code == 200:
                LogicHelper.logger.log_debug(f"Got the success response from {url}.")

                # create an iterator for all lines
                lines_iterator = res.iter_lines()

                # create a CSV reader object and encode the content using the codecs module
                reader = csv.reader(
                    codecs.iterdecode(lines_iterator, encoding="utf-8"), delimiter=","
                )

                # reding the data from stream
                data = list(reader)
                if len(data) > skiprows:
                    header = [i.strip() for i in data[skiprows]]
                    rows = data[(skiprows + 1) :]  # noqa E203

                    data = [dict(zip(header, v)) for v in rows]

                LogicHelper.logger.log_debug(f"{len(data)} records found from {url}.")
                return data

            elif res.status_code == 429:
                message = f"Too many reconnects from {url}."
                LogicHelper.logger.log_critical(message=message)
                raise
            else:
                message = f"Unhandled status `{format(res.status_code)}` retreived from {url}."
                LogicHelper.logger.log_critical(message=message)
                raise

        except requests.exceptions.Timeout:
            message = f"Timed-out exception from {url}."
            LogicHelper.logger.log_critical(message=message)
            raise
        except requests.exceptions.RequestException as e:
            message = f"Request exception from {url} - `{format(e)}`."
            LogicHelper.logger.log_critical(message=message)
            raise

    @staticmethod
    def reading_csv_pandas_web(url: str, header=0, skiprows=None, delimiter: str = ","):
        """This task is used to pull the data from the website"""

        LogicHelper.logger.log_debug(f"Started with {url}.")
        try:
            # fetch page source using pandas
            data = pd.read_csv(
                url,
                sep=delimiter,
                skiprows=skiprows,
                skipfooter=0,
                header=header,
                encoding="ISO-8859-1",
                lineterminator="\n",
            )
            LogicHelper.logger.log_debug(f"{len(data)} records found from {url}.")
            return data
        except Exception as e:
            message = f"Request exception from {url} - `{format(e)}`."
            LogicHelper.logger.log_critical(message=message)
            raise

    @staticmethod
    def reading_csv_pandas(path: str, header=0, skiprows=None, delimiter: str = ","):
        """This task is used to pull the data from the website"""

        LogicHelper.logger.log_debug(f"Started with {path}.")
        try:
            # fetch page source using pandas
            data = pd.read_csv(
                path,
                sep=delimiter,
                skiprows=skiprows,
                skipfooter=0,
                header=header,
                engine="python",
            )
            LogicHelper.logger.log_debug(f"{len(data)} records found from {path}.")
            return data
        except Exception as e:
            message = f"Request exception from {path} - `{format(e)}`."
            LogicHelper.logger.log_critical(message=message)
            raise
