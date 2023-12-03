import asyncio
 
class CountDownLatch:
    def __init__(self, count=1):
        self.condition = asyncio.Condition()
        self.count = count

    async def wait(self):
        async with self.condition:
            while self.count > 0:
                await self.condition.wait()

    def count_down(self):
        async def _notify():
            async with self.condition:
                self.count -= 1
                if self.count <= 0:
                    self.condition.notify_all()

        asyncio.ensure_future(_notify())

    async def wait_and_count_down(self):
        async with self.condition:
            while self.count > 0:
                await self.condition.wait()
            self.count_down()