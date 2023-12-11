import asyncio
import datetime

class Worker:
    def __init__(self, task_func):
        self.task_func = task_func
        self.is_running = True

    async def start(self):
        print("Starting worker...")
        while self.is_running:
            await self.task_func()
            await asyncio.sleep(15 * 60)  # Sleep for 15 minutes

    def stop(self):
        self.is_running = False