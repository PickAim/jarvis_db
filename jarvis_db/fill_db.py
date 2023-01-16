import asyncio
import time

from jdu.request.downloading.wildberries import SyncWildBerriesDataProvider, AsyncWildberriesDataProvider
from db_config import session
from jarvis_db.fill.db_fillers import SyncWildberriesDBFiller, AsyncWildberriesDbFiller
from create_tables import create_tables


def fill_db():
    key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NJRCI6IjZkNDVmMmRjLTQ5ODEtNDFlOS1hMzRkLTlhNDA5YmY2MGZiMSJ9' \
          '.1VoUp9Od9dzSWSNVSQjQnRujUvqOUY4oxO-pZXAqI1Q '
    wildberries_api = SyncWildBerriesDataProvider(key)
    filler = SyncWildberriesDBFiller(wildberries_api, session)
    create_tables()
    filler.fill_categories()
    filler.fill_niches()
    filler.fill_niche_products('Автобаферы')
    filler.fill_niche_price_history('Автобаферы')


async def fill_db_async():
    key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NJRCI6IjZkNDVmMmRjLTQ5ODEtNDFlOS1hMzRkLTlhNDA5YmY2MGZiMSJ9' \
          '.1VoUp9Od9dzSWSNVSQjQnRujUvqOUY4oxO-pZXAqI1Q '
    async with AsyncWildberriesDataProvider(key) as api:
        create_tables()
        filler = AsyncWildberriesDbFiller(api, session)
        await filler.fill_categories()
        await filler.fill_niches()
        await filler.fill_niche_products('Автобаферы')
        await filler.fill_niche_price_history('Автобаферы')


if __name__ == '__main__':
    # fix Windows event loop problem
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    start = time.time()
    asyncio.run(fill_db_async())
    print("Time: " + str(time.time() - start))
