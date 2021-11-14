from abc import ABC, abstractmethod
import datetime
from typing import List

from mercado_bitcoin.api import DaySummary
from mercado_bitcoin.writers import DataWriter


class DataIngestor(ABC):

    def __init__(self, writer: DataWriter, coins: List[str], date: datetime.date) -> None:
        self.writer = writer
        self.coins = coins
        self.date = date
        self._checkpoint = self._load_checkpoint()

    @property
    def _checkpoint_filename(self) -> str:
        return f"{self.__class__.__name__}.checkpoint"

    def _write_checkpoint(self):
        with open(self._checkpoint_filename, "w") as f:
            f.write(f"{self._checkpoint}")

    def _load_checkpoint(self) -> datetime.date:
        try:
            with open(self._checkpoint_filename, "r") as f:
                return datetime.datetime.strptime(f.read(), "%Y-%m-%d").date()
        except FileNotFoundError:
            return self.date

    def _get_checkpoint(self):
        if not self._checkpoint:
            return self.date
        else:
            self._checkpoint

    def _update_checkpoint(self, value):
        self._checkpoint = value
        self._write_checkpoint()

    @abstractmethod
    def ingest(self) -> None:
        pass


class DaySummaryIngestor(DataIngestor):

    def ingest(self) -> None:
        date = self.date
        if date < datetime.date.today():
            for coin in self.coins:
                api = DaySummary(coin=coin)
                data = api.get_data(date=date)
                self.writer(coin=coin, api=api.type).write(data)
            self._update_checkpoint(date + datetime.timedelta(days=1))
