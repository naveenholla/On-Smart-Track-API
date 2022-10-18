import pytest

from ontrack.market_lookup.logic.data_pull import DataPull
from ontrack.utils.config import Configurations


@pytest.mark.integration
@pytest.mark.parametrize(
    "index_name",
    [
        "India Vix",
        "Nifty 50",
        "Nifty Total Market",
        "Nifty Bank",
        "Nifty Pharma",
        "Nifty Realty",
    ],
)
def test_pull_indices_market_cap(index_name):
    urls = Configurations.get_urls_config()

    datapull_obj = DataPull()
    indices_percentage_urls = urls["indices_percentage"]
    record = [x for x in indices_percentage_urls if x["name"] == index_name][0]
    result = datapull_obj.pull_indices_market_cap(record)

    if "url" not in record:
        assert result is None
    else:
        assert result is not None
        assert len(result) == 2

        datapull_obj.parse_indices_market_cap(result[0])


@pytest.mark.integration
@pytest.mark.slow
def test_pull_indices_market_cap_all():
    urls = Configurations.get_urls_config()

    datapull_obj = DataPull()
    indices_percentage_urls = urls["indices_percentage"]
    for record in indices_percentage_urls:
        result = datapull_obj.pull_indices_market_cap(record)
        if "url" not in record:
            assert result is None
        else:
            assert result is not None
            assert len(result) == 2
