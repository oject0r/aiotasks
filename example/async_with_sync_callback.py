from aioqueues import AioTasks
import asyncio

aiotasks = AioTasks()

def sync_callback(result):
    # Synchronous callback for an asynchronous task
    print(f"Sync callback received result: {result}")

@aiotasks.task(seconds=4, callback=sync_callback)
async def async_task_with_sync_callback():
    # Asynchronous periodic task
    print("Async task executed")
    return "Async result"

async def main():
    # Running the mixed task
    await asyncio.sleep(12)  # Allow the task to run multiple iterations

asyncio.run(main())
