import pandas as pd
from django.db import transaction
from django.utils.text import slugify

from ontrack.lookup.models import Setting as AdminSetting
from ontrack.market.logic.data_pull import DataPull
from ontrack.utils.base.enum import AdminSettingKey, ExchangeType
from ontrack.utils.config import Configurations
from ontrack.utils.context import (
    application_context,
    application_context_destroy,
    get_context_value_by_key,
    get_correlation_id,
)
from ontrack.utils.datetime import DateTimeHelper
from ontrack.utils.exception import Error_While_Data_Pull
from ontrack.utils.logger import ApplicationLogger
from ontrack.utils.logic import LogicHelper

from ..models.equity import Equity, Index
from ..models.index import EquityIndex
from ..models.lookup import Exchange
from ..serializers.lookup import ExchangeSerializer


class LookupDataPullLogic:
    def __init__(self):
        self.logger = ApplicationLogger()

    def create_lookup_files(self):
        exchanges = Exchange.backend.all()
        Configurations.save_exchanges(ExchangeSerializer(exchanges, many=True).data)

    def can_run_pull_equity_lookup_data_task(self):
        date_key = AdminSettingKey.DATAPULL_EQUITY_LOOKUP_DATE
        days_pause_key = AdminSettingKey.DATAPULL_EQUITY_LOOKUP_DAY_PAUSE

        last_pull_date = AdminSetting.backend.get_setting(date_key)
        days_pause = AdminSetting.backend.get_setting(days_pause_key)

        if days_pause is None:
            days_pause = Configurations.get_default_values_config()[
                "default_datapull_equity_lookup_pause"
            ]

        if last_pull_date is not None:
            date = DateTimeHelper.string_to_datetime(last_pull_date)
            if DateTimeHelper.current_date_time() < DateTimeHelper.get_future_date(
                date=date, days=days_pause
            ):
                return False
        return True

    def save_pull_equity_lookup_data_task_time(self):
        date_key = AdminSettingKey.DATAPULL_EQUITY_LOOKUP_DATE
        AdminSetting.backend.save_setting(
            date_key,
            DateTimeHelper.convert_datetime_to_string(
                DateTimeHelper.current_date_time()
            ),
        )

    def pull_equity_data(self, urls):
        url = urls["listed_equities"]  # get the all listed equity url

        self.logger.log_debug(f"Started with {url}.")

        # fetch page source using requests.get()
        data = LogicHelper.reading_csv_pandas_web(
            url=url
        )  # pull csv containing all the listed equities from web
        data.columns = (
            data.columns.str.strip()
        )  # remove extra spaces from the column names
        data.rename(
            columns={"SYMBOL": "symbol", "NAME OF COMPANY": "name"}, inplace=True
        )  # rename the column name
        data["symbol"] = data.symbol.str.strip()  # remove whitespace from the data
        data["name"] = data.name.str.strip()  # remove whitespace from the data
        data = data[["symbol", "name"]]  # select only specific columns
        data = data.assign(exchange_name=get_context_value_by_key(key="exchange_name"))
        self.logger.log_debug(f"{data.count}")

        return data

    def pull_equity_marketlot_data(self, urls):
        url = urls["fo_marketlot"]  # get the all listed equity url

        self.logger.log_debug(f"Started with {url}.")

        data = LogicHelper.reading_csv_pandas_web(
            url=url
        )  # pull csv containing the market lot for the equities
        data.columns = (
            data.columns.str.strip()
        )  # remove extra spaces from the column names
        data.rename(
            columns={"SYMBOL": "symbol"}, inplace=True
        )  # rename the column name
        data.columns.values[2] = "lot_size"  # rename the column name
        data["symbol"] = data.symbol.str.strip()  # remove whitespace from the data
        data["lot_size"] = data.lot_size.str.strip()  # remove whitespace from the data
        data = data.iloc[:, 1:3]  # select only specific columns
        self.logger.log_debug(f"{data.count}")

        return data

    def pull_indices_market_cap(self, record):
        # get indices details
        index_name = str(record["name"])
        index_symbol = record["symbol"]
        index_is_sectoral = bool(record["is_sector"])

        data_updated = DataPull().pull_indices_market_cap(record)

        try:
            df = pd.json_normalize(
                data_updated[0]["groups"],
                "groups",
                ["label", "weight", "id"],
                record_prefix="_",
            )
            df["label"] = df["label"].str.rsplit(" ", n=1).str.get(0)
            df["_label"] = df["_label"].str.rsplit(" ", n=1).str.get(0)
            df = df.assign(name=index_name)
            df = df.assign(index_symbol=index_symbol)
            df = df.assign(is_sector=index_is_sectoral)
            df.rename(
                columns={
                    "_label": "symbol",
                    "_weight": "equity_weightage",
                    "label": "sector_name",
                    "weight": "sector_weightage",
                },
                inplace=True,
            )  # rename the column name
        except Exception:
            # exception will be thrown if there is no nested records
            df = pd.DataFrame(data_updated[0]["groups"])
            df["label"] = df["label"].str.rsplit(" ", n=1).str.get(0)
            df = df.assign(sector_name=index_name.replace("_", " "))
            df = df.assign(name=index_name)
            df = df.assign(index_symbol=index_symbol)
            df = df.assign(sector_weightage=100)
            df = df.assign(is_sector=index_is_sectoral)
            df.rename(
                columns={"label": "symbol", "weight": "equity_weightage"},
                inplace=True,
            )  # rename the column name

        self.logger.log_debug(f"{df.count}")
        return df

    @transaction.atomic
    def save_equity_sectors_from_indices(self, data):
        equities = Equity.backend.all()
        indices = Index.backend.all()

        records_to_create = []
        records_to_update = []
        for _, record in data.iterrows():
            obj = EquityIndex.backend.unique_search(record).first()
            index = indices.unique_search(record).first()
            equity = equities.unique_search(record).first()

            if equity is None:
                self.logger.log_warning(
                    f"Can't find equity with name [symbol='{record['symbol']}',"
                    "name='{record['name']}', sector_name='{record['sector_name']}']."
                )
                continue

            if index is None:
                self.logger.log_warning(
                    f"Can't find sector with name [symbol='{record['symbol']}',"
                    "name='{record['name']}', sector_name='{record['sector_name']},"
                    " index_symbol='{record['index_symbol']}']."
                )
                continue

            if obj is None:
                d = EquityIndex(
                    index=index,
                    equity=equity,
                    equity_weightage=float(record["equity_weightage"]),
                    sector=record["sector_name"],
                    sector_weightage=float(record["sector_weightage"]),
                    updated_at=DateTimeHelper.current_date_time(),
                    created_at=DateTimeHelper.current_date_time(),
                )
                records_to_create.append(d)
            else:
                d = EquityIndex(
                    id=obj.id,
                    index=index,
                    equity=equity,
                    equity_weightage=float(record["equity_weightage"]),
                    sector=record["sector_name"],
                    sector_weightage=float(record["sector_weightage"]),
                    updated_at=DateTimeHelper.current_date_time(),
                )
                records_to_update.append(d)

        EquityIndex.backend.bulk_create_or_update(
            records_to_create,
            records_to_update,
            [
                "index",
                "equity",
                "equity_weightage",
                "sector",
                "sector_weightage",
                "updated_at",
            ],
        )

        return f"{len(records_to_create)} records created, {len(records_to_update)} records updated."

    @transaction.atomic
    def pull_and_save_equity_data(self):
        urls = Configurations.get_urls_config()  # get the urls from configurations
        data = self.pull_equity_data(urls)  # pull equity data
        data_marketlot = self.pull_equity_marketlot_data(urls)  # pull market lot size

        # merge two dataframes
        mergedRecords = pd.merge(data, data_marketlot, on="symbol", how="left")
        mergedRecords["lot_size"] = mergedRecords["lot_size"].fillna(
            0
        )  # set 0 to null values
        # records = mergedRecords.to_dict('records') # convert to dictionary

        exchanges = Exchange.backend.all()

        records_to_create = []
        records_to_update = []
        for _, record in mergedRecords.iterrows():
            obj = Equity.backend.unique_search(record).first()
            exchange = exchanges.unique_search(record).first()

            if exchange is None:
                self.logger.log_warning(
                    f"Can't find exchange with name [symbol='{record['symbol']}'"
                    ",name='{record['name']}', "
                    "exchange_name='{record['exchange_name']}']."
                )
                continue

            if obj is None:
                d = Equity(
                    exchange=exchange,
                    name=record["name"],
                    lot_size=int(record["lot_size"]),
                    symbol=record["symbol"],
                    chart_symbol=record["chart_symbol"]
                    if "chart_symbol" in record
                    else record["symbol"],
                    slug=slugify(f"{exchange.name}:{record['symbol']}"),
                    strike_difference=0,
                    updated_at=DateTimeHelper.current_date_time(),
                    created_at=DateTimeHelper.current_date_time(),
                )
                records_to_create.append(d)
            else:
                d = Equity(
                    id=obj.id,
                    exchange=exchange,
                    name=record["name"],
                    lot_size=int(record["lot_size"]),
                    symbol=record["symbol"],
                    chart_symbol=record["chart_symbol"]
                    if "chart_symbol" in record
                    else record["symbol"],
                    slug=slugify(f"{exchange.name}:{record['symbol']}"),
                    strike_difference=0,
                    updated_at=DateTimeHelper.current_date_time(),
                )
                records_to_update.append(d)

        Equity.backend.bulk_create_or_update(
            records_to_create,
            records_to_update,
            [
                "exchange",
                "name",
                "lot_size",
                "symbol",
                "chart_symbol",
                "slug",
                "strike_difference",
                "updated_at",
            ],
        )
        return f"{len(records_to_create)} records created, {len(records_to_update)} records updated."

    def pull_and_save_index_data(self):
        urls = Configurations.get_urls_config()
        indices_percentage_urls = urls["indices_percentage"]
        data_marketlot = self.pull_equity_marketlot_data(urls)  # pull market lot size

        exchanges = Exchange.backend.all()

        data_day_list = []
        records_to_create = []
        records_to_update = []
        for record in indices_percentage_urls:
            record["exchange_name"] = get_context_value_by_key(key="exchange_name")
            marketlot_record = data_marketlot[
                data_marketlot["symbol"] == record["symbol"]
            ]
            record["lot_size"] = 0
            if not marketlot_record.empty:
                for _, record_lot in marketlot_record.iterrows():
                    record["lot_size"] = record_lot["lot_size"]
                    break

            obj = Index.backend.unique_search(record).first()
            exchange = exchanges.unique_search(record).first()

            index_name = str(record["name"])
            index_symbol = record["symbol"]
            index_chart_symbol = (
                record["chart_symbol"] if "chart_symbol" in record else index_symbol
            )
            index_lot_size = record["lot_size"]
            index_ordinal = record["ordinal"]
            index_is_sectoral = bool(record["is_sector"])
            index_is_active = bool(record["is_active"])
            index_slug = slugify(f"{exchange.name}:{record['symbol']}")

            if exchange is None:
                self.logger.log_warning(
                    f"Can't find exchange with name [symbol='{record['symbol']}',"
                    "name='{record['name']}', exchange_name='{record['exchange_name']}']."
                )
                continue

            if obj is None:
                d = Index(
                    exchange=exchange,
                    name=index_name,
                    symbol=index_symbol,
                    chart_symbol=index_chart_symbol,
                    lot_size=index_lot_size,
                    ordinal=index_ordinal,
                    slug=index_slug,
                    is_sectoral=index_is_sectoral,
                    is_active=index_is_active,
                    strike_difference=0,
                    updated_at=DateTimeHelper.current_date_time(),
                    created_at=DateTimeHelper.current_date_time(),
                )
                records_to_create.append(d)

            else:
                d = Index(
                    id=obj.id,
                    exchange=exchange,
                    name=index_name,
                    symbol=index_symbol,
                    chart_symbol=index_chart_symbol,
                    lot_size=index_lot_size,
                    ordinal=index_ordinal,
                    slug=index_slug,
                    is_sectoral=index_is_sectoral,
                    is_active=index_is_active,
                    strike_difference=0,
                    updated_at=DateTimeHelper.current_date_time(),
                )
                records_to_update.append(d)

            if "url" in record:
                data = self.pull_indices_market_cap(record)
                data_day_list.append(data)
                self.logger.log_debug(
                    f"{len(data_day_list)} records found for {record['name']}."
                )

        Index.backend.bulk_create_or_update(
            records_to_create,
            records_to_update,
            [
                "exchange",
                "name",
                "lot_size",
                "symbol",
                "chart_symbol",
                "slug",
                "strike_difference",
                "ordinal",
                "is_sectoral",
                "is_active",
                "strike_difference",
                "updated_at",
            ],
        )

        concatenate_dataframe = pd.concat(data_day_list)
        return concatenate_dataframe

    def pull_and_save_indices_percentages(self):
        records = self.pull_and_save_index_data()

        output = ""
        result = self.save_equity_sectors_from_indices(records)
        output += f"[{result}]"

        return output

    def delete_old_records(self):
        EquityIndex.backend.delete_old_records()

    def execute_equity_lookup_data_task(self):
        try:
            output = ""
            correlationid = get_correlation_id()
            with application_context(
                correlationid=correlationid, exchange_name=ExchangeType.NSE
            ):

                self.logger.log_info("Started pull_equity_lookup_data task.")

                if not self.can_run_pull_equity_lookup_data_task():
                    message = "Task is paused for time being."
                    self.logger.log_info(message)
                    return message

                result = self.pull_and_save_equity_data()
                output += f"[{result}]"

                result = self.pull_and_save_indices_percentages()
                output += f"[{result}]"

                self.delete_old_records()

                self.save_pull_equity_lookup_data_task_time()
                self.logger.log_info(
                    f"Completed pull_equity_lookup_data task. {output}"
                )
                application_context_destroy()
            return output

        except Exception as e:
            message = (
                f"Request exception from pull_equity_lookup_data task - `{format(e)}`."
            )
            self.logger.log_critical(message=message)
            raise Error_While_Data_Pull() from e

    def execute_create_lookup_data_files(self):
        try:
            correlationid = get_correlation_id()
            with application_context(
                correlationid=correlationid, exchange_name=ExchangeType.NSE
            ):

                self.logger.log_info("Started execute_create_lookup_data_files task.")

                self.create_lookup_files()

                self.logger.log_info("Completed execute_create_lookup_data_files task.")
                application_context_destroy()
            return "Done"
        except Exception as e:
            message = f"Request exception from execute_create_lookup_data_files task - `{format(e)}`."
            self.logger.log_critical(message=message)
            raise Error_While_Data_Pull() from e
