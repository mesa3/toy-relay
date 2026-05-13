import asyncio
import time
from unittest.mock import AsyncMock

async def main():
    class MockClient:
        async def send(self, message):
            await asyncio.sleep(0) # simulate IO
            pass

    clients = [MockClient() for _ in range(10)]
    loop = asyncio.get_running_loop()

    # Old way
    async def _broadcast_coro(message):
        if clients:
            await asyncio.gather(*[client.send(message) for client in clients], return_exceptions=True)

    def broadcast_old(message):
        asyncio.run_coroutine_threadsafe(_broadcast_coro(message), loop)

    # New way
    bg_tasks = set()
    async def _send_to_client(client, message):
        try:
            await client.send(message)
        except Exception:
            pass

    def _broadcast_to_clients(message):
        for client in clients:
            task = loop.create_task(_send_to_client(client, message))
            bg_tasks.add(task)
            task.add_done_callback(bg_tasks.discard)

    def broadcast_new(message):
        loop.call_soon_threadsafe(_broadcast_to_clients, message)

    # benchmark
    start = time.time()
    for _ in range(1000):
        broadcast_old("test")
    # wait for tasks
    await asyncio.sleep(1)
    print(f"Old way took: {time.time() - start - 1:.4f}s")

    start = time.time()
    for _ in range(1000):
        broadcast_new("test")
    await asyncio.sleep(1)
    print(f"New way took: {time.time() - start - 1:.4f}s")

asyncio.run(main())
