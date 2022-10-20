# import pytest

# from ontrack.market_lookup.logic.data_pull import DataPull
# from ontrack.market_lookup.logic.tests.factories import EquityFactory
# from ontrack.utils.config import Configurations
# from ontrack.market_lookup.models import Exchange

# class TestDataPull:
#     @pytest.mark.integration
#     @pytest.mark.parametrize(
#         "index_name",
#         [
#             "India Vix",
#             "Nifty 50",
#             "Nifty Total Market",
#             "Nifty Bank",
#             "Nifty Pharma",
#             "Nifty Realty",
#         ],
#     )
#     def test_pull_indices_market_cap(self, equity_fixture:EquityFactory, index_name):
#         obj = equity_fixture.create_batch()
#         assert Exchange.objects.all().count() > 0

#         urls = Configurations.get_urls_config()

#         datapull_obj = DataPull()
#         indices_percentage_urls = urls["indices_percentage"]
#         record = [x for x in indices_percentage_urls if x["name"] == index_name][0]
#         weightage_obj = datapull_obj.pull_indices_market_cap(record)
#         index_record = datapull_obj.parse_index_data("NSE", record)

#         if "url" not in record:
#             assert index_record is not None
#             assert index_record["name"] == index_name

#             assert weightage_obj is None

#         else:
#             assert index_record is not None
#             assert index_record["name"] == index_name

#             assert weightage_obj is not None
#             assert len(weightage_obj) == 2

#             records = datapull_obj.parse_indices_market_cap(
#                 record["name"], weightage_obj[0]
#             )
#             assert records is not None
#             assert len(records) > 0


#     @pytest.mark.integration
#     @pytest.mark.slow
#     def test_pull_indices_market_cap_all():
#         urls = Configurations.get_urls_config()

#         indices_percentage_urls = urls["indices_percentage"]
#         for record in indices_percentage_urls:
#             test_pull_indices_market_cap(record["name"])
