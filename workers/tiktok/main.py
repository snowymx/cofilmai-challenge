
import os
import asyncio
from worker import Worker
from prisma import Prisma

prisma = Prisma(datasource={
    'url': os.environ.get('DATABASE_URL'),
})


async def scrape_tiktok_trends():
    # TODO: Implement scraping of trending TikTok videos
    pass

async def main():
    # Connecting database
    await prisma.connect()

    # Start the worker
    worker = Worker(scrape_tiktok_trends)
    await worker.start()

# Run the worker
asyncio.run(main())