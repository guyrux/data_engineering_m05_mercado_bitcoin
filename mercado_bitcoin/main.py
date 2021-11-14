import datetime
import time

from schedule import repeat, every, run_pending

from mercado_bitcoin.ingestors import DaySummaryIngestor
from mercado_bitcoin.writers import DataWriter


if __name__ == "__main__":
    day_summary_ingestor = DaySummaryIngestor(
        writer=DataWriter,
        coins=["BTC", "ETH", "LTC"],
        date=datetime.date(2021, 10, 20)
    )

    @repeat(every(1).seconds)
    def job():
        day_summary_ingestor.ingest()

    while True:
        run_pending()
        time.sleep(0.5)
