from unittest import mock

import pytest

from ontrack.utils.config import Configurations


@pytest.mark.unittest
def test_urls_config():
    url_config = Configurations.get_urls_config()
    assert "holidays" in url_config


@pytest.mark.unittest
def test_get_default_values_config():
    get_default_values_config = Configurations.get_default_values_config()
    assert "default_datapull_equity_lookup_pause" in get_default_values_config
    assert "days_for_delete_lookup_data" in get_default_values_config
    assert "days_for_delete_equity_eod_data" in get_default_values_config
    assert "days_for_delete_indices_eod_data" in get_default_values_config
    assert "default_date_format" in get_default_values_config
    assert "default_time_format" in get_default_values_config
    assert "default_date_time_format" in get_default_values_config
    assert "average_days_count" in get_default_values_config


@pytest.mark.unittest
def test_get_default_value_by_key():
    value = Configurations.get_default_value_by_key("option_chain_strick_price_count")
    assert value == 20

    value = Configurations.get_default_value_by_key(
        "option_chain_strick_price_count".upper()
    )
    assert value == 20

    value = Configurations.get_default_value_by_key("NOT_EXISTS")
    assert value is None

    value = Configurations.get_default_value_by_key(None)
    assert value is None


@pytest.mark.unittest
@pytest.mark.skip
def test_urls_config_caching():
    Configurations.clear_cache()

    with mock.patch.object(
        Configurations, "_Configurations__get_config", return_value="value"
    ) as obj_mock:
        Configurations.get_urls_config()
        Configurations.get_urls_config()
        Configurations.get_urls_config()
        obj_mock.assert_called_once()


@pytest.mark.unittest
@pytest.mark.skip
def test_get_default_values_config_caching():
    Configurations.clear_cache()

    with mock.patch.object(
        Configurations, "_Configurations__get_config", return_value="value"
    ) as obj_mock:
        Configurations.get_default_values_config()
        Configurations.get_default_values_config()
        Configurations.get_default_values_config()
        obj_mock.assert_called_once()


#     from unittest import mock

# import pytest

# from tut9.myapp.sample import guess_number, get_ip


# @pytest.mark.parametrize("_input,expected", [(3, "You won!"), (4, "You lost!")])
# @mock.patch("tut9.myapp.sample.roll_dice")
# def test_guess_number(mock_roll_dice, _input, expected):
#     mock_roll_dice.return_value = 3
#     assert guess_number(_input) == expected
#     mock_roll_dice.assert_called_once()


# @mock.patch("tut9.myapp.sample.requests.get")
# def test_get_ip(mock_requests_get):
#     mock_requests_get.return_value = mock.Mock(name="mock response",
#                                                **{"status_code": 200, "json.return_value": {"origin": "0.0.0.0"}})

#     assert get_ip() == "0.0.0.0"
#     mock_requests_get.assert_called_once_with("https://httpbin.org/ip")
