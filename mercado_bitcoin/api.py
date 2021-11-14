from abc import ABC, abstractmethod
import datetime
import logging
import ratelimit

from backoff import on_exception, expo
import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# requests.get("https://www.mercadobitcoin.net/api/BTC/day-summary/2013/6/20/").json()


class MercadoBitcoinApi(ABC):
    def __init__(self, coin: str = "btc") -> None:
        self.coin = coin.upper()
        self.base_endpoint = "https://www.mercadobitcoin.net/api/"

    @abstractmethod
    def _get_endpoint(self, **kwargs) -> str:
        pass

    @on_exception(expo, ratelimit.exception.RateLimitException, max_tries=10)
    @ratelimit.limits(calls=29, period=30)
    @on_exception(expo, requests.exceptions.HTTPError, max_tries=10)
    def get_data(self, **kwargs) -> dict:
        endpoint = self._get_endpoint(**kwargs)
        logger.info(f"Getting data from endpoint: {endpoint}")
        response = requests.get(endpoint)
        response.raise_for_status()
        return response.json()


class DaySummary(MercadoBitcoinApi):
    type = "day-summary"

    def _get_endpoint(self, date: datetime.date) -> str:
        return f"{self.base_endpoint}{self.coin}/{self.type}/{date.year}/{date.month}/{date.day}/"


class TradesApi(MercadoBitcoinApi):
    type = "trades"

    def _get_unix_epoch(self, date: datetime.datetime) -> int:
        seconds = (date - datetime.datetime(1970, 1, 1)).total_seconds()
        return int(seconds)

    def _get_endpoint(self, initial_date: datetime.datetime, end_date: datetime.datetime) -> str:
        if initial_date and end_date:
            if initial_date > end_date:
                raise RuntimeError("initial_date cannot be greater than end date.")
            unix_initial_date = self._get_unix_epoch(initial_date)
            unix_end_date = self._get_unix_epoch(end_date)
            return f"{self.base_endpoint}{self.coin}/{self.type}/{unix_initial_date}/{unix_end_date}/"
        elif initial_date:
            unix_initial_date = self._get_unix_epoch(initial_date)
            return f"{self.base_endpoint}{self.coin}/{self.type}/{unix_initial_date}/"
        else:
            return f"{self.base_endpoint}{self.coin}/{self.type}/"
