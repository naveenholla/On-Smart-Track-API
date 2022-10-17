from unittest import mock

from ontrack.utils.config import Configurations


def test_urls_config_caching():
    with mock.patch.object(
        Configurations, "_Configurations__get_config", return_value="value"
    ) as obj_mock:
        Configurations.get_urls_config()
        Configurations.get_urls_config()
        Configurations.get_urls_config()
        obj_mock.assert_called_once()


def test_urls_config():
    url_config = Configurations.get_urls_config()
    assert "holidays" in url_config


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
