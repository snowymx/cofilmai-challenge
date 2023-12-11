
import asyncio
from worker import Worker
from prisma import Prisma

async def scrape_tiktok_trends():
    prisma = Prisma()
    await prisma.connect()

    # TODO: Implement scraping of trending TikTok videos
    pass

async def main():
    # Start the worker
    worker = Worker(scrape_tiktok_trends)
    await worker.start()

# Run the worker
asyncio.run(main())