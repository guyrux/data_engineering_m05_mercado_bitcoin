import datetime
from unittest.mock import patch

import pytest
from _pytest.fixtures import fixture
import requests
from requests import status_codes

from mercado_bitcoin.api import DaySummary, TradesApi, MercadoBitcoinApi


class TestDaySummary:
    @pytest.mark.parametrize(
        "coin, date, expected",
        [
            ("BTC", datetime.date(2021, 6, 21), "https://www.mercadobitcoin.net/api/BTC/day-summary/2021/6/21/"),
            ("ETH", datetime.date(2021, 6, 21), "https://www.mercadobitcoin.net/api/ETH/day-summary/2021/6/21/"),
            ("BTC", datetime.date(2019, 1, 1), "https://www.mercadobitcoin.net/api/BTC/day-summary/2019/1/1/"),
        ]
    )
    def test_get_endpoint(self, coin, date, expected):
        actual = DaySummary(coin=coin)._get_endpoint(date=date)
        assert actual == expected

class TestTradesApi:
    @pytest.mark.parametrize(
        "coin, initial_date, end_date, expected",
        [
            ("TESTE", datetime.datetime(2019, 1, 1), datetime.datetime(2019, 1, 2), "https://www.mercadobitcoin.net/api/TESTE/trades/1546300800/1546387200/"),
            ("TESTE", datetime.datetime(2019, 1, 1), None, "https://www.mercadobitcoin.net/api/TESTE/trades/1546300800/"),
            ("TESTE", None, None, "https://www.mercadobitcoin.net/api/TESTE/trades/"),
        ]
    )
    def test_get_endpoint(self, coin, initial_date, end_date, expected):
        actual = TradesApi(coin=coin)._get_endpoint(initial_date=initial_date, end_date=end_date)
        assert actual == expected

    def test_get_endpoint_initail_date_greater_than_end_date(self):
        with pytest.raises(RuntimeError):
            TradesApi(coin="TESTE")._get_endpoint(
                initial_date=datetime.datetime(2021,1,1,0,0,0),
                end_date=datetime.datetime(2019,1,1,0,0,0)
            )


    @pytest.mark.parametrize(
        "date, expected",
        [
            (datetime.datetime(2019,1,1), 1546300800),
            (datetime.datetime(2019,1,1,0,0,0), 1546300800),
            (datetime.datetime(2021,1,1,0,0,0), 1609459200),
        ]
    )
    def test_get_unix_epoch(self, date, expected):
        actual = TradesApi(coin="TEST")._get_unix_epoch(date)
        assert actual == expected

@pytest.fixture()
@patch("mercado_bitcoin.api.MercadoBitcoinApi.__abstractmethods__", set())
def fixture_mercado_bitcoin_api():
    return MercadoBitcoinApi(
        coin="test"
        )

def mocked_requests_get(*args, **kwargs):
    class MockResponse(requests.Response):
        def __init__(self, json_data, status_code) -> None:
            super().__init__()
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        def raise_for_status(self) -> None:
            if self.status_code != 200:
                raise Exception

    if args[0] == "valid_endpoint":
        return MockResponse(json_data={"foo": "bar"}, status_code=200)
    else:
        return MockResponse(json_data=None, status_code=404)


class TestMercadoBitcoinApi:

    @patch("requests.get")
    @patch("mercado_bitcoin.api.MercadoBitcoinApi._get_endpoint", return_value="valid_endpoint")
    def test__requests_is_called(self, mock_get_endpoint, mock_requests, fixture_mercado_bitcoin_api):
        fixture_mercado_bitcoin_api.get_data()
        mock_requests.assert_called_once_with("valid_endpoint")

    @patch("requests.get", side_effect=mocked_requests_get)
    @patch("mercado_bitcoin.api.MercadoBitcoinApi._get_endpoint", return_value="valid_endpoint")
    def test_get_data_with_valid_end_point(self, mock_get_endpoint, mock_requests, fixture_mercado_bitcoin_api):
        actual = fixture_mercado_bitcoin_api.get_data()
        expected = {"foo": "bar"}
        assert actual == expected

    @patch("requests.get", side_effect=mocked_requests_get)
    @patch("mercado_bitcoin.api.MercadoBitcoinApi._get_endpoint", return_value="invalid_endpoint")
    def test_get_data_with_invalid_end_point(self, mock_get_endpoint, mock_requests, fixture_mercado_bitcoin_api):
        with pytest.raises(Exception):
            fixture_mercado_bitcoin_api.get_data()
